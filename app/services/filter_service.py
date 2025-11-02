# app/services/filter_service.py

from __future__ import annotations

from typing import TYPE_CHECKING

from app.exception import NotFoundError
from app.utility import validate_non_empty_string, validate_transaction_type

if TYPE_CHECKING:
    from app.money_manager import MoneyManager


class FilterService:
    """
    Service class responsible for filtering transactions based on various criteria.
    """

    def __init__(self, money_manager: MoneyManager) -> None:
        """
        Initialize the FilterService with a MoneyManager instance.

        Args:
            money_manager (MoneyManager): The central manager containing all data.
        """
        self.money_manager = money_manager
        self.accounts = money_manager.accounts
        self.transactions = money_manager.transactions
        self.income_categories = money_manager.income_categories
        self.expense_categories = money_manager.expense_categories

    def filter_transaction_by_category(self, category: str):
        """
        Filter transactions that belong to a specific category.

        Args:
            category (str): The category name to filter by.

        Returns:
            list: A list of Transaction objects matching the category.

        Raises:
            InvalidInputError: If the category name is empty.
            NotFoundError: If the category does not exist.
        """

        # Validate category name
        category = validate_non_empty_string(category, "Category name")

        # Check if category exist
        category_list = self.money_manager.category_service.get_all_categories()
        if category not in category_list:
            raise NotFoundError(f"Category '{category}' does not exist")

        # Filter transactions which having this category
        return [t for t in self.transactions if t.category == category]

    def filter_transaction_by_account(self, account_name: str):
        """
        Filter transactions belonging to a specific account.

        Args:
            account_name (str): The account name to filter by.

        Returns:
            list: A list of Transaction objects related to the specified account.

        Raises:
            InvalidInputError: If account name is empty.
            NotFoundError: If the account does not exist.
        """

        # Validate account name
        account_name = validate_non_empty_string(account_name, "Account name")

        # Validate if account exist
        account = self.money_manager.account_service.get_account(account_name)
        if not account:
            raise NotFoundError(f"Account '{account_name}' does not exist.")

        # Filter transactions which are realted to this account
        return [
            t
            for t in self.transactions
            if t.account.account_name == account.account_name
        ]

    def filter_transaction_by_transaction_type(self, transaction_type_input: str):
        """
        Filter transactions by transaction type (e.g., 'income' or 'expense').

        Args:
            transaction_type_input (str): The transaction type input string.

        Returns:
            list: A list of Transaction objects matching the transaction type.

        Raises:
            InvalidInputError: If the transaction type is invalid.
        """

        # Validate transaction type
        transaction_type = validate_transaction_type(transaction_type_input)

        # Get all categories for the transaction type
        category_list = self.money_manager.category_service.get_categories(
            transaction_type
        )

        # Filter all transactions mathced with the specified transacion type
        return [t for t in self.transactions if t.category in category_list]
