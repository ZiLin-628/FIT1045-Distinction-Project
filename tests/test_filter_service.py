# test/test_filter_service.py

from unittest.mock import MagicMock

import pytest

from app.exception import InvalidInputError, NotFoundError
from app.models import TransactionType
from app.services.filter_service import FilterService


class FakeAccount:
    def __init__(self, name):
        self.account_name = name
        self.transactions = []


class FakeTransaction:
    def __init__(self, transaction_id, account, category, transaction_type):
        self.transaction_id = transaction_id
        self.account = account
        self.category = category
        self.transaction_type = transaction_type


class FakeCategoryService:
    def __init__(self):
        self.income_categories = []
        self.expense_categories = []

    def get_all_categories(self):
        return self.income_categories + self.expense_categories

    def get_categories(self, transaction_type):
        if transaction_type == TransactionType.INCOME:
            return self.income_categories
        return self.expense_categories


class FakeMoneyManager:
    def __init__(self):
        self.accounts = {}
        self.transactions = []
        self.income_categories = []
        self.expense_categories = []
        self.account_service = MagicMock()
        self.category_service = FakeCategoryService()


@pytest.fixture
def money_manager():
    """
    Returns a FakeMoneyManager instance with mocked account_service and category_service.
    """
    return FakeMoneyManager()


@pytest.fixture
def filter_service(money_manager):
    """
    Returns a FilterService instance using the fake MoneyManager.
    """
    return FilterService(money_manager)


class TestFilterByCategory:

    def test_filter_existing_category(self, filter_service, money_manager):
        acc = FakeAccount("Checking")
        t1 = FakeTransaction(1, acc, "Food", TransactionType.EXPENSE)
        t2 = FakeTransaction(2, acc, "Food", TransactionType.EXPENSE)
        t3 = FakeTransaction(3, acc, "Salary", TransactionType.INCOME)
        money_manager.transactions.extend([t1, t2, t3])
        money_manager.category_service.income_categories.append("Salary")
        money_manager.category_service.expense_categories.append("Food")

        result = filter_service.filter_transaction_by_category("food")
        assert len(result) == 2
        assert all(t.category == "Food" for t in result)

    def test_category_no_transactions_returns_empty(
        self, filter_service, money_manager
    ):
        money_manager.category_service.expense_categories.append("Utilities")
        result = filter_service.filter_transaction_by_category("Utilities")
        assert result == []

    def test_category_with_spaces_and_case(self, filter_service, money_manager):
        acc = FakeAccount("Checking")
        t1 = FakeTransaction(1, acc, "Food", TransactionType.EXPENSE)
        money_manager.transactions.append(t1)
        money_manager.category_service.expense_categories.append("Food")
        result = filter_service.filter_transaction_by_category("  fOoD ")
        assert result == [t1]

    def test_empty_category_raises(self, filter_service):
        with pytest.raises(InvalidInputError):
            filter_service.filter_transaction_by_category("")

    def test_category_not_exist_raises(self, filter_service, money_manager):
        money_manager.category_service.income_categories.append("Salary")
        with pytest.raises(NotFoundError):
            filter_service.filter_transaction_by_category("Bonus")


class TestFilterByAccount:

    def test_filter_existing_account(self, filter_service, money_manager):
        acc = FakeAccount("Checking")
        t1 = FakeTransaction(1, acc, "Food", TransactionType.EXPENSE)
        t2 = FakeTransaction(2, acc, "Salary", TransactionType.INCOME)
        money_manager.transactions.extend([t1, t2])
        money_manager.accounts["Checking"] = acc
        money_manager.account_service.get_account.side_effect = lambda name: (
            acc if name == "Checking" else None
        )

        result = filter_service.filter_transaction_by_account("Checking")
        assert result == [t1, t2]

    def test_account_no_transactions_returns_empty(self, filter_service, money_manager):
        acc = FakeAccount("Savings")
        money_manager.accounts["Savings"] = acc
        money_manager.account_service.get_account.side_effect = lambda name: acc
        result = filter_service.filter_transaction_by_account("Savings")
        assert result == []

    def test_account_with_spaces_and_case(self, filter_service, money_manager):
        acc = FakeAccount("Checking")
        t1 = FakeTransaction(1, acc, "Food", TransactionType.EXPENSE)
        money_manager.transactions.append(t1)
        money_manager.accounts["Checking"] = acc
        money_manager.account_service.get_account.side_effect = lambda name: acc
        result = filter_service.filter_transaction_by_account("  cHeCkInG ")
        assert result == [t1]

    def test_empty_account_raises(self, filter_service):
        with pytest.raises(InvalidInputError):
            filter_service.filter_transaction_by_account("")

    def test_account_not_exist_raises(self, filter_service, money_manager):
        money_manager.account_service.get_account.side_effect = lambda name: None
        with pytest.raises(NotFoundError):
            filter_service.filter_transaction_by_account("Unknown")


class TestFilterByTransactionType:

    def test_filter_income_transactions(self, filter_service, money_manager):
        acc = FakeAccount("Checking")
        t1 = FakeTransaction(1, acc, "Salary", TransactionType.INCOME)
        t2 = FakeTransaction(2, acc, "Food", TransactionType.EXPENSE)
        money_manager.transactions.extend([t1, t2])
        money_manager.category_service.income_categories.append("Salary")
        money_manager.category_service.expense_categories.append("Food")

        result = filter_service.filter_transaction_by_transaction_type("income")
        assert result == [t1]

    def test_filter_expense_transactions(self, filter_service, money_manager):
        acc = FakeAccount("Checking")
        t1 = FakeTransaction(1, acc, "Salary", TransactionType.INCOME)
        t2 = FakeTransaction(2, acc, "Food", TransactionType.EXPENSE)
        money_manager.transactions.extend([t1, t2])
        money_manager.category_service.income_categories.append("Salary")
        money_manager.category_service.expense_categories.append("Food")

        result = filter_service.filter_transaction_by_transaction_type("EXPENSE")
        assert result == [t2]

    def test_transaction_type_with_spaces_and_case(self, filter_service, money_manager):
        acc = FakeAccount("Checking")
        t1 = FakeTransaction(1, acc, "Salary", TransactionType.INCOME)
        money_manager.transactions.append(t1)
        money_manager.category_service.income_categories.append("Salary")
        result = filter_service.filter_transaction_by_transaction_type("  InCoMe  ")
        assert result == [t1]

    def test_invalid_transaction_type_raises(self, filter_service):
        with pytest.raises(InvalidInputError):
            filter_service.filter_transaction_by_transaction_type("unknown")

    def test_empty_transaction_type_raises(self, filter_service):
        with pytest.raises(InvalidInputError):
            filter_service.filter_transaction_by_transaction_type("")

