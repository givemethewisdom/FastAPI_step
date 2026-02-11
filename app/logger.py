import logging


def setup_logger():
    """Настраиваем КОРНЕВОЙ логгер - работает для ВСЕХ модулей"""

    # Настраиваем корневой логгер
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

    return root_logger