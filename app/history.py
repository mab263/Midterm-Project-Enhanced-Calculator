"""Calculation history: pandas-based CSV persistence."""

from abc import ABC, abstractmethod
from typing import Callable, List

import pandas as pd

from app.calculation import Calculation
from app.exceptions import OperationError

COLUMNS = ["operation", "operand1", "operand2", "result", "timestamp"]


def save_history(history: List[Calculation], config) -> None:
    """Write the history to the configured CSV file using pandas.

    Raises:
        OperationError: if the file or its directory can't be written.
    """
    try:  # EAFP: attempt the write, handle the failure
        config.history_dir.mkdir(parents=True, exist_ok=True)
        frame = pd.DataFrame([item.to_dict() for item in history], columns=COLUMNS)
        frame.to_csv(config.history_file, index=False, encoding=config.default_encoding)
    except OSError as error:
        raise OperationError(f"Failed to save history: {error}")


def load_history(config) -> List[Calculation]:
    """Read the history CSV with pandas and rebuild the Calculation objects.

    Returns an empty list if no history file exists yet.

    Raises:
        OperationError: if the file is unreadable, empty, or malformed.
    """
    if not config.history_file.exists():  # LBYL: a missing file is normal on first run
        return []

    try:
        frame = pd.read_csv(
            config.history_file,
            dtype=str,
            keep_default_na=False,
            encoding=config.default_encoding,
        )
    except (OSError, ValueError) as error:
        raise OperationError(f"Failed to load history: {error}")

    return [Calculation.from_dict(row) for row in frame.to_dict("records")]



class Observer(ABC):
    """Base class for anything that reacts to a completed calculation."""

    @abstractmethod
    def update(self, calculation: Calculation) -> None:
        """Called each time a calculation completes."""


class LoggingObserver(Observer):
    """Writes the details of each calculation to the log."""

    def __init__(self, logger):
        self._logger = logger

    def update(self, calculation: Calculation) -> None:
        self._logger.info(
            f"Calculation performed: operation={calculation.operation}, "
            f"operand1={calculation.operand1}, operand2={calculation.operand2}, "
            f"result={calculation.result}"
        )


class AutoSaveObserver(Observer):
    """Saves the full history to CSV after each calculation, if auto-save is on."""

    def __init__(self, config, get_history: Callable[[], List[Calculation]], logger):
        self._config = config
        self._get_history = get_history
        self._logger = logger

    def update(self, calculation: Calculation) -> None:
        if not self._config.auto_save:
            return
        try:
            save_history(self._get_history(), self._config)
        except OperationError as error:
            # The calculation itself succeeded, so a failed save is a warning, not a crash.
            self._logger.warning(f"Auto-save failed: {error}")