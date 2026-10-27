"""Command pattern: every REPL request is an object with an execute method."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Type

from app import output
from app.calculator import Calculator
from app.operations import OperationFactory

CANCEL = "cancel"


class Command(ABC):
    """A request the REPL can run against a calculator."""

    ends_session = False  # True for commands that should stop the REPL

    @abstractmethod
    def execute(self, calc: Calculator) -> None:
        """Carry out the request."""


# Registries filled by the decorator below; the help menu is built from them.
COMMAND_CLASSES: Dict[str, Type[Command]] = {}
COMMAND_HELP: Dict[str, str] = {}


def register_command(name: str, description: str):
    """Class decorator: register a command under a name, with its help text."""

    def decorator(command_class):
        COMMAND_CLASSES[name] = command_class
        COMMAND_HELP[name] = description
        return command_class

    return decorator


@register_command("help", "Show this help menu")
class HelpCommand(Command):
    def execute(self, calc: Calculator) -> None:
        output.info(
            "\nOperations (type the name and you'll be asked for two numbers,\n"
            "or give everything on one line, e.g. 'add 2 3'):"
        )
        for name, description in OperationFactory.describe().items():
            print(f"  {name:<12}{description}")
        output.info("\nCommands:")
        for name, description in COMMAND_HELP.items():
            print(f"  {name:<12}{description}")


@register_command("history", "Show calculation history")
class HistoryCommand(Command):
    def execute(self, calc: Calculator) -> None:
        lines = calc.show_history()
        if not lines:
            output.warning("No calculations in history")
            return
        output.info("\nCalculation History:")
        for index, line in enumerate(lines, 1):
            print(f"{index}. {line}")


@register_command("clear", "Clear calculation history")
class ClearCommand(Command):
    def execute(self, calc: Calculator) -> None:
        calc.clear_history()
        output.success("History cleared")


@register_command("undo", "Undo the last calculation")
class UndoCommand(Command):
    def execute(self, calc: Calculator) -> None:
        if calc.undo():
            output.success("Operation undone")
        else:
            output.warning("Nothing to undo")


@register_command("redo", "Redo the last undone calculation")
class RedoCommand(Command):
    def execute(self, calc: Calculator) -> None:
        if calc.redo():
            output.success("Operation redone")
        else:
            output.warning("Nothing to redo")


@register_command("save", "Save history to the CSV file")
class SaveCommand(Command):
    def execute(self, calc: Calculator) -> None:
        calc.save()
        output.success("History saved successfully")


@register_command("load", "Load history from the CSV file")
class LoadCommand(Command):
    def execute(self, calc: Calculator) -> None:
        calc.load()
        output.success("History loaded successfully")


@register_command("exit", "Exit the calculator")
class ExitCommand(Command):
    ends_session = True

    def execute(self, calc: Calculator) -> None:
        output.info("Goodbye!")


def ask(prompt: str) -> Optional[str]:
    """Ask for input. Returns None if the user types 'cancel'."""
    value = input(prompt).strip()
    return None if value.lower() == CANCEL else value


class CalculationCommand(Command):
    """Run one operation. The operation and numbers are the command's parameters.

    If the numbers weren't given, the user is prompted for them.
    """

    def __init__(self, operation_name: str, first: Optional[str] = None,
                 second: Optional[str] = None):
        self.operation_name = operation_name
        self.first = first
        self.second = second

    def execute(self, calc: Calculator) -> None:
        first, second = self.first, self.second  # locals, so the command can be reused
        if first is None:
            output.info(f"Enter two numbers (or '{CANCEL}' to abort):")
            first = ask("First number: ")
            if first is None:
                output.warning("Operation cancelled")
                return
            second = ask("Second number: ")
            if second is None:
                output.warning("Operation cancelled")
                return

        calc.set_operation(OperationFactory.create_operation(self.operation_name))
        result = calc.perform_operation(first, second)
        output.success(f"Result: {format(result.normalize(), 'f')}")


class UsageCommand(Command):
    """Shown when an operation is given the wrong number of arguments."""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name

    def execute(self, calc: Calculator) -> None:
        output.warning(f"Usage: {self.operation_name} <number1> <number2>")


class UnknownCommand(Command):
    """Shown when the input isn't a known command or operation."""

    def __init__(self, text: str):
        self.text = text

    def execute(self, calc: Calculator) -> None:
        output.warning(
            f"Unknown command: '{self.text}'. Type 'help' for available commands."
        )


def parse_command(line: str) -> Optional[Command]:
    """Turn a line of user input into a Command, or None for a blank line."""
    line = line.strip().lower()
    parts = line.split()
    if not parts:
        return None
    if line in COMMAND_CLASSES:  # LBYL: look the name up before building anything
        return COMMAND_CLASSES[line]()
    if parts[0] in OperationFactory.available_operations():
        if len(parts) == 1:
            return CalculationCommand(parts[0])
        if len(parts) == 3:
            return CalculationCommand(parts[0], parts[1], parts[2])
        return UsageCommand(parts[0])
    return UnknownCommand(line)