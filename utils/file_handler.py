"""File handling utilities for the Sales Analytics System.

This module focuses on reading messy sales transaction data from disk,
parsing it into Python dictionaries, cleaning common data issues, and
validating/filtering transactions based on rules provided in the assignment.

All functions are written to be readable and beginner-friendly.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Any


REQUIRED_KEYS = [
    "TransactionID",
    "Date",
    "ProductID",
    "ProductName",
    "Quantity",
    "UnitPrice",
    "CustomerID",
    "Region",
]


def read_sales_data(filename: str) -> List[str]:
    """Reads sales data from file handling encoding issues.

    Args:
        filename: Path to the input sales_data.txt file.

    Returns:
        List of raw transaction lines (strings), with header removed and empty
        lines skipped.

    Requirements (from assignment):
        - Use 'with' statement
        - Try encodings: 'utf-8', 'latin-1', 'cp1252'
        - Handle FileNotFoundError with appropriate message
        - Skip the header row
        - Remove empty lines
    """

    encodings_to_try = ["utf-8", "latin-1", "cp1252"]
    last_error: Optional[Exception] = None

    try:
        for enc in encodings_to_try:
            try:
                with open(filename, "r", encoding=enc) as f:
                    lines = f.read().splitlines()
                # If we reached here, decoding worked.
                break
            except UnicodeDecodeError as e:
                last_error = e
                lines = []
        else:
            # All encodings failed.
            raise UnicodeDecodeError(
                "unknown",
                b"",
                0,
                1,
                f"Could not decode file using {encodings_to_try}",
            )

    except FileNotFoundError:
        print(f"Error: File not found -> {filename}")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        if last_error is not None:
            print(f"Last decode error: {last_error}")
        return []

    # Remove header row if present.
    # Many datasets have header like: TransactionID|Date|...
    if lines and "TransactionID" in lines[0]:
        lines = lines[1:]

    # Remove empty lines and whitespace-only lines.
    cleaned_lines = [ln.strip() for ln in lines if ln.strip()]
    return cleaned_lines


def parse_transactions(raw_lines: List[str]) -> List[Dict[str, Any]]:
    """Parses raw lines into clean list of dictionaries.

    Data quality issues handled:
        - Pipe-delimited format
        - Commas within ProductName: removed
        - Commas inside numeric fields: removed (e.g., 1,500 -> 1500)
        - Quantity converted to int
        - UnitPrice converted to float
        - Rows with incorrect number of fields are skipped

    Args:
        raw_lines: List of raw transaction strings.

    Returns:
        List of transaction dictionaries with keys:
        ['TransactionID','Date','ProductID','ProductName','Quantity','UnitPrice','CustomerID','Region']
    """

    transactions: List[Dict[str, Any]] = []

    for line in raw_lines:
        parts = line.split("|")

        # Skip rows with incorrect number of fields.
        if len(parts) != 8:
            continue

        tid, date, pid, pname, qty, price, cid, region = parts

        # Clean commas in ProductName (e.g., Mouse,Wireless -> MouseWireless or Mouse Wireless).
        # We'll remove commas and extra spaces.
        pname_clean = pname.replace(",", " ").strip()
        pname_clean = " ".join(pname_clean.split())  # collapse multiple spaces

        # Clean commas in numeric fields.
        qty_clean = qty.replace(",", "").strip()
        price_clean = price.replace(",", "").strip()

        try:
            qty_int = int(qty_clean)
            price_float = float(price_clean)
        except ValueError:
            # If numeric conversion fails, skip the row.
            continue

        txn = {
            "TransactionID": tid.strip(),
            "Date": date.strip(),
            "ProductID": pid.strip(),
            "ProductName": pname_clean,
            "Quantity": qty_int,
            "UnitPrice": price_float,
            "CustomerID": cid.strip(),
            "Region": region.strip(),
        }
        transactions.append(txn)

    return transactions


def _transaction_amount(txn: Dict[str, Any]) -> float:
    return float(txn.get("Quantity", 0)) * float(txn.get("UnitPrice", 0.0))


def validate_and_filter(
    transactions: List[Dict[str, Any]],
    region: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> Tuple[List[Dict[str, Any]], int, Dict[str, int]]:
    """Validates transactions and applies optional filters.

    Validation Rules (from assignment):
        - Quantity must be > 0
        - UnitPrice must be > 0
        - All required fields must be present
        - TransactionID must start with 'T'
        - ProductID must start with 'P'
        - CustomerID must start with 'C'

    Filtering:
        - region: filter by specific region
        - min_amount/max_amount: filter by transaction amount (Quantity * UnitPrice)

    Also prints:
        - Available regions
        - Transaction amount range (min/max)
        - Record counts after each filter

    Returns:
        (valid_transactions, invalid_count, filter_summary)
    """

    total_input = len(transactions)

    # Display available regions and amount range to user BEFORE filtering.
    # To avoid confusing negative/zero values from invalid rows, we compute the
    # range from rows that *look* valid for amounts (qty>0 and price>0).
    regions = sorted({(t.get("Region") or "").strip() for t in transactions if t.get("Region")})

    amount_candidates = []
    for t in transactions:
        try:
            qty = int(t.get("Quantity"))
            price = float(t.get("UnitPrice"))
            if qty > 0 and price > 0:
                amount_candidates.append(qty * price)
        except Exception:
            continue

    min_amt = min(amount_candidates) if amount_candidates else 0.0
    max_amt = max(amount_candidates) if amount_candidates else 0.0

    print("[Filter Options Available]")
    print("Regions:", ", ".join(regions) if regions else "(none)")
    print(f"Amount Range: {min_amt:.2f} - {max_amt:.2f}")

    # First, validate.
    valid: List[Dict[str, Any]] = []
    invalid_count = 0

    for t in transactions:
        # Required fields present
        if not all(k in t and t[k] not in (None, "") for k in REQUIRED_KEYS):
            invalid_count += 1
            continue

        # Type/Value rules
        try:
            qty = int(t["Quantity"])
            price = float(t["UnitPrice"])
        except (ValueError, TypeError):
            invalid_count += 1
            continue

        if qty <= 0 or price <= 0:
            invalid_count += 1
            continue

        tid = str(t["TransactionID"]).strip()
        pid = str(t["ProductID"]).strip()
        cid = str(t["CustomerID"]).strip()

        if not tid.startswith("T"):
            invalid_count += 1
            continue
        if not pid.startswith("P"):
            invalid_count += 1
            continue
        if not cid.startswith("C"):
            invalid_count += 1
            continue

        valid.append(t)

    after_validation = len(valid)

    # Now apply optional filters.
    filtered_by_region = 0
    filtered_by_amount = 0

    filtered = valid

    if region:
        before = len(filtered)
        filtered = [t for t in filtered if str(t.get("Region", "")).strip().lower() == region.strip().lower()]
        filtered_by_region = before - len(filtered)
        print(f"After region filter ({region}): {len(filtered)} records")

    if min_amount is not None or max_amount is not None:
        before = len(filtered)

        def in_range(t: Dict[str, Any]) -> bool:
            amt = _transaction_amount(t)
            if min_amount is not None and amt < float(min_amount):
                return False
            if max_amount is not None and amt > float(max_amount):
                return False
            return True

        filtered = [t for t in filtered if in_range(t)]
        filtered_by_amount = before - len(filtered)
        rng_txt = f"{min_amount if min_amount is not None else '-inf'} to {max_amount if max_amount is not None else 'inf'}"
        print(f"After amount filter ({rng_txt}): {len(filtered)} records")

    summary = {
        "total_input": total_input,
        "invalid": invalid_count,
        "validated_count": after_validation,
        "filtered_by_region": filtered_by_region,
        "filtered_by_amount": filtered_by_amount,
        "final_count": len(filtered),
    }

    return filtered, invalid_count, summary
