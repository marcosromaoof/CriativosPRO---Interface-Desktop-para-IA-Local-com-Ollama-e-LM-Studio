import asyncio
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
        """Processa uma mensagem recebida do frontend."""
        if not fsm.is_idle():
            print(f"[Controller] Sistema ocupado ({fsm.current_state.value}). Ignorando mensagem.")
            return

        session_id = data.get("session_id", "default")
        user_message = data.get("content", "")
        provider_name = data.get("provider")
        model_name = data.get("model")

        if not user_message or not provider_name or not model_name:
            print("[Controller] Dados insuficientes para processar mensagem.")
            return

        # 1. Registrar mensagem do usuário e gerar título
        history_manager.add_message(session_id, "user", user_message)
        context = history_manager.get_context(session_id)
        
        # Só gera título via LLM se a sessão for realmente persistente (ignora 'Oi', 'Olá', etc)
        if history_manager.is_session_persistent(session_id) and len(context) == 1:
            from core.title_generator import title_generator
            title = title_generator.generate(user_message)
            history_manager.set_session_title(session_id, title)
            await self.sio.emit("new_session_title", {"session_id": session_id, "title": title}, to=sid)
        
        # 1.5. Injetar System Prompt baseado no tipo de provedor (Fase 2)
        prompt_type = "general"  # Padrão
        if provider_name.lower() == "ollama":
            prompt_type = "ollama"
        elif provider_name.lower() == "lmstudio":
            prompt_type = "lmstudio"
        
        system_prompt = config.get_prompt(prompt_type)
        
        # Injeção de Perfil do Usuário
        user_profile = config.get_user_profile()
        if user_profile:
            profile_str = "\n\n=== USER PROFILE ===\n"
            # Adiciona apenas campos preenchidos
            for key, val in user_profile.items():
                if val and str(val).strip():
                   profile_str += f"{key.capitalize()}: {val}\n"
            
            if system_prompt:
                system_prompt += profile_str
            else:
                system_prompt = profile_str

        if system_prompt:
            # Adicionar system prompt no início do contexto
            context = [{"role": "system", "content": system_prompt}] + context
        
        # 2. Alterar estado para processando
        fsm.change_to(SystemState.PROCESSING)

        try:
            # 3. Obter Provedor
            from core.providers.provider_manager import provider_manager
            api_key = config.get_api_key(provider_name)
            
            # Provedores locais não precisam de API key real
            is_local = provider_name.lower() in ['ollama', 'lmstudio']
            
            if not api_key and not is_local:
                raise ValueError(f"Chave de API para {provider_name} não configurada.")
            
            if not api_key:
                api_key = "none"

            provider = provider_manager.get_provider(provider_name, api_key)
            if not provider:
                raise ValueError(f"Não foi possível carregar o provedor {provider_name}.")

            # 4. Iniciar tarefa de geração real
            import time
            start_time = time.time()
            
            self._current_task = asyncio.create_task(
                provider.generate_response(model_name, context, stream=True)
            )
            response_stream = await self._current_task
            
            # 5. Processar Stream
            full_response = ""
            token_count = 0
            first_chunk_time = None
            is_thinking = False
            
            async for chunk in response_stream:
                content = chunk.choices[0].delta.content if chunk.choices[0].delta.content else ""
                
                # Filtro de raciocínio (DeepSeek R1 fix)
                if "<think>" in content:
                    is_thinking = True
                    content = content.split("<think>")[-1]
                if "</think>" in content:
                    is_thinking = False
                    content = content.split("</think>")[-1]
                
                if content and not is_thinking:
                    if first_chunk_time is None:
                        first_chunk_time = time.time()
                    
                    full_response += content
                    token_count += 1
                    await self.sio.emit("chat_chunk", {"content": content}, to=sid)

            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            # Cálculo de TPS (Tokens por Segundo)
            tps = 0
            if first_chunk_time:
                gen_duration = end_time - first_chunk_time
                tps = round(token_count / gen_duration, 1) if gen_duration > 0 else 0

            # Métricas finais
            metrics = {
                "tokens": token_count, # Idealmente pegar o usage real se disponível
                "tps": tps,
                "duration": duration
            }

            # 5.5 Salvar Telemetria (Fase 4 - Dashboard)
            try:
                # Estimativa de tokens de entrada (aproximada: caracteres / 4)
                input_chars = sum([len(m['content']) for m in context])
                estimated_input_tokens = int(input_chars / 4)
                
                telemetry_data = {
                    "input_tokens": estimated_input_tokens,
                    "output_tokens": token_count,
                    "latency": duration,
                    "status": "success",
                    "cost": 0.0 # Futuramente: calcular baseado no modelo
                }
                db.save_metric(session_id, provider_name, model_name, telemetry_data)
                print("[Controller] Telemetria salva com sucesso.")
            except Exception as e_metrics:
                print(f"[Controller] Erro ao salvar telemetria: {e_metrics}")

            # 6. Salvar resposta e Notificar fim
            history_manager.add_message(session_id, "assistant", full_response, metadata=metrics)
            await self.sio.emit("chat_end", {
                "total_content": full_response,
                "metrics": metrics
            }, to=sid)

            # 7. Se áudio ativado, gerar TTS
            if full_response:
                audio_path = await tts_service.speak(full_response)
                if audio_path:
                    await self.sio.emit("audio_ready", {"path": audio_path}, to=sid)
            
        except asyncio.CancelledError:
            print("[Controller] Geração cancelada.")
        except Exception as e:
            print(f"[Controller] Erro: {e}")
            fsm.change_to(SystemState.ERROR)
            await self.sio.emit("error", {"message": str(e)}, to=sid)
        finally:
            if not fsm.current_state == SystemState.ERROR:
                fsm.change_to(SystemState.IDLE)
            self._current_task = None

    async def stop_generation(self, sid):
        """Interrompe a geração atual se estiver em curso."""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            fsm.change_to(SystemState.IDLE)
            await self.sio.emit("generation_stopped", {}, to=sid)
