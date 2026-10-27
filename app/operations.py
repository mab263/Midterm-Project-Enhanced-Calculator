"""Arithmetic operations and the factory that creates them."""

from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation

from app.exceptions import OperationError


class Operation(ABC):
    """Base class for every operation (Strategy pattern)."""

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Apply the operation to a and b."""

class OperationFactory:
    """Creates operation objects from command names (Factory pattern)."""

    _operations = {}
    _descriptions = {}

    @classmethod
    def register(cls, name: str, description: str = ""):
        """Register an operation class and its description."""

        def decorator(operation_class):
            key = name.lower()
            cls._operations[key] = operation_class
            cls._descriptions[key] = description
            operation_class.description = description
            return operation_class

        return decorator

    @classmethod
    def create_operation(cls, name: str) -> Operation:
        """Create an operation instance from its command name."""
        operation_class = cls._operations.get(name.lower())

        if operation_class is None:
            raise OperationError(f"Unknown operation: '{name}'")

        return operation_class()

    @classmethod
    def describe(cls, name: str = None):
        """Return all descriptions, or the description for one operation."""
        if name is None:
            return dict(cls._descriptions)

        description = cls._descriptions.get(name.lower())

        if description is None:
            raise OperationError(f"Unknown operation: '{name}'")

        return description

    @classmethod
    def available_operations(cls) -> list:
        """Return the command names that can be created."""
        return list(cls._operations)
  
    
@OperationFactory.register("add", "Add two numbers")
class Addition(Operation):
    """Return a + b."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a + b


@OperationFactory.register("divide", "Divide the first number by the second")
class Division(Operation):
    """Return a / b."""

    def execute(self, a, b):
        if b == 0:  # LBYL: check first
            raise OperationError("Division by zero is not allowed")
        return a / b


@OperationFactory.register("multiply", "Multiply two numbers")
class Multiplication(Operation):
    """Return a * b."""

    def execute(self, a, b):
        return a * b


@OperationFactory.register("subtract", "Subtract the second number from the first")
class Subtraction(Operation):
    """Return a - b."""

    def execute(self, a, b):
        return a - b


@OperationFactory.register("power", "Raise the first number to the power of the second")
class Power(Operation):
    """Return a raised to the power b."""

    def execute(self, a, b):
        if a == 0 and b < 0:  # LBYL: check first
            raise OperationError("Zero cannot be raised to a negative power")
        try:  # EAFP: try it and handle the failure
            return a ** b
        except ArithmeticError:
            raise OperationError("Invalid power operation")


@OperationFactory.register("root", "Take the nth root of the first number (n is the second)")
class Root(Operation):
    """Return a ** (Decimal(1) / b)."""

    def execute(self, a, b):
        if b == 0 or a < 0 or (a == 0 and b < 0):  # LBYL: check first
            raise OperationError("Invalid root operation")
        return a ** (Decimal(1) / b)


@OperationFactory.register("modulus", "Remainder of dividing the first number by the second")
class Modulus(Operation):
    """Return a % b."""

    def execute(self, a, b):
        if b == 0 :  # LBYL: check first
            raise OperationError("Invalid modulus operation")
        return a % b


@OperationFactory.register("int_divide", "Divide and discard the fractional part")
class IntegerDivision(Operation):
    """Return a // b."""

    def execute(self, a, b):
        if b == 0:  # LBYL: check first
            raise OperationError("Invalid integer division operation")
        return a // b


@OperationFactory.register("percent", "First number as a percentage of the second")
class Percentage(Operation):
    """Return (a / b) * 100."""

    def execute(self, a, b):
        if b == 0:  # LBYL: check first
            raise OperationError("Invalid percentage operation")
        return (a / b) * 100


@OperationFactory.register("abs_diff", "Absolute difference between the two numbers")
class AbsoluteDifference(Operation):
    """Return abs(a - b)."""

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return abs(a - b)