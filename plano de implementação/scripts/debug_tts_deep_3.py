import sys
import os
import wave

# Adicionar DLLs ao caminho (CRUCIAL PARA WINDOWS)
base_dir = os.getcwd()
piper_bin = os.path.join(base_dir, "backend", "bin", "piper")

if os.path.exists(piper_bin):
    print(f"Adicionando DLLs do Piper ao PATH: {piper_bin}")
    os.environ["PATH"] += os.pathsep + piper_bin
    try:
        os.add_dll_directory(piper_bin)
        print("✅ os.add_dll_directory executado com sucesso.")
    except AttributeError:
        pass # Python < 3.8

sys.path.append(base_dir)
from piper.voice import PiperVoice

model_path = "backend/bin/piper/pt_BR-faber-medium.onnx"
voice = PiperVoice.load(model_path)

print("\n--- Teste 8: Iterando Generator com Correção de PATH ---")
output_file = "debug_test_8.wav"

try:
    # Usando None para obter generator de áudio raw
    stream = voice.synthesize("Teste final, um dois três.", None)
    
    with wave.open(output_file, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(voice.config.sample_rate)
        
        count_bytes = 0
        for chunk in stream:
            wav_file.writeframes(chunk)
            count_bytes += len(chunk)
            
    print(f"✅ Sucesso! Bytes gravados: {count_bytes}")
    
except Exception as e:
    print(f"❌ Falha durante síntese: {e}")
    import traceback
    traceback.print_exc()
