#This is the main file which reads the input file and generates analytics
import csv
import sys

from reconcile import (
    compute_expected_balance,
    compute_discrepancy,
    flag_significant_days,
    summarize_day,
)


def read_transactions(path):
    """Reads a CSV of individual transactions (date, amount) and sums them per date."""
    transactions = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row["date"]
            amount = float(row["amount"])
            transactions[date] = transactions.get(date, 0) + amount
    return transactions


def read_actual_balances(path):
    """Reads a CSV of reported balances (date, balance) into a dict."""
    actual_balance = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            actual_balance[row["date"]] = float(row["balance"])
    return actual_balance


def main():
    transactions_path = sys.argv[1] if len(sys.argv) > 1 else "/Users/sprihapandey/Collective-take-home-reconciliation/tests/05_self_correction/transactions.csv"
    balances_path = sys.argv[2] if len(sys.argv) > 2 else "/Users/sprihapandey/Collective-take-home-reconciliation/tests/05_self_correction/balances.csv"

    transactions = read_transactions(transactions_path)
    actual_balance = read_actual_balances(balances_path)
    expected_balance = compute_expected_balance(transactions)
    print("Expected Balance:", expected_balance)
    cumulative_discrepancy = compute_discrepancy(expected_balance, actual_balance)
    significant_days = flag_significant_days(cumulative_discrepancy)

    print("Reconciliation Report")
    print("=" * 40)
    for date in sorted(cumulative_discrepancy):
        print(f"{date}: discrepancy = {cumulative_discrepancy[date]:.2f}")

    print()
    print("Significant Changes")
    print("=" * 40)
    if not significant_days:
        print("No significant discrepancies found.")
    else:
        for date in sorted(significant_days):
            print(summarize_day(date, significant_days))

    total_discrepancy = list(cumulative_discrepancy.values())[-1]
    print()
    print(f"Total cumulative discrepancy: {total_discrepancy:.2f}")


if __name__ == "__main__":
    main()
