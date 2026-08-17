"""
Section 7.5 - Extending the Analysis Beyond the Core Use Cases

Runs the two extensibility test queries against the populated warehouse
built in Chapter 6, printing each result exactly as reported in
Section 7.5. Both test specific claims made in Section 3.4 about the
Travel Segment dimension supporting analyses beyond the ten core use
cases, using nationality and age_group, neither of which is drawn on
by any of UC1-UC10. Run this from the same directory as warehouse.db.
"""

import sqlite3


def nationality_by_category(cur):
    print("Extensibility test 1: nationality x service_category")
    print("(which visitor profiles are associated with particular service types)")
    print("-" * 60)
    cur.execute("""
        SELECT t.nationality, s.service_category,
               ROUND(AVG(f.polarity_score), 3) AS avg_polarity, COUNT(*) AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        JOIN D_REVIEW r ON f.review_key = r.review_key
        JOIN D_TRAVEL_SEGMENT t ON r.travel_segment_key = t.travel_segment_key
        WHERE t.nationality IS NOT NULL
        GROUP BY t.nationality, s.service_category
        HAVING COUNT(*) >= 8
        ORDER BY t.nationality, s.service_category
    """)
    for row in cur.fetchall():
        print(f"  {row[0]:15s} {row[1]:15s} polarity={row[2]:.3f}  n={row[3]}")
    print()


def age_group_by_category(cur):
    print("Extensibility test 2: age_group x service_category (emotion)")
    print("(how demographic groups differ in emotional response to the same category)")
    print("-" * 60)
    cur.execute("""
        SELECT t.age_group, s.service_category,
               ROUND(AVG(f.joy_score), 3) AS avg_joy,
               ROUND(AVG(f.fear_score), 3) AS avg_fear,
               COUNT(*) AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        JOIN D_REVIEW r ON f.review_key = r.review_key
        JOIN D_TRAVEL_SEGMENT t ON r.travel_segment_key = t.travel_segment_key
        WHERE t.age_group IS NOT NULL
        GROUP BY t.age_group, s.service_category
        HAVING COUNT(*) >= 8
        ORDER BY t.age_group, s.service_category
    """)
    for row in cur.fetchall():
        print(f"  {row[0]:8s} {row[1]:15s} joy={row[2]:.3f}  fear={row[3]:.3f}  n={row[4]}")
    print()


def main():
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()

    print("=" * 60)
    print("SECTION 7.5 - Extending the Analysis Beyond the Core Use Cases")
    print("=" * 60 + "\n")

    nationality_by_category(cur)
    age_group_by_category(cur)

    conn.close()


if __name__ == "__main__":
    main()
