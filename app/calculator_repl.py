"""Command-line REPL (Read-Eval-Print Loop) for the calculator."""

from typing import Callable, Dict, Optional

from app.calculator import Calculator
from app.exceptions import CalculatorError
from app.operations import OperationFactory

CANCEL = "cancel"

COMMANDS: Dict[str, Callable] = {}
COMMAND_HELP: Dict[str, str] = {}


def command(name: str, description: str):
    """Decorator: register a REPL command, with its help text, under a name.

    The help menu is built from these registries, so a new command shows up
    in it automatically.
    """

    def decorator(handler):
        COMMANDS[name] = handler
        COMMAND_HELP[name] = description
        return handler

    return decorator


@command("help", "Show this help menu")
def show_help(_calc: Calculator) -> None:
    """Print the operations and commands, built from the registries."""
    print("\nOperations (type the name and you'll be asked for two numbers,")
    print("or give everything on one line, e.g. 'add 2 3'):")
    for name, description in OperationFactory.describe().items():
        print(f"  {name:<12}{description}")
    print("\nCommands:")
    for name, description in COMMAND_HELP.items():
        print(f"  {name:<12}{description}")


@command("history", "Show calculation history")
def show_history(calc: Calculator) -> None:
    lines = calc.show_history()
    if not lines:
        print("No calculations in history")
        return
    print("\nCalculation History:")
    for index, line in enumerate(lines, 1):
        print(f"{index}. {line}")


@command("clear", "Clear calculation history")
def clear_history(calc: Calculator) -> None:
    calc.clear_history()
    print("History cleared")


@command("undo", "Undo the last calculation")
def undo(calc: Calculator) -> None:
    print("Operation undone" if calc.undo() else "Nothing to undo")


@command("redo", "Redo the last undone calculation")
def redo(calc: Calculator) -> None:
    print("Operation redone" if calc.redo() else "Nothing to redo")


@command("save", "Save history to the CSV file")
def save(calc: Calculator) -> None:
    calc.save()
    print("History saved successfully")


@command("load", "Load history from the CSV file")
def load(calc: Calculator) -> None:
    calc.load()
    print("History loaded successfully")


@command("exit", "Exit the calculator")
def exit_calculator(_calc: Calculator) -> bool:
    print("Goodbye!")
    return True  # tells the loop to stop


def ask(prompt: str) -> Optional[str]:
    """Ask for input. Returns None if the user types 'cancel'."""
    value = input(prompt).strip()
    return None if value.lower() == CANCEL else value


def run_calculation(calc: Calculator, name: str, first=None, second=None) -> None:
    """Perform the named operation, prompting for the numbers if they weren't given."""
    if first is None:
        print(f"Enter two numbers (or '{CANCEL}' to abort):")
        first = ask("First number: ")
        if first is None:
            print("Operation cancelled")
            return
        second = ask("Second number: ")
        if second is None:
            print("Operation cancelled")
            return

    calc.set_operation(OperationFactory.create_operation(name))
    result = calc.perform_operation(first, second)
    print(f"Result: {format(result.normalize(), 'f')}")


def calculator_repl(calc: Optional[Calculator] = None) -> None:
    """Read commands and run them until the user types 'exit'."""
    calc = calc or Calculator()
    print("Calculator started. Type 'help' for commands.")

    while True:
        try:
            line = input("\nEnter command: ").strip().lower()
            parts = line.split()

            if line in COMMANDS:  # LBYL: look the command up before running it
                if COMMANDS[line](calc):  # handlers return True to stop the REPL
                    return
            elif parts and parts[0] in OperationFactory.available_operations():
                if len(parts) == 1:
                    run_calculation(calc, parts[0])
                elif len(parts) == 3:
                    run_calculation(calc, parts[0], parts[1], parts[2])
                else:
                    print(f"Usage: {parts[0]} <number1> <number2>")
            elif line:
                print(f"Unknown command: '{line}'. Type 'help' for available commands.")
        except CalculatorError as error:  # EAFP: try it, handle the failure
            print(f"Error: {error}")
        except KeyboardInterrupt:  # Ctrl+C cancels the current command
            print("\nOperation cancelled")
        except EOFError:  # Ctrl+D or no more input
            print("\nInput ended. Goodbye!")
            return
        except Exception as error:  # last resort, so a bug never kills the session
            print(f"Unexpected error: {error}")