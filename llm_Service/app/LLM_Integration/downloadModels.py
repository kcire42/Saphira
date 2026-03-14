import os
from .config import EMBEDDING_MODEL_NAME
from sentence_transformers import SentenceTransformer

def download():
    """
    Gestiona la descarga y actualización del modelo de embeddings 
    directamente desde Hugging Face.
    """
    # 1. Configuramos la ruta de caché para que Docker persista los datos
    # Es mejor usar la variable de entorno estándar de HF
    base_dir = os.path.abspath(os.getcwd())
    local_cache_path = os.path.join(base_dir, "model_cache")
    
    os.environ['HF_HOME'] = local_cache_path # Establece la raíz de HF en tu carpeta
    os.environ['SENTENCE_TRANSFORMERS_HOME'] = local_cache_path

    print(f"→ Punto de control: Usando caché en {local_cache_path}")

    try:
        # 2. Intentamos cargar/descargar el modelo
        # Al tener internet, SentenceTransformer busca primero localmente, 
        # y si no existe o hay una actualización, lo baja de Hugging Face.
        print(f"⏳ Sincronizando modelo '{EMBEDDING_MODEL_NAME}' con Hugging Face...")
        
        model = SentenceTransformer(
            EMBEDDING_MODEL_NAME, 
            cache_folder=local_cache_path,
            trust_remote_code=True # Recomendado para modelos nuevos en HF
        )
        
        # 3. Verificación simple
        print(f"✅ ÉXITO: Modelo listo. Dimensiones de embedding: {model.get_sentence_embedding_dimension()}")

    except Exception as e:
        print(f"❌ ERROR al conectar con Hugging Face: {e}")
        # Aquí podrías decidir si quieres que la app falle o use un fallback


   

if __name__ == "__main__":
    download()
    