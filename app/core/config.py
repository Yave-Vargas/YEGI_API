import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMP_DIR = BASE_DIR / "storage" / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv()

class Settings:
    def __init__(self):
        self.FRONTEND_ORIGINS = self._get_origins()
        self.API_KEYS = self._get_api_keys()

    def _get_origins(self):
        origins = os.getenv("FRONTEND_ORIGINS", "")
        return [o.strip() for o in origins.split(",") if o.strip()]

    def _get_api_keys(self):
        return {
            "internal": [k for k in os.getenv("API_KEYS_INTERNAL", "").split(",") if k],
            "frontend": [k for k in os.getenv("API_KEYS_FRONTEND", "").split(",") if k],
            "public": [k for k in os.getenv("API_KEYS_PUBLIC", "").split(",") if k],
        }

settings = Settings()

