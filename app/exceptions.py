class CalculatorError(Exception):
    """Base class for all calculator-specific errors."""

class OperationError(CalculatorError):
    """Raised when a calculation can't be performed (e.g., division by zero)."""

class ValidationError(CalculatorError):
    """Raised when user input is invalid (e.g., not a number, or too large)."""

class ConfigurationError(CalculatorError):
    """Raised when a configuration setting is missing or invalid."""