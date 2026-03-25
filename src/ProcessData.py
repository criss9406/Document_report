"""
Data Processing Pipeline
Reads raw Kaggle CSVs and produces processed report data as CSV files.
"""

import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ──────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DATA_DIR = BASE_DIR / "src" / "report_data"

OUTPUT_DIR.mkdir(exist_ok=True)
REPORT_DATA_DIR.mkdir(exist_ok=True)


def load_csv(filename):
    path = DATA_DIR / filename
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(filename, rows, fieldnames):
    path = REPORT_DATA_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  ✓ {filename} ({len(rows)} rows)")


def main():
    print("Loading raw data...")
    prices = load_csv("2017PurchasePricesDec.csv")
    beg_inv = load_csv("BegInvFINAL12312016.csv")
    end_inv = load_csv("EndInvFINAL12312016.csv")
    invoices = load_csv("InvoicePurchases12312016.csv")

    # ──────────────────────────────────────────
    # Price map (brand → product info)
    # ──────────────────────────────────────────

    price_map = {}
    for r in prices:
        price_map[r["Brand"]] = {
            "description": r["Description"].strip(),
            "price": float(r["Price"]),
            "purchase_price": float(r["PurchasePrice"]),
            "vendor": r["VendorName"].strip(),
            "size": r["Size"],
        }

    # ──────────────────────────────────────────
    # Executive Summary
    # ──────────────────────────────────────────

    beg_total_units = sum(int(r["onHand"]) for r in beg_inv)
    end_total_units = sum(int(r["onHand"]) for r in end_inv)
    beg_total_value = sum(int(r["onHand"]) * float(r["Price"]) for r in beg_inv)
    end_total_value = sum(int(r["onHand"]) * float(r["Price"]) for r in end_inv)
    total_purchase_spend = sum(float(r["Dollars"]) for r in invoices)
    total_freight = sum(float(r["Freight"]) for r in invoices)
    unique_stores = len(set(r["Store"] for r in beg_inv))
    unique_skus_beg = len(set(r["Brand"] for r in beg_inv))
    unique_skus_end = len(set(r["Brand"] for r in end_inv))

    margins_all = []
    for brand, info in price_map.items():
        if info["purchase_price"] > 0:
            margin_pct = ((info["price"] - info["purchase_price"]) / info["purchase_price"]) * 100
            margins_all.append(margin_pct)
    avg_margin = round(sum(margins_all) / len(margins_all), 1)

    # Count dead stock
    beg_by_brand = defaultdict(int)
    for r in beg_inv:
        beg_by_brand[r["Brand"]] += int(r["onHand"])

    end_by_brand = defaultdict(int)
    for r in end_inv:
        end_by_brand[r["Brand"]] += int(r["onHand"])

    dead_stock_count = sum(
        1 for b in beg_by_brand
        if beg_by_brand[b] > 0 and end_by_brand.get(b, 0) - beg_by_brand[b] == 0
    )

    vendor_count = len(set(r["VendorName"].strip() for r in invoices))

    es_fields = [
        "total_stores", "unique_skus_beg", "unique_skus_end",
        "beg_total_units", "end_total_units", "unit_change_pct",
        "beg_total_value", "end_total_value", "value_change_pct",
        "total_purchase_spend", "total_freight",
        "avg_margin_pct", "total_vendors", "dead_stock_count",
    ]
    es_row = {
        "total_stores": unique_stores,
        "unique_skus_beg": unique_skus_beg,
        "unique_skus_end": unique_skus_end,
        "beg_total_units": beg_total_units,
        "end_total_units": end_total_units,
        "unit_change_pct": round(((end_total_units - beg_total_units) / beg_total_units) * 100, 1),
        "beg_total_value": round(beg_total_value, 2),
        "end_total_value": round(end_total_value, 2),
        "value_change_pct": round(((end_total_value - beg_total_value) / beg_total_value) * 100, 1),
        "total_purchase_spend": round(total_purchase_spend, 2),
        "total_freight": round(total_freight, 2),
        "avg_margin_pct": avg_margin,
        "total_vendors": vendor_count,
        "dead_stock_count": dead_stock_count,
    }

    print("\nWriting processed data...")
    write_csv("executive_summary.csv", [es_row], es_fields)

    # ──────────────────────────────────────────
    # Store Overview
    # ──────────────────────────────────────────

    store_city = {}
    for r in beg_inv:
        store_city[r["Store"]] = r["City"]

    beg_by_store = defaultdict(lambda: {"units": 0, "value": 0.0})
    for r in beg_inv:
        s = r["Store"]
        qty = int(r["onHand"])
        beg_by_store[s]["units"] += qty
        beg_by_store[s]["value"] += qty * float(r["Price"])

    end_by_store = defaultdict(lambda: {"units": 0, "value": 0.0})
    for r in end_inv:
        s = r["Store"]
        qty = int(r["onHand"])
        end_by_store[s]["units"] += qty
        end_by_store[s]["value"] += qty * float(r["Price"])

    store_rows = []
    for s in set(list(beg_by_store.keys()) + list(end_by_store.keys())):
        store_rows.append({
            "store": s,
            "city": store_city.get(s, "Unknown"),
            "beg_units": beg_by_store[s]["units"],
            "end_units": end_by_store[s]["units"],
            "beg_value": round(beg_by_store[s]["value"], 2),
            "end_value": round(end_by_store[s]["value"], 2),
            "delta_units": end_by_store[s]["units"] - beg_by_store[s]["units"],
        })
    store_rows.sort(key=lambda x: x["end_value"], reverse=True)

    store_fields = ["store", "city", "beg_units", "end_units", "delta_units", "beg_value", "end_value"]
    write_csv("store_overview.csv", store_rows[:10], store_fields)

    # ──────────────────────────────────────────
    # Margin Analysis
    # ──────────────────────────────────────────

    margin_rows = []
    for brand, info in price_map.items():
        if info["purchase_price"] > 0:
            margin_pct = ((info["price"] - info["purchase_price"]) / info["purchase_price"]) * 100
            margin_rows.append({
                "brand": brand,
                "description": info["description"],
                "price": info["price"],
                "cost": info["purchase_price"],
                "margin_abs": round(info["price"] - info["purchase_price"], 2),
                "margin_pct": round(margin_pct, 1),
            })

    margin_rows.sort(key=lambda x: x["margin_pct"], reverse=True)
    margin_fields = ["brand", "description", "price", "cost", "margin_abs", "margin_pct"]

    write_csv("top_margin.csv", margin_rows[:10], margin_fields)
    write_csv("bottom_margin.csv", margin_rows[-10:], margin_fields)

    # ──────────────────────────────────────────
    # Stock Rotation
    # ──────────────────────────────────────────

    all_brands = set(list(beg_by_brand.keys()) + list(end_by_brand.keys()))
    rotation_rows = []
    for b in all_brands:
        beg_q = beg_by_brand.get(b, 0)
        end_q = end_by_brand.get(b, 0)
        desc = price_map.get(b, {}).get("description", "Unknown")
        rotation_rows.append({
            "brand": b,
            "description": desc,
            "beg_stock": beg_q,
            "end_stock": end_q,
            "delta": end_q - beg_q,
        })

    rotation_fields = ["brand", "description", "beg_stock", "end_stock", "delta"]

    fastest = sorted(rotation_rows, key=lambda x: x["delta"])[:10]
    slowest = sorted(rotation_rows, key=lambda x: x["delta"], reverse=True)[:10]

    write_csv("fastest_moving.csv", fastest, rotation_fields)
    write_csv("slowest_moving.csv", slowest, rotation_fields)

    # ──────────────────────────────────────────
    # Supplier Analysis
    # ──────────────────────────────────────────

    vendor_data = defaultdict(lambda: {"spend": 0.0, "freight": 0.0, "orders": 0, "pay_days": []})
    for r in invoices:
        v = r["VendorName"].strip()
        vendor_data[v]["spend"] += float(r["Dollars"])
        vendor_data[v]["freight"] += float(r["Freight"])
        vendor_data[v]["orders"] += 1
        try:
            inv_date = datetime.strptime(r["InvoiceDate"], "%Y-%m-%d")
            pay_date = datetime.strptime(r["PayDate"], "%Y-%m-%d")
            vendor_data[v]["pay_days"].append((pay_date - inv_date).days)
        except (ValueError, KeyError):
            pass

    vendor_rows = []
    for name, d in vendor_data.items():
        avg_pay = round(sum(d["pay_days"]) / len(d["pay_days"]), 0) if d["pay_days"] else 0
        vendor_rows.append({
            "name": name,
            "spend": round(d["spend"], 2),
            "freight": round(d["freight"], 2),
            "orders": d["orders"],
            "avg_pay_days": int(avg_pay),
            "pct_of_total": round((d["spend"] / total_purchase_spend) * 100, 1),
        })
    vendor_rows.sort(key=lambda x: x["spend"], reverse=True)

    vendor_fields = ["name", "spend", "freight", "orders", "avg_pay_days", "pct_of_total"]
    write_csv("vendor_top10.csv", vendor_rows[:10], vendor_fields)

    print(f"\nDone. All files saved to {REPORT_DATA_DIR}/")


if __name__ == "__main__":
    main()