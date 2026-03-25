from typing import List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Keys
    DISCORD_BOT_TOKEN: str
    GEMINI_API_KEY: str
    
    # Database
    MONGODB_URI: str
    DATABASE_NAME: str = "discord_bot"
    
    # Bot Configuration
    BOT_PREFIX: str = "!"
    MAX_MESSAGE_LENGTH: int = 1700
    BOT_ACTIVITY: str = "with your feelings"
    TRACKED_CHANNELS: List[int] = []
    
    # Gemini Configuration
    TEXT_GENERATION_CONFIG: Dict[str, Any] = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        # "max_output_tokens": 512,
    }
    
    IMAGE_GENERATION_CONFIG: Dict[str, Any] = {
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32,
        # "max_output_tokens": 512,
    }
    
    SAFETY_SETTINGS: List[Dict[str, str]] = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
    
    # Bot personality/system prompt template
    BOT_TEMPLATE: List[Dict[str, Any]] = []

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
