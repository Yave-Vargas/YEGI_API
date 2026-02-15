import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class Settings:
    def __init__(self):
        self.FRONTEND_ORIGINS: List[str] = self._get_origins()

    def _get_origins(self) -> List[str]:
        origins = os.getenv("FRONTEND_ORIGINS", "")
        return [
            origin.strip()
            for origin in origins.split(",")
            if origin.strip()
        ]

settings = Settings()
