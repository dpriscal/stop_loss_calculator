from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

try:
    from dotenv import dotenv_values, load_dotenv  # type: ignore
except ImportError:  # pragma: no cover - optional dependency in production
    load_dotenv = None
    dotenv_values = None

from pydantic import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"


def _load_env_if_possible() -> None:
    if load_dotenv is not None:
        load_dotenv(ENV_PATH, override=True)
    else:
        raise RuntimeError(
            "python-dotenv is required to load environment variables from .env"
        )


_load_env_if_possible()


class AppSettings(BaseSettings):
    FINANCIALMODELINGPREP_API_KEY: Optional[str] = None

    class Config:
        env_file = str(ENV_PATH)
        case_sensitive = True


@lru_cache()
def get_settings() -> AppSettings:
    settings = AppSettings()
    if not settings.FINANCIALMODELINGPREP_API_KEY and dotenv_values is not None:
        vals = dotenv_values(ENV_PATH)
        settings.FINANCIALMODELINGPREP_API_KEY = vals.get(
            "FINANCIALMODELINGPREP_API_KEY"
        )
    return settings
