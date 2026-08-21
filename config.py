import os
from typing import List, Optional
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    class AppSettings(BaseSettings):
        APP_NAME: str = "Multimodal Document Intelligence Engine"
        VERSION: str = "1.0.0"
        HOST: str = "0.0.0.0"
        PORT: int = 8000
        DEFAULT_VISION_MODEL: str = "gpt-4o-mini-vision"
        SUPPORTED_MODELS: List[str] = [
            "gpt-4o-mini-vision",
            "qwen2-vl-7b-instruct",
            "claude-3-5-sonnet-vision"
        ]
        MAX_UPLOAD_SIZE_MB: int = 25
        CONFIDENCE_THRESHOLD: float = 0.85
        OPENAI_API_KEY: Optional[str] = None
        ANTHROPIC_API_KEY: Optional[str] = None
        model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    settings = AppSettings()
except ImportError:
    class StandaloneSettings:
        APP_NAME: str = "Multimodal Document Intelligence Engine"
        VERSION: str = "1.0.0"
        HOST: str = "0.0.0.0"
        PORT: int = 8000
        DEFAULT_VISION_MODEL: str = "gpt-4o-mini-vision"
        SUPPORTED_MODELS: List[str] = ["gpt-4o-mini-vision", "qwen2-vl-7b-instruct", "claude-3-5-sonnet-vision"]
        MAX_UPLOAD_SIZE_MB: int = 25
        CONFIDENCE_THRESHOLD: float = 0.85
        OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
        ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    settings = StandaloneSettings()
