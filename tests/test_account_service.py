# test/test_account_service.py

from unittest.mock import MagicMock

import pytest

from app.exception import AlreadyExistsError, InvalidInputError, NotFoundError
from app.models import Account
from app.services.account_service import AccountService
from app.utility import format_amount


class FakeMoneyManager:
    def __init__(self) -> None:
        self.accounts = {}
        self.transactions = []
        self.save = MagicMock()


@pytest.fixture
def money_manager() -> FakeMoneyManager:
    return FakeMoneyManager()


@pytest.fixture
def account_service(money_manager) -> AccountService:
    return AccountService(money_manager)


class TestAddAccount:

    @pytest.mark.parametrize(
        "name, initial_balance",
        [
            ("Cash", "100.00"),
            ("Cash", "100  "),
            ("saVINgs", "102.999999"),
            ("     Credit Card    ", "250.19"),
            ("cAsH", "0.01"),
            ("my acc", "0.00"),
        ],
    )
    def test_add_account_success(self, account_service, name, initial_balance):
        account = account_service.add_account(name, initial_balance)

        assert account.account_name == name.strip().capitalize()
        assert account.balance == format_amount(initial_balance)
        assert account_service.accounts[account.account_name] == account
        account_service.money_manager.save.assert_called_once()

    def test_add_account_empty_name(self, account_service):
        with pytest.raises(InvalidInputError):
            account_service.add_account("", "100.00")

    def test_add_account_negative_balance(self, account_service):
        with pytest.raises(InvalidInputError):
            account_service.add_account("Checking", "-50.00")

    def test_add_account_duplicate_name(self, account_service):
        account_service.add_account("Checking", "100.00")
        with pytest.raises(AlreadyExistsError):
            account_service.add_account("checking", "50.00")


class TestGetAccount:

    @pytest.fixture
    def account_service_with_acc(self, money_manager):
        service = AccountService(money_manager)
        service.add_account("Checking", "100.00")
        return service

    def test_get_existing_account(self, account_service_with_acc):
        account = account_service_with_acc.get_account("Checking")
        assert account is not None
        assert isinstance(account, Account)
        assert account.account_name == "Checking"
        assert account.balance == format_amount("100.00")

    def test_get_nonexistent_account(self, account_service_with_acc):
        account = account_service_with_acc.get_account("Savings")
        assert account is None

    @pytest.mark.parametrize(
        "input_name, expected_name",
        [
            ("  checking  ", "Checking"),  # extra spaces trimmed
            ("cHeCkInG", "Checking"),  # different capitalization
        ],
    )
    def test_get_account_normalization(
        self, account_service_with_acc, input_name, expected_name
    ):
        account = account_service_with_acc.get_account(input_name)
        assert account is not None
        assert account.account_name == expected_name

    def test_get_account_empty_name(self, account_service_with_acc):
        with pytest.raises(InvalidInputError):
            account_service_with_acc.get_account("")


class TestGetAllAccount:

    def test_get_all_accounts_empty(self, account_service):
        # No accounts added yet
        accounts = account_service.get_all_accounts()
        assert isinstance(accounts, list)
        assert len(accounts) == 0

    def test_get_all_accounts_multiple(self, account_service):
        # Add multiple accounts
        account_service.add_account("Checking", "100.00")
        account_service.add_account("Savings", "200.00")
        account_service.add_account("Investment", "500.50")

        accounts = account_service.get_all_accounts()
        names = [acc.account_name for acc in accounts]

        assert len(accounts) == 3
        # Ensure all accounts are included
        assert "Checking" in names
        assert "Savings" in names
        assert "Investment" in names

    def test_get_all_accounts_case_insensitivity(self, account_service):
        # Add accounts with different capitalization
        account_service.add_account("checking", "100.00")
        account_service.add_account("SAVINGS", "200.00")

        accounts = account_service.get_all_accounts()
        names = [acc.account_name for acc in accounts]

        # AccountService normalizes names on addition
        assert "Checking" in names
        assert "Savings" in names
        assert len(accounts) == 2

    def test_get_all_accounts_after_deletion(self, account_service):
        # Add accounts
        account_service.add_account("Checking", "100.00")
        account_service.add_account("Savings", "200.00")
        account_service.add_account("Investment", "500.50")

        # Delete one account
        account_service.delete_account("Savings")

        accounts = account_service.get_all_accounts()
        names = [acc.account_name for acc in accounts]

        assert "Savings" not in names
        assert "Checking" in names
        assert "Investment" in names
        assert len(accounts) == 2


