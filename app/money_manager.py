# money_manager.py

import datetime
import json
import os
import shutil

from app.models import Account, Transaction, TransactionType
from app.services.account_service import AccountService
from app.services.category_service import CategoryService
from app.services.filter_service import FilterService
from app.services.summary_service import SummaryService
from app.services.transaction_service import TransactionService
from app.utility import parse_datetime


class MoneyManager:
    """
    Central manager for managing accounts, transactions, and categories.

    Attributes:
        accounts (dict[str, Account]): Dictionary of accounts keyed by name.
        transactions (list[Transaction]): List of all transactions.
        income_categories (list[str]): List of income categories.
        expense_categories (list[str]): List of expense categories.
        account_service (AccountService): Service to manage accounts.
        transaction_service (TransactionService): Service to manage transactions.
        category_service (CategoryService): Service to manage categories.
        filter_service (FilterService): Service to filter transactions.
        summary_service (SummaryService): Service to generate summaries.
    """

    def __init__(self, data_path="data/data.json") -> None:
        """
        Initialize MoneyManager, load data from JSON file, and setup services.

        Args:
            data_path (str, optional): Path to JSON file storing data.
                Defaults to "data/data.json".
        """

        self._data_path = data_path

        self.accounts: dict[str, Account] = {}
        self.transactions: list[Transaction] = []

        # Default income and expense categories
        self.income_categories = [
            "Salary",
            "Business",
            "Investment",
            "Gift",
            "Other Income",
        ]
        self.expense_categories = [
            "Food",
            "Transport",
            "Entertainment",
            "Bills",
            "Shopping",
            "Healthcare",
            "Other Expense",
        ]

        # Load data from file if it exists
        self._load_data()

        # Initialize service objects
        self.account_service = AccountService(money_manager=self)
        self.transaction_service = TransactionService(money_manager=self)
        self.category_service = CategoryService(money_manager=self)
        self.filter_service = FilterService(money_manager=self)
        self.summary_service = SummaryService(money_manager=self)

    def _load_data(self):
        """Load accounts, transactions, and categories from the JSON data file."""

        try:
            with open(self._data_path, "r") as f:
                data = json.load(f)

            # Load accounts
            for acc_data in data.get("accounts", []):
                account = Account(
                    account_name=acc_data["account_name"], balance=acc_data["balance"]
                )
                self.accounts[account.account_name] = account

            # Load transactions and associate them with accounts
            for trans_data in data.get("transactions", []):
                account_name = trans_data["account"]
                account = self.accounts[account_name]

                transaction = Transaction(
                    transaction_id=trans_data["transaction_id"],
                    datetime=parse_datetime(trans_data["datetime"]),
                    transaction_type=TransactionType(trans_data["transaction_type"]),
                    category=trans_data["category"],
                    account=account,
                    amount=trans_data["amount"],
                    description=trans_data["description"],
                )

                self.transactions.append(transaction)
                account.add_transaction(transaction)

            # Load categories if saved, otherwise keep defaults
            self.income_categories = data.get(
                "income_categories", self.income_categories
            )
            self.expense_categories = data.get(
                "expense_categories", self.expense_categories
            )

        except FileNotFoundError:
            # If file does not exist, initialize empty and default data
            pass

    def _save_data(self):
        """Save accounts, transactions, and categories to the JSON data file."""
        data_to_save = {
            "accounts": [a.to_dict() for a in self.accounts.values()],
            "transactions": [t.to_dict() for t in self.transactions],
            "income_categories": self.income_categories,
            "expense_categories": self.expense_categories,
        }

        with open(self._data_path, "w") as f:
            json.dump(data_to_save, f, indent=4)

    def save(self):
        """Public method to save all data."""
        self._save_data()


def backup_data(data_path="data/data.json", backup_dir="data/backups") -> bool:
    """
    Create a backup of the data file.

    Args:
        data_path (str): Path to the data JSON file.
        backup_dir (str): Directory where backups will be stored.

    Returns:
        bool: True if backup succeeded, False otherwise.
    """

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Use current datetime to create unique backup filename
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    backup_filename = f"money_manager_backup_{timestamp}.json"
    backup_filepath = os.path.join(backup_dir, backup_filename)

    try:
        shutil.copy(data_path, backup_filepath)
        return True
    except Exception:
        return False
