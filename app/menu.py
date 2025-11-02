# app/menu.py

from abc import ABC, abstractmethod
from decimal import Decimal

from tabulate import tabulate

from app.exception import (
    AlreadyExistsError,
    CategoryInUseError,
    InvalidInputError,
    NotFoundError,
)
from app.models import TransactionType
from app.money_manager import MoneyManager, backup_data
from app.utility import (
    read_date,
    read_integer,
    read_positive_float,
    read_positive_integer,
)


def format_header(key: str) -> str:
    """Convert dictionary key to properly formatted header (Title Case with spaces)."""
    return key.replace("_", " ").title()


def print_table(data: list[dict]) -> None:
    """Print data as a formatted table with proper headers."""
    if not data:
        print("(No data)")
        return

    # Get column keys and format them as headers
    keys = list(data[0].keys())
    headers = [format_header(k) for k in keys]

    # Convert list of dicts to list of lists (rows)
    rows = [[record[k] for k in keys] for record in data]

    print(tabulate(rows, headers=headers))


def add_transaction(money_manager: MoneyManager):
    """Add a new transaction."""

    # Collect input data from user
    transaction_type_input = input("Transaction type (Income/Expense): ")
    category = input("Category: ")
    account_name = input("Account: ")
    amount = input("Amount: ")
    description = input("Description: ")

    try:
        # Call the backend function
        money_manager.transaction_service.add_transaction(
            transaction_type_input=transaction_type_input,
            category=category,
            account_name=account_name,
            amount=amount,
            description=description,
        )
        print("Added successfully")
    except (InvalidInputError, NotFoundError) as e:
        print(f"Error: {e}")


def view_all_transactions(money_manager: MoneyManager):
    """View all transactions."""
    transactions = money_manager.transaction_service.get_all_transactions()
    transactions = [t.to_dict() for t in transactions]
    print_table(transactions)


def edit_transaction(money_manager: MoneyManager):
    """Edit an existing transaction."""
    transaction_id = read_positive_integer("Enter Transaction ID to edit: ")

    transaction = money_manager.transaction_service.get_transaction(transaction_id)
    if not transaction:
        print(f"Transaction with ID {transaction_id} not found.")
        return

    print(f"\n--- Editing Transaction ID: {transaction_id} ---")
    print("Leave field blank to keep current value.")

    print(f"Current Type: {transaction.transaction_type.value}")
    new_type = input("New Type (Income/Expense): ") or ""

    print(f"Current Category: {transaction.category}")
    new_category = input("New Category: ") or ""

    print(f"Current Account: {transaction.account.account_name}")
    new_account_name = input("New Account: ") or ""

    print(f"Current Amount: {transaction.amount}")
    new_amount = input("New Amount: ") or ""

    print(f"Current Description: {transaction.description}")
    new_description = input("New Description: ") or ""

    try:
        money_manager.transaction_service.edit_transaction(
            transaction_id=transaction_id,
            transaction_type_input=new_type,
            category=new_category,
            account_name=new_account_name,
            amount=new_amount,
            description=new_description,
        )
        print(f"Transaction ID {transaction_id} updated successfully!")
    except (InvalidInputError, NotFoundError) as e:
        print(f"Error: {e}")


def delete_transaction(money_manager: MoneyManager):
    """Delete a transaction."""
    transaction_id = read_positive_integer("Enter Transaction ID to remove: ")

    try:
        money_manager.transaction_service.delete_transaction(transaction_id)
        print(f"Transaction ID {transaction_id} removed successfully!")
    except NotFoundError as e:
        print(f"Error: {e}")


def add_account(money_manager: MoneyManager):
    """Add a new account."""
    account_name = input("Account name: ")
    initial_balance = str(read_positive_float("Initial balance: "))

    try:
        new_account = money_manager.account_service.add_account(
            account_name, initial_balance
        )
        print(f"Account '{new_account.account_name}' created successfully")
    except (InvalidInputError, AlreadyExistsError) as e:
        print(f"Error: {e}")


