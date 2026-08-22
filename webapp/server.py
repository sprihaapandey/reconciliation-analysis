"""
Light web server for the reconciliation app.

This server does no reconciliation math itself — every computed number
comes from calling straight into ../reconcile.py.
"""
import csv
import io
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from reconcile import (
    valid_input,
    compute_expected_balance,
    compute_discrepancy,
    flag_significant_days,
    summarize_day,
)

WEBAPP_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
}


class ReconciliationError(Exception):
    pass


def parse_transactions_csv(text):
    """Reads transactions from an in-memory string."""
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or "date" not in reader.fieldnames or "amount" not in reader.fieldnames:
        raise ReconciliationError(
            'Transactions CSV must have "date" and "amount" columns.'
        )
    transactions = {}
    for row in reader:
        date = row["date"]
        if not date:
            continue
        try:
            amount = float(row["amount"])
        except (TypeError, ValueError):
            raise ReconciliationError(f'Invalid amount "{row["amount"]}" on date {date}.')
        transactions[date] = transactions.get(date, 0) + amount
    if not transactions:
        raise ReconciliationError("Transactions CSV has no rows.")
    return transactions


def parse_balances_csv(text):
    """Reads balance from an in-memory string."""
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or "date" not in reader.fieldnames or "balance" not in reader.fieldnames:
        raise ReconciliationError(
            'Balances CSV must have "date" and "balance" columns.'
        )
    actual_balance = {}
    for row in reader:
        date = row["date"]
        if not date:
            continue
        try:
            actual_balance[date] = float(row["balance"])
        except (TypeError, ValueError):
            raise ReconciliationError(f'Invalid balance "{row["balance"]}" on date {date}.')
    if not actual_balance:
        raise ReconciliationError("Balances CSV has no rows.")
    return actual_balance


def run_reconciliation(transactions_text, balances_text):
    transactions = parse_transactions_csv(transactions_text)
    actual_balance = parse_balances_csv(balances_text)

    is_valid, validation_message = valid_input(transactions, actual_balance)
    if not is_valid:
        raise ReconciliationError(validation_message.strip())

    expected_balance = compute_expected_balance(transactions)
    cumulative_discrepancy = compute_discrepancy(expected_balance, actual_balance)
    significant_days = flag_significant_days(cumulative_discrepancy)

    dates = sorted(cumulative_discrepancy.keys())
    summaries = {date: summarize_day(date, significant_days) for date in dates}

    latest_date = dates[-1]
    total_discrepancy = list(cumulative_discrepancy.values())[-1]  

    return {
        "dates": dates,
        "expected_balance": expected_balance,
        "actual_balance": actual_balance,
        "cumulative_discrepancy": cumulative_discrepancy,
        "significant_days": significant_days,
        "summaries": summaries,
        "latest_date": latest_date,
        "expected_balance_latest": expected_balance[latest_date],
        "actual_balance_latest": actual_balance.get(latest_date, 0),
        "total_discrepancy": total_discrepancy,
        "reconciled": round(total_discrepancy, 2) == 0,
        "warning": round(total_discrepancy, 2) == 0 and len(significant_days) > 0,
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        entry = STATIC_FILES.get(self.path.split("?")[0])
        if entry is None:
            self.send_response(404)
            self.end_headers()
            return
        filename, content_type = entry
        path = os.path.join(WEBAPP_DIR, filename)
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/reconcile":
            self.send_response(404)
            self.end_headers()
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            payload = json.loads(raw)
            transactions_text = payload["transactions_csv"]
            balances_text = payload["balances_csv"]
            result = run_reconciliation(transactions_text, balances_text)
            self._send_json(200, result)
        except ReconciliationError as e:
            self._send_json(400, {"error": str(e)})
        except Exception as e:
            self._send_json(400, {"error": f"Could not process files: {e}"})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 5050))
    host = "0.0.0.0" if "PORT" in os.environ else "127.0.0.1"
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Reconciliation app running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
