import streamlit as st
from pydub import AudioSegment
import os
import shutil
import warnings

# Suprimir SyntaxWarnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

# Verificar caminho do ffprobe
ffprobe_path = shutil.which("ffprobe")
ffmpeg_path = shutil.which("ffmpeg")

if ffprobe_path and ffmpeg_path:
    AudioSegment.ffprobe = ffprobe_path
    AudioSegment.ffmpeg = ffmpeg_path
else:
    st.error("FFmpeg ou FFprobe não encontrado. Verifique a configuração do ambiente.")

# Função para dividir áudio
def dividir_audio_em_partes(input_file, output_folder, max_size_mb):
    try:
        audio = AudioSegment.from_file(input_file)
    except Exception as e:
        raise Exception(f"Erro ao carregar o arquivo de áudio: {e}")

    total_duration = len(audio)  # em milissegundos
    max_size_bytes = max_size_mb * 1024 * 1024

    part_duration = (max_size_bytes / audio.frame_rate / audio.frame_width) * 1000
    num_parts = int(total_duration / part_duration) + 1

    for i in range(num_parts):
        start = int(i * part_duration)
        end = int(min((i + 1) * part_duration, total_duration))
        part = audio[start:end]
        output_path = os.path.join(output_folder, f"part_{i + 1}.mp3")
        part.export(output_path, format="mp3")

    return num_parts

# Interface Streamlit
st.title("Divisor de Áudio")

uploaded_file = st.file_uploader("Faça upload de um arquivo de áudio")
output_folder = "output"  # Substitua pelo caminho desejado no Streamlit Cloud
max_size_mb = st.number_input("Tamanho máximo de cada parte (em MB)", value=5)

if st.button("Dividir Áudio"):
    if uploaded_file is not None:
        try:
            os.makedirs(output_folder, exist_ok=True)
            num_parts = dividir_audio_em_partes(uploaded_file, output_folder, max_size_mb)
            st.success(f"Áudio dividido em {num_parts} partes!")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
    else:
        st.warning("Por favor, faça upload de um arquivo primeiro.")

# Executar script adicional
if st.button("Executar Script Adicional"):
    script_path = "novo-baserow.py"  # Altere para o caminho do script adicional
    os.system(f"python {script_path}")
    st.success("Script adicional executado com sucesso!")
