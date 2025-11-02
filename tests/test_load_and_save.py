# test/test_load_and_save_service.py

import json
from datetime import datetime
from decimal import Decimal

import pytest

from app.models import Account, Transaction, TransactionType
from app.money_manager import MoneyManager


@pytest.fixture
def money_manager(tmp_path):
    """Return a MoneyManager that uses a temporary JSON file."""
    data_path = tmp_path / "data.json"
    manager = MoneyManager(data_path=str(data_path))

    manager.accounts.clear()
    manager.transactions.clear()

    return manager, data_path


def test_save_and_load_data(money_manager):
    manager, data_path = money_manager

    # Create and insert account + transaction
    acc = Account(account_name="Wallet", balance="500.00")
    manager.accounts[acc.account_name] = acc

    t = Transaction(
        transaction_id=1,
        datetime=datetime(2025, 1, 1, 12, 0, 0),
        transaction_type=TransactionType.EXPENSE,
        category="Food",
        account=acc,
        amount="50.00",
        description="Lunch",
    )
    manager.transactions.append(t)
    acc.add_transaction(t)

    # Save to JSON file
    manager._save_data()

    # Verify file content 
    with open(data_path, "r") as f:
        data = json.load(f)

    assert "accounts" in data
    assert "transactions" in data

    assert len(data["accounts"]) == 1
    assert len(data["transactions"]) == 1
    assert data["accounts"][0]["account_name"] == "Wallet"
    assert data["transactions"][0]["category"] == "Food"
    assert data["transactions"][0]["transaction_type"] == "expense"

    # Load into a new manager
    new_manager = MoneyManager(data_path=str(data_path))

    # Verify data was restored correctly
    assert "Wallet" in new_manager.accounts
    loaded_acc = new_manager.accounts["Wallet"]
    assert Decimal(loaded_acc.balance) == Decimal("500.00")

    assert len(new_manager.transactions) == 1
    loaded_trans = new_manager.transactions[0]

    assert loaded_trans.transaction_id == 1
    assert loaded_trans.category == "Food"
    assert loaded_trans.amount == Decimal("50.00")
    assert loaded_trans.transaction_type == TransactionType.EXPENSE
    assert loaded_trans.account.account_name == "Wallet"
