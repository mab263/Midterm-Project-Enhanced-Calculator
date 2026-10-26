import pytest

from app.calculator_repl import calculator_repl

ALL_COMMANDS = [
    "add", "subtract", "multiply", "divide", "power",
    "root", "modulus", "int_divide", "percent", "abs_diff",
    "history", "clear", "undo", "redo", "save", "load", "help", "exit",
]


@pytest.fixture
def run(calculator, monkeypatch, capsys):
    """Run the REPL with scripted input and return everything it printed."""

    def run_with(*lines):
        script = iter(lines)

        def fake_input(prompt=""):
            try:
                line = next(script)
            except StopIteration:
                raise EOFError
            if isinstance(line, BaseException):
                raise line
            return line

        monkeypatch.setattr("builtins.input", fake_input)
        calculator_repl(calculator)
        return capsys.readouterr().out

    return run_with


def test_exit_says_goodbye(run):
    output = run("exit")
    assert "Calculator started" in output
    assert "Goodbye!" in output


def test_end_of_input_exits(run):
    assert "Input ended" in run()


def test_keyboard_interrupt_cancels_and_continues(run):
    output = run(KeyboardInterrupt(), "exit")
    assert "Operation cancelled" in output
    assert "Goodbye!" in output


@pytest.mark.parametrize("command", ALL_COMMANDS)
def test_help_lists_every_command(run, command):
    assert command in run("help", "exit")


@pytest.mark.parametrize(
    "name, a, b, expected",
    [
        ("add", "2", "3", "5"),
        ("divide", "10", "4", "2.5"),
        ("power", "2", "3", "8"),
        ("percent", "1", "4", "25"),
        ("abs_diff", "3", "10", "7"),
        ("multiply", "100", "1", "100"),
    ],
)
def test_operation_prints_result(run, name, a, b, expected):
    assert f"Result: {expected}" in run(name, a, b, "exit")


def test_commands_are_case_insensitive(run):
    assert "Result: 5" in run("ADD", "2", "3", "exit")


@pytest.mark.parametrize(
    "inputs",
    [("add", "cancel"), ("add", "2", "cancel")],
)
def test_cancel_at_either_prompt(run, inputs):
    output = run(*inputs, "history", "exit")
    assert "Operation cancelled" in output
    assert "No calculations in history" in output


@pytest.mark.parametrize(
    "name, a, b, message",
    [
        ("add", "abc", "1", "Invalid number"),
        ("add", "1", "9999999", "exceeds the maximum"),
        ("divide", "1", "0", "Division by zero"),
    ],
)
def test_errors_are_reported_and_the_loop_continues(run, name, a, b, message):
    output = run(name, a, b, "history", "exit")
    assert f"Error: " in output
    assert message in output
    assert "No calculations in history" in output


def test_unexpected_errors_do_not_crash_the_repl(run, calculator, monkeypatch):
    def boom(*args):
        raise RuntimeError("boom")

    monkeypatch.setattr(calculator, "perform_operation", boom)
    output = run("add", "2", "3", "exit")
    assert "Unexpected error: boom" in output
    assert "Goodbye!" in output


def test_unknown_command(run):
    assert "Unknown command: 'bogus'" in run("bogus", "exit")


def test_empty_command_is_ignored(run):
    assert "Unknown" not in run("", "exit")


def test_history_shows_numbered_entries(run):
    assert "1. Addition(2, 3) = 5" in run("add", "2", "3", "history", "exit")


def test_clear_empties_history(run):
    output = run("add", "2", "3", "clear", "history", "exit")
    assert "History cleared" in output
    assert "No calculations in history" in output


@pytest.mark.parametrize(
    "command, message",
    [("undo", "Nothing to undo"), ("redo", "Nothing to redo")],
)
def test_nothing_to_undo_or_redo(run, command, message):
    assert message in run(command, "exit")


def test_undo_and_redo(run):
    output = run("add", "2", "3", "undo", "redo", "exit")
    assert "Operation undone" in output
    assert "Operation redone" in output


def test_save_and_load_round_trip(run):
    output = run("add", "2", "3", "save", "clear", "load", "history", "exit")
    assert "History saved successfully" in output
    assert "History loaded successfully" in output
    assert "1. Addition(2, 3) = 5" in output


def test_save_failure_is_reported(run, config, tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("this is a file, not a folder")
    config.history_dir = blocker
    assert "Error: Failed to save history" in run("save", "exit")


def test_load_failure_is_reported(run, config):
    config.history_dir.mkdir(parents=True, exist_ok=True)
    config.history_file.write_bytes(b"")
    assert "Error: Failed to load history" in run("load", "exit")


def test_default_calculator_is_created_when_none_is_given(calculator, monkeypatch, capsys):
    monkeypatch.setattr("app.calculator_repl.Calculator", lambda: calculator)
    monkeypatch.setattr("builtins.input", lambda prompt="": "exit")
    calculator_repl()
    assert "Goodbye!" in capsys.readouterr().out