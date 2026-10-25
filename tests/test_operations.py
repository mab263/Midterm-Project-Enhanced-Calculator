from decimal import Decimal

import pytest

from app.operations import OperationFactory


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