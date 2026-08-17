"""
run_pipeline.py
===============
Builds the sentiment-aware data warehouse from scratch.

Run this script from the directory containing all pipeline files:

    python3 run_pipeline.py

It will:
  1. Delete any existing warehouse.db and create a fresh one.
  2. Apply the warehouse schema (schema.sql) and raw schema (raw_schema.sql).
  3. Populate the three independent warehouse dimensions: D_DATE, D_LOCATION,
     D_ASPECT (no dependencies between them; run in any order).
  4. Generate 500 synthetic raw reviews into RAW_REVIEW.
  5. Populate the aspect keyword detection dictionary (RAW_ASPECT_KEYWORD).
  6. Run the transformation step: sentence splitting, aspect identification
     and sentiment derivation via VADER, TextBlob and NRC Emotion Lexicon.
     Output goes to TRANSFORMED_OBSERVATIONS (staging table, not a warehouse
     target).
  7. Load the four dependent warehouse dimensions: D_PLATFORM, D_SERVICE,
     D_TRAVEL_SEGMENT, then D_REVIEW (which requires D_TRAVEL_SEGMENT first).
  8. Load the fact table F_ASPECT_SENTIMENT_OBSERVATION (requires all
     dimensions to be in place).

Dependencies:
    pip install vaderSentiment textblob nrclex nltk

The random seed in generate_raw_reviews.py is fixed (42), so every run
produces the identical 500-row dataset and identical warehouse contents.

All scripts import sqlite3 and connect to warehouse.db in the current
directory. Do not move warehouse.db while the pipeline is running.
"""

import os
import sqlite3
import sys
import time

# ---- helpers --------------------------------------------------------

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


def run_sql_file(conn, path):
    with open(path, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()


def row_count(conn, table):
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    return cur.fetchone()[0]


# ---- steps ----------------------------------------------------------

def step_create_database(db_path):
    if os.path.exists(db_path):
        os.remove(db_path)
        log(f"Removed existing {db_path}.")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    log(f"Created fresh {db_path}.")
    return conn


def step_apply_schemas(conn):
    run_sql_file(conn, "schema.sql")
    run_sql_file(conn, "raw_schema.sql")
    log("Schemas applied (warehouse + raw).")


def step_populate_d_date(conn):
    from populate_d_date import main as _main
    _main()
    log(f"D_DATE populated: {row_count(conn, 'D_DATE')} rows.")


def step_populate_d_location(conn):
    from populate_d_location import main as _main
    _main()
    log(f"D_LOCATION populated: {row_count(conn, 'D_LOCATION')} rows.")


def step_populate_d_aspect(conn):
    from populate_d_aspect import main as _main
    _main()
    log(f"D_ASPECT populated: {row_count(conn, 'D_ASPECT')} rows.")


def step_generate_raw_reviews(conn):
    from generate_raw_reviews import main as _main
    _main()
    log(f"RAW_REVIEW populated: {row_count(conn, 'RAW_REVIEW')} rows.")


def step_populate_keyword_dict(conn):
    from populate_keyword_dict import main as _main
    _main()
    log(f"RAW_ASPECT_KEYWORD populated: {row_count(conn, 'RAW_ASPECT_KEYWORD')} rows.")


def step_transform(conn):
    from transform import main as _main
    _main()
    log(f"TRANSFORMED_OBSERVATIONS populated: {row_count(conn, 'TRANSFORMED_OBSERVATIONS')} rows.")


def step_load_d_platform(conn):
    from load_d_platform import main as _main
    _main()
    log(f"D_PLATFORM populated: {row_count(conn, 'D_PLATFORM')} rows.")


def step_load_d_service(conn):
    from load_d_service import main as _main
    _main()
    log(f"D_SERVICE populated: {row_count(conn, 'D_SERVICE')} rows.")


def step_load_d_travel_segment(conn):
    from load_d_travel_segment import main as _main
    _main()
    log(f"D_TRAVEL_SEGMENT populated: {row_count(conn, 'D_TRAVEL_SEGMENT')} rows.")


def step_load_d_review(conn):
    from load_d_review import main as _main
    _main()
    log(f"D_REVIEW populated: {row_count(conn, 'D_REVIEW')} rows.")


def step_load_fact_table(conn):
    from load_fact_table import main as _main
    _main()
    log(f"F_ASPECT_SENTIMENT_OBSERVATION populated: {row_count(conn, 'F_ASPECT_SENTIMENT_OBSERVATION')} rows.")


# ---- summary --------------------------------------------------------

def print_summary(conn):
    tables = [
        "D_DATE", "D_LOCATION", "D_SERVICE", "D_ASPECT",
        "D_TRAVEL_SEGMENT", "D_REVIEW", "D_PLATFORM",
        "F_ASPECT_SENTIMENT_OBSERVATION",
        "RAW_REVIEW", "RAW_ASPECT_KEYWORD", "TRANSFORMED_OBSERVATIONS",
    ]
    print("\n" + "="*50)
    print("PIPELINE COMPLETE — Final row counts")
    print("="*50)
    for t in tables:
        print(f"  {t:40s} {row_count(conn, t)}")
    print("="*50)


# ---- main -----------------------------------------------------------

def main():
    db_path = "warehouse.db"

    start = time.time()
    log("Starting pipeline...")

    conn = step_create_database(db_path)

    # Step 2: schemas
    step_apply_schemas(conn)

    # Step 3: independent warehouse dimensions (any order)
    step_populate_d_date(conn)
    step_populate_d_location(conn)
    step_populate_d_aspect(conn)

    # Step 4: raw data generation
    step_generate_raw_reviews(conn)

    # Step 5: keyword dictionary
    step_populate_keyword_dict(conn)

    # Step 6: transformation (text fragmentation + sentiment derivation)
    log("Running transformation (this may take a moment)...")
    step_transform(conn)

    # Step 7: dependent dimensions (D_REVIEW needs D_TRAVEL_SEGMENT first)
    step_load_d_platform(conn)
    step_load_d_service(conn)
    step_load_d_travel_segment(conn)
    step_load_d_review(conn)

    # Step 8: fact table (needs all dimensions)
    step_load_fact_table(conn)

    elapsed = time.time() - start
    print_summary(conn)
    log(f"Pipeline finished in {elapsed:.1f}s.")
    conn.close()


if __name__ == "__main__":
    main()
