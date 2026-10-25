from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.calculation import Calculation
from app.exceptions import OperationError
from app.history import (
    AutoSaveObserver,
    LoggingObserver,
    Observer,
    load_history,
    save_history,
)

HEADER = "operation,operand1,operand2,result,timestamp"


@pytest.fixture
def config(tmp_path):
    return SimpleNamespace(
        history_dir=tmp_path / "history",
        history_file=tmp_path / "history" / "history.csv",
        default_encoding="utf-8",
        auto_save=True,
    )


@pytest.fixture
def blocked_config(tmp_path, config):
    """A config whose history 'directory' is really a file, so saving must fail."""
    blocker = tmp_path / "blocker"
    blocker.write_text("this is a file, not a folder")
    config.history_dir = blocker
    config.history_file = blocker / "history.csv"
    return config


def make_history():
    return [
        Calculation("add", Decimal("2"), Decimal("3"), Decimal("5"), datetime(2026, 1, 15, 10, 30, 0)),
        Calculation("divide", Decimal("1"), Decimal("4"), Decimal("0.25"), datetime(2026, 1, 15, 10, 31, 0)),
    ]


def test_save_creates_directory_and_file(config):
    save_history(make_history(), config)
    assert config.history_file.exists()


def test_round_trip_preserves_history(config):
    history = make_history()
    save_history(history, config)
    assert load_history(config) == history


def test_saving_empty_history_writes_header_only(config):
    save_history([], config)
    assert config.history_file.read_text().strip() == HEADER
    assert load_history(config) == []


def test_load_missing_file_returns_empty_list(config):
    assert load_history(config) == []


@pytest.mark.parametrize(
    "content",
    [
        b"",
        b"a,b\n1,2\n",
        (HEADER + "\nadd,abc,3,5,2026-01-15T10:30:00\n").encode(),
        b"\xff\xfe\x00\xff",
    ],
)
def test_load_rejects_malformed_files(config, content):
    config.history_dir.mkdir()
    config.history_file.write_bytes(content)
    with pytest.raises(OperationError):
        load_history(config)


def test_save_failure_raises_operation_error(blocked_config):
    with pytest.raises(OperationError):
        save_history(make_history(), blocked_config)
        
class FakeLogger:
    """Records messages so tests can check what was logged."""

    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(("INFO", message))

    def warning(self, message):
        self.messages.append(("WARNING", message))


def test_observer_is_abstract():
    with pytest.raises(TypeError):
        Observer()


def test_logging_observer_logs_calculation_details():
    logger = FakeLogger()
    LoggingObserver(logger).update(make_history()[0])
    level, message = logger.messages[0]
    assert level == "INFO"
    for expected in ("add", "2", "3", "5"):
        assert expected in message


def test_autosave_saves_when_enabled(config):
    history = make_history()
    observer = AutoSaveObserver(config, lambda: history, FakeLogger())
    observer.update(history[-1])
    assert load_history(config) == history


def test_autosave_skips_when_disabled(config):
    config.auto_save = False
    observer = AutoSaveObserver(config, make_history, FakeLogger())
    observer.update(make_history()[0])
    assert not config.history_file.exists()


def test_autosave_logs_warning_when_save_fails(blocked_config):
    logger = FakeLogger()
    observer = AutoSaveObserver(blocked_config, make_history, logger)
    observer.update(make_history()[0])  # must not raise
    assert logger.messages[0][0] == "WARNING"