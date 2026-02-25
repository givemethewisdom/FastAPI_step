# app/config.py
import logging
from dataclasses import dataclass

from environs import Env


# Просто получаем логгер, он будет использовать корневой логгер
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    database_url: str


@dataclass
class Config:
    db: DatabaseConfig
    secret_key: str
    debug: bool


_config: Config = None


def load_config(path: str = None) -> Config:
    global _config
    if _config is None:
        env = Env()
        logger.info("Loading config from environment")  # Будет использовать корневой логгер
        env.read_env(path)

        _config = Config(
            db=DatabaseConfig(database_url=env("DATABASE_URL")),
            secret_key=env("SECRET_KEY"),
            debug=env.bool("DEBUG", default=False),
        )
    return _config


def get_config() -> Config:
    if _config is None:
        raise RuntimeError("Config not loaded. Call load_config() first.")
    return _config
