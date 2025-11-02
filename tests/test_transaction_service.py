from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.exception import InvalidInputError, NotFoundError
from app.models import TransactionType
from app.services.transaction_service import TransactionService
from app.utility import format_amount



class FakeAccount:
    def __init__(self, name, balance="0.00"):
        self.account_name = name
        self.balance = balance
        self.transactions = []

    def update_balance(self, amount, transaction_type):
        self.balance = str(
            Decimal(self.balance) + Decimal(amount)
            if transaction_type == TransactionType.INCOME
            else Decimal(self.balance) - Decimal(amount)
        )

    def reverse_balance(self, amount, transaction_type):
        self.balance = str(
            Decimal(self.balance) - Decimal(amount)
            if transaction_type == TransactionType.INCOME
            else Decimal(self.balance) + Decimal(amount)
        )

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def remove_transaction(self, transaction):
        if transaction in self.transactions:
            self.transactions.remove(transaction)


class FakeCategoryService:
    def __init__(self):
        self.income_categories = []
        self.expense_categories = []

    def is_valid_category(self, category, transaction_type):
        if transaction_type == TransactionType.INCOME:
            return category in self.income_categories
        return category in self.expense_categories


class FakeMoneyManager:
    def __init__(self):
        self.transactions = []
        self.account_service = MagicMock()
        self.category_service = FakeCategoryService()
        self.save = MagicMock()


@pytest.fixture
def money_manager():
    return FakeMoneyManager()


@pytest.fixture
def transaction_service(money_manager):
    return TransactionService(money_manager)


@pytest.fixture
def setup_accounts_and_categories(transaction_service, money_manager):
    acc1 = FakeAccount("Checking")
    acc2 = FakeAccount("Savings")
    money_manager.account_service.get_account.side_effect = lambda name: (
        acc1 if name == "Checking" else (acc2 if name == "Savings" else None)
    )
    money_manager.category_service.income_categories.append("Salary")
    money_manager.category_service.expense_categories.append("Food")
    return acc1, acc2




class TestNextTransactionID:
    def test_no_transactions_returns_1(self, transaction_service):
        assert transaction_service.next_transaction_id == 1

    def test_transactions_exist_returns_max_plus_1(
        self, transaction_service, setup_accounts_and_categories
    ):
        acc1, _ = setup_accounts_and_categories
        for tid in [1, 3, 7]:
            t = MagicMock(
                transaction_id=tid,
                account=acc1,
                amount="10.00",
                transaction_type=TransactionType.INCOME,
            )
            transaction_service.transactions.append(t)
        assert transaction_service.next_transaction_id == 8


class TestAddTransaction:
    def test_add_income_transaction_success(
        self, transaction_service, setup_accounts_and_categories
    ):
        acc1, _ = setup_accounts_and_categories
        trans = transaction_service.add_transaction(
            "income", "salary", "Checking", "100.00", "Monthly salary"
        )
        assert trans in transaction_service.transactions
        assert trans.account == acc1
        assert acc1.transactions[-1] == trans
        transaction_service.money_manager.save.assert_called()
        assert trans.transaction_type == TransactionType.INCOME
        assert trans.category == "Salary"
        assert trans.amount == format_amount("100.00")
        assert trans.description == "Monthly salary"
        assert trans.transaction_id == 1
        assert hasattr(trans, "datetime")

    def test_add_expense_transaction_success(
        self, transaction_service, setup_accounts_and_categories
    ):
        _, acc2 = setup_accounts_and_categories
        trans = transaction_service.add_transaction(
            "expense", "Food", "Savings", "50.00", ""
        )
        assert trans in transaction_service.transactions
        assert trans.account == acc2
        assert trans.description == ""

    def test_add_transaction_invalid_type_raises(
        self, transaction_service, setup_accounts_and_categories
    ):
        with pytest.raises(InvalidInputError):
            transaction_service.add_transaction(
                "invalid", "Salary", "Checking", "100", "desc"
            )

    def test_add_transaction_category_not_exist_raises(
        self, transaction_service, setup_accounts_and_categories
    ):
        with pytest.raises(NotFoundError):
            transaction_service.add_transaction(
                "income", "Bonus", "Checking", "100", "desc"
            )

    def test_add_transaction_account_not_exist_raises(
        self, transaction_service, setup_accounts_and_categories
    ):
        with pytest.raises(NotFoundError):
            transaction_service.add_transaction(
                "income", "Salary", "Unknown", "100", "desc"
            )

    def test_add_transaction_invalid_amount_raises(
        self, transaction_service, setup_accounts_and_categories
    ):
        with pytest.raises(InvalidInputError):
            transaction_service.add_transaction(
                "income", "Salary", "Checking", "-10", "desc"
            )


