import os
import re
import asyncio
import subprocess
import time
import shutil
import threading
from core.fsm import fsm, SystemState

class TTSService:
    """
    Serviço de síntese de voz usando o executável Piper local.
    Abordagem via subprocesso para evitar conflitos de DLL da lib Python.
    """
    
    def __init__(self):
        # Caminhos absolutos
        self.base_dir = os.getcwd()
        self.piper_dir = os.path.join(self.base_dir, "backend", "bin", "piper")
        
        # Seleciona executável baseado no SO
        piper_filename = "piper.exe" if os.name == 'nt' else "piper"
        self.piper_exe = os.path.join(self.piper_dir, piper_filename)
        
        self.model_path = os.path.join(self.piper_dir, "pt_BR-faber-medium.onnx")
        self.output_dir = os.path.join(self.base_dir, "backend", "temp_audio")
        
        self._is_enabled = True
        
        # Validação inicial
        if not os.path.exists(self.piper_exe):
            print(f"[TTS] ERRO CRÍTICO: Executável não encontrado em {self.piper_exe}")
            self._is_enabled = False
        
        if not os.path.exists(self.model_path):
            print(f"[TTS] ERRO CRÍTICO: Modelo não encontrado em {self.model_path}")
            self._is_enabled = False
            
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        if self._is_enabled:
            print("[TTS] Serviço inicializado usando Piper CLI.")
            # Iniciar limpeza em background
            threading.Thread(target=self.cleanup_temp_files, daemon=True).start()

    def _clean_text(self, text):
        """
        Limpa o texto para o TTS, otimizando a prosódia (ritmo/pausas).
        Converte estrutura visual (markdown, parágrafos) em pontuação auditiva.
        """
        if not text: return ""

        # 1. Estrutura Markdown para Pontuação (Prosódia Artificial)
        # Títulos (# ...) -> Ponto final.
        text = re.sub(r'#+\s+(.*?)\n', r'\1. ', text)
        # Listas (- ... ou * ...) -> Ponto final.
        text = re.sub(r'[\-\*]\s+(.*?)\n', r'\1. ', text)
        
        # 2. Remover blocos de código e tecnicidades mudas
        text = re.sub(r'```[\s\S]*?```', ' código omitido. ', text)
        text = re.sub(r'`[^`]*`', '', text) 
        
        # 3. Links e HTML
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'<[^>]+>', '', text)
        
        # 4. Converter Quebras de Linha em Pausas
        # Parágrafos duplos (\n\n) -> Pausa longa (...)
        text = re.sub(r'\n\s*\n', '... ', text)
        # Quebra simples -> Vírgula ou Ponto (contexto) - Vamos usar Ponto para garantir.
        text = re.sub(r'\n', '. ', text)
        
        # 5. Lista Branca (Whitelist)
        # Preserva letras, números e pontuação de pausa (.,!?;:)
        allowed_pattern = r"[^a-zA-Z0-9\s\.,!?;:áàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ\-\'\"]"
        text = re.sub(allowed_pattern, '', text)
        
        # 6. Limpeza final de pontuação duplicada
        # Evitar ".." ou ",." gerado pelas substituições acima
        text = re.sub(r'\.{2,}', '.', text) # remove reticencias excessivas (mantem 1 ponto) se colou
        text = re.sub(r'\s+', ' ', text).strip() # Normaliza espaços
        
        # Correção fina: Reticências propositais do passo 4 podem ter virado um ponto só no passo 6? 
        # Ajuste: Se quisermos reticências, o passo 6 atrapalha. Vamos simplificar:
        # Piper entende melhor ponto final e vírgula.
        
        return text

    async def speak(self, text, filename=None):
        if not self._is_enabled:
            return None

        clean_text = self._clean_text(text)
        if not clean_text:
            return None

        if not filename:
            filename = f"speech_{int(time.time())}.wav"
            
        # O Piper CLI cria o arquivo no CWD, então usamos um nome temp lá e movemos depois
        temp_filename = f"temp_{int(time.time())}_{id(text)}.wav"
        temp_path = os.path.join(self.piper_dir, temp_filename)
        final_path = os.path.join(self.output_dir, filename)

        print(f"[TTS] Sintetizando: '{clean_text[:50]}...'")
        fsm.change_to(SystemState.SPEAKING)

        try:
            # Executa subprocesso de forma assíncrona (non-blocking) wrappada
            await asyncio.to_thread(self._run_piper_process, clean_text, temp_filename)
            
            # Verificar se gerou
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
                # Mover para pasta de audio pública
                shutil.move(temp_path, final_path)
                print(f"[TTS] Áudio gerado com sucesso: {filename}")
                result = filename
            else:
                print("[TTS] Falha: Arquivo não gerado ou muito pequeno.")
                result = None

        except Exception as e:
            print(f"[TTS] Erro na síntese: {e}")
            result = None
        finally:
            fsm.change_to(SystemState.IDLE)
            # Limpeza de emergência do temp se sobrou
            if os.path.exists(temp_path):
                try: os.remove(temp_path)
                except: pass
                
        return result

    def _run_piper_process(self, text, output_filename):
        """Roda o executável piper.exe bloqueando a thread (mas ok dentro de run_in_executor)."""
        cmd = [
            self.piper_exe,
            "--model", self.model_path,
            "--output_file", output_filename
        ]
        
        try:
            # Importante: cwd=self.piper_dir para achar DLLs
            # Configuração específica para esconder a janela no Windows
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.piper_dir,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            stdout, stderr = process.communicate(input=text.encode('utf-8'))
            
            if process.returncode != 0:
                print(f"[TTS] Piper exited with code {process.returncode}")
                print(f"[TTS] STDERR: {stderr.decode()}")
                
        except Exception as e:
            print(f"[TTS] Subprocess error: {e}")

    def cleanup_temp_files(self):
        """Remove arquivos de áudio mais antigos que 24h."""
        if not os.path.exists(self.output_dir): return
        
        now = time.time()
        print("[TTS] Iniciando monitor de limpeza...")
        while True: # Loop contínuo a cada hora
            try:
                for f in os.listdir(self.output_dir):
                    path = os.path.join(self.output_dir, f)
                    if os.path.isfile(path) and path.endswith('.wav'):
                        if now - os.path.getmtime(path) > 86400: # 24h
                            try: 
                                os.remove(path)
                                print(f"[TTS] Arquivo limpo: {f}")
                            except Exception: pass
            except Exception as e:
                 print(f"[TTS] Erro no cleanup: {e}")
            
            time.sleep(3600) # Dorme 1 hora

# Instância global
tts_service = TTSService()
