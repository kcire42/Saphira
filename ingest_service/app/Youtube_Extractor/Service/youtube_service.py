import yt_dlp
import os
from app.utilities.utilities import generate_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
storage_audio_path = os.path.join(BASE_DIR, 'data')

def get_videos_from_youtube_channel(channel_url, current_start=1, batch_size=20):
    # Aseguramos que apunte a la pestaña de videos para evitar confusiones
    if not channel_url.endswith('/videos'):
        channel_url = f"{channel_url.rstrip('/')}/videos"
        
    print(f"→ Explorando videos en: {channel_url}")
    # Placeholder function to get video URLs from a YouTube channel
    print(f"Obteniendo videos del canal: {channel_url}")
    ydl_opts = {
        'extract_flat': True,  # 👈 Clave: No descarga nada, solo lista.
        'quiet': True,
        'playliststart': current_start,
            'playlistend': current_start + batch_size - 1,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extraer información del canal sin descargar los videos
        result = ydl.extract_info(channel_url, download=False)
        print(result.keys())
        if 'entries' not in result or not result['entries']:
            print("❌ No se encontraron videos en el canal.")
            return []
        video_info = []
        # Extraemos el ID del canal y el nombre del canal para referencia
        channel_id = result.get('id')
        channel_name = result.get('uploader') or result.get('title')
        
        print(f"→ Encontrados {len(result['entries'])} videos en el canal.")
        for entry in result['entries']:
            video_id = entry.get('id')
            video_url = entry.get('url') or f"https://www.youtube.com/watch?v={video_id}"
            video_info.append({
                    'video_id': video_id,
                    'title': entry.get('title'),
                    'url': video_url,
                    'duration': entry.get('duration'),
                    'view_count': entry.get('view_count'),
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'hash': generate_hash(entry.get('title') + str(entry.get('id'))),
                    'upload_date': entry.get('upload_date'),
                    'status': 'pending'
                })
        return video_info


def download_audio(video_url, video_id):
    # Placeholder function to download audio from a YouTube video
    print(f"Downloading audio from {video_url}, video ID: {video_id}")
    # Configuración de yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',  # Elegir el mejor audio
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',   # Convertir a mp3
            'preferredquality': '192', # Calidad (192kbps es un buen estándar)
        }],
        'writeinfojson': True, # Guardar información del video en un archivo JSON
        'outtmpl': f'{storage_audio_path}/%(title)s.%(ext)s', # Nombre del archivo
        'quiet': True, # Muestra el progreso en consola
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"→ Iniciando descarga de {len(video_url)} elementos...")
            ydl.download([video_url])
            print(f"✅ ¡Proceso completado! Archivos guardados en: {storage_audio_path}")
        except Exception as e:
            print(f"❌ Ocurrió un error: {e}")
    
    return {'video_id': video_id, 'status': 'downloaded'}


    
        

            
    

if __name__ == "__main__":
    # Ejemplo de uso
    video_url = "https://www.youtube.com/watch?v=EmE7CJuRXA4"  # Reemplaza con una URL real
    canal = "https://www.youtube.com/@MeDicenDai"
    #download_audio(video_url)
    info = get_videos_from_youtube_channel(canal, current_start=1, batch_size=2)
    print(info)