import sys
import os
import subprocess

# Caminhos
base_dir = os.getcwd()
piper_dir = os.path.join(base_dir, "backend", "bin", "piper")
piper_exe = os.path.join(piper_dir, "piper.exe")
model_path = os.path.join(piper_dir, "pt_BR-faber-medium.onnx")
output_wav = "debug_exe.wav"

print(f"Testando Piper EXE: {piper_exe}")
print(f"Modelo: {model_path}")

if not os.path.exists(piper_exe):
    print("❌ Executável piper.exe não encontrado!")
    sys.exit(1)

if not os.path.exists(model_path):
    print("❌ Modelo ONNX não encontrado!")
    sys.exit(1)

# Comando
# echo "Teste" | piper.exe -m model.onnx -f para_arquivo.wav
cmd = [
    piper_exe,
    "--model", model_path,
    "--output_file", output_wav
]

print(f"Executando: {' '.join(cmd)}")

try:
    # No Windows, echo | cmd é trickier via subprocess. 
    # Vamos passar input via communicate.
    process = subprocess.Popen(
        cmd, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        cwd=piper_dir # Importante rodar no dir para achar DLLs locais
    )
    
    stdout, stderr = process.communicate(input="Teste de síntese via executável.".encode('utf-8'))
    
    print(f"Exit Code: {process.returncode}")
    if stdout: print(f"STDOUT: {stdout.decode()}")
    if stderr: print(f"STDERR: {stderr.decode()}")
    
    if os.path.exists(output_wav):
        size = os.path.getsize(output_wav)
        print(f"✅ Arquivo gerado: {output_wav} ({size} bytes)")
        if size > 44:
            print("✅ SUCESSO! O executável funciona.")
        else:
            print("❌ Arquivo gerado vazio (apenas header).")
    else:
        print("❌ Arquivo não gerado.")

except Exception as e:
    print(f"❌ Exceção ao rodar subprocesso: {e}")
