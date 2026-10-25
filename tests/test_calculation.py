from datetime import datetime
from decimal import Decimal

import pytest

from app.calculation import Calculation
from app.exceptions import OperationError

TIMESTAMP = datetime(2026, 1, 15, 10, 30, 0)

GOOD = {
    "operation": "add",
    "operand1": "2",
    "operand2": "3",
    "result": "5",
    "timestamp": "2026-01-15T10:30:00",
}


def make_calculation():
    return Calculation("add", Decimal("2"), Decimal("3"), Decimal("5"), TIMESTAMP)


def test_str_representation():
    assert str(make_calculation()) == "add(2, 3) = 5"


def test_to_dict():
    assert make_calculation().to_dict() == GOOD


def test_round_trip_through_dict():
    original = make_calculation()
    assert Calculation.from_dict(original.to_dict()) == original


def test_timestamp_defaults_to_now():
    before = datetime.now()
    calculation = Calculation("add", Decimal("1"), Decimal("1"), Decimal("2"))
    assert before <= calculation.timestamp <= datetime.now()


@pytest.mark.parametrize(
    "bad_data",
    [
        {},
        {**GOOD, "operand1": "abc"},
        {**GOOD, "result": "abc"},
        {**GOOD, "timestamp": "not a date"},
        {**GOOD, "operand2": None},
        {key: value for key, value in GOOD.items() if key != "operation"},
    ],
)
def test_from_dict_rejects_bad_data(bad_data):
    with pytest.raises(OperationError):
        Calculation.from_dict(bad_data)