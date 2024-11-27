import streamlit as st
from moviepy.editor import AudioFileClip
from pathlib import Path
import os

# Função para dividir áudio em partes
def dividir_audio_em_partes(input_file, output_folder, max_size_mb):
    try:
        # Carregar o áudio usando moviepy
        audio = AudioFileClip(str(input_file))
    except Exception as e:
        raise Exception(f"Erro ao carregar o arquivo de áudio: {e}")

    total_duration = audio.duration  # em segundos
    max_size_bytes = max_size_mb * 1024 * 1024

    # Estimando a duração de cada parte com base no tamanho do arquivo
    part_duration = (max_size_bytes / audio.fps / audio.reader.nchannels) / audio.reader.bytes_per_sample
    num_parts = int(total_duration / part_duration) + 1

    # Usar pathlib para garantir que os arquivos de saída são criados corretamente
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)  # Cria a pasta de saída, se não existir

    for i in range(num_parts):
        start = i * part_duration
        end = min((i + 1) * part_duration, total_duration)
        part = audio.subclip(start, end)
        part_output_path = output_folder / f"part_{i + 1}.mp3"  # Criar caminho usando pathlib
        part.write_audiofile(str(part_output_path), codec="libmp3lame")  # Passar como string

    return num_parts

# Interface Streamlit
st.title("Divisor de Áudio")

uploaded_file = st.file_uploader("Faça upload de um arquivo de áudio")
output_folder = "output"  # Caminho da pasta de saída, pode ser ajustado
max_size_mb = st.number_input("Tamanho máximo de cada parte (em MB)", value=5)

if st.button("Dividir Áudio"):
    if uploaded_file is not None:
        try:
            # Usar pathlib para garantir que o arquivo é salvo corretamente
            input_file = Path(uploaded_file.name)
            with open(input_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            num_parts = dividir_audio_em_partes(input_file, output_folder, max_size_mb)
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
