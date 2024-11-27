import os
from pydub import AudioSegment
from pydub.utils import which
import streamlit as st
import subprocess

# Configurar o caminho para o FFmpeg
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

def dividir_audio_em_partes(input_file, output_folder, max_size_mb=10):
    """
    Divide um arquivo de áudio longo em partes menores do que max_size_mb.

    :param input_file: Caminho do arquivo de áudio de entrada.
    :param output_folder: Pasta onde as partes divididas serão salvas.
    :param max_size_mb: Tamanho máximo de cada parte em MB (padrão: 10 MB).
    """
    # Verificar se o arquivo de entrada existe
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"O arquivo {input_file} não foi encontrado.")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Carregar o áudio
    try:
        audio = AudioSegment.from_file(input_file)
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar o arquivo de áudio: {e}")

    # Estimativa do tamanho de áudio por segundo em MB (taxa de bits típica de 128 kbps para MP3)
    bitrate_kbps = 128  # Taxa de bits típica para MP3
    bytes_per_second = (bitrate_kbps * 1000) // 8
    max_size_bytes = max_size_mb * 1024 * 1024
    max_duration_ms = (max_size_bytes / bytes_per_second) * 1000  # Duração máxima por parte em ms

    # Dividir o áudio em partes
    num_parts = 0
    for i in range(0, len(audio), int(max_duration_ms)):
        part = audio[i:i + int(max_duration_ms)]
        part_file = os.path.join(output_folder, f"parte_{num_parts + 1}.mp3")
        try:
            part.export(part_file, format="mp3", bitrate=f"{bitrate_kbps}k")
            print(f"Parte {num_parts + 1} salva em: {part_file}")
        except Exception as e:
            raise RuntimeError(f"Erro ao exportar a parte {num_parts + 1}: {e}")
        num_parts += 1

    print(f"Divisão concluída. Total de partes: {num_parts}")
    return num_parts

def run_script(script_path):
    """
    Executa um script Python adicional.
    
    :param script_path: Caminho do script Python a ser executado.
    """
    if not os.path.isfile(script_path):
        raise FileNotFoundError(f"Script {script_path} não encontrado.")
    try:
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Erro ao executar o script: {result.stderr}")
    except Exception as e:
        raise RuntimeError(f"Erro ao executar o script: {e}")

# Interface do Streamlit
st.title("Divisor de Áudio")
st.write("Carregue um arquivo de áudio para dividi-lo em partes menores.")

# Upload do arquivo
uploaded_file = st.file_uploader("Carregue um arquivo de áudio", type=["mp3", "wav", "ogg"])

if uploaded_file:
    # Salvar o arquivo temporariamente
    input_file = "temp_audio_file"
    output_folder = "partes_divididas"
    max_size_mb = st.number_input("Tamanho máximo de cada parte (MB)", min_value=1, value=10, step=1)

    with open(input_file, "wb") as f:
        f.write(uploaded_file.read())

    try:
        # Dividir o áudio
        st.write("Processando o arquivo...")
        num_parts = dividir_audio_em_partes(input_file, output_folder, max_size_mb)
        st.success(f"Arquivo dividido em {num_parts} partes!")

        # Exibir os arquivos divididos
        st.write("Partes geradas:")
        for part_file in os.listdir(output_folder):
            st.write(part_file)
            with open(os.path.join(output_folder, part_file), "rb") as f:
                st.download_button(label=f"Baixar {part_file}", data=f, file_name=part_file)
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")

# Botão para executar script adicional
if st.button("Executar Script Adicional"):
    script_path = "novo-baserow.py"  # Altere para o caminho do script adicional
    try:
        run_script(script_path)
        st.success("Script adicional executado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao executar o script adicional: {e}")
