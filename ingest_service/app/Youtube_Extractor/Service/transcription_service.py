import os 
import whisper
from tqdm import tqdm
import json
from app.utilities.utilities import generate_hash


# Carpeta actual del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Subir un nivel
ROOT_DIR = os.path.dirname(BASE_DIR)
storage_audio_path = os.path.join(ROOT_DIR, 'data')
MODEL_PATH = os.path.join(ROOT_DIR, 'models')

def setup_model(model_name="small"):
    print(f"✅ Cargando modelo {model_name} desde el directorio: {MODEL_PATH}")
    return whisper.load_model(model_name, download_root=MODEL_PATH)

def transcribe_audio(model, storage_audio_path, title):
    print(f"→ Iniciando transcripción de archivos en: {storage_audio_path}")
    # 1. Lista de archivos
    files = [file for file in os.listdir(storage_audio_path) if file.endswith('.mp3')]
    metaData = [file for file in os.listdir(storage_audio_path) if file.endswith('.json')]
    print(f"→ Encontrados {len(files)} archivos para transcribir.")
    if title+'.mp3' in files:
        audio_full_path = os.path.join(storage_audio_path, title+'.mp3')
        try:
            # Transcribimos con verbose=False para no romper la barra de carga
            # fp16=False porque estás en CPU
            result = model.transcribe(audio_full_path, fp16=False)
            
            try:
                if title+ '.info.json' in metaData:
                    file_path = os.path.join(storage_audio_path, title + '.info.json')
                    # Leemos el archivo JSON para obtener información adicional del video
                    # utf-8 para evitar problemas con caracteres especiales en los títulos
                    with open(file_path, 'r',encoding='utf-8') as f: 
                        meta_info = json.load(f)

                    print(f"Información adicional para {title}:\n{meta_info}")
                    id_video = meta_info.get('id')
            except Exception as e:
                print(f"Error al leer metadata para: {title}: {e}")

            #print(f"✅ id_video: {id_video}")
            #print(f"Transcripción de {file} con nombre {name_file}:\n{result['text']}")
            return {
                'video_id': id_video,
                'transcription': result['text']}
        except Exception as e:
            print(f"Error al transcribir {title+'.mp3'}: {e}")

if __name__ == "__main__":
    model = setup_model()
    trans = transcribe_audio(model, storage_audio_path, 'Naruto： Kakashi Vs Pain - QUIÉN DEBIÓ GANAR')
    print(f"Transcripción {trans}")


