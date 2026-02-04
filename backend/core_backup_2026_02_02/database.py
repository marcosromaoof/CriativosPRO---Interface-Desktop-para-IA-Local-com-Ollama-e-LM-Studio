import sqlite3
import os
from cryptography.fernet import Fernet

class DatabaseManager:
    def __init__(self, db_path="criativospro.db", key_path="security.key"):
        self.db_path = db_path
        self.key_path = key_path
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
        self._init_db()

    def _load_or_generate_key(self):
        """Carrega a chave de segurança ou gera uma nova no primeiro boot."""
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as key_file:
                key_file.write(key)
            return key

    def _init_db(self):
        """Inicializa as tabelas do banco de dados se não existirem."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de Configurações (Configurações globais e API Keys criptografadas)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    is_encrypted INTEGER DEFAULT 0
                )
            ''')
            
            # Tabela de Histórico de Conversas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Tabela de Licenças (Proteção Antipirataria)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS licenses (
                    license_key TEXT PRIMARY KEY,
                    status TEXT,
                    activated_at DATETIME,
                    hardware_id TEXT
                )
            ''')
            
            # Tabela de Configuração de Modelos (Fase 2)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS models_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    display_name TEXT,
                    UNIQUE(provider, model_name)
                )
            ''')
            
            # Tabela de Prompts de Sistema (Fase 2)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_type TEXT UNIQUE NOT NULL,
                    content TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Inserir prompts padrão se não existirem
            cursor.execute('''
                INSERT OR IGNORE INTO system_prompts (prompt_type, content) VALUES 
                ('general', 'Você é o CriativosPro, um assistente de IA de elite, especializado em comunicação clara, estruturada e gramaticalmente impecável.'),
                ('ollama', 'Você é o CriativosPro, um assistente local otimizado. Respeite rigorosamente a gramática e pontuação do Português Brasileiro.'),
                ('lmstudio', 'Você é o CriativosPro, um assistente local otimizado. Use Markdown para destacar títulos e partes importantes.')
            ''')
            
            # Tabela de Perfil do Usuário (Fase 2)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    display_name TEXT,
                    email TEXT,
                    gender TEXT,
                    birthdate TEXT,
                    custom_instructions TEXT
                )
            ''')
            
            # Inserir perfil padrão se não existir
            cursor.execute('''
                INSERT OR IGNORE INTO user_profile (id, display_name, custom_instructions) 
                VALUES (1, 'Usuário', '')
            ''')
            
            # Tabela de Métricas (Fase 4 - Dashboard)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    provider TEXT,
                    model TEXT,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    latency REAL,
                    status TEXT,
                    cost REAL DEFAULT 0.0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()

    def set_setting(self, key, value, encrypt=False):
        """Salva uma configuração, opcionalmente criptografando o valor."""
        if encrypt:
            value = self.cipher.encrypt(value.encode()).decode()
            is_encrypted = 1
        else:
            is_encrypted = 0
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, is_encrypted)
                VALUES (?, ?, ?)
            ''', (key, value, is_encrypted))
            conn.commit()

    def get_setting(self, key, default=None):
        """Recupera uma configuração, descriptografando se necessário."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value, is_encrypted FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            if row:
                value, is_encrypted = row
                if is_encrypted:
                    return self.cipher.decrypt(value.encode()).decode()
                return value
            return default

    # === Gerenciamento de Modelos (Fase 2) ===
    
    def sync_models(self, provider, models_list):
        """Sincroniza modelos de um provedor. Adiciona novos, mantém status dos existentes."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for model_name in models_list:
                cursor.execute('''
                    INSERT OR IGNORE INTO models_config (provider, model_name, display_name)
                    VALUES (?, ?, ?)
                ''', (provider, model_name, model_name))
            conn.commit()
    
    def get_active_models(self, provider=None):
        """Retorna apenas os modelos ativos. Se provider for None, retorna todos."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if provider:
                cursor.execute('''
                    SELECT * FROM models_config 
                    WHERE provider = ? AND is_active = 1
                ''', (provider,))
            else:
                cursor.execute('SELECT * FROM models_config WHERE is_active = 1')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_models(self, provider=None):
        """Retorna todos os modelos (ativos e inativos)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if provider:
                cursor.execute('SELECT * FROM models_config WHERE provider = ?', (provider,))
            else:
                cursor.execute('SELECT * FROM models_config')
            return [dict(row) for row in cursor.fetchall()]
    
    def toggle_model(self, provider, model_name, is_active):
        """Ativa ou desativa um modelo específico."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE models_config 
                SET is_active = ? 
                WHERE provider = ? AND model_name = ?
            ''', (1 if is_active else 0, provider, model_name))
            conn.commit()
    
    def toggle_provider(self, provider, is_active):
        """Ativa ou desativa todos os modelos de um provedor."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE models_config 
                SET is_active = ? 
                WHERE provider = ?
            ''', (1 if is_active else 0, provider))
            conn.commit()
    
    # === Gerenciamento de Prompts (Fase 2) ===
    
    def get_prompt(self, prompt_type):
        """Retorna o prompt de sistema para o tipo especificado."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT content FROM system_prompts WHERE prompt_type = ?', (prompt_type,))
            row = cursor.fetchone()
            return row[0] if row else ""
    
    def save_prompt(self, prompt_type, content):
        """Salva ou atualiza um prompt de sistema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO system_prompts (prompt_type, content, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (prompt_type, content))
            conn.commit()
    
    def get_all_prompts(self):
        """Retorna todos os prompts de sistema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM system_prompts')
            return {row['prompt_type']: row['content'] for row in cursor.fetchall()}
    
    # === Gerenciamento de Perfil (Fase 2) ===
    
    def get_user_profile(self):
        """Retorna o perfil do usuário."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_profile WHERE id = 1')
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    def save_user_profile(self, profile_data):
        """Salva ou atualiza o perfil do usuário."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_profile (id, display_name, email, gender, birthdate, custom_instructions)
                VALUES (1, ?, ?, ?, ?, ?)
            ''', (
                profile_data.get('display_name', ''),
                profile_data.get('email', ''),
                profile_data.get('gender', ''),
                profile_data.get('birthdate', ''),
                profile_data.get('custom_instructions', '')
            ))
            conn.commit()

    # === Fase 4: Telemetria e Dashboard ===

    def save_metric(self, session_id, provider, model, metrics_data):
        """Salva métricas de uma geração de IA."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO metrics (session_id, provider, model, input_tokens, output_tokens, latency, status, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id,
                provider,
                model,
                metrics_data.get('input_tokens', 0),
                metrics_data.get('output_tokens', 0),
                metrics_data.get('latency', 0.0),
                metrics_data.get('status', 'unknown'),
                metrics_data.get('cost', 0.0)
            ))
            conn.commit()
            
    def get_dashboard_stats(self):
        """Recupera estatísticas agregadas para o dashboard."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Totais Gerais
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(input_tokens) + SUM(output_tokens) as total_tokens,
                    AVG(latency) as avg_latency,
                    SUM(cost) as total_cost
                FROM metrics
            ''')
            row = cursor.fetchone()
            # Tratar caso de tabela vazia (retorna None ou valores None)
            totals = {
                "total_requests": row["total_requests"] if row and row["total_requests"] else 0,
                "total_tokens": row["total_tokens"] if row and row["total_tokens"] else 0,
                "avg_latency": row["avg_latency"] if row and row["avg_latency"] else 0.0,
                "total_cost": row["total_cost"] if row and row["total_cost"] else 0.0
            }
            
            # Estatísticas por Provedor
            cursor.execute('''
                SELECT provider, COUNT(*) as count, AVG(latency) as latency
                FROM metrics
                GROUP BY provider
            ''')
            providers = [dict(row) for row in cursor.fetchall()]
            
            return {
                "totals": totals,
                "providers": providers
            }

# Instância global para uso no backend
db = DatabaseManager()
