#!/usr/bin/env python3
"""Reconcile the latest attempt for each payment transaction."""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def read_latest_events(path: Path) -> dict[str, dict]:
    """Return the latest readable event for every transaction ID."""
    latest: dict[str, dict] = {}

    with path.open(encoding="utf-8") as payments:
        for line in payments:
            try:
                event = json.loads(line)
            except (json.JSONDecodeError, TypeError):
                continue

            if not isinstance(event, dict) or not event.get("txn_id"):
                continue

            txn_id = event["txn_id"]
            timestamp = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
            previous = latest.get(txn_id)

            if previous is None or timestamp > previous["timestamp"]:
                latest[txn_id] = {"event": event, "timestamp": timestamp}

    return latest


def parse_amount(value: object) -> Decimal:
    """Parse numeric amounts and comma-formatted amount strings exactly."""
    return Decimal(str(value).replace(",", ""))


def main() -> None:
    latest = read_latest_events(BASE_DIR / "payments.jsonl")
    successful = [
        item["event"]
        for item in latest.values()
        if item["event"]["status"] == "success"
    ]
    total = sum((parse_amount(event["amount"]) for event in successful), Decimal(0))
    count = len(successful)

    expected = int((BASE_DIR / "expected.txt").read_text(encoding="utf-8").strip())

    if count != expected:
        print(f"Check failed: counted {count} successful payments, expected {expected}.")
        print("Something in the data isn't being handled the way the README describes.")
    else:
        print(f"Check passed: {count} successful payments.")
        print(f"Your code: KOYA-{round(total)}")


if __name__ == "__main__":
    main()
