import logging

from pika.adapters.blocking_connection import BlockingConnection

from broker.rabbit_params import connection_params


logger = logging.getLogger(__name__)


def callback(ch, method, properties, body):
    logger.info("received message body:%s", body.decode())

    # не удаляю сообщения чтобы наполянть очередь
    # ch.basic_ack(delivery_tag=method.delivery_tag)


def task_consumer():
    with BlockingConnection(connection_params) as conn:
        with conn.channel() as channel:
            channel.queue_declare(queue="task_price")  # надо бы название очереди не палить

            channel.basic_consume(
                queue="task_price",
                on_message_callback=callback,
            )

            channel.start_consuming()


if __name__ == "__main__":
    task_consumer()
