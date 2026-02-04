"""
Módulo de Rate Limiting - CriativosPro
Implementa limitação de taxa para conexões WebSocket e API.
"""
import time
from collections import defaultdict, deque
from core.constants import MAX_MESSAGES_PER_MINUTE

class RateLimiter:
    """
    Controla o número de requisições por cliente.
    Usa algoritmo de Sliding Window Log (simplificado usando deque).
    """
    
    def __init__(self):
        self.requests = defaultdict(deque) # sid -> deque([timestamps])
        self.limit = MAX_MESSAGES_PER_MINUTE
        self.window = 60 # segundos
        
    def is_allowed(self, sid: str) -> bool:
        """
        Verifica se a requisição é permitida para o SID fornecido.
        
        Args:
            sid: ID da sessão do socket
            
        Returns:
            bool: True se permitido, False se bloqueado
        """
        now = time.time()
        user_requests = self.requests[sid]
        
        # Remover requisições antigas (fora da janela)
        while user_requests and user_requests[0] < now - self.window:
            user_requests.popleft()
            
        # Verificar limite
        if len(user_requests) >= self.limit:
            return False
            
        # Registrar nova requisição
        user_requests.append(now)
        return True

    def clear(self, sid: str):
        """Limpa o histórico de um cliente desconectado."""
        if sid in self.requests:
            del self.requests[sid]

# Instância global
rate_limiter = RateLimiter()
