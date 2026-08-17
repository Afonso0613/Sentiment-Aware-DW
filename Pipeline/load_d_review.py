"""
Loads D_REVIEW from TRANSFORMED_OBSERVATIONS.

Applies the four transformation rules specified in Section 5.7.6:
  Rule 1: Standardise review identification and metadata. The source
          identifier (raw_capture_id) is preserved as platform_review_id
          for traceability; review_text is stored as-is (already cleaned
          at the raw generation stage); star_rating_reviewer is validated
          to the [1,5] range; language_raw is standardised into
          review_language. Fields such as review_title are excluded.
  Rule 2: Resolve travel segment reference. The reviewer/trip attribute
          combination is matched against D_TRAVEL_SEGMENT (already
          populated) to produce travel_segment_key. The matching logic
          re-derives the segment code from the raw attributes using the
          same normalisation applied in load_d_travel_segment.py, then
          looks up the key rather than re-inserting.
  Rule 3: Handle review versioning and edit traceability. raw_thread_id
          becomes review_group_id (ties original and edited versions
          together); is_edit is derived from TRANSFORMED_OBSERVATIONS,
          where the earliest captured_at per thread was marked as
          original (is_edit=0) during the transformation step.
  Rule 4: Generate surrogate key review_key and load the record.

Each distinct raw_capture_id produces exactly one row in D_REVIEW.
"""

import sqlite3

# import the normalisation helpers from the travel segment loader
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from load_d_travel_segment import (
    TRIP_TYPE_MAP, TRIP_PURPOSE_MAP, NATIONALITY_CODE, make_segment_code
)

VALID_LANGUAGES = {"en", "pt", "es", "fr", "de"}

def standardise_language(lang_raw):
    """Rule 1: validate language code. Unknown codes become None."""
    if lang_raw and lang_raw.lower().strip() in VALID_LANGUAGES:
        return lang_raw.lower().strip()
    return None

def validate_star_rating(star_rating):
    """Rule 1: validate reviewer star rating to [1.0, 5.0]."""
    if star_rating is None:
        return None
    try:
        val = float(star_rating)
        return val if 1.0 <= val <= 5.0 else None
    except (TypeError, ValueError):
        return None


def load_d_review(conn):
    cur = conn.cursor()

    # Rule 2: build segment_code -> travel_segment_key lookup
    cur.execute("SELECT travel_segment_code, travel_segment_key FROM D_TRAVEL_SEGMENT")
    segment_lookup = {row[0]: row[1] for row in cur.fetchall()}

    # collect one row per distinct raw_capture_id from the staging table.
    # TRANSFORMED_OBSERVATIONS may have multiple rows per capture (one per
    # matched aspect), so we take one representative row per capture using
    # MIN(obs_id) to avoid duplicates.
    cur.execute("""
        SELECT
            raw_capture_id,
            raw_thread_id,
            is_edit,
            review_text,
            star_rating_reviewer,
            language_raw,
            reviewer_nationality,
            reviewer_age_group,
            reviewer_gender,
            trip_type_raw,
            trip_purpose_raw
        FROM TRANSFORMED_OBSERVATIONS
        WHERE obs_id IN (
            SELECT MIN(obs_id)
            FROM TRANSFORMED_OBSERVATIONS
            GROUP BY raw_capture_id
        )
        ORDER BY raw_capture_id
    """)
    raw_reviews = cur.fetchall()

    rows = []
    review_key = 1
    unresolved_segments = 0

    for (raw_capture_id, raw_thread_id, is_edit, review_text, star_rating_raw,
         language_raw, nationality, age_group, gender,
         trip_type_raw, trip_purpose_raw) in raw_reviews:

        # Rule 1: standardise
        star_rating = validate_star_rating(star_rating_raw)
        review_language = standardise_language(language_raw)

        # Rule 2: resolve travel segment
        travel_party_type = TRIP_TYPE_MAP.get(trip_type_raw) if trip_type_raw else None
        trip_purpose = TRIP_PURPOSE_MAP.get(trip_purpose_raw) if trip_purpose_raw else None
        code = make_segment_code(nationality, age_group, gender,
                                  travel_party_type, trip_purpose)
        travel_segment_key = segment_lookup.get(code)
        if travel_segment_key is None:
            unresolved_segments += 1
            continue

        # Rule 3: review_group_id = raw_thread_id; is_edit already derived
        review_group_id = raw_thread_id

        # Rule 4: load
        rows.append((
            review_key,
            raw_capture_id,        # platform_review_id
            travel_segment_key,
            review_group_id,
            is_edit,
            review_text,
            star_rating,
            review_language,
        ))
        review_key += 1

    conn.executemany(
        """INSERT INTO D_REVIEW (
               review_key, platform_review_id, travel_segment_key,
               review_group_id, is_edit, review_text, star_rating, review_language
           ) VALUES (?,?,?,?,?,?,?,?)""",
        rows,
    )
    conn.commit()
    return len(rows), unresolved_segments


def main():
    conn = sqlite3.connect("warehouse.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    n, unresolved = load_d_review(conn)
    print(f"D_REVIEW loaded: {n} rows.")
    print(f"Unresolved segment lookups (should be 0): {unresolved}")

    cur = conn.cursor()

    cur.execute("SELECT is_edit, COUNT(*) FROM D_REVIEW GROUP BY is_edit")
    print("is_edit distribution:", cur.fetchall())

    cur.execute("SELECT COUNT(DISTINCT review_group_id) FROM D_REVIEW")
    print("Distinct review_group_ids (= distinct threads):", cur.fetchone()[0])

    # verify every D_REVIEW row references a valid travel_segment_key
    cur.execute("""
        SELECT COUNT(*) FROM D_REVIEW r
        LEFT JOIN D_TRAVEL_SEGMENT t ON r.travel_segment_key = t.travel_segment_key
        WHERE t.travel_segment_key IS NULL
    """)
    print("D_REVIEW rows with invalid travel_segment_key:", cur.fetchone()[0] or "none")

    # spot check an edited pair
    cur.execute("""
        SELECT review_group_id FROM D_REVIEW
        GROUP BY review_group_id HAVING COUNT(*) > 1 LIMIT 1
    """)
    group = cur.fetchone()
    if group:
        cur.execute("""
            SELECT platform_review_id, review_group_id, is_edit, star_rating
            FROM D_REVIEW WHERE review_group_id = ? ORDER BY is_edit
        """, (group[0],))
        print("\nSample edited pair:")
        for row in cur.fetchall():
            print(f"  {row}")

    conn.close()


if __name__ == "__main__":
    main()
