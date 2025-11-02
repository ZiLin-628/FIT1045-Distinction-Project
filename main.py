# main.py

from app.menu import (
    AccountOperation,
    BackupDataAction,
    CategoryOperation,
    FilterTransactionAction,
    QuitAction,
    ShowSummaryAction,
    TransactionOperation,
)
from app.money_manager import MoneyManager
from app.utility import read_integer


def choose_and_run(money_manager, actions_list):
    """
    Display the main menu and handle user interaction for the money tracker.

    Args:
        money_manager (MoneyManager): Money manager
        actions_list (list): list of action object
    """

    quit_program = False

    while not quit_program:

        print("\n--- Money Tracker Menu ---")

        # Display menu options
        for index, action in enumerate(actions_list, 1):
            print(f"{index}: {action.show_option()}")

        # Prompt user for input and validate as integer
        option: int = read_integer("Select an option: ")
        print()

        # Handle option
        if option == len(actions_list):
            quit_program = True
        elif 1 <= option < len(actions_list):
            actions_list[option - 1].run(money_manager)
        else:
            print("Invalid option. Try again")

        print()

    print("Good Bye!")


def main():
    """
    Entry point for the Money Tracker application.
    """

    money_manager = MoneyManager()

    actions_list = [
        TransactionOperation(),
        AccountOperation(),
        CategoryOperation(),
        FilterTransactionAction(),
        ShowSummaryAction(),
        BackupDataAction(),
        QuitAction(),
    ]

    choose_and_run(money_manager, actions_list)


if __name__ == "__main__":
    main()
