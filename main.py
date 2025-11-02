# main.py

from app.money_manager import MoneyManager
from app.utility import read_integer
from app.menu import (
    QuitAction,
    TransactionOperation,
    AccountOperation,
    CategoryOperation,
    FilterTransactionAction,
    ShowSummaryAction,
    BackupDataAction,
)


def choose_and_run(money_manager, actions_list):
    quit_program = False

    while not quit_program:

        print("\n--- Money Tracker Menu ---")

        for index, action in enumerate(actions_list, 1):
            print(f"{index}: {action.show_option()}")

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
