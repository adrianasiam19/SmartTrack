#!/usr/bin/env python
"""CLI: scrape university programmes and merge into Course Directory.

Usage (from smarttrack-backend):
  python -m scripts.scrape_programmes
  python -m scripts.scrape_programmes --universities ug,upsa
  python -m scripts.scrape_programmes --skip-merge
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.scrape_programmes.common import PoliteClient, ensure_data_dir
from scripts.scrape_programmes.merge_course_directory import merge_into_course_directory
from scripts.scrape_programmes.scrape_knust import scrape_knust
from scripts.scrape_programmes.scrape_ucc import scrape_ucc
from scripts.scrape_programmes.scrape_ug import scrape_ug
from scripts.scrape_programmes.scrape_upsa import scrape_upsa


SCRAPERS = {
    "ug": scrape_ug,
    "knust": lambda client=None: scrape_knust(),
    "ucc": scrape_ucc,
    "upsa": scrape_upsa,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scrape programmes → Course Directory")
    parser.add_argument(
        "--universities",
        default="ug,knust,ucc,upsa",
        help="Comma-separated codes: ug,knust,ucc,upsa",
    )
    parser.add_argument(
        "--skip-merge",
        action="store_true",
        help="Only write data/programmes/*.json; do not update course_directory.json",
    )
    args = parser.parse_args(argv)

    ensure_data_dir()
    codes = [c.strip().lower() for c in args.universities.split(",") if c.strip()]
    unknown = [c for c in codes if c not in SCRAPERS]
    if unknown:
        print("Unknown university codes:", ", ".join(unknown), file=sys.stderr)
        return 2

    client = PoliteClient()
    results = []
    try:
        for code in codes:
            fn = SCRAPERS[code]
            print(f"Scraping {code}...")
            if code == "knust":
                payload = fn()
            else:
                payload = fn(client)
            results.append(
                {
                    "code": code,
                    "status": payload.get("status"),
                    "count": payload.get("count"),
                    "notes": payload.get("notes"),
                }
            )
            print(f"  -> {payload.get('status')} ({payload.get('count')} programmes)")
            if payload.get("notes"):
                print(f"     {payload['notes']}")
    finally:
        client.close()

    merge_stats = None
    if not args.skip_merge:
        print("Merging into course_directory.json...")
        merge_stats = merge_into_course_directory(write=True)
        print("  ->", json.dumps(merge_stats))

    print(json.dumps({"scrapes": results, "merge": merge_stats}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
