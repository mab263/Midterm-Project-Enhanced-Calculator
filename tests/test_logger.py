from types import SimpleNamespace

import pytest

from app.logger import Logger
from logging.handlers import RotatingFileHandler


@pytest.fixture
def config(tmp_path):
    return SimpleNamespace(
        log_dir=tmp_path / "logs",
        log_file=tmp_path / "logs" / "test.log",
        default_encoding="utf-8",
    )


def test_creates_log_directory(config):
    Logger(config)
    assert config.log_dir.exists()


@pytest.mark.parametrize(
    "method, level",
    [("info", "INFO"), ("warning", "WARNING"), ("error", "ERROR")],
)
def test_logs_message_at_each_level(config, method, level):
    logger = Logger(config)
    getattr(logger, method)("hello log")
    text = config.log_file.read_text(encoding="utf-8")
    assert "hello log" in text
    assert level in text


def test_creating_logger_twice_does_not_duplicate_lines(config):
    Logger(config)
    logger = Logger(config)
    logger.info("only once")
    text = config.log_file.read_text(encoding="utf-8")
    assert text.count("only once") == 1
    
def test_log_file_rotates_instead_of_growing_forever(config):
    handler = Logger(config)._logger.handlers[0]
    assert isinstance(handler, RotatingFileHandler)
    assert handler.maxBytes == 1_000_000
    assert handler.backupCount == 3