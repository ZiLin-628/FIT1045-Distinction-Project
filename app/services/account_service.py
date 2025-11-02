# app/services/account_service.py

from __future__ import annotations

from typing import TYPE_CHECKING

from app.exception import AlreadyExistsError, NotFoundError
from app.models import Account
from app.utility import validate_non_empty_string, validate_non_negative_amount

if TYPE_CHECKING:
    from app.money_manager import MoneyManager


class AccountService:
    """
    Service class for managing accounts within MoneyManager.
    """

    def __init__(self, money_manager: MoneyManager) -> None:
        """
        Initialize AccountService with reference to MoneyManager.

        Args:
            money_manager (MoneyManager): Core MoneyManager instance.
        """
        self.money_manager = money_manager
        self.accounts = money_manager.accounts

    def add_account(self, account_name: str, initial_balance: str) -> Account:
        """
        Add a new account with the given name and initial balance.

        Args:
            account_name (str): Name of the account to add.
            initial_balance (str): Initial balance as string.

        Returns:
            Account: The newly created Account object.

        Raises:
            InvalidInputError: If name is empty or balance is negative.
            AlreadyExistsError: If an account with the same name exists.
        """

        # Validate account name
        account_name = validate_non_empty_string(account_name, "Account name")

        # Validate if is duplicate account name
        if account_name in self.accounts:
            raise AlreadyExistsError(
                f"An account named '{account_name}' already exists."
            )

        # Validate initial balance is non-negative
        validate_non_negative_amount(initial_balance, "Initial balance")

        # Create and store the new account
        new_account = Account(account_name=account_name, balance=initial_balance)
        self.accounts[account_name] = new_account

        # Save changes
        self.money_manager.save()
        return new_account

    def get_account(self, account_name: str) -> Account | None:
        """
        Retrieve an account by name.

        Args:
            account_name (str): Name of the account to retrieve.

        Returns:
            Account | None: The Account object if found, otherwise None.

        Raises:
            InvalidInputError: If account name is empty.
        """

        # Validate account name
        account_name = validate_non_empty_string(account_name, "Account name")

        # Return the account if found, else None
        return self.accounts.get(account_name)

    def get_all_accounts(self) -> list[Account]:
        """
        Get a list of all accounts.

        Returns:
            list[Account]: List containing all Account objects.
        """
        return list(self.accounts.values())

    def edit_account_name(self, old_name: str, new_name: str) -> Account:
        """
        Rename an existing account.

        Args:
            old_name (str): Current account name.
            new_name (str): New name for the account.

        Returns:
            Account: The updated Account object.

        Raises:
            InvalidInputError: If either name is empty.
            NotFoundError: If the old account does not exist.
            AlreadyExistsError: If an account with the new name already exists.
        """

        # Validate names
        old_name = validate_non_empty_string(old_name, "Old account name")
        new_name = validate_non_empty_string(new_name, "New account name")

        # Ensure the old account exists
        account = self.get_account(old_name)
        if not account:
            raise NotFoundError(f"Account '{old_name}' does not exist.")

        # Prevent naming collision
        if new_name in self.accounts and new_name != old_name:
            raise AlreadyExistsError(f"An account named '{new_name}' already exists.")

        # Update the account object's name and the dictionary key
        account.account_name = new_name
        # Remove old key and insert new key mapping to the same object
        del self.accounts[old_name]
        self.accounts[new_name] = account

        # Save changes
        self.money_manager.save()
        return account

    def delete_account(self, account_name: str) -> bool:
        """
        Delete an account by name and remove associated transactions.

        Args:
            account_name (str): Name of the account to delete.

        Returns:
            bool: True if deletion succeeded.

        Raises:
            InvalidInputError: If account name is empty.
            NotFoundError: If account does not exist.
        """

        # Validate account name
        account_name = validate_non_empty_string(account_name, "Account name")

        # Retrieve the account object, raise error if not found
        account = self.get_account(account_name)
        if not account:
            raise NotFoundError(f"Account '{account_name}' does not exist.")

        # Remove all transactions associated with this account
        self.money_manager.transactions = [
            t for t in self.money_manager.transactions if t.account != account
        ]

        # Remove the account from the accounts dictionary
        del self.accounts[account_name]

        # Save changes
        self.money_manager.save()
        return True
