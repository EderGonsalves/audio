import os
from pydub import AudioSegment
import subprocess
import streamlit as st

def dividir_audio_em_partes(input_file, output_folder, max_size_mb=10):
    """
    Divide um arquivo de áudio longo em partes menores do que max_size_mb.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Carregar o áudio
    audio = AudioSegment.from_file(input_file)
    
    # Estimativa do tamanho de áudio por segundo em MB (128 kbps para MP3)
    bitrate_kbps = 128
    bytes_per_second = (bitrate_kbps * 1000) // 8
    max_size_bytes = max_size_mb * 1024 * 1024
    max_duration_ms = (max_size_bytes / bytes_per_second) * 1000

    # Dividir o áudio em partes
    num_parts = 0
    parts = []
    for i in range(0, len(audio), int(max_duration_ms)):
        part = audio[i:i + int(max_duration_ms)]
        part_file = os.path.join(output_folder, f"parte_{num_parts + 1}.mp3")
        part.export(part_file, format="mp3", bitrate=f"{bitrate_kbps}k")
        print(f"Parte {num_parts + 1} salva em: {part_file}")
        parts.append(part_file)
        num_parts += 1

    print(f"Divisão concluída. Total de partes: {num_parts}")
    return parts

def run_script(script_path):
    """Executa outro script Python após a execução de um arquivo"""
    try:
        result = subprocess.run(['python', script_path], check=True, capture_output=True, text=True)
        print(f"Script {script_path} executado com sucesso!")
        print("Saída:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o script {script_path}.")
        print("Erro:", e.stderr)

# Interface com Streamlit
st.title("Divisor de Áudio com Execução de Scripts")
st.write("Divida arquivos de áudio em partes menores e execute scripts adicionais.")

# Upload do arquivo de áudio
uploaded_file = st.file_uploader("Faça upload de um arquivo de áudio", type=["mp3", "wav", "ogg"])
max_size_mb = st.slider("Tamanho máximo de cada parte (MB)", 1, 20, 10)

if uploaded_file:
    # Salvar arquivo temporariamente
    input_file = "temp_audio_file"
    with open(input_file, "wb") as f:
        f.write(uploaded_file.read())
    
    output_folder = "output_parts"
    parts = dividir_audio_em_partes(input_file, output_folder, max_size_mb)

    st.success(f"Áudio dividido em {len(parts)} partes.")
    for part in parts:
        st.audio(part, format="audio/mp3")
        st.download_button(
            label=f"Baixar {os.path.basename(part)}",
            data=open(part, "rb").read(),
            file_name=os.path.basename(part)
        )
    
    # Executar outro script após a divisão
    if st.button("Executar Script Adicional"):
        script_path = "novo-baserow.py"  # Altere para o caminho do script adicional
        run_script(script_path)
        st.success("Script adicional executado com sucesso!")
