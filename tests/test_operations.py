from decimal import Decimal

import pytest

from app.exceptions import OperationError
from app.operations import OperationFactory, Addition

@pytest.mark.parametrize(
    "name, a, b, expected",
    [
        ("add", "2", "3", "5"),
        ("subtract", "5", "3", "2"),
        ("multiply", "4", "3", "12"),
        ("divide", "10", "4", "2.5"),
        ("power", "2", "3", "8"),
        ("modulus", "7", "2", "1"),
        ("int_divide", "7", "2", "3"),
        ("percent", "1", "4", "25"),
        ("abs_diff", "5", "0", "5"),
        ("abs_diff", "3", "10", "7"),
    ],
)
def test_operations_happy_path(name, a, b, expected):
    operation = OperationFactory.create_operation(name)
    assert operation.execute(Decimal(a), Decimal(b)) == Decimal(expected)
    
@pytest.mark.parametrize(
    "a, b, expected",
    [("27", "3", "3"), ("16", "2", "4")],
)
def test_root(a, b, expected):
    operation = OperationFactory.create_operation("root")
    result = operation.execute(Decimal(a), Decimal(b))
    assert result == pytest.approx(Decimal(expected))
    
@pytest.mark.parametrize(
    "name, a, b",
    [
        ("divide", "1", "0"),
        ("modulus", "1", "0"),
        ("int_divide", "1", "0"),
        ("percent", "1", "0"),
        ("root", "4", "0"),
        ("root", "-4", "2"),
        ("root", "0", "-2"),
        ("power", "0", "-1"),
        ("power", "-8", "0.5"),
    ],
)
def test_operations_raise_operation_error(name, a, b):
    operation = OperationFactory.create_operation(name)
    with pytest.raises(OperationError):
        operation.execute(Decimal(a), Decimal(b))
        
def test_factory_returns_correct_class():
    assert isinstance(OperationFactory.create_operation("add"), Addition)


def test_factory_is_case_insensitive():
    assert isinstance(OperationFactory.create_operation("ADD"), Addition)


def test_factory_unknown_operation_raises():
    with pytest.raises(OperationError, match="bogus"):
        OperationFactory.create_operation("bogus")

      
def test_available_operations_lists_every_command():
    assert set(OperationFactory.available_operations()) == {
        "add", "subtract", "multiply", "divide", "power",
        "root", "modulus", "int_divide", "percent", "abs_diff",
    }