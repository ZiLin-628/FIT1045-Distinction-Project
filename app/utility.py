# app/utility.py

from __future__ import annotations

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

from app.exception import InvalidInputError

if TYPE_CHECKING:
    from app.models import TransactionType

DATETIME_FORMAT = "%d-%m-%Y %H:%M:%S"


def format_datetime(dt: datetime) -> str:
    """
    Convert a datetime object to a formatted string.

    Args:
        dt (datetime): The datetime object to format

    Returns:
        str: Formatted datetime string in DD-MM-YYYY HH:MM:SS format
    """
    return dt.strftime(DATETIME_FORMAT)


def parse_datetime(dt_str: str) -> datetime:
    """
    Parse a datetime string into a datetime object.

    Args:
        dt_str (str): Datetime string in DD-MM-YYYY HH:MM:SS format

    Returns:
        datetime: Parsed datetime object

    Raises:
        ValueError: If the string doesn't match the expected format
    """
    return datetime.strptime(dt_str, DATETIME_FORMAT)


def format_amount(amount: str) -> Decimal:
    """
    Round a amount to two decimal places.

    Args:
        amount (str): The amount to round (can be string or numeric)

    Returns:
        Decimal: Amount rounded to 2 decimal places
    """

    # Convert to Decimal and quantize to 0.01 (2 decimal places)
    return Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_current_time() -> datetime:
    """
    Get the current system time with microseconds removed.

    Returns:
        datetime: Current datetime with microseconds set to 0
    """

    return datetime.now().replace(microsecond=0)


def read_integer(prompt: str) -> int:
    """
    Prompt user for integer input with validation.

    Args:
        prompt (str): The prompt message to display to the user

    Returns:
        int: Valid integer entered by user
    """

    while True:
        try:
            # Attempt to convert user input to integer
            return int(input(prompt))
        except ValueError:
            # Invalid input - show error and retry
            print("You must input a valid integer!")


def read_positive_integer(prompt: str) -> int:
    """
    Prompt user for a positive integer (> 0) with validation.

    Args:
        prompt (str): The prompt message to display to the user

    Returns:
        int: Valid positive integer entered by user

    """

    # Get initial integer input
    num: int = read_integer(prompt)

    # Keep prompting until we get a positive value
    while num <= 0:
        print("Please enter a positive integer value")
        num = read_integer(prompt)

    return num


def read_integer_range(prompt: str, low: int, high: int) -> int:
    """
    Prompt user for an integer within a specified range (inclusive).

    Args:
        prompt (str): The prompt message to display to the user
        low (int): Minimum acceptable value (inclusive)
        high (int): Maximum acceptable value (inclusive)

    Returns:
        int: Valid integer within the specified range
    """

    # Get initial integer input
    num: int = read_integer(prompt)

    # Keep prompting until value is within range
    while num < low or num > high:
        print(f"Please enter a value between {low} and {high}")
        num = read_integer(prompt)

    return num


def read_float(prompt: str) -> float:
    """
    Prompt user for float input with validation and retry logic.

    Args:
        prompt (str): The prompt message to display to the user

    Returns:
        float: Valid float entered by user
    """

    while True:
        try:
            # Attempt to convert user input to float
            return float(input(prompt))
        except ValueError:
            # Invalid input - show error and retry
            print("You must input a valid float!")


def read_positive_float(prompt: str) -> float:
    """
    Prompt user for a positive float (> 0) with validation.

    Args:
        prompt (str): The prompt message to display to the user

    Returns:
        float: Valid positive float entered by user

    """

    # Get initial float input
    num: float = read_float(prompt)

    # Keep prompting until we get a positive value
    while num <= 0:
        print("Please enter a positive float value")
        num = read_float(prompt)

    return num


def read_date(prompt: str = "Enter date") -> datetime:
    """
    Prompt user to enter a date by collecting day, month, and year separately.

    Args:
        prompt (str): The prompt message to display. Defaults to "Enter date"

    Returns:
        datetime: Valid datetime object (time set to midnight)

    Raises:
        InvalidInputError: If the date components create an invalid date
    """

    # Display the main prompt
    print(prompt)

    # Collect date components from user
    day = read_integer("  Day (1-31): ")
    month = read_integer("  Month (1-12): ")
    year = read_integer("  Year (e.g., 2024): ")

    try:
        # Attempt to create a datetime object (validates date)
        return datetime(year, month, day)
    except ValueError:
        # Invalid date combination (e.g., Feb 30, month 13, etc.)
        raise InvalidInputError("Date entered is invalid")


def validate_non_empty_string(value: str, field_name: str = "Value") -> str:
    """
    Validate that a string is not empty after stripping whitespace and capitalize it.

    Args:
        value (str): The string value to validate
        field_name (str): Name of the field for error messages (default: "Value")

    Returns:
        str: The stripped and capitalized value

    Raises:
        InvalidInputError: If the string is empty after stripping
    """
    stripped_value = value.strip().capitalize()
    if not stripped_value:
        raise InvalidInputError(f"{field_name} cannot be empty.")
    return stripped_value


def validate_transaction_type(transaction_type_input: str) -> "TransactionType":
    """
    Validate and convert a transaction type string to TransactionType enum.

    Args:
        transaction_type_input (str): The transaction type string (e.g., "income", "EXPENSE")

    Returns:
        TransactionType: The validated TransactionType enum value

    Raises:
        InvalidInputError: If the string is not a valid transaction type
    """
    from app.models import TransactionType

    try:
        return TransactionType(transaction_type_input.strip().lower())
    except ValueError:
        raise InvalidInputError(
            f"'{transaction_type_input}' is not a valid transaction type."
        )


def validate_non_negative_amount(amount: str, field_name: str = "Amount") -> Decimal:
    """
    Validate that an amount is non-negative (>= 0).

    Args:
        amount (str): The amount to validate as a string
        field_name (str): Name of the field for error messages (default: "Amount")

    Returns:
        Decimal: The validated amount as a Decimal

    Raises:
        InvalidInputError: If the amount is negative
    """
    decimal_amount = format_amount(amount)
    if decimal_amount < Decimal("0.00"):
        raise InvalidInputError(f"{field_name} cannot be negative.")
    return decimal_amount
