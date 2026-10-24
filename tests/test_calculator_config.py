from decimal import Decimal

import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError

ENV_VARS = [
    "CALCULATOR_LOG_DIR",
    "CALCULATOR_HISTORY_DIR",
    "CALCULATOR_LOG_FILE",
    "CALCULATOR_HISTORY_FILE",
    "CALCULATOR_MAX_HISTORY_SIZE",
    "CALCULATOR_AUTO_SAVE",
    "CALCULATOR_PRECISION",
    "CALCULATOR_MAX_INPUT_VALUE",
    "CALCULATOR_DEFAULT_ENCODING",
]


@pytest.fixture
def clean_env(monkeypatch):
    """Remove every calculator setting so each test starts from a blank environment."""
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_defaults_when_no_env_vars_set(clean_env):
    config = CalculatorConfig()
    assert config.max_history_size == 100
    assert config.auto_save is True
    assert config.precision == 10
    assert config.max_input_value == Decimal("1000000")
    assert config.default_encoding == "utf-8"
    assert config.log_file_name == "calculator.log"
    assert config.history_file_name == "calculator_history.csv"


def test_custom_values_are_read_from_env(clean_env, monkeypatch):
    monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "50")
    monkeypatch.setenv("CALCULATOR_PRECISION", "4")
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "500")
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", "latin-1")

    config = CalculatorConfig()

    assert config.max_history_size == 50
    assert config.precision == 4
    assert config.max_input_value == Decimal("500")
    assert config.default_encoding == "latin-1"


@pytest.mark.parametrize(
    "value, expected",
    [("true", True), ("TRUE", True), ("false", False), ("no", False)],
)
def test_auto_save_parsing(clean_env, monkeypatch, value, expected):
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", value)
    assert CalculatorConfig().auto_save is expected


def test_file_paths_resolve_relative_to_their_directories(clean_env, monkeypatch, tmp_path):
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setenv("CALCULATOR_LOG_FILE", "app.log")
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "hist"))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "h.csv")

    config = CalculatorConfig()

    assert config.log_file == tmp_path / "logs" / "app.log"
    assert config.history_file == tmp_path / "hist" / "h.csv"


def test_validate_passes_with_defaults(clean_env):
    CalculatorConfig().validate()


@pytest.mark.parametrize(
    "env_var, value",
    [
        ("CALCULATOR_MAX_HISTORY_SIZE", "0"),
        ("CALCULATOR_MAX_HISTORY_SIZE", "-5"),
        ("CALCULATOR_PRECISION", "0"),
        ("CALCULATOR_PRECISION", "-1"),
        ("CALCULATOR_MAX_INPUT_VALUE", "0"),
        ("CALCULATOR_MAX_INPUT_VALUE", "-10"),
    ],
)
def test_validate_rejects_non_positive_values(clean_env, monkeypatch, env_var, value):
    monkeypatch.setenv(env_var, value)
    with pytest.raises(ConfigurationError):
        CalculatorConfig().validate()