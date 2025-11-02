# Money Tracker

A personal finance management application built with Python that helps track income and expenses, manage accounts and categories, and generate insightful financial summaries.

- [Money Tracker](#money-tracker)
  - [Features](#features)
    - [Transaction Management](#transaction-management)
    - [Account Management](#account-management)
    - [Category Management](#category-management)
    - [Filtering \& Analysis](#filtering--analysis)
    - [Summaries](#summaries)
    - [Data Management](#data-management)
  - [Installation](#installation)
    - [Step 1: Clone or Download the Repository](#step-1-clone-or-download-the-repository)
    - [Step 2: Install Dependencies](#step-2-install-dependencies)
  - [Usage](#usage)
    - [Running the Application](#running-the-application)
    - [Main Menu](#main-menu)
    - [Getting Started](#getting-started)

## Features

### Transaction Management

-   **Add Transactions**: Record income and expenses with details including amount, date, category, account, and optional notes
-   **Edit Transactions**: Modify existing transaction details
-   **Delete Transactions**: Remove unwanted transactions
-   **View All Transactions**: Display all transactions in a formatted table

### Account Management

-   **Create Accounts**: Set up multiple accounts with initial balances
-   **View Accounts**: See all accounts with their current balances
-   **Edit Accounts**: Edit exisitng account name
-   **Delete Accounts**: Remove accounts

### Category Management

-   **Income Categories**: Manage income sources
-   **Expense Categories**: Organize expenses
-   **Add Categories**: Create custom categories for both income and expenses
-   **Edit Categories**: Rename existing categories
-   **Delete Categories**: Remove unused categories

### Filtering & Analysis

-   **Filter by Category**: View all transactions for a specific category
-   **Filter by Account**: See transactions from a particular account
-   **Filter by Type**: Separate income from expenses

### Summaries

-   **Daily Summary**: View total income and expenses for a specific day
-   **Weekly Summary**: Analyze your finances for any week
-   **Monthly Summary**: Get monthly financial overviews
-   **Expense Breakdown**: See expenses categorized over a date range
-   **Income Breakdown**: View income categorized over a date range

### Data Management

-   **Auto-save**: All changes are automatically saved to JSON
-   **Backup**: Create manual backups of your financial data
-   **Data Persistence**: Your data is preserved between sessions

## Installation

### Step 1: Clone or Download the Repository

```powershell
# If using Git
git clone https://github.com/ZiLin-628/FIT1045-Project.git
cd FIT1045-Project
```

### Step 2: Install Dependencies

Install all required Python packages using pip:

```powershell
pip install -r requirements.txt
```


All tests should pass successfully.

## Usage

### Running the Application

To start the Money Tracker application:

```powershell
python main.py
```

### Main Menu

Once started, you'll see the main menu with the following options:

```
--- Money Tracker Menu ---
1: Transaction
2: Account
3: Category
4: Filter Transaction
5: Show Summary
6: Backup Data
7: Quit
```

### Getting Started

1. **Set up your accounts** (Option 2):

    - Add your bank accounts, cash, credit cards, etc.
    - Set initial balances

2. **Configure categories** (Option 3):

    - Add custom income categories
    - Add custom expense categories

3. **Start tracking transactions** (Option 1):

    - Add your daily income and expenses
    - Include details like amount, date, category, and account

4. **Analyze your finance** (Options 4-5):
    - Use filtering to focus on specific categories or accounts
    - Generate summaries
