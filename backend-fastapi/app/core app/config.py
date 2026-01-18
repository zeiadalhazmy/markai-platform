import os
from typing import List

def _split_csv(v: str) -> List[str]:
    return [x.strip() for x in v.split(",") if x.strip()]

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://hcakrxaaarkufkxrehwy.supabase.co")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    @property
    def cors_origins_list(self) -> List[str]:
        if (self.CORS_ORIGINS or "").strip() == "*" or not self.CORS_ORIGINS:
            return ["*"]
        return _split_csv(self.CORS_ORIGINS)

settings = Settings()
