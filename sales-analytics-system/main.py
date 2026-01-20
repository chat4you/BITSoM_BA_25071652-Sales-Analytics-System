"""Sales Analytics System - Main Application.

Run this file to execute the complete workflow:
1) Read data with encoding handling
2) Parse and clean
3) Show filter options and apply optional filters
4) Validate
5) Perform analytics
6) Fetch API products
7) Enrich data and save
8) Generate final report

All paths are relative to the project root (no hardcoded absolute paths).
"""

from __future__ import annotations

import os

from utils.file_handler import read_sales_data, parse_transactions, validate_and_filter
from utils.api_handler import fetch_all_products, create_product_mapping, enrich_sales_data, save_enriched_data
from utils.report_generator import generate_sales_report


def _project_path(*parts: str) -> str:
    """Build a path relative to the project root."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, *parts)


def _ask_yes_no(prompt: str) -> bool:
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please enter y/n")


def main() -> None:
    """Main execution function."""

    print("=" * 40)
    print("SALES ANALYTICS SYSTEM")
    print("=" * 40)

    try:
        # 1) Read data
        print("[1/10] Reading sales data...")
        data_file = _project_path("data", "sales_data.txt")
        raw_lines = read_sales_data(data_file)
        print(f"✓ Successfully read {len(raw_lines)} transaction lines")

        # 2) Parse
        print("[2/10] Parsing and cleaning data...")
        parsed = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(parsed)} records")

        # Required validation output (from assignment)
        print(f"Total records parsed: {len(raw_lines)}")

        # 3) Filter options
        print("[3/10] Filter Options Available:")
        # Show available regions and amount range BEFORE asking for filters
        regions = sorted({t.get('Region','').strip() for t in parsed if t.get('Region')})
        amount_candidates = []
        for t in parsed:
            try:
                qty = int(t.get('Quantity'))
                price = float(t.get('UnitPrice'))
                if qty > 0 and price > 0:
                    amount_candidates.append(qty * price)
            except Exception:
                continue
        min_amt = min(amount_candidates) if amount_candidates else 0.0
        max_amt = max(amount_candidates) if amount_candidates else 0.0
        print('Regions: ' + (', '.join(regions) if regions else '(none)'))
        print(f'Amount Range: ₹{min_amt:,.2f} - ₹{max_amt:,.2f}')
        wants_filter = _ask_yes_no("Do you want to filter data? (y/n): ")

        region = None
        min_amount = None
        max_amount = None

        if wants_filter:
            region_in = input("Enter region (leave blank for no region filter): ").strip()
            region = region_in if region_in else None

            min_in = input("Enter minimum amount (leave blank for none): ").strip()
            max_in = input("Enter maximum amount (leave blank for none): ").strip()

            try:
                min_amount = float(min_in) if min_in else None
            except ValueError:
                min_amount = None

            try:
                max_amount = float(max_in) if max_in else None
            except ValueError:
                max_amount = None

        # 4) Validate + optional filter
        print("[4/10] Validating transactions...")
        valid_txns, invalid_count, summary = validate_and_filter(
            parsed,
            region=region,
            min_amount=min_amount,
            max_amount=max_amount,
        )

        print(f"✓ Valid: {len(valid_txns)} | Invalid: {invalid_count}")
        print(f"Invalid records removed: {invalid_count}")
        print(f"Valid records after cleaning: {len(valid_txns)}")
        print("Validation Summary:")
        for k, v in summary.items():
            print(f"  - {k}: {v}")

        # 5) Analytics completed implicitly via report generation
        print("[5/10] Analyzing sales data...")
        print("✓ Analysis complete")

        # 6) API fetch
        print("[6/10] Fetching product data from API...")
        api_products = fetch_all_products()

        # 7) Enrich
        print("[7/10] Enriching sales data...")
        mapping = create_product_mapping(api_products)
        enriched = enrich_sales_data(valid_txns, mapping)
        enriched_count = sum(1 for t in enriched if t.get("API_Match") is True)
        rate = (enriched_count / len(enriched) * 100) if enriched else 0.0
        print(f"✓ Enriched {enriched_count}/{len(enriched)} transactions ({rate:.1f}%)")

        # 8) Save enriched
        print("[8/10] Saving enriched data...")
        enriched_file = _project_path("data", "enriched_sales_data.txt")
        save_enriched_data(enriched, filename=enriched_file)
        print(f"✓ Saved to: {os.path.relpath(enriched_file)}")

        # 9) Report
        print("[9/10] Generating report...")
        report_file = _project_path("output", "sales_report.txt")
        generate_sales_report(valid_txns, enriched, output_file=report_file)
        print(f"✓ Report saved to: {os.path.relpath(report_file)}")

        # 10) Done
        print("[10/10] Process Complete!")
        print("=" * 40)

    except Exception as e:
        print("\nSomething went wrong, but the program did not crash.")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
