"""Facade: one simple interface over config, logging, validation, operations,
history persistence, observers, and undo/redo."""

from decimal import Decimal
from typing import List, Optional

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import UndoRedoManager
from app.exceptions import OperationError, ValidationError
from app.history import (
    AutoSaveObserver,
    LoggingObserver,
    Observer,
    load_history,
    save_history,
)
from app.input_validators import InputValidator
from app.logger import Logger
from app.operations import Operation


class Calculator:
    """Coordinates every part of the calculator behind a few simple methods."""

    def __init__(self, config=None, logger=None):
        self.config = config or CalculatorConfig()
        self.config.validate()
        self.logger = logger or Logger(self.config)

        self.history: List[Calculation] = []
        self._operation: Optional[Operation] = None
        self._observers: List[Observer] = []
        self._undo_redo = UndoRedoManager()

        self.add_observer(LoggingObserver(self.logger))
        # A function, not the list itself, so the observer always sees the current history
        self.add_observer(AutoSaveObserver(self.config, lambda: self.history, self.logger))

        # Load saved history, otherwise the first auto-save would overwrite it
        try:
            self.history = load_history(self.config)
        except OperationError as error:
            self.logger.warning(f"Could not load existing history: {error}")
        self.logger.info("Calculator started")

    # --- Observer pattern -------------------------------------------------

    def add_observer(self, observer: Observer) -> None:
        """Register an observer to be told about each new calculation."""
        self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        """Stop notifying an observer."""
        self._observers.remove(observer)

    def _notify(self, calculation: Calculation) -> None:
        for observer in self._observers:
            observer.update(calculation)

    # --- Strategy pattern -------------------------------------------------

    def set_operation(self, operation: Operation) -> None:
        """Choose which operation the next calculation will use."""
        self._operation = operation

    def perform_operation(self, a, b) -> Decimal:
        """Validate the inputs, run the current operation, and record the result.

        Raises:
            OperationError: if no operation is set or the operation fails.
            ValidationError: if an input is not a usable number.
        """
        if self._operation is None:  # LBYL: check before doing any work
            raise OperationError("No operation selected")

        name = type(self._operation).__name__
        try:
            number_a = InputValidator.validate_number(a, self.config)
            number_b = InputValidator.validate_number(b, self.config)
            result = self._round(self._operation.execute(number_a, number_b))
        except (ValidationError, OperationError) as error:
            self.logger.error(f"{name} failed: {error}")
            raise

        calculation = Calculation(name, number_a, number_b, result)
        self._undo_redo.save_state(self.history)
        self.history.append(calculation)
        if len(self.history) > self.config.max_history_size:
            self.history.pop(0)
        self._notify(calculation)
        return result

    def _round(self, result: Decimal) -> Decimal:
        """Round to the configured number of decimal places, only if there are more."""
        if result.as_tuple().exponent < -self.config.precision:
            return result.quantize(Decimal(1).scaleb(-self.config.precision))
        return result

    # --- Undo / redo (Memento pattern) -----------------------------------

    def undo(self) -> bool:
        """Step back one calculation. Returns False if there is nothing to undo."""
        previous = self._undo_redo.undo(self.history)
        if previous is None:  # not "if not previous": an empty history is a valid result
            return False
        self.history = previous
        return True

    def redo(self) -> bool:
        """Step forward again after an undo. Returns False if there is nothing to redo."""
        following = self._undo_redo.redo(self.history)
        if following is None:
            return False
        self.history = following
        return True

    # --- History ----------------------------------------------------------

    def show_history(self) -> List[str]:
        """Return the history as printable strings."""
        return [str(calculation) for calculation in self.history]

    def clear_history(self) -> None:
        """Empty the history and forget all undo/redo states."""
        self.history = []
        self._undo_redo.clear()
        self.logger.info("History cleared")

    def save(self) -> None:
        """Write the history to the CSV file."""
        save_history(self.history, self.config)
        self.logger.info(f"History saved to {self.config.history_file}")

    def load(self) -> None:
        """Replace the current history with the contents of the CSV file."""
        self.history = load_history(self.config)
        self._undo_redo.clear()
        self.logger.info(f"History loaded from {self.config.history_file}")