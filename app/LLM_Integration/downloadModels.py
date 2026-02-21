import os
import ssl
from .config import EMBEDDING_MODEL_NAME
from langchain_community.embeddings import SentenceTransformerEmbeddings

def download():
    # 1. Mode offline enable
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_HUB_OFFLINE'] = '1'
    
    # 2. Get the absolute path of the model_cache folder
    # We look for the folder in the project root (/app in Docker)
    base_dir = os.path.abspath(os.getcwd())
    local_path = os.path.join(base_dir, "model_cache")
    
    print(f"→ Buscando modelo en ruta absoluta: {local_path}")

    if os.path.exists(local_path) and os.listdir(local_path):
        try:
           # We load from the local route found
            SentenceTransformerEmbeddings(model_name=local_path)
            print("✅ ÉXITO: Modelo cargado desde la carpeta local.")
        except Exception as e:
            print(f"❌ Error al cargar el modelo local: {e}")
            raise e
    else:
        print(f"❌ ERROR: La carpeta {local_path} no existe o está vacía.")
        print(f"Contenido actual de {base_dir}: {os.listdir(base_dir)}")
        raise FileNotFoundError("No se encontró la carpeta model_cache dentro del contenedor.")

if __name__ == "__main__":
    download()