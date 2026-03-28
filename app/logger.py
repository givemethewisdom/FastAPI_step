import logging


def setup_logger():
    """Настраиваем корневой логгер"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Очищаем существующие обработчики
    root_logger.handlers.clear()

    # Создаем консольный обработчик
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)

    root_logger.addHandler(ch)

    # Устанавливаем уровень WARNING для pika, чтобы убрать DEBUG логи
    logging.getLogger("pika").setLevel(logging.WARNING)
    # Также можно для других библиотек
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return root_logger