def view_all_accounts(money_manager: MoneyManager):
    """View all accounts."""
    accounts = money_manager.account_service.get_all_accounts()
    data = [a.to_dict() for a in accounts]
    print_table(data)


def edit_account_name(money_manager: MoneyManager):
    """Rename an existing account."""
    old_name = input("Current account name: ")
    new_name = input("New account name: ")

    try:
        updated = money_manager.account_service.edit_account_name(old_name, new_name)
        print(f"Account renamed to '{updated.account_name}' successfully")
    except (InvalidInputError, NotFoundError, AlreadyExistsError) as e:
        print(f"Error: {e}")


def delete_account(money_manager: MoneyManager):
    """Delete an account."""
    account_name = input("Account name to delete: ")
    try:
        money_manager.account_service.delete_account(account_name)
        print(f"Account '{account_name}' deleted successfully")
    except (InvalidInputError, NotFoundError) as e:
        print(f"Error: {e}")


def add_category(money_manager: MoneyManager):
    """Add a new category."""
    transaction_type_category = input("Type (Income/Expense): ")
    category = input("New Category: ")

    try:
        money_manager.category_service.add_category(category, transaction_type_category)
        print(f"Category '{category}' added successfully")
    except (InvalidInputError, AlreadyExistsError) as e:
        print(f"Error: {e}")


def view_all_categories(money_manager: MoneyManager):
    """View all categories."""
    income_category = money_manager.category_service.get_categories(
        TransactionType.INCOME
    )
    expense_category = money_manager.category_service.get_categories(
        TransactionType.EXPENSE
    )

    print("\nIncome Categories:")
    for i, cat in enumerate(income_category, 1):
        print(f"  {i}. {cat}")

    print("\nExpense Categories:")
    for i, cat in enumerate(expense_category, 1):
        print(f"  {i}. {cat}")


def edit_category(money_manager: MoneyManager):
    """Edit a category name."""
    transaction_type_category = input("Type (Income/Expense): ")
    old_category_name = input("Old category name: ")
    new_category_name = input("New category name: ")

    try:
        money_manager.category_service.edit_category(
            old_category_name, new_category_name, transaction_type_category
        )
        print(
            f"Category renamed from '{old_category_name}' to '{new_category_name}' successfully"
        )
    except (InvalidInputError, NotFoundError, AlreadyExistsError) as e:
        print(f"Error: {e}")


def delete_category(money_manager: MoneyManager):
    """Delete a category."""
    transaction_type_category = input("Type (Income/Expense): ")
    category_name = input("Category name: ")

    try:
        money_manager.category_service.delete_category(
            category_name, transaction_type_category
        )
        print(f"Category '{category_name}' removed successfully")
    except (InvalidInputError, NotFoundError, CategoryInUseError) as e:
        print(f"Error: {e}")


def filter_by_category(money_manager: MoneyManager):
    """Filter transactions by category."""
    category = input("Enter category name: ")

    try:
        result = money_manager.filter_service.filter_transaction_by_category(category)

        if not result:
            print("No result found!")
        else:
            data = [r.to_dict() for r in result]
            print_table(data)
    except (InvalidInputError, NotFoundError) as e:
        print(f"Error: {e}")


def filter_by_account(money_manager: MoneyManager):
    """Filter transactions by account."""
    account_name = input("Account name: ")

    try:
        result = money_manager.filter_service.filter_transaction_by_account(
            account_name
        )

        if not result:
            print("No result found!")
        else:
            data = [r.to_dict() for r in result]
            print_table(data)
    except (InvalidInputError, NotFoundError) as e:
        print(f"Error: {e}")


def filter_by_transaction_type(money_manager: MoneyManager):
    """Filter transactions by transaction type."""
    transaction_type = input("Transaction type (Income/Expense): ")

    try:
        result = money_manager.filter_service.filter_transaction_by_transaction_type(
            transaction_type
        )

        if not result:
            print("No result found!")
        else:
            data = [r.to_dict() for r in result]
            print_table(data)
    except InvalidInputError as e:
        print(f"Error: {e}")


