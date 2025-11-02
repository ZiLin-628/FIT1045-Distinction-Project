# test/test_summary_service.py

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.models import TransactionType
from app.services.summary_service import SummaryService


class FakeAccount:
    def __init__(self, name):
        self.account_name = name
        self.transactions = []


class FakeTransaction:
    def __init__(
        self, transaction_id, account, category, transaction_type, amount, datetime_obj
    ):
        self.transaction_id = transaction_id
        self.account = account
        self.category = category
        self.transaction_type = transaction_type
        self.amount = Decimal(amount)
        self.datetime = datetime_obj


class FakeCategoryService:
    def __init__(self):
        self.income_categories = []
        self.expense_categories = []


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
    return FakeMoneyManager()


@pytest.fixture
def summary_service(money_manager):
    return SummaryService(money_manager)


class TestDailySummary:

    def test_transactions_exist(self, summary_service, money_manager):
        acc = FakeAccount("Checking")
        money_manager.accounts["Checking"] = acc

        now = datetime.now()
        t1 = FakeTransaction(1, acc, "Salary", TransactionType.INCOME, "100.00", now)
        t2 = FakeTransaction(2, acc, "Food", TransactionType.EXPENSE, "50.00", now)
        money_manager.transactions.extend([t1, t2])

        result = summary_service.get_daily_summary(now)
        assert result["total_income"] == Decimal("100.00")
        assert result["total_expense"] == Decimal("50.00")
        assert result["net"] == Decimal("50.00")
        assert result["transaction_count"] == 2

    def test_no_transactions_returns_zero(self, summary_service):
        now = datetime.now()
        result = summary_service.get_daily_summary(now)
        assert result["total_income"] == 0
        assert result["total_expense"] == 0
        assert result["net"] == 0
        assert result["transaction_count"] == 0

    def test_boundary_times_included(self, summary_service, money_manager):
        acc = FakeAccount("Checking")
        money_manager.accounts["Checking"] = acc
        date = datetime(2025, 10, 28)

        t1 = FakeTransaction(
            1,
            acc,
            "Salary",
            TransactionType.INCOME,
            "10.00",
            datetime(2025, 10, 28, 0, 0, 0),
        )
        t2 = FakeTransaction(
            2,
            acc,
            "Food",
            TransactionType.EXPENSE,
            "5.00",
            datetime(2025, 10, 28, 23, 59, 59),
        )
        t3 = FakeTransaction(
            3,
            acc,
            "Other",
            TransactionType.EXPENSE,
            "3.00",
            datetime(2025, 10, 27, 23, 59, 59),
        )
        money_manager.transactions.extend([t1, t2, t3])

        result = summary_service.get_daily_summary(date)
        assert result["total_income"] == Decimal("10.00")
        assert result["total_expense"] == Decimal("5.00")
        assert result["transaction_count"] == 2


class TestWeeklySummary:

    def test_weekly_summary_totals(self, summary_service, money_manager):
        acc = FakeAccount("Checking")
        money_manager.accounts["Checking"] = acc

        # Monday of the week
        monday = datetime(2025, 10, 27)
        t1 = FakeTransaction(1, acc, "Salary", TransactionType.INCOME, "100.00", monday)
        t2 = FakeTransaction(
            2,
            acc,
            "Food",
            TransactionType.EXPENSE,
            "50.00",
            monday + timedelta(days=6, hours=23),
        )
        # Outside current week
        t3 = FakeTransaction(
            3,
            acc,
            "Other",
            TransactionType.EXPENSE,
            "20.00",
            monday - timedelta(days=1),
        )
        money_manager.transactions.extend([t1, t2, t3])

        result = summary_service.get_weekly_summary(monday)
        assert result["total_income"] == Decimal("100.00")
        assert result["total_expense"] == Decimal("50.00")
        assert result["net"] == Decimal("50.00")
        assert result["transaction_count"] == 2

    def test_no_transactions_weekly(self, summary_service):
        date = datetime(2025, 10, 27)
        result = summary_service.get_weekly_summary(date)
        assert result["total_income"] == 0
        assert result["total_expense"] == 0
        assert result["net"] == 0
        assert result["transaction_count"] == 0


