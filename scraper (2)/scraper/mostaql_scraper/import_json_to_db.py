"""
Migration script: Imports all existing scraped JSON files from output/ into PostgreSQL
using UPSERT to prevent duplicates.
"""
import os
import sys
import json
from scrapers.database import init_db, get_connection, upsert_project

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

PLATFORM_FILES = {
    "mostaql": "mostaql_projects.json",
    "khamsat": "khamsat_projects.json",
    "nafezly": "nafezly_projects.json",
    "freelancer": "freelancer_projects.json",
}

def main():
    print("=" * 60)
    print("  Importing existing JSON projects into PostgreSQL")
    print("=" * 60)

    try:
        init_db()
        conn = get_connection()
        conn.autocommit = True
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to PostgreSQL: {e}")
        print("Please ensure PostgreSQL is running and check .env settings.")
        sys.exit(1)

    grand_total = 0
    grand_inserted = 0
    grand_updated = 0

    for platform_key, filename in PLATFORM_FILES.items():
        filepath = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(filepath):
            print(f"[-] Skipping {filename} (file not found)")
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                items = json.load(f)
        except Exception as e:
            print(f"[!] Error reading {filename}: {e}")
            continue

        inserted = 0
        updated = 0
        for it in items:
            try:
                is_new = upsert_project(conn, it, platform_key)
                if is_new:
                    inserted += 1
                else:
                    updated += 1
            except Exception as e:
                print(f"[!] Error upserting {it.get('url')}: {e}")

        total = inserted + updated
        print(f"[+] {platform_key:10}: Total: {total} (New: {inserted}, Updated: {updated})")
        grand_total += total
        grand_inserted += inserted
        grand_updated += updated

    conn.close()
    print("=" * 60)
    print(f"Finished! Total Processed: {grand_total} | Inserted: {grand_inserted} | Updated: {grand_updated}")
    print("=" * 60)

if __name__ == "__main__":
    main()
