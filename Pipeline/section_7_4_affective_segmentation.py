"""
Section 7.4 - Affective and Segmentation Analysis (UC8-UC10)

Runs the three use case queries from Section 3.4's third stakeholder
group against the populated warehouse built in Chapter 6, printing
each result exactly as reported in Section 7.4. Run this from the
same directory as warehouse.db.
"""

import sqlite3


def uc8_subjectivity_bands(cur):
    print("UC8: Subjectivity's influence on aggregated sentiment")
    print("-" * 60)
    cur.execute("""
        SELECT
            CASE
                WHEN f.subjectivity_score < 0.3 THEN 'Low (<0.3)'
                WHEN f.subjectivity_score < 0.6 THEN 'Medium (0.3-0.6)'
                ELSE 'High (>=0.6)'
            END AS subjectivity_band,
            ROUND(AVG(f.polarity_score), 3) AS avg_polarity,
            ROUND(AVG(f.sentiment_strength), 3) AS avg_strength,
            COUNT(*) AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        GROUP BY subjectivity_band
        ORDER BY MIN(f.subjectivity_score)
    """)
    for row in cur.fetchall():
        print(f"  {row[0]:20s} polarity={row[1]:.3f}  strength={row[2]:.3f}  n={row[3]}")
    print()


def uc9_aspect_by_segment(cur):
    print("UC9: Interaction between aspect category and travel segment")
    print("-" * 60)
    cur.execute("""
        SELECT a.aspect_category, t.travel_party_type,
               ROUND(AVG(f.polarity_score), 3) AS avg_polarity,
               ROUND(AVG(f.subjectivity_score), 3) AS avg_subjectivity,
               ROUND(AVG(f.joy_score), 3) AS avg_joy,
               COUNT(*) AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_ASPECT a ON f.aspect_key = a.aspect_key
        JOIN D_REVIEW r ON f.review_key = r.review_key
        JOIN D_TRAVEL_SEGMENT t ON r.travel_segment_key = t.travel_segment_key
        WHERE t.travel_party_type IS NOT NULL
        GROUP BY a.aspect_category, t.travel_party_type
        HAVING COUNT(*) >= 8
        ORDER BY a.aspect_category, t.travel_party_type
    """)
    for row in cur.fetchall():
        print(f"  {row[0]:25s} {row[1]:10s} polarity={row[2]:.3f}  "
              f"subjectivity={row[3]:.3f}  joy={row[4]:.3f}  n={row[5]}")
    print()


def uc10_segment_by_category(cur):
    print("UC10: Sentiment across travel party type and purpose")
    print("-" * 60)
    cur.execute("""
        SELECT s.service_category, t.travel_party_type, t.trip_purpose,
               ROUND(AVG(f.polarity_score), 3) AS avg_polarity, COUNT(*) AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        JOIN D_REVIEW r ON f.review_key = r.review_key
        JOIN D_TRAVEL_SEGMENT t ON r.travel_segment_key = t.travel_segment_key
        WHERE t.travel_party_type IN ('Solo', 'Family') OR t.trip_purpose = 'Business'
        GROUP BY s.service_category, t.travel_party_type, t.trip_purpose
        HAVING COUNT(*) >= 5
        ORDER BY s.service_category
    """)
    for row in cur.fetchall():
        party = row[1] if row[1] else "—"
        purpose = row[2] if row[2] else "—"
        print(f"  {row[0]:15s} party={party:8s} purpose={purpose:10s} "
              f"polarity={row[3]:.3f}  n={row[4]}")
    print()


def main():
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()

    print("=" * 60)
    print("SECTION 7.4 - Affective and Segmentation Analysis")
    print("=" * 60 + "\n")

    uc8_subjectivity_bands(cur)
    uc9_aspect_by_segment(cur)
    uc10_segment_by_category(cur)

    conn.close()


if __name__ == "__main__":
    main()