class TestMonthlySummary:

    def test_monthly_summary_totals(self, summary_service, money_manager):
        acc = FakeAccount("Checking")
        money_manager.accounts["Checking"] = acc

        # October 2025
        t1 = FakeTransaction(
            1,
            acc,
            "Salary",
            TransactionType.INCOME,
            "200.00",
            datetime(2025, 10, 1, 0, 0),
        )
        t2 = FakeTransaction(
            2,
            acc,
            "Food",
            TransactionType.EXPENSE,
            "50.00",
            datetime(2025, 10, 31, 23, 59),
        )
        t3 = FakeTransaction(
            3, acc, "Other", TransactionType.EXPENSE, "30.00", datetime(2025, 11, 1)
        )
        money_manager.transactions.extend([t1, t2, t3])

        result = summary_service.get_monthly_summary(2025, 10)
        assert result["total_income"] == Decimal("200.00")
        assert result["total_expense"] == Decimal("50.00")
        assert result["net"] == Decimal("150.00")
        assert result["transaction_count"] == 2

    def test_invalid_month_or_year_returns_empty(self, summary_service):
        assert summary_service.get_monthly_summary(0, 5) == {}
        assert summary_service.get_monthly_summary(2025, 0) == {}
        assert summary_service.get_monthly_summary(2025, 13) == {}


class TestExpensesByCategory:

    def test_expenses_by_category(self, summary_service, money_manager):
        acc = FakeAccount("Checking")
        money_manager.accounts["Checking"] = acc

        start = datetime(2025, 10, 1)
        end = datetime(2025, 10, 31)

        t1 = FakeTransaction(
            1, acc, "Food", TransactionType.EXPENSE, "50.00", datetime(2025, 10, 5)
        )
        t2 = FakeTransaction(
            2, acc, "Transport", TransactionType.EXPENSE, "20.00", datetime(2025, 10, 6)
        )
        t3 = FakeTransaction(
            3, acc, "Food", TransactionType.EXPENSE, "30.00", datetime(2025, 10, 10)
        )
        t4 = FakeTransaction(
            4, acc, "Salary", TransactionType.INCOME, "100.00", datetime(2025, 10, 5)
        )
        money_manager.transactions.extend([t1, t2, t3, t4])

        result = summary_service.get_expenses_by_category(start, end)
        assert result == {"Food": Decimal("80.00"), "Transport": Decimal("20.00")}

    def test_expenses_empty_or_invalid_range(self, summary_service):
        start = datetime(2025, 10, 10)
        end = datetime(2025, 10, 5)
        assert summary_service.get_expenses_by_category(start, end) == {}


class TestIncomeByCategory:

    def test_income_by_category(self, summary_service, money_manager):
        acc = FakeAccount("Checking")
        money_manager.accounts["Checking"] = acc

        start = datetime(2025, 10, 1)
        end = datetime(2025, 10, 31)

        t1 = FakeTransaction(
            1, acc, "Salary", TransactionType.INCOME, "100.00", datetime(2025, 10, 5)
        )
        t2 = FakeTransaction(
            2, acc, "Bonus", TransactionType.INCOME, "50.00", datetime(2025, 10, 10)
        )
        t3 = FakeTransaction(
            3, acc, "Food", TransactionType.EXPENSE, "20.00", datetime(2025, 10, 10)
        )
        money_manager.transactions.extend([t1, t2, t3])

        result = summary_service.get_income_by_category(start, end)
        assert result == {"Salary": Decimal("100.00"), "Bonus": Decimal("50.00")}

    def test_income_empty_or_invalid_range(self, summary_service):
        start = datetime(2025, 10, 10)
        end = datetime(2025, 10, 5)
        assert summary_service.get_income_by_category(start, end) == {}
