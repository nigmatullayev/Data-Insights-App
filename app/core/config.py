import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
