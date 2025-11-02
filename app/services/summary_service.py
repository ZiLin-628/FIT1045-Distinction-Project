# summary_service.py

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from app.models import TransactionType

if TYPE_CHECKING:
    from app.money_manager import MoneyManager


class SummaryService:
    """
    Service class responsible for generating financial summaries from transactions.
    """

    def __init__(self, money_manager: MoneyManager) -> None:
        """
        Initialize SummaryService with a MoneyManager instance.

        Args:
            money_manager (MoneyManager): The parent MoneyManager object containing
                transactions, accounts, and categories.
        """
        self.money_manager = money_manager
        self.accounts = money_manager.accounts
        self.transactions = money_manager.transactions
        self.income_categories = money_manager.income_categories
        self.expense_categories = money_manager.expense_categories

    def get_daily_summary(self, date: datetime):
        """
        Generate a financial summary for a specific day.

        Args:
            date (datetime): The date for which to generate the summary.

        Returns:
            dict: Summary containing total income, expenses, net balance, and count of transactions.
        """

        # Set the day start and end boundaries
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Filter transactions happen on this day
        transactions = [
            t for t in self.transactions if start_of_day <= t.datetime <= end_of_day
        ]

        # Initialize amount
        total_income = Decimal("0.00")
        total_expense = Decimal("0.00")

        # Handling summary
        for trans in transactions:
            if trans.transaction_type == TransactionType.INCOME:
                total_income += trans.amount
            else:
                total_expense += trans.amount

        net = total_income - total_expense

        return {
            "date": date.strftime("%d-%m-%Y"),
            "total_income": total_income,
            "total_expense": total_expense,
            "net": net,
            "transaction_count": len(transactions),
        }

    def get_weekly_summary(self, date: datetime):
        """
        Generate a financial summary for the week containing the given date.

        Args:
            date (datetime): Any date within the desired week.

        Returns:
            dict: Summary of income, expenses, and net balance for that week.
        """

        # Get the ISO calendar (year, week_number, weekday)
        # weekday: 1=Monday, 7=Sunday
        iso_year, iso_week, iso_weekday = date.isocalendar()

        # Calculate Monday of this week (start of week)
        week_start = date - timedelta(days=iso_weekday - 1)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        # Calculate Sunday of this week (end of week)
        week_end = week_start + timedelta(days=6)
        week_end = week_end.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Filter transactions for this week
        week_transactions = [
            t for t in self.transactions if week_start <= t.datetime <= week_end
        ]

        # Calculate totals
        total_income = Decimal("0.00")
        total_expense = Decimal("0.00")

        for trans in week_transactions:
            if trans.transaction_type == TransactionType.INCOME:
                total_income += trans.amount
            else:
                total_expense += trans.amount

        net = total_income - total_expense

        return {
            "week_start": week_start.strftime("%d-%m-%Y"),
            "week_end": week_end.strftime("%d-%m-%Y"),
            "total_income": total_income,
            "total_expense": total_expense,
            "net": net,
            "transaction_count": len(week_transactions),
        }

    def get_monthly_summary(self, year: int, month: int) -> dict:
        """
        Generate a financial summary for a given month and year.

        Args:
            year (int): The year to summarize.
            month (int): The month number (1–12).

        Returns:
            dict: Summary with totals for income, expenses, net balance, and transaction count.
                  Returns an empty dict if inputs are invalid.
        """

        # Validate month and year
        if month < 1 or month > 12 or year <= 0:
            return {}

        # Get month name
        month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        month_name = month_names[month - 1]

        # Calculate first day of month
        month_start = datetime(year, month, 1, 0, 0, 0)

        # Calculate last day of month
        # Get first day of next month, then subtract one day
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)

        month_end = next_month - timedelta(days=1)
        month_end = month_end.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Filter transactions for this month
        month_transactions = [
            t for t in self.transactions if month_start <= t.datetime <= month_end
        ]

        # Calculate totals
        total_income = Decimal("0.00")
        total_expense = Decimal("0.00")

        for trans in month_transactions:
            if trans.transaction_type == TransactionType.INCOME:
                total_income += trans.amount
            else:
                total_expense += trans.amount

        net = total_income - total_expense

        return {
            "month": month_name,
            "year": year,
            "total_income": total_income,
            "total_expense": total_expense,
            "net": net,
            "transaction_count": len(month_transactions),
        }

    def get_expenses_by_category(
        self, start_date: datetime, end_date: datetime
    ) -> dict:
        """
        Summarize total expenses grouped by category within a date range.

        Args:
            start_date (datetime): Start date of range.
            end_date (datetime): End date of range.

        Returns:
            dict: Mapping of category name -> total expense amount.
        """

        # Validate dates
        if start_date > end_date:
            return {}

        # Set time boundaries
        start_of_day = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Filter expense transactions for this date range
        expense_transactions = [
            t
            for t in self.transactions
            if start_of_day <= t.datetime <= end_of_day
            and t.transaction_type == TransactionType.EXPENSE
        ]

        # Group by category
        expenses_by_category = {}

        for trans in expense_transactions:
            category = trans.category
            if category not in expenses_by_category:
                expenses_by_category[category] = Decimal("0.00")
            expenses_by_category[category] += trans.amount

        return expenses_by_category

    def get_income_by_category(self, start_date: datetime, end_date: datetime) -> dict:
        """
        Summarize total income grouped by category within a date range.

        Args:
            start_date (datetime): Start date of range.
            end_date (datetime): End date of range.

        Returns:
            dict: Mapping of category name -> total income amount.
        """

        # Validate dates
        if start_date > end_date:
            return {}

        # Set time boundaries
        start_of_day = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Filter income transactions for this date range
        income_transactions = [
            t
            for t in self.transactions
            if start_of_day <= t.datetime <= end_of_day
            and t.transaction_type == TransactionType.INCOME
        ]

        # Group by category
        income_by_category = {}

        for trans in income_transactions:
            category = trans.category
            if category not in income_by_category:
                income_by_category[category] = Decimal("0.00")
            income_by_category[category] += trans.amount

        return income_by_category
