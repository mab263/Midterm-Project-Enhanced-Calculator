from dataclasses import FrozenInstanceError
from datetime import datetime
from decimal import Decimal

import pytest

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento, UndoRedoManager


def calc(number):
    return Calculation("add", Decimal(number), Decimal(1), Decimal(number) + 1, datetime(2026, 1, 1))


def test_memento_is_a_snapshot_of_the_history():
    history = [calc(1)]
    memento = CalculatorMemento.from_history(history)
    history.append(calc(2))
    assert memento.restore() == [calc(1)]


def test_restore_returns_a_new_list():
    memento = CalculatorMemento.from_history([calc(1)])
    restored = memento.restore()
    restored.append(calc(2))
    assert memento.restore() == [calc(1)]


def test_memento_is_immutable():
    memento = CalculatorMemento.from_history([calc(1)])
    with pytest.raises(FrozenInstanceError):
        memento.history = ()


@pytest.mark.parametrize("method", ["undo", "redo"])
def test_nothing_to_undo_or_redo_returns_none(method):
    manager = UndoRedoManager()
    assert getattr(manager, method)([calc(1)]) is None


def test_undo_restores_previous_state():
    manager = UndoRedoManager()
    manager.save_state([calc(1)])
    assert manager.undo([calc(1), calc(2)]) == [calc(1)]


def test_redo_restores_undone_state():
    manager = UndoRedoManager()
    manager.save_state([calc(1)])
    manager.undo([calc(1), calc(2)])
    assert manager.redo([calc(1)]) == [calc(1), calc(2)]


def test_undo_to_empty_history_returns_empty_list_not_none():
    manager = UndoRedoManager()
    manager.save_state([])
    assert manager.undo([calc(1)]) == []


def test_new_change_clears_redo():
    manager = UndoRedoManager()
    manager.save_state([calc(1)])
    manager.undo([calc(1), calc(2)])
    manager.save_state([calc(1)])
    assert manager.redo([calc(1), calc(3)]) is None


def test_clear_empties_both_stacks():
    manager = UndoRedoManager()
    manager.save_state([calc(1)])
    manager.undo([calc(1), calc(2)])
    manager.clear()
    assert manager.undo([]) is None
    assert manager.redo([]) is None


def test_full_undo_redo_sequence():
    a, b = calc(1), calc(2)
    manager = UndoRedoManager()
    manager.save_state([])
    manager.save_state([a])
    assert manager.undo([a, b]) == [a]
    assert manager.undo([a]) == []
    assert manager.undo([]) is None
    assert manager.redo([]) == [a]
    assert manager.redo([a]) == [a, b]
    assert manager.redo([a, b]) is None