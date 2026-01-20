"""Report generation utilities.

Creates a comprehensive text report at output/sales_report.txt
with the exact 8 sections required by the assignment.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Any, Tuple

from utils.data_processor import (
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products,
)


def _money(value: float) -> str:
    """Format number with commas and 2 decimals."""
    return f"₹{value:,.2f}"


def _write_table(rows: List[List[str]], col_widths: List[int]) -> str:
    """Simple fixed-width table builder."""
    lines = []
    for r in rows:
        padded = [str(cell).ljust(w) for cell, w in zip(r, col_widths)]
        lines.append(" ".join(padded).rstrip())
    return "\n".join(lines)


def generate_sales_report(
    transactions: List[Dict[str, Any]],
    enriched_transactions: List[Dict[str, Any]],
    output_file: str = "output/sales_report.txt",
) -> None:
    """Generates a comprehensive formatted text report.

    Report includes 8 sections in required order.
    """

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_records = len(transactions)

    total_revenue = calculate_total_revenue(transactions)
    total_transactions = len(transactions)
    avg_order_value = (total_revenue / total_transactions) if total_transactions else 0.0

    dates = sorted({t.get("Date", "") for t in transactions if t.get("Date")})
    date_range = (dates[0], dates[-1]) if dates else ("", "")

    reg_stats = region_wise_sales(transactions)
    top_products = top_selling_products(transactions, n=5)
    cust_stats = customer_analysis(transactions)
    top_customers = list(cust_stats.items())[:5]
    trend = daily_sales_trend(transactions)
    peak_date, peak_rev, peak_count = find_peak_sales_day(transactions)
    lows = low_performing_products(transactions, threshold=10)

    # Enrichment summary
    enriched_count = sum(1 for t in enriched_transactions if t.get("API_Match") is True)
    success_rate = (enriched_count / len(enriched_transactions) * 100) if enriched_transactions else 0.0

    not_enriched_products = sorted({t.get("ProductName") for t in enriched_transactions if not t.get("API_Match")})

    # Average transaction value per region
    avg_value_per_region: List[Tuple[str, float]] = []
    for reg, s in reg_stats.items():
        cnt = int(s.get("transaction_count", 0)) or 1
        avg_val = float(s.get("total_sales", 0.0)) / cnt
        avg_value_per_region.append((reg, avg_val))
    avg_value_per_region.sort(key=lambda x: x[1], reverse=True)

    with open(output_file, "w", encoding="utf-8") as f:
        # 1. HEADER
        f.write("=" * 44 + "\n")
        f.write("SALES ANALYTICS REPORT\n")
        f.write(f"Generated: {now}\n")
        f.write(f"Records Processed: {total_records}\n")
        f.write("=" * 44 + "\n\n")

        # 2. OVERALL SUMMARY
        f.write("OVERALL SUMMARY\n")
        f.write("-" * 44 + "\n")
        f.write(f"Total Revenue: {_money(total_revenue)}\n")
        f.write(f"Total Transactions: {total_transactions}\n")
        f.write(f"Average Order Value: {_money(avg_order_value)}\n")
        f.write(f"Date Range: {date_range[0]} to {date_range[1]}\n\n")

        # 3. REGION-WISE PERFORMANCE
        f.write("REGION-WISE PERFORMANCE\n")
        f.write("-" * 44 + "\n")
        rows = [["Region", "Sales", "% of Total", "Transactions"]]
        for reg, s in reg_stats.items():
            rows.append(
                [
                    reg,
                    _money(float(s["total_sales"])),
                    f"{float(s['percentage']):.2f}%",
                    str(int(s["transaction_count"])),
                ]
            )
        col_widths = [12, 14, 10, 12]
        f.write(_write_table(rows, col_widths) + "\n\n")

        # 4. TOP 5 PRODUCTS
        f.write("TOP 5 PRODUCTS\n")
        f.write("-" * 44 + "\n")
        rows = [["Rank", "Product Name", "Qty Sold", "Revenue"]]
        for i, (name, qty, rev) in enumerate(top_products, start=1):
            rows.append([str(i), name, str(qty), _money(rev)])
        col_widths = [6, 20, 10, 14]
        f.write(_write_table(rows, col_widths) + "\n\n")

        # 5. TOP 5 CUSTOMERS
        f.write("TOP 5 CUSTOMERS\n")
        f.write("-" * 44 + "\n")
        rows = [["Rank", "Customer ID", "Total Spent", "Order Count"]]
        for i, (cid, s) in enumerate(top_customers, start=1):
            rows.append([str(i), cid, _money(float(s["total_spent"])), str(int(s["purchase_count"]))])
        col_widths = [6, 12, 14, 12]
        f.write(_write_table(rows, col_widths) + "\n\n")

        # 6. DAILY SALES TREND
        f.write("DAILY SALES TREND\n")
        f.write("-" * 44 + "\n")
        rows = [["Date", "Revenue", "Transactions", "Unique Customers"]]
        for d, s in trend.items():
            rows.append([d, _money(float(s["revenue"])), str(int(s["transaction_count"])), str(int(s["unique_customers"]))])
        col_widths = [12, 14, 12, 16]
        f.write(_write_table(rows, col_widths) + "\n\n")

        # 7. PRODUCT PERFORMANCE ANALYSIS
        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write("-" * 44 + "\n")
        f.write(f"Best Selling Day: {peak_date} (Revenue: {_money(peak_rev)}, Transactions: {peak_count})\n\n")

        if lows:
            f.write("Low Performing Products (Qty < 10):\n")
            rows = [["Product", "Qty", "Revenue"]]
            for name, qty, rev in lows:
                rows.append([name, str(qty), _money(rev)])
            col_widths = [20, 6, 14]
            f.write(_write_table(rows, col_widths) + "\n\n")
        else:
            f.write("Low Performing Products: None\n\n")

        f.write("Average Transaction Value per Region:\n")
        rows = [["Region", "Avg Transaction Value"]]
        for reg, avg_val in avg_value_per_region:
            rows.append([reg, _money(avg_val)])
        col_widths = [12, 22]
        f.write(_write_table(rows, col_widths) + "\n\n")

        # 8. API ENRICHMENT SUMMARY
        f.write("API ENRICHMENT SUMMARY\n")
        f.write("-" * 44 + "\n")
        f.write(f"Total Transactions Enriched: {enriched_count}/{len(enriched_transactions)}\n")
        f.write(f"Success Rate: {success_rate:.2f}%\n")
        f.write("Products Not Enriched:\n")
        if not_enriched_products:
            for p in not_enriched_products:
                f.write(f"- {p}\n")
        else:
            f.write("- None\n")
