import os 

ENV = os.getenv('APP_ENV','local')
# ====================
# OLLAMA
# ===================
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'host.docker.internal' if ENV == 'docker' else 'localhost')
OLLAMA_PORT = int(os.getenv('OLLAMA_PORT',11434))
LOCAL_MODEL_NAME = os.getenv('LOCAL_MODEL_NAME','meta-llama/Llama-3.1-8B')
OLLAMA_API_URL = f'http://{OLLAMA_HOST}:{OLLAMA_PORT}'

CLOUD_MODEL_NAME = os.getenv('CLOUD_MODEL_NAME','gemini-2.5-flash')


#===================
#EMBEDDINGS
#==================
EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME','all-MiniLM-L6-v2')

#===================
#CHROMA
#===================

CHROMA_HOST = 'chroma' if ENV == 'docker' else 'localhost'
CHROMA_PORT = 8000 if ENV == 'docker' else 11743
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME","Knowledgebase")
CHROMA_API_URL = f'http://{CHROMA_HOST}:{CHROMA_PORT}'


#=================
#RUNTIME
#================
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", 180))