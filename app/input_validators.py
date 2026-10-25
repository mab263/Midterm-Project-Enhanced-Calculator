"""Validation of user input before it reaches the operations."""

from decimal import Decimal, InvalidOperation

from app.exceptions import ValidationError


class InputValidator:
    """Checks that user input is a usable number."""

    @staticmethod
    def validate_number(value, config) -> Decimal:
        """Convert value to a Decimal and check it is within the allowed range.

        Raises:
            ValidationError: if value is not numeric or exceeds max_input_value.
        """
        try:  # EAFP: attempt the conversion, handle the failure
            number = Decimal(str(value).strip())
        except InvalidOperation:
            raise ValidationError(f"Invalid number: '{value}'")

        if not number.is_finite():  # LBYL: "nan" and "inf" convert fine but aren't usable
            raise ValidationError(f"Invalid number: '{value}'")

        if abs(number) > config.max_input_value:  # LBYL: check the range
            raise ValidationError(
                f"Value {number} exceeds the maximum allowed ({config.max_input_value})"
            )

        return number