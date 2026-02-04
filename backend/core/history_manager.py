import json
import json
import sqlite3
import asyncio
from core.database import db
import uuid
from datetime import datetime

class HistoryManager:
    """Gerencia o armazenamento e recuperação do histórico de conversas."""
    
    # Lista negra de saudações que não devem iniciar uma sessão persistente
    IGNORED_GREETINGS = [
        "oi", "ola", "olá", "bom dia", "boa tarde", "boa noite", 
        "teste", "hello", "hi", "hey", "testando"
    ]

    def __init__(self, context_limit=10):
        self.context_limit = context_limit
        self._ensure_sessions_table()

    def _ensure_sessions_table(self):
        """Garante que a tabela de sessões existe e atualiza esquema se necessário."""
        try:
            with sqlite3.connect(db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_persistent BOOLEAN DEFAULT 0
                    )
                ''')
                
                # Migração: Garante que a coluna existe em bancos antigos
                try:
                    cursor.execute("ALTER TABLE sessions ADD COLUMN is_persistent BOOLEAN DEFAULT 0")
                except sqlite3.OperationalError:
                    pass  # Coluna já existe
                
                conn.commit()
        except Exception as e:
            print(f"[History] Erro ao inicializar tabela sessions: {e}")

    async def is_session_persistent(self, session_id):
        return await asyncio.to_thread(self._is_session_persistent_sync, session_id)

    def _is_session_persistent_sync(self, session_id):
        """Verifica se a sessão está marcada como persistente."""
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT is_persistent FROM sessions WHERE id = ?', (session_id,))
            row = cursor.fetchone()
            return bool(row[0]) if row else False

    async def add_message(self, session_id, role, content, metadata=None):
        await asyncio.to_thread(self._add_message_sync, session_id, role, content, metadata)

    def _add_message_sync(self, session_id, role, content, metadata=None):
        """Salva uma nova mensagem no banco de dados e verifica persistência."""
        
        # 1. Salvar na tabela de histórico (mensagens)
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO history (session_id, role, content, metadata)
                VALUES (?, ?, ?, ?)
            ''', (session_id, role, content, json.dumps(metadata) if metadata else None))
            conn.commit()

        # 2. Verificar regra de Histórico Inteligente (Smart History)
        self._check_smart_persistence(session_id, content)

    def _check_smart_persistence(self, session_id, content):
        """
        Aplica regras para decidir se a sessão deve aparecer na lista de recentes.
        Regra: Conteúdo > 250 caracteres E não ser saudação.
        """
        # Se for muito curto, ignora (exceto se a sessão JÁ estiver salva)
        if len(content) < 10 and self._is_session_saved(session_id):
            return

        # Limpeza básica
        clean_content = content.lower().strip()
        
        # Regra 1: Ignorar se for apenas saudação
        if clean_content in self.IGNORED_GREETINGS:
            return

        # Regra 2: Comprimento > 250 caracteres (ou regra acumulativa futura)
        # O usuário pediu "mais de 250 caracteres".
        # Vamos ser um pouco flexíveis: Se a mensagem for longa ONDE importa (resposta do bot ou prompt complexo)
        is_relevant_length = len(content) > 250

        # Se a sessão JÁ existe, atualizamos timestamp. Se não, criamos SÓ se for relevante.
        if self._is_session_saved(session_id):
            self._touch_session(session_id)
        elif is_relevant_length:
            # Sessão nova qualificada -> Salvar!
            title = self._generate_simple_title(content)
            self._create_session(session_id, title)

    def _is_session_saved(self, session_id):
        """Verifica se a sessão já está na tabela sessions."""
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM sessions WHERE id = ?', (session_id,))
            return cursor.fetchone() is not None

    def _create_session(self, session_id, title):
        """Cria uma nova entrada na tabela sessions."""
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (id, title, created_at, is_persistent)
                VALUES (?, ?, CURRENT_TIMESTAMP, 1)
            ''', (session_id, title))
            conn.commit()
            print(f"[History] Sessão {session_id} persistida: '{title}'")

    async def set_session_title(self, session_id, title):
        await asyncio.to_thread(self._set_session_title_sync, session_id, title)

    def _set_session_title_sync(self, session_id, title):
        """Define ou atualiza o título da sessão."""
        self._create_session(session_id, title)

    def _touch_session(self, session_id):
        """Atualiza o timestamp da sessão para ela subir na lista."""
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE sessions SET created_at = CURRENT_TIMESTAMP WHERE id = ?', (session_id,))
            conn.commit()

    async def get_full_history(self, session_id):
        return await asyncio.to_thread(self._get_full_history_sync, session_id)

    def _get_full_history_sync(self, session_id):
        """Retorna todas as mensagens da sessão para exibição."""
        with sqlite3.connect(db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Ordenar por id (autoincrement) ou timestamp se existir. O schema original não mostrou timestamp create, assumindo padrão.
            # Se não tiver timestamp na tabela history, ORDER BY rowid.
            # Mas vamos tentar timestamp.
            try:
                cursor.execute('''
                    SELECT role, content, metadata FROM history 
                    WHERE session_id = ? ORDER BY id ASC
                ''', (session_id,))
            except sqlite3.OperationalError:
                 # Fallback se não tiver order by id
                 cursor.execute('SELECT role, content, metadata FROM history WHERE session_id = ?', (session_id,))
            
            messages = []
            for row in cursor.fetchall():
                msg = {
                    "role": row["role"],
                    "content": row["content"],
                    "isUser": row["role"] == "user"
                }
                if row["metadata"]:
                    try:
                        meta = json.loads(row["metadata"])
                        # Mapear metadados úteis para o frontend
                        if isinstance(meta, dict):
                            if 'timestamp' in meta: msg['timestamp'] = meta['timestamp']
                            # Recuperar métricas se existirem
                            msg['metrics'] = {k: v for k, v in meta.items() if k in ['tokens', 'tps', 'duration']}
                    except: pass
                messages.append(msg)
            return messages

    def _generate_simple_title(self, content):
        """Gera um título simples baseado nas primeiras palavras."""
        words = content.split()
        return " ".join(words[:5]) + "..." if len(words) > 5 else content

    async def get_context(self, session_id):
        return await asyncio.to_thread(self._get_context_sync, session_id)

    def _get_context_sync(self, session_id):
        """Recupera as últimas mensagens para enviar como contexto à IA."""
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content FROM history
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, self.context_limit))
            rows = cursor.fetchall()
            messages = [{"role": role, "content": content} for role, content in reversed(rows)]
            return messages

    async def clear_session(self, session_id):
        await asyncio.to_thread(self._clear_session_sync, session_id)

    def _clear_session_sync(self, session_id):
        """Remove o histórico de uma sessão específica."""
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM history WHERE session_id = ?', (session_id,))
            # Também remove da tabela de sessões
            cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
            conn.commit()

    async def get_all_sessions(self):
        return await asyncio.to_thread(self._get_all_sessions_sync)

    def _get_all_sessions_sync(self):
        """Retorna a lista de todas as sessões salvas."""
        with sqlite3.connect(db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM sessions ORDER BY created_at DESC')
                return [dict(row) for row in cursor.fetchall()]
            except sqlite3.OperationalError:
                return []

# Instância global
history_manager = HistoryManager()
