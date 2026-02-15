import os
from .config import EMBEDDING_MODEL_NAME
from langchain_community.embeddings import SentenceTransformerEmbeddings

def download():
    model_name = EMBEDDING_MODEL_NAME
    print(f"Download embeddings model {model_name}...")
    SentenceTransformerEmbeddings(model_name=model_name)
    print("Embeddings model ready.")

if __name__ == "__main__":
    download()