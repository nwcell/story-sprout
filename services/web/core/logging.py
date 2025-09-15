import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logger():
    # Clear default handlers
    logging.root.handlers = []
    logging.root.setLevel(logging.INFO)

    # Redirect stdlib logging (Django, Daphne, etc.) -> Loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # Configure Loguru
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        colorize=True,
        backtrace=True,
        diagnose=False,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<magenta>{function}</magenta>:<yellow>{line}</yellow> | "
        "<level>{message}</level>",
    )

    return logger
