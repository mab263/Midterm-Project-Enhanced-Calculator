"""Configuration for the calculator, loaded from environment variables."""

import os
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

load_dotenv()


class CalculatorConfig:
    """Calculator settings read from environment variables, with defaults."""

    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent

        self.log_dir = Path(os.getenv("CALCULATOR_LOG_DIR", base_dir / "logs"))
        self.history_dir = Path(os.getenv("CALCULATOR_HISTORY_DIR", base_dir / "history"))
        self.log_file_name = os.getenv("CALCULATOR_LOG_FILE", "calculator.log")
        self.history_file_name = os.getenv("CALCULATOR_HISTORY_FILE", "calculator_history.csv")
        self.max_history_size = int(os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "100"))
        self.auto_save = os.getenv("CALCULATOR_AUTO_SAVE", "true").lower() == "true"
        self.precision = int(os.getenv("CALCULATOR_PRECISION", "10"))
        self.max_input_value = Decimal(os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1000000"))
        self.default_encoding = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")

    @property
    def log_file(self):
        """Full path to the log file."""
        return self.log_dir / self.log_file_name

    @property
    def history_file(self):
        """Full path to the history CSV file."""
        return self.history_dir / self.history_file_name

    def validate(self):
        """Raise ConfigurationError if any setting is invalid."""
        if self.max_history_size <= 0:
            raise ConfigurationError("max_history_size must be positive")
        if self.precision <= 0:
            raise ConfigurationError("precision must be positive")
        if self.max_input_value <= 0:
            raise ConfigurationError("max_input_value must be positive")