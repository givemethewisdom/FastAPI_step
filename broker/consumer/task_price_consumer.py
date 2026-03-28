import logging

from pika.adapters.blocking_connection import BlockingConnection

from app.logger import setup_logger
from app.services.cashe.rabbit_ticker_cash import RedisCache
from app.services.dependencies import CashRedisDep
from broker.rabbit_params import connection_params


setup_logger()

logging.getLogger("pika").setLevel(logging.WARNING)

logger = logging.getLogger("consumer.task_price")


class TaskPriceConsumer:
    """надо переделать под разные очереди!!!!!!!!!!!!!"""

    def __init__(self, cache: CashRedisDep, queue: str):
        self.cache = cache
        self.queue = "task_price"

    def callback(self, ch, method, properties, body):
        # cash
        ticker = body.decode()
        logger.debug("ticker:%s", ticker)
        cache_key = f"ticker:{ticker}"
        self.cache.set(cache_key, ticker)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def task_consumer(self):
        with BlockingConnection(connection_params) as conn:
            with conn.channel() as channel:
                channel.queue_declare(queue="task_price")  # надо бы название очереди не палить

                channel.basic_consume(
                    queue="task_price",
                    on_message_callback=self.callback,
                )

                channel.start_consuming()


if __name__ == "__main__":
    # пока запускаю так
    cache = RedisCache()
    consumer = TaskPriceConsumer(cache=cache, queue="task_price")
    consumer.task_consumer()
