from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY : str 
    JWT_ALGORITHM : str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES : int 
    REFRESH_TOKEN_EXPIRE_DAYS : int 
    AI_API_KEY: str = ""
    AI_MODEL: str = "openai/gpt-oss-120b"
    
    class Config:
        env_file = '.env',
        env_file_encoding="utf-8",
        extra = 'ignore'
        
settings = Settings()