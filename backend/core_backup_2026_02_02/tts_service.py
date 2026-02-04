import os
import re
import wave
import asyncio
from core.fsm import fsm, SystemState

# Tenta importar a biblioteca Piper. Se falhar, define flag de erro.
try:
    from piper.voice import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    print("[TTS] Biblioteca 'piper' não encontrada. Instale com 'pip install piper-tts'.")

class TTSService:
    """Serviço de síntese de voz local usando biblioteca Piper Python."""
    
    def __init__(self, model_path="backend/bin/piper/pt_BR-faber-medium.onnx"):
        self.model_path = model_path
        self._is_enabled = True
        self.voice = None
        
        if PIPER_AVAILABLE:
            self._load_model()
        else:
            print("[TTS] Serviço desativado por falta de dependências.")
            self._is_enabled = False

    def _load_model(self):
        """Carrega o modelo de voz na memória."""
        if not os.path.exists(self.model_path):
            print(f"[TTS] Modelo não encontrado em: {self.model_path}")
            self._is_enabled = False
            return

        try:
            print(f"[TTS] Carregando modelo de voz: {self.model_path} ...")
            # Carrega o modelo ONNX e config JSON
            # Nota: dependendo da versão do piper-tts, pode precisar do config path explícito
            # Mas geralmente ele acha o .onnx.json automaticamente se tiver mesmo nome
            self.voice = PiperVoice.load(self.model_path)
            print("[TTS] Modelo carregado com sucesso.")
        except Exception as e:
            print(f"[TTS] Erro ao carregar modelo Piper: {e}")
            self._is_enabled = False

    def _clean_text(self, text):
        """Remove markdown e caracteres especiais."""
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'[\*\#\_\[\]\(\)\>\|\-]', '', text)
        text = " ".join(text.split())
        return text

    async def speak(self, text, filename=None):
        """Sintetiza áudio usando a lib Python diretamente."""
        if not self._is_enabled or not self.voice:
            print("[TTS] Serviço indisponível ou modelo não carregado.")
            return None

        clean_text = self._clean_text(text)
        if not clean_text:
            return None

        if not filename:
            import time
            filename = f"speech_{int(time.time())}.wav"
            
        audio_dir = os.path.join(os.getcwd(), "backend", "temp_audio")
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
            
        output_path = os.path.join(audio_dir, filename)

        print(f"[TTS] Sintetizando para: {filename}")
        fsm.change_to(SystemState.SPEAKING)

        try:
            # Operação bloqueante (CPU intensive), rodar em thread separada para não travar async loop
            await asyncio.to_thread(self._synthesize_sync, clean_text, output_path)
            
            fsm.change_to(SystemState.IDLE)
            return filename
        except Exception as e:
            print(f"[TTS] Erro na síntese: {e}")
            fsm.change_to(SystemState.IDLE)
            return None

    def _synthesize_sync(self, text, output_path):
        """Método síncrono que roda na thread."""
        with wave.open(output_path, "wb") as wav_file:
            self.voice.synthesize(text, wav_file)

# Instância global
tts_service = TTSService()
