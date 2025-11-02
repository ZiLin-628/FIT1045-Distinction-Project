# test/test_category_service.py

from unittest.mock import MagicMock

import pytest

from app.exception import (AlreadyExistsError, CategoryInUseError,
                           InvalidInputError, NotFoundError)
from app.models import TransactionType
from app.services.category_service import CategoryService


class FakeMoneyManager:
    def __init__(self):
        self.income_categories = []
        self.expense_categories = []
        self.transactions = []
        self.save = MagicMock()


@pytest.fixture
def money_manager() -> FakeMoneyManager:
    return FakeMoneyManager()


@pytest.fixture
def category_service(money_manager):
    return CategoryService(money_manager)


class TestGetCategories:
    def test_get_income_categories(self, category_service):
        category_service.money_manager.income_categories.extend(["Salary", "Bonus"])
        result = category_service.get_categories(TransactionType.INCOME)
        assert result == ["Salary", "Bonus"]

    def test_get_expense_categories(self, category_service):
        category_service.money_manager.expense_categories.extend(["Food", "Rent"])
        result = category_service.get_categories(TransactionType.EXPENSE)
        assert result == ["Food", "Rent"]

    def test_get_categories_empty(self, category_service):
        assert category_service.get_categories(TransactionType.INCOME) == []
        assert category_service.get_categories(TransactionType.EXPENSE) == []


class TestGetAllCategories:
    def test_get_all_categories(self, category_service):
        category_service.money_manager.income_categories.extend(["Salary"])
        category_service.money_manager.expense_categories.extend(["Food"])
        result = category_service.get_all_categories()
        assert result == ["Salary", "Food"]

    def test_get_all_categories_empty(self, category_service):
        assert category_service.get_all_categories() == []


class TestIsValidCategory:
    def test_category_exists(self, category_service):
        category_service.money_manager.income_categories.append("Salary")
        assert (
            category_service.is_valid_category("Salary", TransactionType.INCOME) is True
        )

    def test_category_not_exists(self, category_service):
        assert (
            category_service.is_valid_category("Bonus", TransactionType.INCOME) is False
        )

    def test_category_with_spaces(self, category_service):
        category_service.money_manager.income_categories.append("Salary")
        # Extra spaces not trimmed
        assert (
            category_service.is_valid_category("  Salary  ", TransactionType.INCOME)
            is False
        )

    def test_category_case_sensitivity(self, category_service):
        category_service.money_manager.income_categories.append("Salary")
        assert (
            category_service.is_valid_category("salary", TransactionType.INCOME)
            is False
        )


class TestAddCategory:
    def test_add_income_category_success(self, category_service):
        category_service.add_category("Salary", "income")
        assert "Salary" in category_service.money_manager.income_categories
        category_service.money_manager.save.assert_called_once()

    def test_add_expense_category_success(self, category_service):
        category_service.add_category("Food", "expense")
        assert "Food" in category_service.money_manager.expense_categories
        category_service.money_manager.save.assert_called_once()

    def test_add_category_with_spaces_and_mixed_case(self, category_service):
        category_service.add_category("  sAlAry  ", "  INCOME ")
        assert "Salary" in category_service.money_manager.income_categories

    def test_add_category_long_name(self, category_service):
        long_name = "A" * 1000
        category_service.add_category(long_name, "income")
        assert (
            long_name.capitalize() in category_service.money_manager.income_categories
        )

    def test_add_category_empty_raises(self, category_service):
        with pytest.raises(InvalidInputError):
            category_service.add_category("", "income")

    def test_add_category_invalid_transaction_type_raises(self, category_service):
        with pytest.raises(InvalidInputError):
            category_service.add_category("Salary", "invalid_type")

    def test_add_category_already_exists_raises(self, category_service):
        category_service.add_category("Salary", "income")
        with pytest.raises(AlreadyExistsError):
            category_service.add_category("salary", "income")


class TestEditCategory:
    def test_edit_category_success(self, category_service):
        category_service.add_category("Salary", "income")
        # mock transaction
        trans = MagicMock(category="Salary", transaction_type=TransactionType.INCOME)
        category_service.money_manager.transactions.append(trans)

        category_service.edit_category("Salary", "Bonus", "income")
        assert "Bonus" in category_service.money_manager.income_categories
        assert "Salary" not in category_service.money_manager.income_categories
        # transaction updated
        assert trans.category == "Bonus"
        category_service.money_manager.save.assert_called()

    def test_edit_category_same_name_allowed(self, category_service):
        category_service.add_category("Salary", "income")
        category_service.edit_category("Salary", "Salary", "income")
        assert "Salary" in category_service.money_manager.income_categories

    def test_edit_category_trim_and_capitalize(self, category_service):
        category_service.add_category("Salary", "income")
        category_service.edit_category("Salary", "  bonus  ", "  INCOME ")
        assert "Bonus" in category_service.money_manager.income_categories

    def test_edit_category_empty_new_name_raises(self, category_service):
        category_service.add_category("Salary", "income")
        with pytest.raises(InvalidInputError):
            category_service.edit_category("Salary", "", "income")

    def test_edit_category_invalid_transaction_type_raises(self, category_service):
        category_service.add_category("Salary", "income")
        with pytest.raises(InvalidInputError):
            category_service.edit_category("Salary", "Bonus", "invalid")

    def test_edit_category_old_category_not_found_raises(self, category_service):
        with pytest.raises(NotFoundError):
            category_service.edit_category("Missing", "New", "income")

    def test_edit_category_new_category_exists_raises(self, category_service):
        category_service.add_category("Salary", "income")
        category_service.add_category("Bonus", "income")
        with pytest.raises(AlreadyExistsError):
            category_service.edit_category("Salary", "Bonus", "income")


class TestDeleteCategory:
    def test_delete_income_category_success(self, category_service):
        category_service.add_category("Salary", "income")
        result = category_service.delete_category("Salary", "income")
        assert result is True
        assert "Salary" not in category_service.money_manager.income_categories
        category_service.money_manager.save.assert_called()

    def test_delete_expense_category_success(self, category_service):
        category_service.add_category("Food", "expense")
        result = category_service.delete_category("Food", "expense")
        assert result is True
        assert "Food" not in category_service.money_manager.expense_categories

    def test_delete_category_with_spaces_and_trim(self, category_service):
        category_service.add_category("Salary", "income")
        category_service.delete_category("  salary  ", " income ")
        assert "Salary" not in category_service.money_manager.income_categories

    def test_delete_category_used_in_transaction_raises(self, category_service):
        category_service.add_category("Salary", "income")
        trans = MagicMock(category="Salary", transaction_type=TransactionType.INCOME)
        category_service.money_manager.transactions.append(trans)
        with pytest.raises(CategoryInUseError):
            category_service.delete_category("Salary", "income")

    def test_delete_nonexistent_category_raises(self, category_service):
        with pytest.raises(NotFoundError):
            category_service.delete_category("Missing", "income")

    def test_delete_empty_category_raises(self, category_service):
        with pytest.raises(InvalidInputError):
            category_service.delete_category("", "income")

    def test_delete_invalid_transaction_type_raises(self, category_service):
        with pytest.raises(InvalidInputError):
            category_service.delete_category("Salary", "invalid")


