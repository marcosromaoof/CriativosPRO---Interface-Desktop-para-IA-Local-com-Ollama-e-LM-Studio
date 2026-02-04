import asyncio
import re
from core.fsm import fsm, SystemState
from core.history_manager import history_manager
from core.config import config
from core.database import db
from core.tts_service import tts_service

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

        session_id = data.get("session_id", "default")
        user_message = data.get("content", "")
        provider_name = data.get("provider")
        model_name = data.get("model")

        if not user_message or not provider_name or not model_name:
            print("[Controller] Dados insuficientes.")
            return

        # Validações Rápidas
        if len(user_message) > 50000:
            await self.sio.emit("error", {"message": "Mensagem muito longa."}, to=sid)
            return
        if session_id != "default" and not re.match(r'^[a-zA-Z0-9_\-]+$', session_id):
            await self.sio.emit("error", {"message": "ID inválido."}, to=sid)
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

            # System Prompt
            prompt_type = "ollama" # Padrão agora é local
            if provider_name.lower() == "lmstudio": prompt_type = "lmstudio"
            
            system_prompt = config.get_prompt(prompt_type)
            user_profile = config.get_user_profile()
            
            if user_profile:
                profile_str = "\n\n=== USER PROFILE ===\n"
                for k, v in user_profile.items():
                    if v and str(v).strip(): profile_str += f"{k.capitalize()}: {v}\n"
                system_prompt = (system_prompt or "") + profile_str

            if system_prompt:
                context = [{"role": "system", "content": system_prompt}] + context

            # 2. Obter Provedor
            from core.providers.provider_manager import provider_manager
            api_key = config.get_api_key(provider_name) or "none"
            is_local = provider_name.lower() in ['ollama', 'lmstudio']

            if api_key == "none" and not is_local:
                 raise ValueError(f"API Key não configurada para {provider_name}")

            provider = provider_manager.get_provider(provider_name, api_key)
            if not provider:
                raise ValueError(f"Provedor {provider_name} indisponível.")

            # 3. Geração e Stream
            import time
            start_time = time.time()
            
            # Chama o provedor (awaitable)
            response_stream = await provider.generate_response(model_name, context, stream=True)
            
            full_response = ""
            token_count = 0
            first_chunk_time = None
            is_thinking = False
            
            async for chunk in response_stream:
                content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
                
                # DeepSeek R1 Filter
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
            except: pass

            # 5. TTS (Opcional)
            if full_response:
                audio_path = await tts_service.speak(full_response)
                if audio_path:
                    await self.sio.emit("audio_ready", {"path": audio_path}, to=sid)

        except asyncio.CancelledError:
            print("[Controller] Geração cancelada (Task Killed).")
            # Não emitimos 'error' aqui, o stop_generation cuida do evento
            raise
        except Exception as e:
            print(f"[Controller] Erro na Task: {e}")
            await self.sio.emit("error", {"message": str(e)}, to=sid)
            fsm.change_to(SystemState.IDLE) # Garante reset
        finally:
            if fsm.current_state != SystemState.IDLE:
                 fsm.change_to(SystemState.IDLE)
            self._current_task = None

    async def stop_generation(self, sid):
        """Interrompe a geração atual."""
        if self._current_task and not self._current_task.done():
            print("[Controller] Solicitando cancelamento da task...")
            self._current_task.cancel()
            try:
                await self._current_task
            except asyncio.CancelledError:
                print("[Controller] Task cancelada com sucesso.")
            
            fsm.change_to(SystemState.IDLE)
            await self.sio.emit("generation_stopped", {}, to=sid)
        else:
            print("[Controller] Nenhuma task ativa para cancelar.")
