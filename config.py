import os
from pathlib import Path
from typing import List, Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    class AppSettings(BaseSettings):
        APP_NAME: str = "ReconcileAI"
        VERSION: str = "2.0.0"
        HOST: str = "0.0.0.0"
        PORT: int = 8000
        DEFAULT_VISION_MODEL: str = "gemini-2.5-flash"
        SUPPORTED_MODELS: List[str] = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
        MAX_UPLOAD_SIZE_MB: int = 25
        CONFIDENCE_THRESHOLD: float = 0.85
        GEMINI_API_KEY: Optional[str] = None
        DATA_DIR: Path = Path("data")
        DATABASE_PATH: Path = Path("data/reconcile_ai.db")
        MAX_PAGES: int = 10
        MAX_ESTIMATED_COST_USD: float = 20.0
        GEMINI_INPUT_USD_PER_M_TOKEN: float = 0.30
        GEMINI_OUTPUT_USD_PER_M_TOKEN: float = 2.50
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    settings = AppSettings()
except ImportError:
    class StandaloneSettings:
        APP_NAME: str = "ReconcileAI"
        VERSION: str = "2.0.0"
        HOST: str = "0.0.0.0"
        PORT: int = 8000
        DEFAULT_VISION_MODEL: str = "gemini-2.5-flash"
        SUPPORTED_MODELS: List[str] = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
        MAX_UPLOAD_SIZE_MB: int = 25
        CONFIDENCE_THRESHOLD: float = 0.85
        GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
        DATA_DIR: Path = Path(os.getenv("DATA_DIR", "data"))
        DATABASE_PATH: Path = Path(os.getenv("DATABASE_PATH", "data/reconcile_ai.db"))
        MAX_PAGES: int = 10
        MAX_ESTIMATED_COST_USD: float = 20.0
        GEMINI_INPUT_USD_PER_M_TOKEN: float = 0.30
        GEMINI_OUTPUT_USD_PER_M_TOKEN: float = 2.50
    settings = StandaloneSettings()