class TestGetTransaction:
    def test_get_existing_transaction(
        self, transaction_service, setup_accounts_and_categories
    ):
        acc1, _ = setup_accounts_and_categories
        trans = transaction_service.add_transaction(
            "income", "Salary", "Checking", "100", "desc"
        )
        assert transaction_service.get_transaction(trans.transaction_id) == trans

    def test_get_nonexistent_transaction_returns_none(self, transaction_service):
        assert transaction_service.get_transaction(999) is None
        assert transaction_service.get_transaction(-5) is None


class TestGetAllTransactions:
    def test_sorted_transactions_descending_and_ascending(
        self, transaction_service, setup_accounts_and_categories
    ):
        acc1, _ = setup_accounts_and_categories
        now = datetime.now()
        t1 = transaction_service.add_transaction(
            "income", "Salary", "Checking", "100", "t1"
        )
        t2 = transaction_service.add_transaction(
            "income", "Salary", "Checking", "50", "t2"
        )
        t1.datetime = now
        t2.datetime = now + timedelta(seconds=10)

        sorted_desc = transaction_service.get_all_transactions()
        assert sorted_desc[0] == t2
        assert sorted_desc[1] == t1

        sorted_asc = transaction_service.get_all_transactions(
            reverse_chronological=False
        )
        assert sorted_asc[0] == t1
        assert sorted_asc[1] == t2


class TestEditTransaction:
    def test_edit_all_fields(self, transaction_service, setup_accounts_and_categories):
        acc1, acc2 = setup_accounts_and_categories
        trans = transaction_service.add_transaction(
            "income", "Salary", "Checking", "100", "desc"
        )
        edited = transaction_service.edit_transaction(
            trans.transaction_id, "expense", "food", "Savings", "50.00", "edited"
        )
        assert edited.transaction_type == TransactionType.EXPENSE
        assert edited.category == "Food"
        assert edited.account == acc2
        assert edited.amount == Decimal("50.00") or edited.amount == "50.00"
        assert edited.description == "edited"
        transaction_service.money_manager.save.assert_called()

    def test_edit_partial_fields(
        self, transaction_service, setup_accounts_and_categories
    ):
        acc1, _ = setup_accounts_and_categories
        trans = transaction_service.add_transaction(
            "income", "Salary", "Checking", "100", "desc"
        )
        edited = transaction_service.edit_transaction(
            trans.transaction_id, "", "", "", "200", ""
        )
        assert edited.amount == Decimal("200") or edited.amount == "200"
        assert edited.description == ""


class TestDeleteTransaction:
    def test_delete_existing_transaction(
        self, transaction_service, setup_accounts_and_categories
    ):
        acc1, _ = setup_accounts_and_categories
        trans = transaction_service.add_transaction(
            "income", "Salary", "Checking", "100", "desc"
        )
        result = transaction_service.delete_transaction(trans.transaction_id)
        assert result is True
        assert trans not in transaction_service.transactions
        assert trans not in acc1.transactions
        transaction_service.money_manager.save.assert_called()

    def test_delete_nonexistent_transaction_raises(self, transaction_service):
        with pytest.raises(NotFoundError):
            transaction_service.delete_transaction(999)



