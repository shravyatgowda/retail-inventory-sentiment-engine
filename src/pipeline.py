"""
pipeline.py

Extracts and aggregates disorganized SKU inventory data from multiple
warehouse export files (varying column names/formats) into one clean,
analysis-ready DataFrame, then writes output for the Excel macro layer
to consume.

Usage:
    python src/pipeline.py --input_dir sample_data --out clean_inventory.csv
"""

import argparse
import glob
import os
import pandas as pd

# Warehouses export with inconsistent column names — map them to a
# canonical schema instead of assuming every file looks the same.
COLUMN_ALIASES = {
    "sku": ["sku", "SKU", "item_code", "product_code"],
    "warehouse_id": ["warehouse_id", "wh_id", "location", "warehouse"],
    "quantity_on_hand": ["qty", "quantity", "quantity_on_hand", "stock"],
    "reorder_point": ["reorder_point", "reorder_level", "min_stock"],
    "unit_cost": ["unit_cost", "cost", "unit_price"],
}


def _canonicalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in df.columns:
                rename_map[alias] = canonical
                break
    return df.rename(columns=rename_map)


def load_warehouse_files(input_dir: str) -> pd.DataFrame:
    files = glob.glob(os.path.join(input_dir, "*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")

    frames = []
    for path in files:
        df = pd.read_csv(path)
        df = _canonicalize_columns(df)
        missing = set(COLUMN_ALIASES.keys()) - set(df.columns)
        if missing:
            print(f"[warn] {path}: missing columns {missing}, filling with NA")
            for col in missing:
                df[col] = pd.NA
        frames.append(df[list(COLUMN_ALIASES.keys())])

    return pd.concat(frames, ignore_index=True)


def clean_and_aggregate(df: pd.DataFrame) -> pd.DataFrame:
    df["quantity_on_hand"] = pd.to_numeric(df["quantity_on_hand"], errors="coerce")
    df["reorder_point"] = pd.to_numeric(df["reorder_point"], errors="coerce")
    df["unit_cost"] = pd.to_numeric(df["unit_cost"], errors="coerce")

    df = df.dropna(subset=["sku", "warehouse_id"])
    df["quantity_on_hand"] = df["quantity_on_hand"].fillna(0)

    agg = (
        df.groupby(["sku", "warehouse_id"], as_index=False)
        .agg(
            quantity_on_hand=("quantity_on_hand", "sum"),
            reorder_point=("reorder_point", "max"),
            unit_cost=("unit_cost", "mean"),
        )
    )
    agg["below_reorder_point"] = agg["quantity_on_hand"] < agg["reorder_point"]
    agg["inventory_value"] = agg["quantity_on_hand"] * agg["unit_cost"]
    return agg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="sample_data")
    parser.add_argument("--out", default="clean_inventory.csv")
    args = parser.parse_args()

    raw = load_warehouse_files(args.input_dir)
    clean = clean_and_aggregate(raw)
    clean.to_csv(args.out, index=False)

    print(f"Processed {len(raw)} raw rows -> {len(clean)} SKU/warehouse rows")
    print(f"SKUs below reorder point: {int(clean['below_reorder_point'].sum())}")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
