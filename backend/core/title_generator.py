import re

class TitleGenerator:
    """Gera títulos curtos e descritivos para sessões de chat."""
    
    def generate(self, first_message: str) -> str:
        """
        Gera um título baseado na primeira mensagem do usuário.
        Atualmente utiliza uma lógica de extração, mas pode ser 
        expandido para usar um modelo de IA 'lightweight'.
        """
        # Limpeza básica
        title = first_message.strip()
        
        # Remove caracteres especiais do início
        title = re.sub(r'^[\s\W]+', '', title)
        
        # Pega as primeiras palavras (máximo 5 ou 40 caracteres)
        words = title.split()
        short_title = " ".join(words[:5])
        
        if len(short_title) > 40:
            short_title = short_title[:37] + "..."
            
        # Capitaliza a primeira letra
        if short_title:
            short_title = short_title[0].upper() + short_title[1:]
        else:
            short_title = "Nova Conversa"
            
        return short_title

# Instância global
title_generator = TitleGenerator()
