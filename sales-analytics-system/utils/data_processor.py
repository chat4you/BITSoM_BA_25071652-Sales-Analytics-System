"""Data processing and analytics functions.

This module contains pure functions that compute summary statistics from the
cleaned sales transaction data.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Any


def calculate_total_revenue(transactions: List[Dict[str, Any]]) -> float:
    """Calculates total revenue from all transactions.

    Revenue per transaction = Quantity * UnitPrice

    Returns:
        float: total revenue
    """
    total = 0.0
    for t in transactions:
        total += float(t["Quantity"]) * float(t["UnitPrice"])
    return total


def region_wise_sales(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Analyzes sales by region.

    Returns dict of region -> stats:
        {
          'North': {'total_sales': 450000.0, 'transaction_count': 15, 'percentage': 29.13},
          ...
        }

    Output is sorted by total_sales descending (insertion order for Python 3.7+).
    """

    region_totals: Dict[str, float] = {}
    region_counts: Dict[str, int] = {}

    for t in transactions:
        reg = str(t.get("Region", "")).strip()
        amt = float(t["Quantity"]) * float(t["UnitPrice"])
        region_totals[reg] = region_totals.get(reg, 0.0) + amt
        region_counts[reg] = region_counts.get(reg, 0) + 1

    overall_total = sum(region_totals.values()) or 1.0

    rows = []
    for reg, total_sales in region_totals.items():
        pct = (total_sales / overall_total) * 100
        rows.append((reg, total_sales, region_counts.get(reg, 0), pct))

    rows.sort(key=lambda x: x[1], reverse=True)

    result: Dict[str, Dict[str, float]] = {}
    for reg, total_sales, count, pct in rows:
        result[reg] = {
            "total_sales": float(total_sales),
            "transaction_count": int(count),
            "percentage": round(float(pct), 2),
        }

    return result


def top_selling_products(transactions: List[Dict[str, Any]], n: int = 5) -> List[Tuple[str, int, float]]:
    """Finds top n products by total quantity sold.

    Returns:
        List of tuples: (ProductName, TotalQuantity, TotalRevenue)
    """

    agg: Dict[str, Dict[str, float]] = {}

    for t in transactions:
        name = str(t.get("ProductName", "")).strip()
        qty = int(t["Quantity"])
        rev = float(t["Quantity"]) * float(t["UnitPrice"])

        if name not in agg:
            agg[name] = {"qty": 0, "rev": 0.0}
        agg[name]["qty"] += qty
        agg[name]["rev"] += rev

    items = [(name, int(vals["qty"]), float(vals["rev"])) for name, vals in agg.items()]
    items.sort(key=lambda x: x[1], reverse=True)
    return items[:n]


def customer_analysis(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Analyzes customer purchase patterns.

    Returns dict sorted by total_spent descending (insertion order).
    """

    stats: Dict[str, Dict[str, Any]] = {}

    for t in transactions:
        cid = str(t.get("CustomerID", "")).strip()
        amt = float(t["Quantity"]) * float(t["UnitPrice"])
        pname = str(t.get("ProductName", "")).strip()

        if cid not in stats:
            stats[cid] = {
                "total_spent": 0.0,
                "purchase_count": 0,
                "products_bought": set(),
            }

        stats[cid]["total_spent"] += amt
        stats[cid]["purchase_count"] += 1
        stats[cid]["products_bought"].add(pname)

    # Convert sets -> sorted lists and compute avg
    rows = []
    for cid, s in stats.items():
        total = float(s["total_spent"])
        count = int(s["purchase_count"]) or 1
        avg = total / count
        products = sorted(list(s["products_bought"]))
        rows.append((cid, total, count, avg, products))

    rows.sort(key=lambda x: x[1], reverse=True)

    result: Dict[str, Dict[str, Any]] = {}
    for cid, total, count, avg, products in rows:
        result[cid] = {
            "total_spent": round(total, 2),
            "purchase_count": count,
            "avg_order_value": round(avg, 2),
            "products_bought": products,
        }
    return result


def daily_sales_trend(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Analyzes sales trends by date (chronologically sorted).

    Output:
        {
          '2024-12-01': {'revenue': ..., 'transaction_count': ..., 'unique_customers': ...},
          ...
        }
    """

    day_stats: Dict[str, Dict[str, Any]] = {}

    for t in transactions:
        d = str(t.get("Date", "")).strip()
        amt = float(t["Quantity"]) * float(t["UnitPrice"])
        cid = str(t.get("CustomerID", "")).strip()

        if d not in day_stats:
            day_stats[d] = {
                "revenue": 0.0,
                "transaction_count": 0,
                "customers": set(),
            }

        day_stats[d]["revenue"] += amt
        day_stats[d]["transaction_count"] += 1
        day_stats[d]["customers"].add(cid)

    # Sort by date string (YYYY-MM-DD sorts correctly lexicographically)
    result: Dict[str, Dict[str, Any]] = {}
    for d in sorted(day_stats.keys()):
        result[d] = {
            "revenue": round(float(day_stats[d]["revenue"]), 2),
            "transaction_count": int(day_stats[d]["transaction_count"]),
            "unique_customers": len(day_stats[d]["customers"]),
        }
    return result


def find_peak_sales_day(transactions: List[Dict[str, Any]]) -> Tuple[str, float, int]:
    """Identifies the date with highest revenue.

    Returns:
        (date, revenue, transaction_count)
    """

    trend = daily_sales_trend(transactions)
    if not trend:
        return ("", 0.0, 0)

    peak_date = max(trend.keys(), key=lambda d: trend[d]["revenue"])
    return (peak_date, float(trend[peak_date]["revenue"]), int(trend[peak_date]["transaction_count"]))


def low_performing_products(transactions: List[Dict[str, Any]], threshold: int = 10) -> List[Tuple[str, int, float]]:
    """Identifies products with total quantity < threshold.

    Returns list of (ProductName, TotalQuantity, TotalRevenue), sorted by TotalQuantity ascending.
    """

    agg: Dict[str, Dict[str, float]] = {}

    for t in transactions:
        name = str(t.get("ProductName", "")).strip()
        qty = int(t["Quantity"])
        rev = float(t["Quantity"]) * float(t["UnitPrice"])

        if name not in agg:
            agg[name] = {"qty": 0, "rev": 0.0}
        agg[name]["qty"] += qty
        agg[name]["rev"] += rev

    lows = [(name, int(v["qty"]), float(v["rev"])) for name, v in agg.items() if int(v["qty"]) < threshold]
    lows.sort(key=lambda x: x[1])
    return lows
