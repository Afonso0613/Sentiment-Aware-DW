"""
Section 7.3 - Aspect-Level and Operational Analysis (UC5-UC7)

Runs the three use case queries from Section 3.4's second stakeholder
group against the populated warehouse built in Chapter 6, printing
each result exactly as reported in Section 7.3. Run this from the
same directory as warehouse.db.

UC7 is answered directly in this dataset instance: three services
(SVC_002, SVC_015, SVC_033) carry a genuine, dated attribute change,
so D_Service holds real SCD Type 2 version history rather than only
supporting it architecturally. This script verifies that version
history exists before reporting the before/after result for each.
"""

import sqlite3


def uc5_negative_aspects(cur):
    print("UC5: Aspects most associated with negative sentiment (Accommodation)")
    print("-" * 60)
    cur.execute("""
        SELECT a.aspect_name,
               ROUND(AVG(f.polarity_score), 3) AS avg_polarity,
               ROUND(AVG(f.anger_score), 3)    AS avg_anger,
               ROUND(AVG(f.disgust_score), 3)  AS avg_disgust,
               COUNT(*)                        AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        JOIN D_ASPECT a ON f.aspect_key = a.aspect_key
        WHERE s.service_category = 'Accommodation'
        GROUP BY a.aspect_name
        HAVING COUNT(*) >= 5
        ORDER BY avg_polarity ASC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]:22s} polarity={row[1]:.3f}  anger={row[2]:.3f}  "
              f"disgust={row[3]:.3f}  n={row[4]}")
    print()


def uc6_emotion_by_category(cur):
    print("UC6: Emotion prevalence across service categories")
    print("-" * 60)
    cur.execute("""
        SELECT s.service_category,
               ROUND(AVG(f.joy_score), 3)          AS joy,
               ROUND(AVG(f.trust_score), 3)        AS trust,
               ROUND(AVG(f.fear_score), 3)         AS fear,
               ROUND(AVG(f.surprise_score), 3)     AS surprise,
               ROUND(AVG(f.sadness_score), 3)      AS sadness,
               ROUND(AVG(f.disgust_score), 3)      AS disgust,
               ROUND(AVG(f.anger_score), 3)        AS anger,
               ROUND(AVG(f.anticipation_score), 3) AS anticipation
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        GROUP BY s.service_category
    """)
    for row in cur.fetchall():
        print(f"  {row[0]:15s} joy={row[1]:.3f} trust={row[2]:.3f} fear={row[3]:.3f} "
              f"surprise={row[4]:.3f} sadness={row[5]:.3f} disgust={row[6]:.3f} "
              f"anger={row[7]:.3f} anticipation={row[8]:.3f}")
    print()


def uc7_service_change(cur):
    print("UC7: Sentiment change following a service change")
    print("-" * 60)

    cur.execute("""
        SELECT platform_service_id, COUNT(*) AS n_versions
        FROM D_SERVICE
        GROUP BY platform_service_id
        HAVING n_versions > 1
    """)
    multi_version = cur.fetchall()

    if not multi_version:
        print("  No service in the current dataset has more than one SCD Type 2")
        print("  version. This use case is architecturally supported (see the")
        print("  mapping in Section 5.7.3) but not empirically demonstrable")
        print("  against this dataset instance.\n")
        return

    print(f"  {len(multi_version)} service(s) with a genuine version change:")
    for row in multi_version:
        print(f"    {row[0]}: {row[1]} versions")
    print()

    cur.execute("""
        SELECT s.platform_service_id, s.star_rating, s.price_tier, s.valid_from,
               s.valid_to, s.is_current, ROUND(AVG(f.polarity_score), 3) AS avg_polarity,
               COUNT(*) AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        WHERE s.platform_service_id IN ('SVC_002', 'SVC_015', 'SVC_033')
        GROUP BY s.service_key
        ORDER BY s.platform_service_id, s.valid_from
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}  star={row[1]}  tier={row[2]}  "
              f"[{row[3]} to {row[4]}]  current={row[5]}  "
              f"avg_polarity={row[6]}  n={row[7]}")
    print()


def main():
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()

    print("=" * 60)
    print("SECTION 7.3 - Aspect-Level and Operational Analysis")
    print("=" * 60 + "\n")

    uc5_negative_aspects(cur)
    uc6_emotion_by_category(cur)
    uc7_service_change(cur)

    conn.close()


if __name__ == "__main__":
    main()
