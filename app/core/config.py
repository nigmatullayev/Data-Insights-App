import os
from typing import Tuple
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    
    class Config:
        env_file = ".env"
    
    def validate(self) -> Tuple[bool, str]:
        """
        Validate settings
        Returns: (is_valid, error_message)
        """
        if not self.CEREBRAS_API_KEY:
            return False, "CEREBRAS_API_KEY is not set in environment variables. Please create a .env file with your API key."
        
        if len(self.CEREBRAS_API_KEY) < 10:
            return False, "CEREBRAS_API_KEY appears to be invalid (too short). Please check your .env file."
        
        return True, ""

settings = Settings()
