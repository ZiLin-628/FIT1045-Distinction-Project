# app/services/transaction_service.py

from __future__ import annotations

from typing import TYPE_CHECKING

from app.exception import NotFoundError
from app.models import Transaction
from app.utility import (
    get_current_time,
    validate_non_empty_string,
    validate_non_negative_amount,
    validate_transaction_type,
)

if TYPE_CHECKING:
    from app.money_manager import MoneyManager


class TransactionService:
    """
    Service class responsible for managing transactions within a MoneyManager instance.
    """

    def __init__(self, money_manager: MoneyManager) -> None:
        """
        Initialize TransactionService with a MoneyManager instance.

        Args:
            money_manager (MoneyManager): The parent money manager that holds all data.
        """

        self.money_manager = money_manager
        self.transactions = money_manager.transactions

    @property
    def next_transaction_id(self) -> int:
        """
        Returns the next available transaction ID (auto-increment).

        Returns:
            int: The next transaction ID.
        """
        if self.transactions:
            return max(t.transaction_id for t in self.transactions) + 1

        return 1

    def add_transaction(
        self,
        transaction_type_input: str,
        category: str,
        account_name: str,
        amount: str,
        description: str,
    ) -> Transaction:
        """
        Adds a new transaction and updates related account balance.

        Args:
            transaction_type_input (str): Type of transaction.
            category (str): Transaction category name.
            account_name (str): Account involved in the transaction.
            amount (str): Amount string.
            description (str): Description of the transaction.

        Returns:
            Transaction: The newly created Transaction object.

        Raises:
            InvalidInputError: For invalid transaction type, category, account, or amount.
            NotFoundError: If category or account doesn't exist.
        """

        # Convert the transaction type string to an Enum
        transaction_type = validate_transaction_type(transaction_type_input)

        # Validate category name
        category = validate_non_empty_string(category, "Category name")

        # Check if category exist
        if not self.money_manager.category_service.is_valid_category(
            category, transaction_type
        ):
            raise NotFoundError(f"Category '{category}' does not exist")

        # Validate account name
        account_name = validate_non_empty_string(account_name, "Account name")

        # Validate if account exist
        account = self.money_manager.account_service.get_account(account_name)
        if not account:
            raise NotFoundError(f"Account '{account_name}' does not exist.")

        # Validate amount is positive
        validate_non_negative_amount(amount, "Transaction amount")

        # Timestamp always set to current time
        timestamp = get_current_time()

        # Create new transaction object
        transaction = Transaction(
            transaction_id=self.next_transaction_id,
            datetime=timestamp,
            transaction_type=transaction_type,
            category=category,
            account=account,
            amount=amount,
            description=description,
        )

        # Update account balance
        account.update_balance(transaction.amount, transaction_type)

        # Add to collections
        self.transactions.append(transaction)
        account.add_transaction(transaction)

        # Save changes
        self.money_manager.save()
        return transaction

    def get_transaction(self, transaction_id: int):
        """
        Retrieve a transaction by its ID.

        Args:
            transaction_id (int): ID of the transaction to retrieve.

        Returns:
            Transaction | None: The transaction object, or None if not found.
        """
        for trans in self.transactions:
            if trans.transaction_id == transaction_id:
                return trans
        return None

    def get_all_transactions(self, reverse_chronological: bool = True):
        """
        Retrieve all transactions, optionally sorted by date (descending by default).

        Args:
            reverse_chronological (bool, optional): Sort from newest to oldest. Defaults to True.

        Returns:
            list[Transaction]: Sorted list of transactions.
        """
        return sorted(
            self.transactions, key=lambda t: t.datetime, reverse=reverse_chronological
        )

    def edit_transaction(
        self,
        transaction_id: int,
        transaction_type_input: str,
        category: str,
        account_name: str,
        amount: str,
        description: str,
    ) -> Transaction:
        """
        Edit an existing transaction by ID.

        Args:
            transaction_id (int): ID of the transaction to edit.
            transaction_type_input (str): Updated transaction type ("income" or "expense").
            category (str): Updated category name.
            account_name (str): Updated account name.
            amount (str): Updated amount.
            description (str): Updated description text.

        Returns:
            Transaction: The updated transaction.

        Raises:
            InvalidInputError: For invalid field values.
            NotFoundError: If transaction, category, or account doesn't exist.
        """

        # Check if transaction exist
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction with ID {transaction_id} not found.")

        # Capture old values for reversal
        old_account = transaction.account
        old_amount = transaction.amount
        old_transaction_type = transaction.transaction_type

        # Process and validate new inputs

        # Transaction Type - only update if non-empty
        new_transaction_type = old_transaction_type
        if transaction_type_input.strip():
            new_transaction_type = validate_transaction_type(transaction_type_input)

        # Category - only update if non-empty
        new_category = transaction.category
        if category.strip():
            new_category = category.strip().capitalize()
            # Validate category against the (potentially) new transaction type
            if not self.money_manager.category_service.is_valid_category(
                new_category, new_transaction_type
            ):
                raise NotFoundError(
                    f"Category '{new_category}' is not valid for {new_transaction_type.value} transactions."
                )

        # Account - only update if non-empty
        new_account = old_account
        if account_name.strip():
            new_account_name = validate_non_empty_string(account_name, "Account name")
            new_account = self.money_manager.account_service.get_account(
                new_account_name
            )
            if not new_account:
                raise NotFoundError(f"Account '{new_account_name}' not found.")

        # Amount - only update if non-empty
        new_amount = old_amount
        if amount.strip():
            new_amount = validate_non_negative_amount(amount, "Transaction amount")

        # Description - always update (can be set to empty)
        new_description = description.strip()

        # Reverse the original transaction's impact
        old_account.reverse_balance(old_amount, old_transaction_type)
        if old_account is not new_account:
            old_account.remove_transaction(transaction)

        # Update the Transaction object
        transaction.transaction_type = new_transaction_type
        transaction.category = new_category
        transaction.account = new_account
        transaction.amount = new_amount
        transaction.description = new_description

        # Add to new account if changed
        if old_account is not new_account:
            new_account.add_transaction(transaction)

        # Apply the new transaction's impact
        new_account.update_balance(new_amount, new_transaction_type)

        self.money_manager.save()
        return transaction

    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a transaction by ID and reverse its effect on the account.

        Args:
            transaction_id (int): ID of the transaction to delete.

        Returns:
            bool: True if deletion succeeded.

        Raises:
            NotFoundError: If transaction does not exist.
        """

        # Check if transaction exist
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            raise NotFoundError(f"Transaction ID '{transaction_id}' does not exist")

        account = transaction.account
        amount = transaction.amount
        transaction_type = transaction.transaction_type

        # Reverse the impact on the account balance
        account.reverse_balance(amount, transaction_type)

        # Remove transaction from the account's list
        account.remove_transaction(transaction)

        # Remove transaction from the global list
        self.transactions.remove(transaction)

        # Save changes
        self.money_manager.save()
        return True
