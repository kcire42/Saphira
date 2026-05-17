import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from .config import OLLAMA_API_URL, LOCAL_MODEL_NAME, CLOUD_MODEL_NAME, REQUEST_TIMEOUT_SECONDS
from google import genai
from google.genai import types
from app.Local_Model.LocalClient import LocalClient

saphira_local_client = LocalClient()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

env_path = BASE_DIR / ".env"

load_dotenv(env_path)

def selectLLM(prompt: str, llmResource:bool = False) -> str:
    """
    Función para seleccionar entre LLM local (Ollama) o en la nube (Gemini).
    Por defecto, se utiliza el LLM local. Si llmType es True, se llama al LLM en la nube.
    """
    print(f"LLM Resource Selected: llmResource={llmResource}")
    if llmResource:
        return callLLM_Cloud(prompt)
    else:
        return callLLM_Local(prompt)

def callLLM_Local(prompt: str) -> str:
    try:
        response = saphira_local_client.generate(prompt)
        print(f"Ollama API Response: {response.raw}")
        return {
            "text": response.text, # Extrae el texto principal
            "prompt_tokens": response.prompt_tokens, # Extrae el conteo de tokens del prompt
            "completion_tokens": response.completion_tokens, # Extrae el conteo de tokens de la respuesta
            "total_duration": response.total_duration # Extrae la duración total de la generación
        }
    except Exception as e:
        return f"Error al llamar a Ollama: {str(e)}"

def callLLM_Cloud(prompt: str) -> str:
    """
    Envía un prompt a la API de Gemini y retorna la respuesta de texto.
    Optimizada para la SDK v2 de Google GenAI.
    """
    try:
        # Inicialización del cliente
        client = genai.Client(api_key=os.getenv("API_KEY"))
        model_id = os.getenv("CLOUD_MODEL_NAME", "gemini-3.1-flash-lite")

        # Generación de contenido
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            # Configuración opcional para mayor control
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
        )
        print(f"Gemini API Response: {response}")
        #gemini regresa un objeto 
        return {
            "text": response.text, # Extrae el texto principal
            "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
            "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
            "total_duration": 0 # Google no devuelve duración total en el metadata de tokens
        }

    except Exception as e:
        return f"Error al llamar a la API: {str(e)}"
        
