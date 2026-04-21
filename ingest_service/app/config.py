import os 
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent



class Settings:
    PROJECT_NAME: str = "Ingest Service"
    PROJECT_VERSION: str = "1.0.0"
    MODEL_WHISPER: str = "small"
    LLM_SERVICE_URL: str = "http://llm_service:8000//text/"
    DATA_DIR: Path = Path(os.getenv("DATA_PATH", BASE_DIR / "app" / "Youtube_Extractor" / "data"))
    MODELS_DIR: Path = Path(os.getenv("MODELS_PATH", BASE_DIR / "app" / "Youtube_Extractor" / "models"))

settings = Settings()

