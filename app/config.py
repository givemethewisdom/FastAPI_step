# config.py
from dataclasses import dataclass

from environs import Env

from .logger import logger

domens = r'@(mail\.ru|gmail\.com|yandex\.ru)$'  # почта для проверки в модели Contacts


@dataclass
class DatabaseConfig:
    database_url: str


@dataclass
class Config:
    db: DatabaseConfig
    secret_key: str
    debug: bool


def load_config(path: str = None) -> Config:
    env = Env()
    logger.info(f'Loading config from')
    env.read_env(path)  # Загружаем переменные окружения из файла .env

    return Config(
        db=DatabaseConfig(database_url=env("DATABASE_URL")),
        secret_key=env("SECRET_KEY"),
        debug=env.bool("DEBUG", default=False)
    )
