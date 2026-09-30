"""
Generates two intentionally inconsistent warehouse CSV exports so
src/pipeline.py has something realistic to clean and merge.

Usage:
    python sample_data/generate_sample_data.py
"""

import csv
import random

SKUS = [f"SKU-{i:04d}" for i in range(1, 121)]


def write_warehouse_a(path="warehouse_A.csv", n=300):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sku", "warehouse_id", "qty", "reorder_point", "unit_cost"])
        for _ in range(n):
            w.writerow([
                random.choice(SKUS), "WH-A",
                random.randint(0, 500),
                random.randint(20, 100),
                round(random.uniform(50, 2000), 2),
            ])


def write_warehouse_b(path="warehouse_B.csv", n=300):
    # Different column names on purpose — this is what pipeline.py normalizes.
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item_code", "location", "stock", "min_stock", "cost"])
        for _ in range(n):
            w.writerow([
                random.choice(SKUS), "WH-B",
                random.randint(0, 500),
                random.randint(20, 100),
                round(random.uniform(50, 2000), 2),
            ])


if __name__ == "__main__":
    write_warehouse_a()
    write_warehouse_b()
    print("Wrote warehouse_A.csv and warehouse_B.csv")
