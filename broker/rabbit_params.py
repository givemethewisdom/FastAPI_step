import pika
from pika.credentials import PlainCredentials

from app import load_config


config = load_config()

# Создаем credentials из config
credentials = PlainCredentials(config.rabbit.user, config.rabbit.password)

connection_params = pika.ConnectionParameters(host=config.rabbit.host, port=config.rabbit.port, credentials=credentials)
