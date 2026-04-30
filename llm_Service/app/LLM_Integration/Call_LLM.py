import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from .config import OLLAMA_API_URL, MODEL_NAME , REQUEST_TIMEOUT_SECONDS
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

env_path = BASE_DIR / ".env"

load_dotenv(env_path)

def selectLLM(prompt: str, llmResource:bool = False) -> str:
    """
    Función para seleccionar entre LLM local (Ollama) o en la nube (Gemini).
    Por defecto, se utiliza el LLM local. Si llmType es True, se llama al LLM en la nube.
    """
    if llmResource:
        return callLLM_Cloud(prompt)
    else:
        return callLLM_Local(prompt)

def callLLM_Local(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 250
        }
    }

    response = requests.post(OLLAMA_API_URL, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    data = response.json()

    return {
        "response": data.get("response", ""),
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "completion_tokens": data.get("eval_count", 0),
        "total_duration": data.get("total_duration", 0)
    }

def callLLM_Cloud(prompt: str) -> str:
    """
    Envía un prompt a la API de Gemini y retorna la respuesta de texto.
    Optimizada para la SDK v2 de Google GenAI.
    """
    try:
        # Inicialización del cliente
        client = genai.Client(api_key=os.getenv("API_KEY"))
        model_id = os.getenv("MODEL_NAME", "gemini-2.5-flash")

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

        # Es crucial retornar .text para obtener solo el string de respuesta
        return response.text

    except Exception as e:
        return f"Error al llamar a la API: {str(e)}"
        
