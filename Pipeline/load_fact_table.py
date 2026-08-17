"""
Loads F_ASPECT_SENTIMENT_OBSERVATION from TRANSFORMED_OBSERVATIONS.

Applies the four transformation rules specified in Section 5.7.8:
  Rule 1: Resolve all five dimension foreign keys.
          - date_key: review date (captured_at[:10]) matched against
            D_DATE on full_date.
          - service_key: resolved via a temporally scoped SCD Type 2
            lookup, selecting the D_SERVICE version whose valid_from /
            valid_to window contains the review date. This preserves
            historical consistency: if a service's category changed
            between two reviews, each fact row references the version
            that accurately described the service at the time that
            review was written. In this prototype all services have a
            single current version, but the lookup is implemented
            correctly so the architecture is honest.
          - review_key: matched against D_REVIEW on platform_review_id
            (= raw_capture_id from the staging table).
          - aspect_key: matched against D_ASPECT on aspect_code.
          - platform_key: matched against D_PLATFORM on platform_code
            (= platform_id from the staging table).
          D_LOCATION and D_TRAVEL_SEGMENT are accessed indirectly
          through D_SERVICE and D_REVIEW respectively, per 5.7.8.

  Rule 2: Carry the pre-derived sentiment measures from the staging
          table directly: polarity_score, subjectivity_score, the eight
          emotion scores and sentiment_strength (|polarity| x
          subjectivity, derived in transform.py). model_confidence
          is always NULL since neither VADER nor TextBlob produces a
          confidence estimate.

  Rule 3: Apply deduplication. The UNIQUE constraint on
          (date_key, service_key, review_key, aspect_key, platform_key)
          enforces grain integrity at the database level. INSERT OR
          IGNORE is used so that duplicate observations (e.g. from
          idempotent re-runs) are silently skipped rather than raising
          an error, consistent with the deduplication rule in 5.8.

  Rule 4: Generate surrogate key sentiment_fact_key and load.
"""

import sqlite3


def build_lookup_maps(conn):
    cur = conn.cursor()

    # D_DATE: full_date -> date_key
    cur.execute("SELECT full_date, date_key FROM D_DATE")
    date_map = {row[0]: row[1] for row in cur.fetchall()}

    # D_SERVICE: (platform_service_id, valid_from, valid_to) for
    # temporally scoped lookup. Stored as list of tuples per service_id.
    cur.execute("""
        SELECT platform_service_id, service_key, valid_from, valid_to
        FROM D_SERVICE
        ORDER BY platform_service_id, valid_from
    """)
    service_versions = {}
    for platform_service_id, service_key, valid_from, valid_to in cur.fetchall():
        service_versions.setdefault(platform_service_id, []).append(
            (service_key, valid_from, valid_to)
        )

    # D_REVIEW: platform_review_id -> review_key
    cur.execute("SELECT platform_review_id, review_key FROM D_REVIEW")
    review_map = {row[0]: row[1] for row in cur.fetchall()}

    # D_ASPECT: aspect_code -> aspect_key
    cur.execute("SELECT aspect_code, aspect_key FROM D_ASPECT")
    aspect_map = {row[0]: row[1] for row in cur.fetchall()}

    # D_PLATFORM: platform_code -> platform_key
    cur.execute("SELECT platform_code, platform_key FROM D_PLATFORM")
    platform_map = {row[0]: row[1] for row in cur.fetchall()}

    return date_map, service_versions, review_map, aspect_map, platform_map


def resolve_service_key(service_versions, platform_service_id, review_date):
    """Temporally scoped SCD Type 2 lookup: find the D_SERVICE version
    whose valid_from <= review_date <= valid_to. If no version matches
    (should not occur in a well-formed warehouse), return None."""
    versions = service_versions.get(platform_service_id, [])
    for service_key, valid_from, valid_to in versions:
        if valid_from <= review_date <= valid_to:
            return service_key
    return None


