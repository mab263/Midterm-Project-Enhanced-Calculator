from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.exceptions import ValidationError
from app.input_validators import InputValidator

CONFIG = SimpleNamespace(max_input_value=Decimal("1000"))


@pytest.mark.parametrize(
    "value, expected",
    [
        ("5", "5"),
        ("-2.5", "-2.5"),
        ("  7  ", "7"),
        ("10", "10"),
        (10, "10"),
        (2.5, "2.5"),
        (Decimal("4"), "4"),
        ("1000", "1000"),
        ("-1000", "-1000"), 
    ],
)
def test_valid_numbers(value, expected):
    assert InputValidator.validate_number(value, CONFIG) == Decimal(expected)


@pytest.mark.parametrize(
    "value",
    [
        "abc",
        "",
        "   ",
        "1.2.3",
        None,
        "nan",
        "inf",
        "1001",
        "-1001",
    ],
)
def test_invalid_numbers_raise_validation_error(value):
    with pytest.raises(ValidationError):
        InputValidator.validate_number(value, CONFIG)