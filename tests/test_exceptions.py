import pytest

from app.exceptions import (
    CalculatorError,
    OperationError,
    ValidationError,
    ConfigurationError,
)

@pytest.mark.parametrize(
    "exception_class",
    [OperationError, ValidationError, ConfigurationError],
)
def test_exception_can_be_raised_and_caught(exception_class):
    with pytest.raises(exception_class, match="something went wrong"):
        raise exception_class("something went wrong")

@pytest.mark.parametrize(
    "exception_class",
    [OperationError, ValidationError, ConfigurationError],
)
def test_exception_inherits_from_calculator_error(exception_class):
    assert issubclass(exception_class, CalculatorError)

def test_calculator_error_catches_subclasses():
    with pytest.raises(CalculatorError):
        raise OperationError("division by zero")