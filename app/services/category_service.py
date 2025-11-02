# app/services/category_service.py

from __future__ import annotations

from typing import TYPE_CHECKING

from app.exception import AlreadyExistsError, CategoryInUseError, NotFoundError
from app.models import TransactionType
from app.utility import validate_non_empty_string, validate_transaction_type

if TYPE_CHECKING:
    from app.money_manager import MoneyManager


class CategoryService:
    """
    Service class to manage income and expense categories for a MoneyManager instance.
    """

    def __init__(self, money_manager: MoneyManager) -> None:
        """
        Initialize the CategoryService with a MoneyManager instance.

        Args:
            money_manager (MoneyManager): The MoneyManager instance containing categories and transactions.
        """
        self.money_manager = money_manager
        self.income_categories = money_manager.income_categories
        self.expense_categories = money_manager.expense_categories

    def get_categories(self, transaction_type: TransactionType) -> list[str]:
        """
        Get a list of categories for a specific transaction type.

        Args:
            transaction_type (TransactionType): Either INCOME or EXPENSE.

        Returns:
            list[str]: List of category names for the given type.
        """

        return (
            self.income_categories
            if transaction_type == TransactionType.INCOME
            else self.expense_categories
        )

    def get_all_categories(self) -> list[str]:
        """
        Get all categories (income + expense).

        Returns:
            list[str]: Combined list of all categories.
        """

        return self.income_categories + self.expense_categories

    def is_valid_category(
        self, category: str, transaction_type: TransactionType
    ) -> bool:
        """
        Check if a category exists for a given transaction type.

        Args:
            category (str): The category name to check.
            transaction_type (TransactionType): Type of transaction (INCOME or EXPENSE).

        Returns:
            bool: True if category exists, False otherwise.
        """
        return category in self.get_categories(transaction_type)

    def add_category(self, category: str, transaction_type_input: str) -> None:
        """
        Add a new category to the specified transaction type.

        Args:
            category (str): Name of the new category.
            transaction_type_input (str): Type of transaction ("income" or "expense").

        Raises:
            InvalidInputError: If category is empty or transaction type is invalid.
            AlreadyExistsError: If category already exists.
        """

        # Convert string input to TransactionType enum
        transaction_type = validate_transaction_type(transaction_type_input)

        # Validate category name
        category = validate_non_empty_string(category, "Category name")

        # Check if the category already exist
        category_list = self.get_categories(transaction_type)
        if category in category_list:
            raise AlreadyExistsError(f"A category named '{category}' already exists.")

        # Add the category to the appropriate list
        if transaction_type == TransactionType.INCOME:
            self.income_categories.append(category)
        else:
            self.expense_categories.append(category)

        # Save changes
        self.money_manager.save()

    def edit_category(
        self, old_category: str, new_category: str, transaction_type_input: str
    ):
        """
        Edit an existing category's name.

        Args:
            old_category (str): Current name of the category.
            new_category (str): New name to replace the old category.
            transaction_type_input (str): Type of transaction ("income" or "expense").

        Raises:
            InvalidInputError: If new category is empty or transaction type is invalid.
            NotFoundError: If the old category does not exist.
            AlreadyExistsError: If new category already exists.
        """

        # Convert string input to TransactionType enum
        transaction_type = validate_transaction_type(transaction_type_input)

        # Validate new category name
        old_category = validate_non_empty_string(old_category, "Old category name")
        new_category = validate_non_empty_string(new_category, "New category name")

        # Get the appropriate category list
        category_list = self.get_categories(transaction_type)

        # Check if old category exists
        if old_category not in category_list:
            raise NotFoundError(
                f"Category '{old_category}' not found in {transaction_type.value} categories."
            )

        # Check if new category already exists (and is different from old)
        if new_category in category_list and new_category != old_category:
            raise AlreadyExistsError(
                f"Category '{new_category}' already exists. Choose a different name."
            )

        # Update category in the list
        category_list[category_list.index(old_category)] = new_category

        # Update all transactions that use this category
        for trans in self.money_manager.transactions:
            if (
                trans.category == old_category
                and trans.transaction_type == transaction_type
            ):
                trans.category = new_category

        self.money_manager.save()

    def delete_category(self, category: str, transaction_type_input: str) -> bool:
        """
        Delete a category if it is not used by any transactions.

        Args:
            category (str): Name of the category to delete.
            transaction_type_input (str): Type of transaction ("income" or "expense").

        Returns:
            bool: True if deletion was successful.

        Raises:
            InvalidInputError: If category is empty or transaction type is invalid.
            NotFoundError: If category does not exist.
            CategoryInUseError: If category is used in any transactions.
        """

        # Convert string input to TransactionType enum
        transaction_type = validate_transaction_type(transaction_type_input)

        # Validate category name
        category = validate_non_empty_string(category, "Category name")

        category_list = self.get_categories(transaction_type)

        # Check if category exists
        if category not in category_list:
            raise NotFoundError(f"Category '{category}' does not exist")

        # Check if any transactions use this category
        used_by = [
            t
            for t in self.money_manager.transactions
            if t.category == category and t.transaction_type == transaction_type
        ]

        if used_by:
            raise CategoryInUseError(
                f"Category '{category}' is used by {len(used_by)} transaction(s)."
            )

        # Remove category and save changes
        category_list.remove(category)
        self.money_manager.save()

        return True
