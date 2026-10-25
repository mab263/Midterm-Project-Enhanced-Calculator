"""Arithmetic operations and the factory that creates them."""

from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation

from app.exceptions import OperationError


class Operation(ABC):
    """Base class for every operation (Strategy pattern)."""

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Apply the operation to a and b."""


class Addition(Operation):
    """Return a + b."""

    def execute(self, a, b):
        return a + b


class Division(Operation):
    """Return a / b."""

    def execute(self, a, b):
        if b == 0:  # LBYL: check first
            raise OperationError("Division by zero is not allowed")
        return a / b


class Multiplication(Operation):
    """Return a * b."""

    def execute(self, a, b):
        return a * b


class Subtraction(Operation):
    """Return a - b."""

    def execute(self, a, b):
        return a - b


class Power(Operation):
    """Return a raised to the power b."""

    def execute(self, a, b):
        try:  # EAFP: try it and handle the failure
            return a ** b
        except (ArithmeticError):
            raise OperationError("Invalid power operation")


class Root(Operation):
    """Return a ** (Decimal(1) / b)."""

    def execute(self, a, b):
        if b == 0 or a < 0 or (a == 0 and b < 0):  # LBYL: check first
            raise OperationError("Invalid root operation")
        return a ** (Decimal(1) / b)


class Modulus(Operation):
    """Return a % b."""

    def execute(self, a, b):
        if b == 0 :  # LBYL: check first
            raise OperationError("Invalid modulus operation")
        return a % b


class IntegerDivision(Operation):
    """Return a // b."""

    def execute(self, a, b):
        if b == 0:  # LBYL: check first
            raise OperationError("Invalid integer division operation")
        return a // b


class Percentage(Operation):
    """Return (a / b) * 100."""

    def execute(self, a, b):
        if b == 0:  # LBYL: check first
            raise OperationError("Invalid percentage operation")
        return (a / b) * 100


class AbsoluteDifference(Operation):
    """Return abs(a - b)."""

    def execute(self, a, b):
        return abs(a - b)


class OperationFactory:
    """Creates operation objects from command names (Factory pattern)."""

    _operations = {
        "add": Addition,
        "divide": Division,
        "multiply": Multiplication,
        "subtract": Subtraction,
        "power": Power,
        "root": Root,
        "modulus": Modulus,
        "int_divide": IntegerDivision,
        "percent": Percentage,
        "abs_diff": AbsoluteDifference
    }

    @classmethod
    def create_operation(cls, name: str) -> Operation:
        operation_class = cls._operations.get(name.lower())
        if operation_class is None:
            raise OperationError(f"Unknown operation: '{name}'")
        return operation_class()