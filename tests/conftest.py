import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig


@pytest.fixture
def config(tmp_path, monkeypatch):
    """A real config whose files all live in a throwaway folder."""
    settings = {
        "CALCULATOR_LOG_DIR": str(tmp_path / "logs"),
        "CALCULATOR_HISTORY_DIR": str(tmp_path / "history"),
        "CALCULATOR_LOG_FILE": "test.log",
        "CALCULATOR_HISTORY_FILE": "history.csv",
        "CALCULATOR_MAX_HISTORY_SIZE": "100",
        "CALCULATOR_AUTO_SAVE": "true",
        "CALCULATOR_PRECISION": "10",
        "CALCULATOR_MAX_INPUT_VALUE": "1000000",
        "CALCULATOR_DEFAULT_ENCODING": "utf-8",
    }
    for name, value in settings.items():
        monkeypatch.setenv(name, value)
    return CalculatorConfig()


@pytest.fixture
def calculator(config):
    return Calculator(config)