def daily_summary(money_manager: MoneyManager):
    """Show daily summary."""
    try:
        date = read_date("Enter date for daily summary")
        summary = money_manager.summary_service.get_daily_summary(date)
        print_table([summary])
    except InvalidInputError as e:
        print(f"Error: {e}")


def weekly_summary(money_manager: MoneyManager):
    """Show weekly summary."""
    try:
        date = read_date("Enter any date within the week")
        summary = money_manager.summary_service.get_weekly_summary(date)
        print_table([summary])
    except InvalidInputError as e:
        print(f"Error: {e}")


def monthly_summary(money_manager: MoneyManager):
    """Show monthly summary."""
    month = read_integer("Enter month (1-12): ")
    year = read_integer("Enter year (e.g., 2024): ")

    try:
        summary = money_manager.summary_service.get_monthly_summary(year, month)
        print_table([summary])
    except InvalidInputError as e:
        print(f"Error: {e}")


def expenses_summary(money_manager: MoneyManager):
    """Show expenses summary by category for a date range."""
    try:
        start_date = read_date("Enter start date: ")
        end_date = read_date("Enter end date:")

        expenses_by_category = money_manager.summary_service.get_expenses_by_category(
            start_date, end_date
        )
        total_expense = sum(expenses_by_category.values(), Decimal("0.00"))

        if not expenses_by_category or total_expense == Decimal("0.00"):
            print("No expenses found in this period.")
        else:
            print(
                f"\nExpenses from {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            )
            print("=" * 60)
            print("\nBreakdown by Category:")
            print("-" * 60)

            sorted_expenses = sorted(
                expenses_by_category.items(), key=lambda x: x[1], reverse=True
            )

            for category, amount in sorted_expenses:
                print(f"  {category:30s} ${amount:>12}")

            print("-" * 60)
            print(f"  {'TOTAL EXPENSES':30s} ${total_expense:>12}")
            print("=" * 60)
    except InvalidInputError as e:
        print(f"Error: {e}")


def income_summary(money_manager: MoneyManager):
    """Show income summary by category for a date range."""
    try:
        start_date = read_date("Enter start date: ")
        end_date = read_date("Enter end date:")

        income_by_category = money_manager.summary_service.get_income_by_category(
            start_date, end_date
        )
        total_income = sum(income_by_category.values(), Decimal("0.00"))

        if not income_by_category or total_income == Decimal("0.00"):
            print("No incomes found in this period.")
        else:
            print(
                f"\nIncomes from {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"
            )
            print("=" * 60)
            print("\nBreakdown by Category:")
            print("-" * 60)

            sorted_incomes = sorted(
                income_by_category.items(), key=lambda x: x[1], reverse=True
            )

            for category, amount in sorted_incomes:
                print(f"  {category:30s} ${amount:>12}")

            print("-" * 60)
            print(f"  {'TOTAL INCOME':30s} ${total_income:>12}")
            print("=" * 60)
    except InvalidInputError as e:
        print(f"Error: {e}")


def backup_data_action(money_manager: MoneyManager):
    """Create a backup of the current data."""
    try:
        success = backup_data()
        if success:
            print("Backup created successfully!")
        else:
            print("Backup failed!")
    except Exception as e:
        print(f"Error creating backup: {e}")


class UserAction(ABC):
    """Abstract class for actions that can be performed on a user."""

    @abstractmethod
    def show_option(self) -> str:
        """
        Method that return string representation of the action in menu

        Returns:
            str: Menu option label
        """
        pass

    @abstractmethod
    def run(self, money_manager: MoneyManager):
        """
        Perform action based on the action, will be implemented by child class

        Args:
            money_manager (MoneyManager): The money manager object which will be affect by the action
        """
        pass


class QuitAction(UserAction):
    def show_option(self) -> str:
        return "Quit"

    def run(self, money_manager: MoneyManager):
        pass


class AccountOperation(UserAction):
    def show_option(self) -> str:
        return "Account Operation"

    def run(self, money_manager: MoneyManager):
        while True:
            print("\n--- Account Operations ---")
            print("1. Add New Account")
            print("2. View All Accounts")
            print("3. Edit Account Name")
            print("4. Delete Account")
            print("5. Back to Main Menu")

            choice = read_integer("Select an option: ")
            print()

            if choice == 1:
                add_account(money_manager)
            elif choice == 2:
                view_all_accounts(money_manager)
            elif choice == 3:
                edit_account_name(money_manager)
            elif choice == 4:
                delete_account(money_manager)
            elif choice == 5:
                break
            else:
                print("Invalid option. Try again.")


class CategoryOperation(UserAction):
    def show_option(self) -> str:
        return "Category Operation"

    def run(self, money_manager: MoneyManager):
        while True:
            print("\n--- Category Operations ---")
            print("1. Add New Category")
            print("2. View All Categories")
            print("3. Edit Category")
            print("4. Remove Category")
            print("5. Back to Main Menu")

            choice = read_integer("Select an option: ")
            print()

            if choice == 1:
                add_category(money_manager)
            elif choice == 2:
                view_all_categories(money_manager)
            elif choice == 3:
                edit_category(money_manager)
            elif choice == 4:
                delete_category(money_manager)
            elif choice == 5:
                break
            else:
                print("Invalid option. Try again.")


class TransactionOperation(UserAction):
    def show_option(self) -> str:
        return "Transaction Operation"

    def run(self, money_manager: MoneyManager):
        while True:
            print("\n--- Transaction Operations ---")
            print("1. Add New Transaction")
            print("2. View All Transactions")
            print("3. Edit Transaction")
            print("4. Delete Transaction")
            print("5. Back to Main Menu")

            choice = read_integer("Select an option: ")
            print()

            if choice == 1:
                add_transaction(money_manager)
            elif choice == 2:
                view_all_transactions(money_manager)
            elif choice == 3:
                edit_transaction(money_manager)
            elif choice == 4:
                delete_transaction(money_manager)
            elif choice == 5:
                break
            else:
                print("Invalid option. Try again.")


class FilterTransactionAction(UserAction):
    def show_option(self) -> str:
        return "Filter Transaction"

    def run(self, money_manager: MoneyManager):
        while True:
            print("\n--- Filter Transactions ---")
            print("1. Filter by category")
            print("2. Filter by account")
            print("3. Filter by transaction type")
            print("4. Back to Main Menu")

            option = read_integer("Select an option: ")
            print()

            if option == 1:
                filter_by_category(money_manager)
            elif option == 2:
                filter_by_account(money_manager)
            elif option == 3:
                filter_by_transaction_type(money_manager)
            elif option == 4:
                break
            else:
                print("Invalid option. Try again.")


class ShowSummaryAction(UserAction):
    def show_option(self) -> str:
        return "View Summary"

    def run(self, money_manager: MoneyManager):
        while True:
            print("\n--- View Summary ---")
            print("1. Daily Summary")
            print("2. Weekly Summary")
            print("3. Monthly Summary")
            print("4. Expenses Summary")
            print("5. Income Summary")
            print("6. Back to Main Menu")

            option = read_integer("Select an option: ")
            print()

            if option == 1:
                daily_summary(money_manager)
            elif option == 2:
                weekly_summary(money_manager)
            elif option == 3:
                monthly_summary(money_manager)
            elif option == 4:
                expenses_summary(money_manager)
            elif option == 5:
                income_summary(money_manager)
            elif option == 6:
                break
            else:
                print("Invalid option. Try again.")


class BackupDataAction(UserAction):
    def show_option(self) -> str:
        return "Backup Data"

    def run(self, money_manager: MoneyManager):
        backup_data_action(money_manager)
