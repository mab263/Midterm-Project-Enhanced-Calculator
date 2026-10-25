"""A record of one completed calculation, as stored in the history."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.exceptions import OperationError


@dataclass
class Calculation:
    """One calculation: what was done, to what, the result, and when."""

    operation: str
    operand1: Decimal
    operand2: Decimal
    result: Decimal
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"{self.operation}({self.operand1}, {self.operand2}) = {self.result}"

    def to_dict(self) -> dict:
        """Convert to plain strings so the calculation can be saved to a CSV."""
        return {
            "operation": self.operation,
            "operand1": str(self.operand1),
            "operand2": str(self.operand2),
            "result": str(self.result),
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Calculation":
        """Rebuild a Calculation from a dict (e.g., one row of the history CSV).

        Raises:
            OperationError: if the data is missing fields or has invalid values.
        """
        try:  # EAFP: attempt the conversion, handle the failure
            return cls(
                operation=data["operation"],
                operand1=Decimal(data["operand1"]),
                operand2=Decimal(data["operand2"]),
                result=Decimal(data["result"]),
                timestamp=datetime.fromisoformat(data["timestamp"]),
            )
        except (KeyError, TypeError, ValueError, InvalidOperation) as error:
            raise OperationError(f"Invalid calculation data: {error}")