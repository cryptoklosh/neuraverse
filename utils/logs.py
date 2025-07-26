import asyncio
import logging
from functools import wraps
from loguru import logger



class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Перенаправляем записи из logging в loguru
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())

#logger = logging.getLogger(__name__)

def log_methods_with_module_name(module_name_attr='__module_name__'):
    def decorate_class(cls):
        module_name = getattr(cls, module_name_attr, cls.__name__)

        for attr_name in dir(cls):
            if attr_name.startswith('_'):
                continue

            method = getattr(cls, attr_name)
            if callable(method) and asyncio.iscoroutinefunction(method):
                wrapped = _make_logged_method(method, module_name)
                setattr(cls, attr_name, wrapped)

        return cls

    return decorate_class

def _make_logged_method(method, module_name):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        chain_name = getattr(getattr(self, 'client', None), 'network', None)
        chain_name = getattr(chain_name, 'name', 'unknown').capitalize()
        logger.info(f"[{module_name}] | [{chain_name}] | {method.__name__} started")
        try:
            result = await method(self, *args, **kwargs)
            logger.info(f"[{module_name}] | [{chain_name}] | {result}")
            return result
        except Exception as e:
            logger.error(f"[{module_name}] | [{chain_name}] | {method.__name__} FAILED: {e}")
            raise
    return wrapper
