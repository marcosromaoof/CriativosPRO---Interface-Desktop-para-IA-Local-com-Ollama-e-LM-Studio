import asyncio
import re
import time
from core.fsm import fsm, SystemState
from core.history_manager import history_manager
from core.config import config
from core.database import db
from core.tts_service import tts_service
from core.validators import validator, ValidationError
from core.constants import SUPPORTED_PROVIDERS, STREAM_TIMEOUT
from core.logger import root_logger as logger

class Controller:
    """Orquestrador principal do ciclo de vida das mensagens e eventos."""
    
    def __init__(self, sio):
        self.sio = sio
        self._current_task = None

    async def handle_message(self, sid, data):
        """Prepara e inicia o processamento de mensagem em background."""
        if not fsm.is_idle():
            print(f"[Controller] Sistema ocupado ({fsm.current_state.value}). Ignorando mensagem.")
            return

        try:
            session_id = data.get("session_id", "default")
            user_message = data.get("content", "")
            provider_name = data.get("provider")
            model_name = data.get("model")

            # Validações usando o módulo de validação
            if not user_message or not provider_name or not model_name:
                print("[Controller] Dados insuficientes.")
                return

            # Validar mensagem
            user_message = validator.validate_message(user_message)
            
            # Validar provedor
            provider_name = validator.validate_provider_name(provider_name)
            
            # Validar session_id se não for default
            if session_id != "default":
                session_id = validator.validate_session_id(session_id)

        except ValidationError as e:
            await self.sio.emit("error", {"message": str(e)}, to=sid)
            return

        # Muda estado imediatamente
        fsm.change_to(SystemState.PROCESSING)

        # Inicia a Task de Processamento Completo (que poderá ser cancelada)
        self._current_task = asyncio.create_task(
            self._process_message_flow(sid, session_id, user_message, provider_name, model_name)
        )
        # Opcional: Adicionar callback de conclusão para logging ou limpeza
        # self._current_task.add_done_callback(...)

    async def _process_message_flow(self, sid, session_id, user_message, provider_name, model_name):
        """Lógica pesada de geração, isolada para permitir cancelamento."""
        try:
            # 1. Registrar mensagem e Contexto
            await history_manager.add_message(session_id, "user", user_message)
            context = await history_manager.get_context(session_id)
            
            # Título (se aplicável)
            if await history_manager.is_session_persistent(session_id) and len(context) == 1:
                from core.title_generator import title_generator
                title = title_generator.generate(user_message)
                await history_manager.set_session_title(session_id, title)
                await self.sio.emit("new_session_title", {"session_id": session_id, "title": title}, to=sid)

            # --- Injeção de System Prompt ---
            system_prompt = config.get_system_prompt('ollama' if 'ollama' in provider_name.lower() else 'lmstudio')
            user_profile = config.get_user_profile()
            
            # Constrói o System Prompt final
            if user_profile:
                profile_context = f"\nINFO USUARIO: {user_profile.get('display_name', 'User')}"
                if user_profile.get('custom_instructions'):
                     profile_context += f"\nINSTRUCOES: {user_profile.get('custom_instructions')}"
                system_prompt += profile_context

            if system_prompt:
                context = [{"role": "system", "content": system_prompt}] + context

            # 2. Obter Provedor
            from core.providers.provider_manager import provider_manager
            api_key = config.get_api_key(provider_name) or "local"

            provider = provider_manager.get_provider(provider_name, api_key)
            if not provider:
                raise ValueError(f"Provedor {provider_name} indisponível.")
            
            # Chama o provedor (awaitable) com timeout
            response_stream = await provider.generate_response(model_name, context, stream=True)
            
            full_response = ""
            token_count = 0
            first_chunk_time = None
            is_thinking = False
            
            # Timeout para o stream inteiro ou por chunk se preferir. 
            # Aqui aplicamos timeout total de segurança.
            async with asyncio.timeout(STREAM_TIMEOUT):
                async for chunk in response_stream:
                    content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
                    
                    # Brain Thinking Filter (Tag <think>)
                    if "<think>" in content: is_thinking = True; content = content.split("<think>")[-1]
                    if "</think>" in content: is_thinking = False; content = content.split("</think>")[-1]
                    
                    if content and not is_thinking:
                        if not first_chunk_time: first_chunk_time = time.time()
                        full_response += content
                        token_count += 1
                        await self.sio.emit("chat_chunk", {"content": content}, to=sid)

            # 4. Finalização e Métricas
            duration = round(time.time() - start_time, 2)
            tps = round(token_count / (time.time() - first_chunk_time), 1) if first_chunk_time else 0
            
            metrics = { "tokens": token_count, "tps": tps, "duration": duration }
            
            # Salvar no Histórico
            await history_manager.add_message(session_id, "assistant", full_response, metadata=metrics)
            await self.sio.emit("chat_end", { "total_content": full_response, "metrics": metrics }, to=sid)

            # Telemetria (Fire-and-forget)
            try:
                db.save_metric(session_id, provider_name, model_name, {
                    "input_tokens": int(len(str(context))/4), "output_tokens": token_count,
                    "latency": duration, "status": "success"
                })
            except Exception as e:
                logger.debug(f"Erro ao salvar métricas: {e}")

            # 5. TTS (Opcional)
            await tts_service.auto_speak_if_enabled(full_response)
            
        except asyncio.CancelledError:
            logger.info("Geração cancelada pelo usuário.")
            await self.sio.emit("error", {"message": "Geração cancelada."}, to=sid)
        except asyncio.TimeoutError:
            logger.error("Timeout na geração da resposta.")
            await self.sio.emit("error", {"message": "Tempo limite de resposta excedido."}, to=sid)
        except Exception as e:
            logger.error(f"Erro no fluxo de mensagem: {e}")
            import traceback
            traceback.print_exc()
            await self.sio.emit("error", {"message": f"Erro interno: {str(e)}"}, to=sid)
        finally:
             if fsm.current_state != SystemState.IDLE:
                fsm.change_to(SystemState.IDLE)
             self._current_task = None

    async def stop_generation(self, sid):
        """Cancela a tarefa atual se existir."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            
            fsm.change_to(SystemState.IDLE)
            await self.sio.emit("generation_stopped", {}, to=sid)
        else:
            print("[Controller] Nenhuma task ativa para cancelar.")
