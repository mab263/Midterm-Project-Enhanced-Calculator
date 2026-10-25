"""Memento pattern: snapshots of the calculation history for undo and redo."""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from app.calculation import Calculation


@dataclass(frozen=True)
class CalculatorMemento:
    """An immutable snapshot of the calculation history."""

    history: Tuple[Calculation, ...]

    @classmethod
    def from_history(cls, history: List[Calculation]) -> "CalculatorMemento":
        """Take a snapshot. The tuple is a copy, so later changes to the list don't affect it."""
        return cls(tuple(history))

    def restore(self) -> List[Calculation]:
        """Return the snapshot as a new list the caller is free to modify."""
        return list(self.history)


class UndoRedoManager:
    """Caretaker: keeps the undo and redo stacks of mementos."""

    def __init__(self):
        self._undo_stack: List[CalculatorMemento] = []
        self._redo_stack: List[CalculatorMemento] = []

    def save_state(self, history: List[Calculation]) -> None:
        """Snapshot the history before it changes. A new change makes old redos invalid."""
        self._undo_stack.append(CalculatorMemento.from_history(history))
        self._redo_stack.clear()

    def undo(self, current_history: List[Calculation]) -> Optional[List[Calculation]]:
        """Return the previous history, or None if there is nothing to undo."""
        if not self._undo_stack:
            return None
        self._redo_stack.append(CalculatorMemento.from_history(current_history))
        return self._undo_stack.pop().restore()

    def redo(self, current_history: List[Calculation]) -> Optional[List[Calculation]]:
        """Return the history that was undone, or None if there is nothing to redo."""
        if not self._redo_stack:
            return None
        self._undo_stack.append(CalculatorMemento.from_history(current_history))
        return self._redo_stack.pop().restore()

    def clear(self) -> None:
        """Forget all saved states (used when the history is cleared)."""
        self._undo_stack.clear()
        self._redo_stack.clear()