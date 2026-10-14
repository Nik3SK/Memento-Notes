import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values


DEFAULT_ENV_FILE = ".env"


@dataclass(frozen=True)
class Settings:
    app_name: str = "Memento Notes API"
    app_version: str = "0.2.0"
    log_level: str = "INFO"


def load_settings(env_file: str | Path | None = None) -> Settings:
    env_path = Path(env_file or os.getenv("MEMENTO_ENV_FILE", DEFAULT_ENV_FILE))
    file_values = dotenv_values(env_path) if env_path.exists() else {}

    def get_value(name: str, default: str) -> str:
        return os.getenv(name) or file_values.get(name) or default

    return Settings(
        app_name=get_value("MEMENTO_APP_NAME", Settings.app_name),
        app_version=get_value("MEMENTO_APP_VERSION", Settings.app_version),
        log_level=get_value("MEMENTO_LOG_LEVEL", Settings.log_level),
    )
