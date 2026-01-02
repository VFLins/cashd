from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from cashd_core import const


class StringToCurrency:
    def __init__(self, user_input: str):
        """Handles currency user input, when inserted on a text field."""
        self._user_input = user_input

    @property
    def value(self) -> int:
        """Convert the currency inserted by the user in a text field to an integer.
        This integer preserves two decimal places, so 100 should be interpreted as 1.0.
        """
        try:
            return int(Decimal(self._user_input.replace(",", ".")) * 100)
        except InvalidOperation:
            return 0

    @property
    def display_value(self) -> str:
        """Format the user input to be displayed on the UI."""
        numeric = (
            Decimal(self.value/100)
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        return f"{numeric:,.2f}".replace(",", " ").replace(".", ",")

    @property
    def invalid_reason(self) -> str:
        """Returns a string that explains the reason this input is invalid,
        or None otherwise.
        """
        if self.value == 0:
            return "Valor não pode ser zero"
        if self.value > const.MAX_ALLOWED_VALUE:
            return "Valor acima do permitido"

    def is_valid(self) -> bool:
        """Verify if the integer is a valid input for currency."""
        return self.invalid_reason is None
