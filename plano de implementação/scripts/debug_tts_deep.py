import sys
import os
import wave
import time

sys.path.append(os.getcwd())

from piper.voice import PiperVoice

model_path = "backend/bin/piper/pt_BR-faber-medium.onnx"
voice = PiperVoice.load(model_path)

print(f"Sample Rate: {voice.config.sample_rate}")

# Teste 1: Método Atual
print("\n--- Teste 1: Método Atual (Wave Object) ---")
try:
    with wave.open("debug_test_1.wav", "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(voice.config.sample_rate)
        voice.synthesize("Teste um dois três.", wav_file)
    
    size = os.path.getsize("debug_test_1.wav")
    print(f"Resultado Teste 1: {size} bytes")
except Exception as e:
    print(f"Erro Teste 1: {e}")

# Teste 2: Escrevendo raw bytes (usando synthesize com iterador?)
# Não, o metodo synthesize escreve direto no wav_file se passado.
# Vamos tentar passar None no wav_file para ver se ele retorna bytes?
# A assinatura é: synthesize(text, wav_file, synthesis_args)
# Se wav_file for None, o que acontece?

print("\n--- Teste 2: Texto Vazio? ---")
try:
    with wave.open("debug_test_2.wav", "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(voice.config.sample_rate)
        voice.synthesize("", wav_file) # Texto vazio proposital
    size = os.path.getsize("debug_test_2.wav")
    print(f"Resultado Teste 2 (Texto Vazio): {size} bytes")
except Exception as e:
    print(f"Erro Teste 2: {e}")

# Teste 3: Raw Audio Stream (Simulação)
# Algumas versoes do piper voice tem synthesize_stream_raw
print("\n--- Teste 3: Verificando Métodos Disponíveis ---")
print(dir(voice))
