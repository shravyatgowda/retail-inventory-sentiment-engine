"""
sentiment_classifier.py

Classifies customer review text into sentiment categories using an LLM API,
in batches, with retry/backoff and structured JSON output.

Requires an API key set as an environment variable — never hardcode it.
Works with Anthropic's API by default; swap the `call_model` function to
point at a different provider if needed.

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python src/sentiment_classifier.py --input reviews.csv --out reviews_scored.csv
"""

import argparse
import json
import os
import time

import pandas as pd
import requests

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-6"
BATCH_SIZE = 20

SYSTEM_PROMPT = (
    "You classify customer product reviews. For each review, return a JSON "
    "object with fields: sentiment (positive|neutral|negative), "
    "confidence (0-1), and one short reason phrase. "
    "Respond ONLY with a JSON array, one object per input review, in order. "
    "No prose, no markdown fences."
)


def call_model(reviews_batch: list[str]) -> list[dict]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set ANTHROPIC_API_KEY environment variable first.")

    numbered = "\n".join(f"{i+1}. {r}" for i, r in enumerate(reviews_batch))
    payload = {
        "model": MODEL,
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": numbered}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    for attempt in range(3):
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            text = resp.json()["content"][0]["text"]
            text = text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(text)
        time.sleep(2 ** attempt)

    raise RuntimeError(f"API call failed after retries: {resp.status_code} {resp.text}")


def classify_reviews(df: pd.DataFrame, text_col: str = "review_text") -> pd.DataFrame:
    results = []
    for start in range(0, len(df), BATCH_SIZE):
        batch = df[text_col].iloc[start:start + BATCH_SIZE].tolist()
        scored = call_model(batch)
        results.extend(scored)
        print(f"Classified rows {start}-{start + len(batch)}")

    result_df = pd.DataFrame(results)
    return pd.concat([df.reset_index(drop=True), result_df], axis=1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", default="reviews_scored.csv")
    parser.add_argument("--text_col", default="review_text")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    scored = classify_reviews(df, text_col=args.text_col)
    scored.to_csv(args.out, index=False)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
