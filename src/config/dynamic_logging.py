"""
Simple multi-color logging formatter like loguru.

Colors different parts of each log line:
- Timestamp: dim
- Level: level-specific colors
- Logger name: app-specific colors
- Message: white
"""

import logging


class MultiColorFormatter(logging.Formatter):
    """Simple multi-color formatter with different colors per log line component."""

    # ANSI color codes
    COLORS = {
        "reset": "\033[0m",
        "dim": "\033[2m",
        "white": "\033[37m",
        "cyan": "\033[36m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "red": "\033[31m",
        "magenta": "\033[35m",
        "blue": "\033[34m",
    }

    # Level colors
    LEVEL_COLORS = {
        "DEBUG": "dim",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "magenta",
    }

    # Logger colors by app
    LOGGER_COLORS = {
        "apps.ai": "cyan",
        "apps.accounts": "green",
        "apps.stories": "yellow",
        "celery": "magenta",
        "django": "dim",
    }

    def format(self, record: logging.LogRecord) -> str:
        # Get colors
        timestamp_color = self.COLORS["dim"]
        level_color = self.COLORS[self.LEVEL_COLORS.get(record.levelname, "white")]

        # Logger color based on app
        logger_color = self.COLORS["white"]
        for prefix, color in self.LOGGER_COLORS.items():
            if record.name.startswith(prefix):
                logger_color = self.COLORS[color]
                break

        message_color = self.COLORS["white"]
        reset = self.COLORS["reset"]

        # Format timestamp
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

        # Build colored log line
        return (
            f"{timestamp_color}[{timestamp}]{reset} "
            f"{level_color}{record.levelname:<8}{reset} "
            f"{logger_color}{record.name}{reset}: "
            f"{message_color}{record.getMessage()}{reset}"
        )


def get_multi_color_formatter(**kwargs) -> MultiColorFormatter:
    """Factory function to create a multi-color formatter."""
    return MultiColorFormatter(**kwargs)


def get_contextual_logger(name: str) -> logging.Logger:
    """
    Get a logger with enhanced context methods.
    """
    logger = logging.getLogger(name)

    # Add convenience methods for common patterns
    def task_start(message: str, task_id: str = None):
        prefix = "🚀 TASK STARTING"
        if task_id:
            prefix += f" [{task_id}]"
        logger.info(f"{prefix}: {message}")

    def task_complete(message: str, task_id: str = None):
        prefix = "✅ TASK COMPLETE"
        if task_id:
            prefix += f" [{task_id}]"
        logger.info(f"{prefix}: {message}")

    def task_error(message: str, task_id: str = None):
        prefix = "❌ TASK ERROR"
        if task_id:
            prefix += f" [{task_id}]"
        logger.error(f"{prefix}: {message}")

    def ai_processing(message: str):
        logger.info(f"🤖 AI PROCESSING: {message}")

    def user_action(message: str, user_id: str = None):
        prefix = "👤 USER ACTION"
        if user_id:
            prefix += f" [{user_id}]"
        logger.info(f"{prefix}: {message}")

    def data_operation(message: str, operation: str = None):
        prefix = "💾 DATA"
        if operation:
            prefix += f" {operation.upper()}"
        logger.info(f"{prefix}: {message}")

    # Attach methods to logger instance
    logger.task_start = task_start
    logger.task_complete = task_complete
    logger.task_error = task_error
    logger.ai_processing = ai_processing
    logger.user_action = user_action
    logger.data_operation = data_operation

    return logger
