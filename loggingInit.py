import logging
import pathlib
import sys
import functools

from datetime import datetime

logger = logging.getLogger(__name__)

def my_handler(type, value, tb):
    logging.exception("Uncaught exception: {0}".format(str(value)))


def initLogger():
    curPath = pathlib.Path(__file__).parent.resolve()
    logPath = curPath / "logs"

    sys.excepthook = my_handler

    logging.basicConfig(
        filename=logPath / datetime.today().strftime("%Y-%m-%d"),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
        datefmt='%H:%M:%S'
    )


def log_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Function '{func.__name__}' started.")
        result = func(*args, **kwargs)
        logger.info(f"Function '{func.__name__}' complete.")
        return result

    return wrapper
