# Application configuration / Settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # GroqAI
    GROQ_API_KEY: str
    GROQ_MODEL: str

    LLM_PROVIDER: str = "groq"
    
    # Database
    DATABASE_URL: str

    # FastAPI
    APP_NAME: str
    DEBUG: bool = False

    # WhatsApp
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    VERIFY_TOKEN: str = ""
    WEBHOOK_VERIFY_TOKEN: str = ""
    WHATSAPP_APP_SECRET: str = ""
    WHATSAPP_API_VERSION: str = "v21.0"
    WHATSAPP_BASE_URL: str = "https://graph.facebook.com"
    WEBHOOK_URL: str = ""

    # converation window size
    MEMORY_WINDOW_SIZE: int = 20
    
    # Tool Execution & Checkpointer
    TOOL_EXECUTION_TIMEOUT: int = 15
    CHECKPOINTER_TYPE: str = "memory"
    
    # LangSmith
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    

# It ensures the settings are loaded only once during the application's lifetime instead of reading .env repeatedly.
@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()