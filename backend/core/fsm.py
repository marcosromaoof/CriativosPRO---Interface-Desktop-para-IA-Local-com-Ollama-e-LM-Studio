from enum import Enum

class SystemState(Enum):
    IDLE = "IDLE"           # Aguardando entrada do usuário
    PROCESSING = "PROCESSING" # IA gerando resposta (Streaming)
    SPEAKING = "SPEAKING"     # TTS emitindo áudio
    ERROR = "ERROR"           # Ocorreu uma falha no pipeline

class FSM:
    """Máquina de Estados Finita para controle do ciclo de vida da aplicação."""
    
    def __init__(self):
        self._current_state = SystemState.IDLE
        self._on_change_callback = None

    def set_on_change(self, callback):
        """Define uma função de callback para ser chamada em cada mudança de estado."""
        self._on_change_callback = callback

    @property
    def current_state(self):
        return self._current_state

    def change_to(self, new_state: SystemState):
        """Altera o estado do sistema e dispara o callback, se definido."""
        if self._current_state != new_state:
            print(f"[FSM] Mudança de estado: {self._current_state.value} -> {new_state.value}")
            self._current_state = new_state
            if self._on_change_callback:
                self._on_change_callback(new_state.value)

    def is_idle(self):
        return self._current_state == SystemState.IDLE

    def is_processing(self):
        return self._current_state == SystemState.PROCESSING

# Instância global da FSM
fsm = FSM()
