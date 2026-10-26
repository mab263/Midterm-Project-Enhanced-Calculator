from decimal import Decimal

import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError, OperationError, ValidationError
from app.operations import OperationFactory

class RecordingObserver:
    """Remembers every calculation it is told about."""

    def __init__(self):
        self.calculations = []

    def update(self, calculation):
        self.calculations.append(calculation)


def use(calculator, name):
    calculator.set_operation(OperationFactory.create_operation(name))


def read_log(config):
    return config.log_file.read_text(encoding="utf-8")


def test_new_calculator_starts_empty(calculator):
    assert calculator.history == []
    assert calculator.show_history() == []


def test_invalid_config_is_rejected(config):
    config.max_history_size = 0
    with pytest.raises(ConfigurationError):
        Calculator(config)


def test_perform_without_operation_raises(calculator):
    with pytest.raises(OperationError, match="No operation"):
        calculator.perform_operation("1", "2")


@pytest.mark.parametrize(
    "name, a, b, expected",
    [
        ("add", "2", "3", "5"),
        ("subtract", " 5 ", "3", "2"),
        ("multiply", 4, 3, "12"),
        ("divide", "10", "4", "2.5"),
        ("power", "2", "3", "8"),
    ],
)
def test_perform_operation_returns_result(calculator, name, a, b, expected):
    use(calculator, name)
    assert calculator.perform_operation(a, b) == Decimal(expected)


def test_perform_operation_records_calculation(calculator):
    use(calculator, "add")
    calculator.perform_operation("2", "3")
    assert calculator.show_history() == ["Addition(2, 3) = 5"]


@pytest.mark.parametrize(
    "name, a, b, error",
    [
        ("add", "abc", "1", ValidationError),
        ("add", "1", "9999999", ValidationError),
        ("divide", "1", "0", OperationError),
    ],
)
def test_failed_operations_raise_and_leave_history_unchanged(
    calculator, config, name, a, b, error
):
    use(calculator, name)
    with pytest.raises(error):
        calculator.perform_operation(a, b)
    assert calculator.history == []
    assert "ERROR" in read_log(config)


@pytest.mark.parametrize(
    "name, a, b, expected",
    [
        ("divide", "10", "3", "3.33"),
        ("divide", "10", "4", "2.5"),
        ("add", "1", "2", "3"),
    ],
)
def test_result_is_rounded_to_configured_precision(calculator, config, name, a, b, expected):
    config.precision = 2
    use(calculator, name)
    assert calculator.perform_operation(a, b) == Decimal(expected)


def test_history_is_trimmed_to_max_size(calculator, config):
    config.max_history_size = 2
    use(calculator, "add")
    for number in ("1", "2", "3"):
        calculator.perform_operation(number, number)
    assert [str(item.operand1) for item in calculator.history] == ["2", "3"]


def test_observers_are_notified_until_removed(calculator):
    observer = RecordingObserver()
    calculator.add_observer(observer)
    use(calculator, "add")
    calculator.perform_operation("1", "1")
    calculator.remove_observer(observer)
    calculator.perform_operation("2", "2")
    assert observer.calculations == [calculator.history[0]]


def test_default_observers_log_and_auto_save(calculator, config):
    use(calculator, "add")
    calculator.perform_operation("2", "3")
    assert "Calculation performed" in read_log(config)
    assert config.history_file.exists()


def test_auto_save_can_be_disabled(calculator, config):
    config.auto_save = False
    use(calculator, "add")
    calculator.perform_operation("2", "3")
    assert not config.history_file.exists()


def test_undo_and_redo(calculator):
    use(calculator, "add")
    calculator.perform_operation("1", "1")
    calculator.perform_operation("2", "2")
    assert calculator.undo() is True
    assert len(calculator.history) == 1
    assert calculator.redo() is True
    assert len(calculator.history) == 2


def test_undo_to_empty_history_still_counts_as_undone(calculator):
    use(calculator, "add")
    calculator.perform_operation("1", "1")
    assert calculator.undo() is True
    assert calculator.history == []


@pytest.mark.parametrize("method", ["undo", "redo"])
def test_nothing_to_undo_or_redo_returns_false(calculator, method):
    assert getattr(calculator, method)() is False


def test_clear_history_empties_history_and_undo(calculator):
    use(calculator, "add")
    calculator.perform_operation("1", "1")
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo() is False


def test_history_is_loaded_when_calculator_starts(calculator, config):
    use(calculator, "add")
    calculator.perform_operation("2", "3")  # auto-save writes the CSV
    restarted = Calculator(config)
    assert restarted.history == calculator.history


def test_malformed_history_file_is_survived_at_startup(config):
    config.history_dir.mkdir(parents=True)
    config.history_file.write_text("not,a,history\n1,2,3\n")
    restarted = Calculator(config)
    assert restarted.history == []
    assert "Could not load" in read_log(config)


def test_save_and_load(calculator, config):
    config.auto_save = False
    use(calculator, "add")
    calculator.perform_operation("2", "3")
    calculator.save()
    calculator.clear_history()
    calculator.load()
    assert calculator.show_history() == ["Addition(2, 3) = 5"]


def test_load_failure_leaves_history_unchanged(calculator, config):
    config.auto_save = False
    use(calculator, "add")
    calculator.perform_operation("2", "3")
    config.history_dir.mkdir(parents=True)
    config.history_file.write_bytes(b"")
    with pytest.raises(OperationError):
        calculator.load()
    assert len(calculator.history) == 1