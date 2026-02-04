import sys
import os
import wave

sys.path.append(os.getcwd())
from piper.voice import PiperVoice

model_path = "backend/bin/piper/pt_BR-faber-medium.onnx"
voice = PiperVoice.load(model_path)

print("\n--- Teste 4: Phonemize ---")
# Verificar se consegue converter texto em fonemas
try:
    phonemes = voice.phonemize("Teste de fonetização")
    print(f"Fonemas gerados: {phonemes}")
    # Retorna lista de lista de fonemas?
    if not phonemes or len(phonemes) == 0:
        print("❌ ERRO: Fonetização retornou vazio!")
    else:
        print("✅ Fonetização OK")
except Exception as e:
    print(f"❌ ERRO na fonetização: {e}")

print("\n--- Teste 5: synthesize stream iteration ---")
# Tentar iterar sobre o resultado de synthesize, caso ele seja um generator
try:
   # Criar arquivo dummy
   # Se synthesize retornar generator, precisamos consumir e escrever
   # Mas a assinatura pede wav_file...
   pass
except:
   pass

print("\n--- Teste 6: synthesize_stream_raw (se existir) ---")
# Não existe na lista anterior.

print("\n--- Teste 7: synthesize_wav ---")
# Se esse metodo existe, deve ser especifico para raw bytes?
try:
    with wave.open("debug_test_7.wav", "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(voice.config.sample_rate)
        
        # Tentar chamar synthesize_wav?
        # A assinatura deve ser descoberta
        # Chutar: synthesize(text, wav_file) falhou (44 bytes).
        # Talvez synthesize retorne bytes se wav_file=None?
        audio_bytes = voice.synthesize("Teste de áudio em bytes", None)
        if audio_bytes:
             print(f"Synthesize (None) retornou {len(audio_bytes)} bytes/items")
             if isinstance(audio_bytes, bytes):
                  wav_file.writeframes(audio_bytes)
                  print("✅ Gravado via bytes retornados")
             else:
                  # Talvez seja generator
                  count = 0
                  for chunk in audio_bytes:
                       wav_file.writeframes(chunk)
                       count += len(chunk)
                  print(f"✅ Gravado via generator: {count} bytes")
        else:
             print("Synthesize (None) retornou Nada.")

except Exception as e:
    print(f"Erro Teste 7: {e}")
