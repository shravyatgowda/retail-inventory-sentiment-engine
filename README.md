# Automated Retail Inventory & Sentiment Analytics Engine

A pipeline that (1) cleans and merges inconsistent SKU inventory exports from
multiple warehouses, and (2) classifies customer review sentiment using an
LLM API — with an Excel/VBA layer on top for non-technical stakeholders.

## Structure

```
src/
  pipeline.py               # cleans + aggregates multi-warehouse inventory CSVs
  sentiment_classifier.py   # batches reviews through an LLM API for sentiment
macros/
  RefreshInventoryReport.bas# Excel VBA macro that ingests pipeline.py output
sample_data/
  generate_sample_data.py   # creates two warehouses' worth of inconsistent test data
requirements.txt
```

## Why this project exists

Real warehouse exports rarely agree on column names (`sku` vs `item_code`,
`qty` vs `stock`), and customer review sentiment is usually read manually or
not at all. This project automates both: a canonical-schema mapping layer
for inventory, and an LLM-based classifier for review text, both feeding a
single Excel report stakeholders already know how to use.

## Getting started

```bash
pip install -r requirements.txt

# 1. Generate test inventory data (2 warehouses, inconsistent columns)
python sample_data/generate_sample_data.py

# 2. Run the cleaning/aggregation pipeline
python src/pipeline.py --input_dir sample_data --out clean_inventory.csv

# 3. (Optional) classify review sentiment — requires an API key
export ANTHROPIC_API_KEY=sk-...
python src/sentiment_classifier.py --input reviews.csv --out reviews_scored.csv
```

Then in Excel: place `clean_inventory.csv` next to your workbook, import
`macros/RefreshInventoryReport.bas` (Developer > Visual Basic > Import File),
and run `RefreshInventoryReport`.

## Honest status

This is a from-scratch portfolio project demonstrating a realistic pipeline
pattern (multi-source cleaning + LLM classification + Excel automation),
built with synthetic data. Any turnaround-time or hours-saved figures you
cite from it should be based on your own timed runs, not assumed.

## License

MIT — see [LICENSE](LICENSE).
