"""Project logger that writes to the file named in the configuration."""

import logging
import os
from logging.handlers import RotatingFileHandler


class Logger:
    """Wraps Python's logging module, writing to the configured log file."""

    def __init__(self, config, name: str = "calculator"):
        config.log_dir.mkdir(parents=True, exist_ok=True)

        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False  # keep log lines out of the terminal

        # Remove old handlers so creating a Logger twice never duplicates lines
        for handler in list(self._logger.handlers):
            self._logger.removeHandler(handler)
            handler.close()

        file_handler = RotatingFileHandler(
            os.path.abspath(str(config.log_file)),
            maxBytes=1_000_000,
            backupCount=3,
            encoding=config.default_encoding,
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self._logger.addHandler(file_handler)

    def info(self, message: str) -> None:
        """Log a normal event (e.g., a completed calculation)."""
        self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log a recoverable problem (e.g., a history file that couldn't be loaded)."""
        self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log a failure (e.g., a calculation that raised an error)."""
        self._logger.error(message)