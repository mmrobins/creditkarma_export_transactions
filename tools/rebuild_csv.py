#!/usr/bin/env python3
"""Rebuild the Mint-format CSV from the raw JSON dump, with correct quoting.

fetch_credit_karma_transactions writes its CSV by interpolating values straight
into a quoted string, so any field containing a newline or a double quote
corrupts the row. The JSON dump is one raw GraphQL transaction object per line
(JSONL) and is unaffected, so it is the reliable source.

This also falls back to the raw description when a transaction has no merchant,
since the original mapping leaves the Mint "Description" (payee) column empty
for roughly 40% of rows, which most importers treat as a missing payee.

Usage:
    tools/rebuild_csv.py [in.json] [out.csv]
"""
import csv
import json
import re
import sys

MINT_HEADER = [
    "Date", "Description", "Original Description", "Amount",
    "Transaction Type", "Category", "Account Name", "Labels", "Notes",
]


def flatten(value):
    """Collapse whitespace so no field can contain a newline."""
    return re.sub(r"\s+", " ", value).strip() if isinstance(value, str) else ""


def nested(record, key, field="name"):
    return flatten((record.get(key) or {}).get(field))


def main(src="creditkarma_transactions.json", dst="creditkarma_transactions_clean.csv"):
    with open(src) as fh:
        records = [json.loads(line) for line in fh if line.strip()]

    fellback = 0
    with open(dst, "w", newline="") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_ALL)
        writer.writerow(MINT_HEADER)
        for record in records:
            description = flatten(record.get("description"))
            payee = nested(record, "merchant")
            if not payee:
                payee = description
                fellback += 1
            value = (record.get("amount") or {}).get("value")
            writer.writerow([
                record.get("date", ""),
                payee,
                description,
                f"{abs(float(value)):.2f}" if value is not None else "",
                "debit" if (value is not None and value < 0) else "credit",
                nested(record, "category"),
                nested(record, "account"),
                "", "",
            ])

    print(f"{dst}: {len(records)} rows "
          f"({fellback} used the description as payee)")


if __name__ == "__main__":
    main(*sys.argv[1:3])
