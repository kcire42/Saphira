from app.Youtube_Extractor.Database.config import Config
import psycopg2

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
        with conn.cursor() as cur:
            cur.execute("""
                CALL "Youtube".register_youtube_ingestion(
                    p_video_id := %s::text,
                    p_title := %s::text,
                    p_url := %s::text,
                    p_duration := %s::bigint,
                    p_view_count := %s::bigint,
                    p_channel_id := %s::text,
                    p_channel_name := %s::text,
                    p_channel_url := %s::text,
                    p_hash_video := %s::text,
                    p_publish_at := %s::timestamp
                        )""",(
                str(metadata['video_id']),
                str(metadata['title']),
                str(metadata['url']),
                duration,     # Enviado como int -> Postgres lo recibe como BIGINT
                views,        # Enviado como int -> Postgres lo recibe como BIGINT
                str(metadata['channel_id']),
                str(metadata['channel_name']),
                str(metadata['channel_url']),
                str(metadata['video_hash']),
                metadata['upload_date'] # '2024-01-01'
            ))
        conn.commit()
        print(f"✅ Metadata del video '{metadata['title']}' ingresada correctamente.")
    except Exception as e:
        print(f"❌ Error al ingresar metadata del video '{metadata['title']}': {e}")
        conn.rollback()

def download_youtube_ingestion(metadata):
    print(f"→ Iniciando descarga del video")  
    conn = get_connection()
    video_id = str(metadata.get('video_id'))
    try:
        with conn.cursor() as cur:
            cur.execute("""CALL 
                        "Youtube".download_youtube_ingestion(
                        p_video_id := %s::text
                        )""",(
                        video_id,
                         ))
        conn.commit()
        print(f"✅ Descarga del video ID '{video_id}' iniciada correctamente.")
    except Exception as e:
        print(f"❌ Error al iniciar descarga del video ID '{video_id}': {e}")
        conn.rollback()

def process_youtube_ingestion(metadata, transcription):
    print(f"Inciando proceso de transcripción de videos")
    conn = get_connection()
    video_id = str(metadata.get('video_id'))
    try:
        with conn.cursor() as cur:
            cur.execute("""CALL 
                        "Youtube".process_youtube_ingestion(
                        p_video_id := %s::text,
                        p_transcript := %s::text
                        )""",(
                        video_id, 
                        str(transcription)
                            ))
        conn.commit()
        print(f"✅ Proceso de transcripción de videos completado.")
    except Exception as e:
        print(f"❌ Error al procesar transcripción de videos: {e}")
        conn.rollback()


if __name__ == "__main__":
    # Ejemplo de uso
    sample_metadata = {
        'video_id': 'abc123',
        'title': 'Ejemplo de Video2',
        'url': 'https://www.youtube.com/watch?v=abc1232',
        'duration': 300,
        'view_count': 1000,
        'channel_id': 'channel1232',
        'channel_name': 'Canal de Ejemplo',
        'channel_url': 'https://www.youtube.com/channel/channel1232',
        'video_hash': 'hash1232',
        'upload_date': '2024-01-02'
    }
    #register_youtube_ingestion(sample_metadata)
    download_youtube_ingestion(sample_metadata)
    #process_youtube_ingestion(sample_metadata, "Transcripción de ejemplo para el video.")
