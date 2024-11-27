import streamlit as st
from moviepy.editor import AudioFileClip
import os
import shutil
import warnings

# Verificar instalação do ffmpeg
import ffmpeg
ffmpeg_path = shutil.which("ffmpeg")

if ffmpeg_path:
    st.write(f"FFmpeg encontrado no caminho: {ffmpeg_path}")
else:
    st.error("FFmpeg não encontrado. Verifique a configuração do ambiente.")

# Função para dividir áudio em partes
def dividir_audio_em_partes(input_file, output_folder, max_size_mb):
    try:
        # Carregar o áudio usando moviepy
        audio = AudioFileClip(input_file)
    except Exception as e:
        raise Exception(f"Erro ao carregar o arquivo de áudio: {e}")

    total_duration = audio.duration  # em segundos
    max_size_bytes = max_size_mb * 1024 * 1024

    # Estimando a duração de cada parte com base no tamanho do arquivo
    part_duration = (max_size_bytes / audio.fps / audio.reader.nchannels) / audio.reader.bytes_per_sample
    num_parts = int(total_duration / part_duration) + 1

    for i in range(num_parts):
        start = i * part_duration
        end = min((i + 1) * part_duration, total_duration)
        part = audio.subclip(start, end)
        output_path = os.path.join(output_folder, f"part_{i + 1}.mp3")
        part.write_audiofile(output_path, codec="libmp3lame")

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
