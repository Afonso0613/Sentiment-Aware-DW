"""
Section 7.2 - Strategic and Comparative Analysis (UC1-UC4)

Runs the four use case queries from Section 3.4's first stakeholder
group against the populated warehouse built in Chapter 6, printing
each result exactly as reported in Section 7.2. Run this from the
same directory as warehouse.db.
"""

import sqlite3


def uc1_sentiment_by_category(cur):
    print("UC1: Overall sentiment across service categories")
    print("-" * 60)
    cur.execute("""
        SELECT s.service_category,
               ROUND(AVG(f.polarity_score), 4)     AS avg_polarity,
               ROUND(AVG(f.subjectivity_score), 4) AS avg_subjectivity,
               ROUND(AVG(f.sentiment_strength), 4) AS avg_strength,
               COUNT(*)                            AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        GROUP BY s.service_category
        ORDER BY avg_polarity DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]:15s} polarity={row[1]:.4f}  subjectivity={row[2]:.4f}  "
              f"strength={row[3]:.4f}  n={row[4]}")
    print()


def uc2_emotion_by_region(cur):
    print("UC2: Emotional response across regions and cities (top 5 by joy)")
    print("-" * 60)
    cur.execute("""
        SELECT l.region, l.municipality,
               ROUND(AVG(f.joy_score), 3)     AS avg_joy,
               ROUND(AVG(f.sadness_score), 3) AS avg_sadness,
               ROUND(AVG(f.anger_score), 3)   AS avg_anger,
               COUNT(*)                       AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        JOIN D_LOCATION l ON s.location_key = l.location_key
        GROUP BY l.region, l.municipality
        ORDER BY avg_joy DESC
        LIMIT 5
    """)
    for row in cur.fetchall():
        print(f"  {row[1]:12s} ({row[0]:28s})  joy={row[2]:.3f}  "
              f"sadness={row[3]:.3f}  anger={row[4]:.3f}  n={row[5]}")
    print()


def uc3_regional_consistency(cur):
    print("UC3: Consistency of regional performance across categories")
    print("-" * 60)
    cur.execute("""
        SELECT l.region, s.service_category,
               ROUND(AVG(f.polarity_score), 3) AS avg_polarity, COUNT(*) AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_SERVICE s ON f.service_key = s.service_key
        JOIN D_LOCATION l ON s.location_key = l.location_key
        GROUP BY l.region, s.service_category
        HAVING COUNT(*) >= 10
        ORDER BY l.region, s.service_category
    """)
    for row in cur.fetchall():
        print(f"  {row[0]:28s} {row[1]:15s} polarity={row[2]:.3f}  n={row[3]}")
    print()


def uc4_seasonal_evolution(cur):
    print("UC4: Sentiment evolution across seasons (Accommodation)")
    print("-" * 60)
    cur.execute("""
        SELECT d.year, d.season,
               ROUND(AVG(f.polarity_score), 3) AS avg_polarity, COUNT(*) AS n
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_DATE d ON f.date_key = d.date_key
        JOIN D_SERVICE s ON f.service_key = s.service_key
        WHERE s.service_category = 'Accommodation'
        GROUP BY d.year, d.season
        ORDER BY d.year,
            CASE d.season WHEN 'Winter' THEN 1 WHEN 'Spring' THEN 2
                           WHEN 'Summer' THEN 3 WHEN 'Autumn' THEN 4 END
    """)
    for row in cur.fetchall():
        flag = "  <- small sample" if row[3] < 10 else ""
        print(f"  {row[0]} {row[1]:8s} polarity={row[2]:.3f}  n={row[3]}{flag}")
    print()


def main():
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()

    print("=" * 60)
    print("SECTION 7.2 - Strategic and Comparative Analysis")
    print("=" * 60 + "\n")

    uc1_sentiment_by_category(cur)
    uc2_emotion_by_region(cur)
    uc3_regional_consistency(cur)
    uc4_seasonal_evolution(cur)

    conn.close()


if __name__ == "__main__":
    main()
