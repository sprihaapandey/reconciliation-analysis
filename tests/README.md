# Reconciliation test fixtures

Each subfolder is a `transactions.csv` / `balances.csv` pair, runnable directly:

```
python3 main.py tests/<scenario>/transactions.csv tests/<scenario>/balances.csv
```

Note: `compute_discrepancy` compares each day's *net transaction total* to
that day's *reported balance* (not a running account balance), and
`flag_significant_days` only flags a date when that day's discrepancy
differs from the previous day's — a persistent, unchanged discrepancy is
not re-flagged.

## Scenarios

- **01_multiple_transactions_per_day** — several transactions land on the
  same date (including a day with three identical amounts) and must be
  summed correctly. Balances match the summed totals exactly, so any
  nonzero discrepancy here indicates the per-date summing is broken.

- **02_fully_reconciled** — one transaction per day, balances match
  exactly every day. Expect zero discrepancy and no significant days.

- **03_multiple_discrepancies** — discrepancy alternates between 0 and a
  nonzero value across seven days, producing several distinct mismatches
  and a significant-day flag on every day after the first.

- **04_persistent_discrepancy** — a $30 discrepancy appears on
  2026-04-02 and continues unchanged through 2026-04-05. Only 04-02 is
  flagged as significant; the later days still show the discrepancy in
  the report but aren't re-flagged since nothing changed day-over-day.

- **05_self_correction** — a $40 discrepancy appears on 2026-05-02,
  persists through 2026-05-03, then resolves back to a match on
  2026-05-04 (flagged as a decrease) and stays matched on 2026-05-05.
