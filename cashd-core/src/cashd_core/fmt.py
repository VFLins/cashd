from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from cashd_core import const


def format_currency(value: str) -> int:
    """Convert the currency inserted by the user in a text field to an integer."""
    try:
        return int(Decimal(value.replace(",", ".")) * 100)
    except InvalidOperation:
        return 0


def display_currency(value: int) -> str:
    """Displays an integer as currency to the user."""
    numeric = Decimal(value/100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{numeric:,.2f}".replace(",", " ").replace(".", ",")


def is_valid_currency(amount: int) -> bool:
    """Verify if the integer is a valid input for currency."""
    if amount == 0:
        return False
    if amount > const.MAX_ALLOWED_VALUE:
        return False
    return True

