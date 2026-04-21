from app.Youtube_Extractor.Service.youtube_service import get_videos_from_youtube_channel, download_audio
from app.Youtube_Extractor.Service.transcription_service import transcribe_audio
from app.Youtube_Extractor.Database.database_manager import register_youtube_ingestion,db_get_videos_by_status,download_youtube_ingestion,process_youtube_ingestion,validate_youtube_video,error_youtube_ingestion
from app.Youtube_Extractor.Validate_Data.integrity_data import validate_video_metadata

if __name__ == "__main__":
    print("🚀 Iniciando el proceso de ingestión de videos de YouTube...")
    youtube_channel = 'https://www.youtube.com/@MeDicenDai'
    # 1. INGESTIÓN: Obtener y registrar videos nuevos
    videos_channel = get_videos_from_youtube_channel(youtube_channel, current_start=1, batch_size=2)
    if not videos_channel:
        print("❌ No se encontraron videos en el canal. Verifica la URL o el estado del canal.")
    else:
        for video in videos_channel:
            if register_youtube_ingestion(video):
                print(f"✅ Registrado: {video['title']}")
            else:
                error_youtube_ingestion(video['video_id'], "Error al registrar video en DB.")
                print(f"❌ Error al registrar: {video['title']}")
    print(f"✅ Videos obtenidos del canal: {len(videos_channel)} with details: {videos_channel}")
    print("✅ Proceso de ingestión de videos de YouTube completado.")
    # 2. DESCARGA: Procesar videos con status 'pending'
    pending_videos = db_get_videos_by_status('pending')
    if len(pending_videos) == 0:
        print("✅ No hay videos pendientes de descarga.")
    else:
        print(f"✅ Videos pendientes de procesamiento: {len(pending_videos)}, details: {pending_videos}")
        for video in pending_videos:
        # Desempaquetado claro (asumiendo el orden de tu SELECT actual)
            video_id, title, video_url, *_ = video 
            
            print(f"→ Descargando: {title}")
            result = download_audio(video_url, video_id)
            
            if result.get('status') == 'downloaded':
                # Actualizar estado en DB y validar
                if download_youtube_ingestion(video_id):
                    print(f"✅ Audio guardado y estado actualizado.")
                    
                    # Validación de integridad
                    if validate_video_metadata(video_id): # Sugerencia: validar por video_id si es posible
                        if validate_youtube_video(video_id): # Cambia a video_id si tu función lo soporta
                            print(f"✅ Validación exitosa.")
                        else:
                            error_youtube_ingestion(video_id, "Error en validación de video en DB.")
                            print(f"❌ Falló validación de video en db.")
                    else:
                        error_youtube_ingestion(video_id, "Error en validación de integridad.")
                        print(f"❌ Falló validación de integridad.")
            else:
                print(f"⚠️ El video: {title} (ID: {video_id}) no se descargó correctamente, por lo que se omite la validación.")
    
    # 3. TRANSCRIPCIÓN: Procesar videos con status 'validate'
    validate_videos = db_get_videos_by_status('validate')
    
    for video in validate_videos:
        video_id,*_ = video
        
        print(f"→ Transcribiendo: {video_id}")
        video_transcription = transcribe_audio(video_id)
        
        # Usamos .get() para evitar KeyErrors
        texto = video_transcription.get('transcription')
        
        if texto:
            if process_youtube_ingestion(video_id, texto):
                print(f"✅ Transcripción procesada y finalizada.")
            else:
                error_youtube_ingestion(video_id, "Error al guardar transcripción en DB.")
                print(f"❌ Error al guardar transcripción en DB.")
        else:
            error_youtube_ingestion(video_id, "Error: La transcripción volvió vacía.")
            print(f"❌ Error: La transcripción volvió vacía.")

    print("🏁 Proceso completado.")


    # 4. Crear resumen del texto 
    

            
        
        
        