class TestEditAccountName:
    @pytest.fixture
    def populated_service(self, account_service) -> AccountService:
        account_service.accounts = {
            "Checking": Account("Checking", "100"),
            "Savings": Account("Savings", "200"),
        }
        return account_service

    def test_edit_success(self, populated_service):
        acc = populated_service.edit_account_name("Checking", "Budget")
        assert acc.account_name == "Budget"
        assert "Budget" in populated_service.accounts
        assert "Checking" not in populated_service.accounts
        populated_service.money_manager.save.assert_called_once()

    def test_edit_same_name_ok(self, populated_service):
        acc = populated_service.edit_account_name("Savings", "Savings")
        assert acc.account_name == "Savings"
        assert "Savings" in populated_service.accounts

    def test_edit_trimmed_names(self, populated_service):
        acc = populated_service.edit_account_name("  checking ", "  budget  ")
        assert "Budget" in populated_service.accounts
        assert acc.account_name == "Budget"

    @pytest.mark.parametrize(
        "old,new,exc",
        [
            ("", "Budget", InvalidInputError),
            ("Checking", "", InvalidInputError),
        ],
    )
    def test_invalid_names(self, populated_service, old, new, exc):
        with pytest.raises(exc):
            populated_service.edit_account_name(old, new)

    def test_old_not_found(self, populated_service):
        with pytest.raises(NotFoundError):
            populated_service.edit_account_name("Missing", "Budget")

    def test_new_name_exists(self, populated_service):
        with pytest.raises(AlreadyExistsError):
            populated_service.edit_account_name("Checking", "Savings")

    def test_object_reused(self, populated_service):
        old_obj = populated_service.accounts["Checking"]
        new_obj = populated_service.edit_account_name("Checking", "Budget")
        assert old_obj is new_obj
        assert "Budget" in populated_service.accounts


class TestDeleteAccount:
    def test_delete_existing_account(self, account_service):
        account_service.add_account("Checking", "100.00")
        result = account_service.delete_account("Checking")
        assert result is True
        assert "Checking" not in account_service.accounts
        account_service.money_manager.save.assert_called()

    def test_delete_account_with_transactions(self, account_service):
        # Add account
        account = account_service.add_account("Checking", "100.00")

        # Add related transactions
        account_service.money_manager.transactions = [
            MagicMock(account=account),
            MagicMock(account=account),
            MagicMock(account=MagicMock(account_name="Other")),
        ]

        account_service.delete_account("Checking")

        # All transactions linked to "Checking" should be removed
        for t in account_service.money_manager.transactions:
            assert getattr(t.account, "account_name") != "Checking"

    def test_delete_last_account(self, account_service):
        account_service.add_account("OnlyAccount", "50.00")
        result = account_service.delete_account("OnlyAccount")
        assert result is True
        assert account_service.get_all_accounts() == []

    @pytest.mark.parametrize(
        "input_name, expected_name",
        [
            ("  checking  ", "Checking"),  # extra spaces trimmed
            ("cHeCkInG", "Checking"),  # different capitalization
        ],
    )
    def test_delete_account_name_normalization(
        self, account_service, input_name, expected_name
    ):
        account_service.add_account("Checking", "100.00")
        result = account_service.delete_account(input_name)
        assert result is True
        assert expected_name not in account_service.accounts

    def test_delete_nonexistent_account_raises(self, account_service):
        with pytest.raises(NotFoundError):
            account_service.delete_account("MissingAccount")

    def test_delete_empty_account_name_raises(self, account_service):
        with pytest.raises(InvalidInputError):
            account_service.delete_account("")


