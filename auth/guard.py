"""
Модуль для создания единого экземпляра guard для всего приложения.
Все модули должны импортировать guard отсюда.
Сделал его так как вынес функцию require_access_with_rate_limit в sequrity
 и теперь guard нужен и там и в ендпоинте
"""
import logging
from rbacx import Guard
from rbacx.policy.loader import FilePolicySource, HotReloader

logger = logging.getLogger(__name__)


guard = Guard(policy={})

def init_guard():
    """Инициализирует guard с загрузкой политик из файла"""
    try:
        logger.info("try to reloader in guard")
        reloader = HotReloader(
            guard,
            FilePolicySource("auth/policy.json"),
            initial_load=True,
        )
        reloader.check_and_reload()
        logger.info("Guard инициализирован с политиками из auth/policy.json")
    except Exception as e:
        logger.error(f" Ошибка инициализации guard: {e}")
        raise

def get_guard():
    """Получить глобальный экземпляр guard"""
    return guard
