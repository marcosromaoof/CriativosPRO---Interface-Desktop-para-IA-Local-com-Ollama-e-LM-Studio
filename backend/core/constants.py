"""
Constantes Centralizadas - CriativosPro
Define todas as constantes usadas no sistema para facilitar manutenção.
"""

import os

# === Provedores de IA ===
SUPPORTED_PROVIDERS = ['ollama', 'lmstudio']
DEFAULT_PROVIDER = 'ollama'

# === Configurações de Rede ===
BACKEND_PORT = 5678
BACKEND_HOST = '127.0.0.1'
CORS_ALLOWED_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']

# === Limites de Validação ===
MAX_MESSAGE_LENGTH = 50000  # 50k caracteres
MAX_SESSION_NAME_LENGTH = 100
MAX_PROMPT_LENGTH = 10000
MAX_PROFILE_FIELD_LENGTH = 500
MIN_MESSAGE_LENGTH = 1

# === Timeouts (em segundos) ===
STREAM_TIMEOUT = 300  # 5 minutos
CONNECTION_TIMEOUT = 30
THINKING_DELAY_MS = 600  # Delay para efeito de "pensando"

# === Rate Limiting ===
MAX_MESSAGES_PER_MINUTE = 20
MAX_CONCURRENT_SESSIONS = 5

# === Caminhos de Diretórios ===
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_DIR = os.path.join(ROOT_DIR, 'temp_audio')
PROVIDERS_DIR = 'providers'

# === Estados do Sistema ===
class SystemState:
    IDLE = "IDLE"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"
    WAITING_INPUT = "WAITING_INPUT"

# === Tipos de Mensagens ===
class MessageRole:
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

# === Eventos WebSocket ===
class SocketEvents:
    # Client -> Server
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    SEND_MESSAGE = "send_message"
    CANCEL_GENERATION = "cancel_generation"
    SAVE_API_KEYS = "save_api_keys"
    SYNC_PROVIDER_MODELS = "sync_provider_models"
    TOGGLE_MODEL = "toggle_model"
    TOGGLE_PROVIDER = "toggle_provider"
    
    # Server -> Client
    SYSTEM_STATUS = "system_status"
    MODELS_DATA = "models_data"
    TEXT_CHUNK = "text_chunk"
    GENERATION_COMPLETE = "generation_complete"
    ERROR = "error"
    KEYS_SAVED = "keys_saved"
    SYNC_ERROR = "sync_error"

# === Configurações de Logging ===
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_LEVEL_PRODUCTION = 'INFO'
LOG_LEVEL_DEVELOPMENT = 'DEBUG'

# === Configurações de Criptografia ===
ENCRYPTION_KEY_FILE = 'security.key'
ENCRYPTION_ALGORITHM = 'Fernet'

# === Configurações de Banco de Dados ===
DB_NAME = 'criativospro.db'
DB_TIMEOUT = 10  # segundos

# === URLs Padrão dos Provedores ===
DEFAULT_URLS = {
    'ollama': 'http://localhost:11434',
    'lmstudio': 'http://localhost:1234'
}

# === Prompts de Sistema Padrão ===
DEFAULT_SYSTEM_PROMPTS = {
    'ollama': 'Você é o CriativosPro, um assistente local otimizado. Respeite rigorosamente a gramática e pontuação do Português Brasileiro.',
    'lmstudio': 'Você é o CriativosPro, um assistente local otimizado. Use Markdown para destacar títulos e partes importantes.'
}
