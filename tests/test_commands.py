import pytest

from app import commands
from app.commands import (
    CalculationCommand,
    Command,
    ExitCommand,
    HelpCommand,
    HistoryCommand,
    UnknownCommand,
    UsageCommand,
    parse_command,
)
from app.operations import OperationFactory


def test_command_is_abstract():
    with pytest.raises(TypeError):
        Command()


@pytest.mark.parametrize(
    "line, expected",
    [
        ("history", HistoryCommand),
        ("EXIT", ExitCommand),
        ("add", CalculationCommand),
        ("add 2 3", CalculationCommand),
        ("add 2", UsageCommand),
        ("add 1 2 3", UsageCommand),
        ("bogus", UnknownCommand),
    ],
)
def test_parse_command(line, expected):
    assert type(parse_command(line)) is expected


def test_blank_line_parses_to_nothing():
    assert parse_command("   ") is None


def test_calculation_command_holds_its_parameters():
    command = parse_command("add 2 3")
    assert (command.operation_name, command.first, command.second) == ("add", "2", "3")


@pytest.mark.parametrize("name, command_class", list(commands.COMMAND_CLASSES.items()))
def test_only_exit_ends_the_session(name, command_class):
    assert command_class.ends_session is (name == "exit")


@pytest.mark.parametrize(
    "command, expected",
    [
        (CalculationCommand("add", "2", "3"), "Result: 5"),
        (UsageCommand("add"), "Usage: add <number1> <number2>"),
        (UnknownCommand("bogus"), "Unknown command: 'bogus'"),
        (ExitCommand(), "Goodbye!"),
    ],
)
def test_command_output(calculator, capsys, command, expected):
    command.execute(calculator)
    assert expected in capsys.readouterr().out


def test_help_lists_operations_and_commands(calculator, capsys):
    HelpCommand().execute(calculator)
    printed = capsys.readouterr().out
    for description in OperationFactory.describe().values():
        assert description in printed
    for description in commands.COMMAND_HELP.values():
        assert description in printed


def test_calculation_command_prompts_when_numbers_are_missing(calculator, monkeypatch, capsys):
    answers = iter(["2", "3"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))
    CalculationCommand("add").execute(calculator)
    assert "Result: 5" in capsys.readouterr().out


@pytest.mark.parametrize("answers", [["cancel"], ["2", "cancel"]])
def test_cancel_at_either_prompt(calculator, monkeypatch, capsys, answers):
    iterator = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(iterator))
    CalculationCommand("add").execute(calculator)
    assert "Operation cancelled" in capsys.readouterr().out
    assert calculator.history == []


def test_commands_can_be_queued_and_run_in_order(calculator, capsys):
    queue = [
        CalculationCommand("add", "2", "3"),
        CalculationCommand("multiply", "4", "5"),
        parse_command("history"),
    ]
    for command in queue:
        command.execute(calculator)
    printed = capsys.readouterr().out
    assert "1. Addition(2, 3) = 5" in printed
    assert "2. Multiplication(4, 5) = 20" in printed


def test_a_command_can_be_run_more_than_once(calculator):
    command = CalculationCommand("add", "1", "1")
    command.execute(calculator)
    command.execute(calculator)
    assert len(calculator.history) == 2