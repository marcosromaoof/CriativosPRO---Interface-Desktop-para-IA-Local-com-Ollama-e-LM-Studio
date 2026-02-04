"""
Módulo de Logging Estruturado - CriativosPro
Fornece logging centralizado com sanitização de dados sensíveis e formatação consistente.
Substitui o uso de print() por loggers configurados.
"""
import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from core.validators import validator
from core.constants import LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL_PRODUCTION, LOG_LEVEL_DEVELOPMENT

class SanitizedFormatter(logging.Formatter):
    """Formatter que sanitiza dados sensíveis antes de logar."""
    
    def format(self, record):
        # Se houver argumentos no log, sanitizá-los
        if record.args:
            sanitized_args = []
            if isinstance(record.args, tuple):
                for arg in record.args:
                    sanitized_args.append(validator.sanitize_for_log(arg))
                record.args = tuple(sanitized_args)
            elif isinstance(record.args, dict):
                sanitized_args = validator.sanitize_for_log(record.args)
                record.args = sanitized_args
            else:
                 record.args = validator.sanitize_for_log(record.args)
                 
        return super().format(record)

def setup_logger(name: str) -> logging.Logger:
    """
    Configura e retorna um logger para o módulo específico.
    
    Args:
        name: Nome do módulo (ex: 'core.main')
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar adicionar múltiplos handlers se já estiver configurado
    if logger.handlers:
        return logger
        
    # Definir nível de log baseado na variável de ambiente ou constante
    env = os.getenv('ENV', 'development')
    level = getattr(logging, LOG_LEVEL_DEVELOPMENT if env == 'development' else LOG_LEVEL_PRODUCTION)
    logger.setLevel(level)
    
    # Formatter sanitizado
    formatter = SanitizedFormatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Handler de Console (Stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler de Arquivo (Rotativo) - Opcional, cria log file
    # log_dir = os.path.join(os.getenv('APPDATA'), 'CriativosPro', 'logs')
    # os.makedirs(log_dir, exist_ok=True)
    # file_handler = RotatingFileHandler(
    #     os.path.join(log_dir, 'app.log'), 
    #     maxBytes=5*1024*1024, # 5MB
    #     backupCount=3,
    #     encoding='utf-8'
    # )
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)
    
    return logger

# Logger raiz
root_logger = setup_logger('criativospro')
