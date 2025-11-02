# models.py

from datetime import datetime
from decimal import Decimal
from enum import Enum

from app.utility import format_amount, format_datetime


class TransactionType(Enum):
    """
    Enum representing types of transactions.

    Attributes:
        EXPENSE: Represents an expense transaction.
        INCOME: Represents an income transaction.
    """

    EXPENSE = "expense"
    INCOME = "income"


class Account:
    """
    Represents a financial account with a balance and list of transactions.

    Attributes:
        account_name (str): Name of the account.
        _balance (Decimal): Current balance of the account (private).
        transactions (list[Transaction]): List of transactions linked to the account.
    """

    def __init__(self, account_name: str, balance: str) -> None:
        """
        Initialize an Account instance.

        Args:
            account_name (str): Name of the account.
            balance (str): Initial balance (as string, will be formatted to Decimal).
        """

        self.account_name = account_name
        self._balance = format_amount(balance)
        self.transactions: list["Transaction"] = []

    @property
    def balance(self) -> Decimal:
        """Return the current balance of the account."""
        return self._balance

    def add_transaction(self, transaction: "Transaction") -> None:
        """Add a transaction to the account's transaction list."""
        self.transactions.append(transaction)

    def remove_transaction(self, transaction: "Transaction") -> None:
        """Remove a transaction from the account's transaction list."""
        self.transactions.remove(transaction)

    def update_balance(
        self, amount: Decimal, transaction_type: TransactionType
    ) -> None:
        """
        Update the account balance based on transaction type.

        Args:
            amount (Decimal): Amount to add or subtract.
            transaction_type (TransactionType): Type of transaction (INCOME or EXPENSE).
        """

        if transaction_type == TransactionType.INCOME:
            self._balance += amount
        elif transaction_type == TransactionType.EXPENSE:
            self._balance -= amount

    def reverse_balance(
        self, amount: Decimal, transaction_type: TransactionType
    ) -> None:
        """
        Reverse the effect of a transaction on the balance.
        Useful when deleting or rolling back a transaction.

        Args:
            amount (Decimal): Amount to reverse.
            transaction_type (TransactionType): Type of transaction (INCOME or EXPENSE).
        """

        if transaction_type == TransactionType.INCOME:
            self._balance -= amount
        elif transaction_type == TransactionType.EXPENSE:
            self._balance += amount

    def to_dict(self) -> dict:
        """Return a dictionary representation of the account."""
        return {"account_name": self.account_name, "balance": str(self._balance)}


class Transaction:
    """
    Represents a financial transaction linked to an account.

    Attributes:
        transaction_id (int): ID of the transaction.
        datetime (datetime): Date and time of the transaction.
        transaction_type (TransactionType): Type of transaction (INCOME or EXPENSE).
        category (str): Category of the transaction
        account (Account): Account associated with the transaction.
        amount (Decimal): Transaction amount.
        description (str): Optional description of the transaction.
    """

    def __init__(
        self,
        transaction_id: int,
        datetime: datetime,
        transaction_type: TransactionType,
        category: str,
        account: Account,
        amount: str,
        description: str,
    ) -> None:
        """
        Initialize a Transaction instance.

        Args:
            transaction_id (int): ID for the transaction.
            datetime (datetime): Date and time of the transaction.
            transaction_type (TransactionType): Type of transaction.
            category (str): Category of the transaction.
            account (Account): Account linked to this transaction.
            amount (str): Transaction amount as string
            description (str): Description or notes about the transaction.
        """

        self.transaction_id = transaction_id
        self.datetime = datetime
        self.transaction_type = transaction_type
        self.category = category
        self.account = account
        self.amount = format_amount(amount)
        self.description = description

    def to_dict(self):
        """
        Return a dictionary representation of the transaction.

        Returns:
            dict: Dictionary containing transaction details.
        """
        return {
            "transaction_id": self.transaction_id,
            "datetime": format_datetime(self.datetime),
            "transaction_type": self.transaction_type.value,
            "category": self.category,
            "account": self.account.account_name,
            "amount": str(self.amount),
            "description": self.description,
        }
