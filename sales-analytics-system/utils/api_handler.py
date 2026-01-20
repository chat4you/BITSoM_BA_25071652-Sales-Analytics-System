"""API integration utilities (DummyJSON Products API).

This module fetches product data from the DummyJSON API, creates a mapping,
and enriches the sales transactions with extra product fields.
"""

from __future__ import annotations

from typing import Dict, List, Any

import requests


DUMMYJSON_PRODUCTS_URL = "https://dummyjson.com/products"


def fetch_all_products() -> List[Dict[str, Any]]:
    """Fetches all products from DummyJSON API.

    Requirements:
        - Fetch all available products (use limit=100)
        - Handle connection errors with try-except
        - Return empty list if API fails
        - Print status message (success/failure)

    Returns:
        List of simplified product dictionaries.
    """

    try:
        resp = requests.get(f"{DUMMYJSON_PRODUCTS_URL}?limit=100", timeout=20)
        resp.raise_for_status()
        data = resp.json()
        products = data.get("products", [])

        simplified = []
        for p in products:
            simplified.append(
                {
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "category": p.get("category"),
                    "brand": p.get("brand"),
                    "price": p.get("price"),
                    "rating": p.get("rating"),
                }
            )

        print(f"✓ Fetched {len(simplified)} products")
        return simplified

    except Exception as e:
        print(f"✗ Failed to fetch products from API: {e}")
        return []


def create_product_mapping(api_products: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Creates a mapping of product IDs to product info.

    Output format:
        {
          1: {'title': 'iPhone 9', 'category': 'smartphones', 'brand': 'Apple', 'rating': 4.69},
          ...
        }
    """

    mapping: Dict[int, Dict[str, Any]] = {}

    for p in api_products:
        try:
            pid = int(p.get("id"))
        except (TypeError, ValueError):
            continue

        mapping[pid] = {
            "title": p.get("title"),
            "category": p.get("category"),
            "brand": p.get("brand"),
            "rating": p.get("rating"),
        }

    return mapping


def enrich_sales_data(transactions: List[Dict[str, Any]], product_mapping: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Enriches transaction data with API product information.

    Enrichment logic:
        - Extract numeric ID from ProductID (P101 -> 101)
        - If ID exists in mapping, add API fields
        - If not, set API_Match False and other fields None

    Adds fields:
        API_Category, API_Brand, API_Rating, API_Match

    Returns:
        List of enriched transactions.
    """

    enriched: List[Dict[str, Any]] = []

    for t in transactions:
        new_t = dict(t)  # copy

        api_category = None
        api_brand = None
        api_rating = None
        api_match = False

        try:
            pid_str = str(t.get("ProductID", "")).strip()
            # Keep only digits after leading letters.
            digits = "".join(ch for ch in pid_str if ch.isdigit())
            numeric_id = int(digits) if digits else None

            if numeric_id is not None and numeric_id in product_mapping:
                info = product_mapping[numeric_id]
                api_category = info.get("category")
                api_brand = info.get("brand")
                api_rating = info.get("rating")
                api_match = True

        except Exception:
            # Gracefully ignore errors and keep api_match False.
            api_match = False

        new_t["API_Category"] = api_category
        new_t["API_Brand"] = api_brand
        new_t["API_Rating"] = api_rating
        new_t["API_Match"] = api_match

        enriched.append(new_t)

    return enriched


def save_enriched_data(enriched_transactions: List[Dict[str, Any]], filename: str = "data/enriched_sales_data.txt") -> None:
    """Saves enriched transactions back to file (pipe-delimited) with header."""

    header = [
        "TransactionID",
        "Date",
        "ProductID",
        "ProductName",
        "Quantity",
        "UnitPrice",
        "CustomerID",
        "Region",
        "API_Category",
        "API_Brand",
        "API_Rating",
        "API_Match",
    ]

    with open(filename, "w", encoding="utf-8") as f:
        f.write("|".join(header) + "\n")

        for t in enriched_transactions:
            row = []
            for k in header:
                val = t.get(k)
                if val is None:
                    row.append("")
                else:
                    row.append(str(val))
            f.write("|".join(row) + "\n")
