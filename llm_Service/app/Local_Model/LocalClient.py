from app.LLM_Integration.config import OLLAMA_API_URL, LOCAL_MODEL_NAME , REQUEST_TIMEOUT_SECONDS

import requests
import json
import os

class LocalResponse:
    def __init__(self, json_data):
        # Mapeamos 'response' de Ollama al atributo .text de Gemini
        self.text = json_data.get("response", "")
        self.model = json_data.get("model", "")
        self.prompt_tokens = json_data.get("prompt_eval_count", 0)
        self.completion_tokens = json_data.get("eval_count", 0)
        self.total_duration = json_data.get("total_duration", 0)
        self.done = json_data.get("done", False)
        # Guardamos el resto por si necesitas métricas de tokens
        self.raw = json_data

class LocalClient:
    def __init__(self,base_url=OLLAMA_API_URL, model_name=LOCAL_MODEL_NAME):
        self.base_url = base_url
        self.model_name = model_name
        self.session = requests.Session()
        self.headers = {
            "Content-Type": "application/json"}
        
    
    def _post(self, endpoint, data):
        """Método privado para manejar la comunicación sucia."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.post(
                url, 
                headers=self.headers, 
                json=data,
                timeout=REQUEST_TIMEOUT_SECONDS # Ollama puede tardar en pensar
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en LocalClient: {e}")
            return {"response": f"Error de conexión: {str(e)}", "done": True}

    def generate(self, prompt, system_prompt=None):
        """Método de alto nivel para generar texto."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False, # Desactivamos stream para recibir el JSON completo
                "options": {
                "temperature": 0.2,
                "num_predict": int(os.getenv("MAX_TOKENS", 2048))
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt

        json_res = self._post("/api/generate", payload)
        return LocalResponse(json_res)
    

    def close(self):
        """Cierra la sesión de forma limpia."""
        self.session.close()
        