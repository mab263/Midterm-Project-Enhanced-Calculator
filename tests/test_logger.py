from types import SimpleNamespace

import pytest

from app.logger import Logger


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