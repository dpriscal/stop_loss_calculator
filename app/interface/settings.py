from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings

# Preload environment variables from project-root .env if present
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)


class AppSettings(BaseSettings):
    FINANCIALMODELINGPREP_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> AppSettings:
    return AppSettings()