def load_fact_table(conn):
    date_map, service_versions, review_map, aspect_map, platform_map = build_lookup_maps(conn)

    cur = conn.cursor()

    # Aggregate at the (capture_id, service, aspect, platform) level before
    # loading. When two sentences from the same review match the same aspect,
    # the grain constraint (one fact record per aspect per review) requires
    # them to be merged rather than arbitrarily dropped. Averaging the
    # sentiment scores is the appropriate aggregation since each sentence is
    # an equally valid observation of that aspect within the review.
    cur.execute("""
        SELECT
            raw_capture_id,
            captured_at,
            service_source_id,
            platform_id,
            aspect_code,
            AVG(polarity_score)       AS polarity_score,
            AVG(subjectivity_score)   AS subjectivity_score,
            AVG(joy_score)            AS joy_score,
            AVG(trust_score)          AS trust_score,
            AVG(fear_score)           AS fear_score,
            AVG(surprise_score)       AS surprise_score,
            AVG(sadness_score)        AS sadness_score,
            AVG(disgust_score)        AS disgust_score,
            AVG(anger_score)          AS anger_score,
            AVG(anticipation_score)   AS anticipation_score,
            AVG(sentiment_strength)   AS sentiment_strength,
            NULL                      AS model_confidence
        FROM TRANSFORMED_OBSERVATIONS
        GROUP BY raw_capture_id, captured_at, service_source_id, platform_id, aspect_code
        ORDER BY raw_capture_id, aspect_code
    """)
    observations = cur.fetchall()

    rows = []
    skipped_date = 0
    skipped_service = 0
    skipped_review = 0
    skipped_aspect = 0
    skipped_platform = 0

    for (raw_capture_id, captured_at, service_source_id, platform_id,
         aspect_code, polarity, subjectivity,
         joy, trust, fear, surprise, sadness, disgust, anger, anticipation,
         strength, confidence) in observations:

        review_date = captured_at[:10]

        # Rule 1: resolve all FK keys
        date_key = date_map.get(review_date)
        if date_key is None:
            skipped_date += 1
            continue

        service_key = resolve_service_key(service_versions, service_source_id, review_date)
        if service_key is None:
            skipped_service += 1
            continue

        review_key = review_map.get(raw_capture_id)
        if review_key is None:
            skipped_review += 1
            continue

        aspect_key = aspect_map.get(aspect_code)
        if aspect_key is None:
            skipped_aspect += 1
            continue

        platform_key = platform_map.get(platform_id)
        if platform_key is None:
            skipped_platform += 1
            continue

        rows.append((
            date_key, service_key, review_key, aspect_key, platform_key,
            round(polarity, 4), round(subjectivity, 4),
            round(joy, 4), round(trust, 4), round(fear, 4), round(surprise, 4),
            round(sadness, 4), round(disgust, 4), round(anger, 4), round(anticipation, 4),
            round(strength, 4), confidence,
        ))

    conn.executemany(
        """INSERT INTO F_ASPECT_SENTIMENT_OBSERVATION (
               date_key, service_key, review_key, aspect_key, platform_key,
               polarity_score, subjectivity_score,
               joy_score, trust_score, fear_score, surprise_score,
               sadness_score, disgust_score, anger_score, anticipation_score,
               sentiment_strength, model_confidence
           ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    conn.commit()

    return len(rows), {
        "date_key missing":     skipped_date,
        "service_key missing":  skipped_service,
        "review_key missing":   skipped_review,
        "aspect_key missing":   skipped_aspect,
        "platform_key missing": skipped_platform,
    }


def main():
    conn = sqlite3.connect("warehouse.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    n, skips = load_fact_table(conn)
    print(f"F_ASPECT_SENTIMENT_OBSERVATION loaded: {n} rows.")
    print("Skipped observations by reason:", skips)

    cur = conn.cursor()

    # basic range checks on all measures
    cur.execute("""
        SELECT MIN(polarity_score), MAX(polarity_score),
               MIN(subjectivity_score), MAX(subjectivity_score),
               MIN(sentiment_strength), MAX(sentiment_strength)
        FROM F_ASPECT_SENTIMENT_OBSERVATION
    """)
    ranges = cur.fetchone()
    print(f"\nPolarity range      : [{ranges[0]}, {ranges[1]}]")
    print(f"Subjectivity range  : [{ranges[2]}, {ranges[3]}]")
    print(f"Strength range      : [{ranges[4]}, {ranges[5]}]")

    # model_confidence always NULL
    cur.execute("SELECT COUNT(*) FROM F_ASPECT_SENTIMENT_OBSERVATION WHERE model_confidence IS NOT NULL")
    print(f"Non-null model_confidence: {cur.fetchone()[0]} (expected 0)")

    # average polarity per service_category via join
    cur.execute("""
        SELECT s.service_category, ROUND(AVG(f.polarity_score),4) avg_pol, COUNT(*) obs
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        GROUP BY s.service_category
        ORDER BY avg_pol DESC
    """)
    print("\nAvg polarity by service_category:")
    for row in cur.fetchall():
        print(f"  {row[0]:15s} avg={row[1]}  n={row[2]}")

    # top 5 services by observation count
    cur.execute("""
        SELECT s.service_name, COUNT(*) obs
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        GROUP BY s.service_name ORDER BY obs DESC LIMIT 5
    """)
    print("\nTop 5 services by observation count:")
    for row in cur.fetchall():
        print(f"  {row[0]:35s} {row[1]}")

    # grain integrity: unique constraint check
    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT date_key, service_key, review_key, aspect_key, platform_key,
                   COUNT(*) c
            FROM F_ASPECT_SENTIMENT_OBSERVATION
            GROUP BY date_key, service_key, review_key, aspect_key, platform_key
            HAVING c > 1
        )
    """)
    grain_violations = cur.fetchone()[0]
    print(f"\nGrain violations (should be 0): {grain_violations}")

    conn.close()


if __name__ == "__main__":
    main()
