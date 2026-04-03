from datetime import datetime
from app.Youtube_Extractor.Database.config import Config
import psycopg2
import os
import json

# Carpeta actual del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Subir un nivel
ROOT_DIR = os.path.dirname(BASE_DIR)
storage_audio_path = os.path.join(ROOT_DIR, 'data')
MODEL_PATH = os.path.join(ROOT_DIR, 'models')


def get_connection():
    print(f"→ Estableciendo conexión a {Config.DB_HOST}, base: {Config.DB_NAME}")
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        connect_timeout=5
    )
    
    return conn

def register_youtube_ingestion(metadata):
    print(f"→ Iniciando ingreso de metadata del video '{metadata['title']}' a la base de datos...")
    conn = get_connection()
    print(f"metadata: {metadata}")
    try:
        duration = int(metadata.get('duration', 0))
        views = int(metadata.get('view_count', 0))
        published_at = datetime.strptime(metadata['upload_date'], '%Y-%m-%d')
        with conn.cursor() as cur:
            cur.execute("""
                CALL "youtube".register_youtube_ingestion(
                    p_video_id := %s::text,
                    p_video_url := %s::text,
                    p_video_title := %s::text,
                    p_video_duration := %s::bigint,
                    p_video_view_count := %s::bigint,
                    p_channel_id := %s::text,
                    p_channel_name := %s::text,
                    p_channel_url := %s::text,
                    p_hash_video := %s::text,
                    p_published_at := %s::timestamp
                        )""",(
                str(metadata['video_id']),
                str(metadata['url']),
                str(metadata['title']),
                duration,     # Enviado como int -> Postgres lo recibe como BIGINT
                views,        # Enviado como int -> Postgres lo recibe como BIGINT
                str(metadata['channel_id']),
                str(metadata['channel_name']),
                str(metadata['channel_url']),
                str(metadata['video_hash']),
                published_at # '2024-01-01'
            ))
        conn.commit()
        print(f"✅ Metadata del video '{metadata['title']}' ingresada correctamente.")
    except Exception as e:
        print(f"❌ Error al ingresar metadata del video '{metadata['title']}': {e}")
        conn.rollback()

def get_video_by_status(status):
    print(f"→ Consultando videos pendientes de descarga...")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT *
                        FROM
                        "youtube".get_pending_videos(
                        p_status := %s::text
                        )""", (status,))
            pending_videos = cur.fetchall()
        print(f"✅ Se encontraron {len(pending_videos)} videos pendientes.")
        return pending_videos
    except Exception as e:
        print(f"❌ Error al obtener videos pendientes: {e}")
        return []
    

def download_youtube_ingestion(metadata):
    print(f"→ Iniciando descarga del video")  
    conn = get_connection()
    video_id = str(metadata.get('video_id'))
    try:
        with conn.cursor() as cur:
            cur.execute("""CALL 
                        "youtube".download_youtube_ingestion(
                        p_video_id := %s::text
                        )""",(
                        video_id,
                         ))
        conn.commit()
        print(f"✅ Descarga del video ID '{video_id}' iniciada correctamente.")
    except Exception as e:
        print(f"❌ Error al iniciar descarga del video ID '{video_id}': {e}")
        conn.rollback()

def confirm_youtube_data(video_id, video_title):
    # query para obtener metadata de la DB y confirmar que los datos del video descargado hagan match con el json 
    try:
        metaData = [file for file in os.listdir(storage_audio_path) if file.endswith('.json')]
        if video_title+ '.info.json' in metaData:
            file_path = os.path.join(storage_audio_path, video_title + '.info.json')
            # Leemos el archivo JSON para obtener información adicional del video
            # utf-8 para evitar problemas con caracteres especiales en los títulos
            with open(file_path, 'r',encoding='utf-8') as f: 
                meta_info = json.load(f)
                video_id_json = meta_info.get('id')
                video_title_json = meta_info.get('title')
                video_url_json = meta_info.get('url')
                video_duration_json = meta_info.get('duration')
                video_view_count_json = meta_info.get('view_count')
                channel_id_json = meta_info.get('channel_id')
                channel_name_json = meta_info.get('channel_name')
    except Exception as e:
        print(f"Error al leer metadata para: {video_title}: {e}")

def get_confirmed_videos():
    pass

def process_youtube_ingestion(metadata, transcription):
    print(f"Inciando proceso de transcripción de videos")
    conn = get_connection()
    video_id = str(metadata.get('video_id'))
    try:
        with conn.cursor() as cur:
            cur.execute("""CALL 
                        "youtube".process_youtube_ingestion(
                        p_video_id := %s::text,
                        p_transcripcion := %s::text
                        )""",(
                        video_id, 
                        str(transcription)
                            ))
        conn.commit()
        print(f"✅ Proceso de transcripción de videos completado.")
    except Exception as e:
        print(f"❌ Error al procesar transcripción de videos: {e}")
        conn.rollback()



# flow text:
# pending -> downloaded -> validate -> processed -> summary -> vector -> learning -> completed 
# error


if __name__ == "__main__":
    # Ejemplo de uso
    sample_metadata = {
        'video_id': '2',
        'url': 'https://www.youtube.com/watch?v=abc1232',
        'title': 'halo 2',     
        'duration': 300,
        'view_count': 1000,
        'channel_id': 'channel1232',
        'channel_name': 'Canal de Ejemplo',
        'channel_url': 'https://www.youtube.com/channel/channel1232',
        'video_hash': 'hash1232',
        'upload_date': '2024-01-02'
    }
    #register_youtube_ingestion(sample_metadata)
    status = get_video_by_status('pending')
    print(f"Videos pendientes: {status}")
    #download_youtube_ingestion(sample_metadata)
    #process_youtube_ingestion(sample_metadata, "Transcripción de ejemplo para el video.")

