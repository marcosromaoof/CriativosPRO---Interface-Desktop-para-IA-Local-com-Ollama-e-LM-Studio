"""
Módulo de Validação de Inputs - CriativosPro
Garante que todos os dados recebidos do usuário sejam validados e sanitizados.
"""
import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse

class ValidationError(Exception):
    """Exceção customizada para erros de validação."""
    pass

class InputValidator:
    """Validador centralizado de inputs do usuário."""
    
    # Constantes de Limites
    MAX_MESSAGE_LENGTH = 50000  # 50k caracteres
    MAX_SESSION_NAME_LENGTH = 100
    MAX_PROMPT_LENGTH = 10000
    MAX_PROFILE_FIELD_LENGTH = 500
    MIN_MESSAGE_LENGTH = 1
    
    # Padrões Regex
    SESSION_ID_PATTERN = re.compile(r'^sess_\d+_[a-z0-9]{9}$')
    SAFE_STRING_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.,!?áéíóúàèìòùâêîôûãõçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ]+$')
    
    @staticmethod
    def validate_message(message: str) -> str:
        """
        Valida uma mensagem do usuário.
        
        Args:
            message: Mensagem a ser validada
            
        Returns:
            Mensagem validada e sanitizada
            
        Raises:
            ValidationError: Se a mensagem for inválida
        """
        if not isinstance(message, str):
            raise ValidationError("Mensagem deve ser uma string")
        
        # Remove espaços extras
        message = message.strip()
        
        if len(message) < InputValidator.MIN_MESSAGE_LENGTH:
            raise ValidationError("Mensagem não pode estar vazia")
        
        if len(message) > InputValidator.MAX_MESSAGE_LENGTH:
            raise ValidationError(f"Mensagem excede o limite de {InputValidator.MAX_MESSAGE_LENGTH} caracteres")
        
        return message
    
    @staticmethod
    def validate_session_id(session_id: str) -> str:
        """
        Valida um ID de sessão.
        
        Args:
            session_id: ID da sessão
            
        Returns:
            ID validado
            
        Raises:
            ValidationError: Se o ID for inválido
        """
        if not isinstance(session_id, str):
            raise ValidationError("Session ID deve ser uma string")
        
        if not InputValidator.SESSION_ID_PATTERN.match(session_id):
            raise ValidationError("Formato de Session ID inválido")
        
        return session_id
    
    @staticmethod
    def validate_provider_name(provider: str) -> str:
        """
        Valida o nome de um provedor.
        
        Args:
            provider: Nome do provedor
            
        Returns:
            Nome validado
            
        Raises:
            ValidationError: Se o provedor for inválido
        """
        ALLOWED_PROVIDERS = ['ollama', 'lmstudio']
        
        if not isinstance(provider, str):
            raise ValidationError("Nome do provedor deve ser uma string")
        
        provider = provider.lower().strip()
        
        if provider not in ALLOWED_PROVIDERS:
            raise ValidationError(f"Provedor '{provider}' não é suportado. Use: {', '.join(ALLOWED_PROVIDERS)}")
        
        return provider
    
    @staticmethod
    def validate_base_url(url: str) -> str:
        """
        Valida uma URL de servidor local.
        
        Args:
            url: URL a ser validada
            
        Returns:
            URL validada
            
        Raises:
            ValidationError: Se a URL for inválida
        """
        if not isinstance(url, str):
            raise ValidationError("URL deve ser uma string")
        
        url = url.strip()
        
        if not url:
            return url  # URL vazia é permitida (usa padrão)
        
        try:
            parsed = urlparse(url)
            
            # Deve ter scheme (http/https)
            if parsed.scheme not in ['http', 'https']:
                raise ValidationError("URL deve começar com http:// ou https://")
            
            # Deve ter netloc (host:port)
            if not parsed.netloc:
                raise ValidationError("URL deve conter host e porta")
            
            # Verificar se é localhost ou IP local
            host = parsed.hostname
            if host not in ['localhost', '127.0.0.1', '0.0.0.0'] and not host.startswith('192.168.'):
                raise ValidationError("Apenas URLs locais são permitidas")
            
            return url
            
        except Exception as e:
            raise ValidationError(f"URL inválida: {str(e)}")
    
    @staticmethod
    def validate_prompt(prompt: str) -> str:
        """
        Valida um prompt de sistema.
        
        Args:
            prompt: Prompt a ser validado
            
        Returns:
            Prompt validado
            
        Raises:
            ValidationError: Se o prompt for inválido
        """
        if not isinstance(prompt, str):
            raise ValidationError("Prompt deve ser uma string")
        
        prompt = prompt.strip()
        
        if len(prompt) > InputValidator.MAX_PROMPT_LENGTH:
            raise ValidationError(f"Prompt excede o limite de {InputValidator.MAX_PROMPT_LENGTH} caracteres")
        
        return prompt
    
    @staticmethod
    def validate_profile_data(profile: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida dados de perfil do usuário.
        
        Args:
            profile: Dicionário com dados do perfil
            
        Returns:
            Perfil validado
            
        Raises:
            ValidationError: Se algum campo for inválido
        """
        if not isinstance(profile, dict):
            raise ValidationError("Perfil deve ser um dicionário")
        
        validated = {}
        
        # Campos permitidos
        allowed_fields = ['display_name', 'email', 'gender', 'birthdate', 'custom_instructions']
        
        for field in allowed_fields:
            value = profile.get(field, '')
            
            if not isinstance(value, str):
                raise ValidationError(f"Campo '{field}' deve ser uma string")
            
            value = value.strip()
            
            if len(value) > InputValidator.MAX_PROFILE_FIELD_LENGTH:
                raise ValidationError(f"Campo '{field}' excede o limite de {InputValidator.MAX_PROFILE_FIELD_LENGTH} caracteres")
            
            validated[field] = value
        
        return validated
    
    @staticmethod
    def sanitize_for_log(data: Any, max_length: int = 100) -> str:
        """
        Sanitiza dados para exibição em logs (remove informações sensíveis).
        
        Args:
            data: Dados a serem sanitizados
            max_length: Comprimento máximo da string de log
            
        Returns:
            String sanitizada para log
        """
        if isinstance(data, str):
            # Truncar se muito longo
            if len(data) > max_length:
                return data[:max_length] + "..."
            return data
        
        if isinstance(data, dict):
            # Ocultar campos sensíveis
            sensitive_fields = ['api_key', 'password', 'token', 'secret']
            sanitized = {}
            for key, value in data.items():
                if any(field in key.lower() for field in sensitive_fields):
                    sanitized[key] = "***HIDDEN***"
                else:
                    sanitized[key] = InputValidator.sanitize_for_log(value, max_length)
            return str(sanitized)
        
        return str(data)[:max_length]

# Instância global
validator = InputValidator()
