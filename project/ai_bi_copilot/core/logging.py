import sys

from loguru import logger


def configure_logging():

    logger.remove()

    logger.add(
        sys.stdout,
        level="INFO",
        backtrace=True,
        diagnose=True
    )

    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="30 days"
    )

    return logger