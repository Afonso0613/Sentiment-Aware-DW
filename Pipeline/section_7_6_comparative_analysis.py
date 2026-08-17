"""
Section 7.6 - Comparative Analysis Against Simpler Sentiment Representations

Runs the three comparisons against the populated warehouse built in
Chapter 6, printing each result exactly as reported in Section 7.6.
Each compares what the aspect-level fact table actually contains
against what a simpler alternative representation would have reported
instead: star ratings alone, a review-level average, and polarity
without subjectivity or emotion. Run this from the same directory as
warehouse.db.
"""

import sqlite3


def star_rating_comparison(cur):
    print("7.6.1: Star rating vs derived aspect sentiment")
    print("-" * 60)

    cur.execute("SELECT COUNT(DISTINCT platform_review_id) FROM D_REVIEW WHERE star_rating >= 4.0")
    n_high_total = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT r.platform_review_id)
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_REVIEW r ON f.review_key = r.review_key
        WHERE r.star_rating >= 4.0 AND f.polarity_score < -0.15
    """)
    n_divergent = cur.fetchone()[0]

    print(f"  Reviews with star_rating >= 4.0: {n_high_total}")
    print(f"  Containing a negative aspect (polarity < -0.15): {n_divergent} "
          f"({n_divergent/n_high_total:.1%})")

    cur.execute("""
        SELECT r.platform_review_id, r.star_rating, a.aspect_name,
               ROUND(f.polarity_score,3) AS polarity_score, r.review_text
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_REVIEW r ON f.review_key = r.review_key
        JOIN D_ASPECT a ON f.aspect_key = a.aspect_key
        WHERE r.star_rating >= 4.5 AND f.polarity_score < -0.2
        ORDER BY f.polarity_score ASC
        LIMIT 5
    """)
    print("\n  Top examples:")
    for row in cur.fetchall():
        print(f"    [{row[0]}] stars={row[1]}  aspect={row[2]}  polarity={row[3]}")
        print(f"      \"{row[4]}\"")
    print()


def review_average_comparison(cur):
    print("7.6.2: Review-level average vs aspect-level spread")
    print("-" * 60)

    cur.execute("""
        WITH review_spread AS (
            SELECT r.platform_review_id,
                   MAX(f.polarity_score) - MIN(f.polarity_score) AS spread,
                   COUNT(*) AS n
            FROM F_ASPECT_SENTIMENT_OBSERVATION f
            JOIN D_REVIEW r ON f.review_key = r.review_key
            GROUP BY r.platform_review_id
            HAVING n >= 2
        )
        SELECT COUNT(*), ROUND(AVG(spread),3),
               SUM(CASE WHEN spread > 0.5 THEN 1 ELSE 0 END)
        FROM review_spread
    """)
    total, avg_spread, n_wide = cur.fetchone()
    print(f"  Reviews with 2+ aspects: {total}")
    print(f"  Average polarity spread: {avg_spread}")
    print(f"  Reviews with spread > 0.5: {n_wide} ({n_wide/total:.1%})")

    cur.execute("""
        SELECT r.platform_review_id, ROUND(AVG(f.polarity_score),3) AS review_average,
               ROUND(MIN(f.polarity_score),3) AS min_aspect,
               ROUND(MAX(f.polarity_score),3) AS max_aspect, COUNT(*) AS n_aspects
        FROM F_ASPECT_SENTIMENT_OBSERVATION f
        JOIN D_REVIEW r ON f.review_key = r.review_key
        GROUP BY r.platform_review_id
        HAVING n_aspects >= 2
        ORDER BY (max_aspect - min_aspect) DESC
        LIMIT 5
    """)
    print("\n  Widest spread examples:")
    for row in cur.fetchall():
        print(f"    {row[0]}  review_average={row[1]}  min={row[2]}  max={row[3]}  n={row[4]}")
    print()


def polarity_vs_emotion_comparison(cur):
    print("7.6.3: Polarity alone vs polarity with subjectivity and emotion")
    print("-" * 60)

    cur.execute("""
        SELECT aspect_code, ROUND(polarity_score,3) AS polarity_score,
               ROUND(sadness_score,2) AS sadness, ROUND(disgust_score,2) AS disgust,
               ROUND(anger_score,2) AS anger, ROUND(fear_score,2) AS fear, sentence
        FROM TRANSFORMED_OBSERVATIONS
        WHERE polarity_score BETWEEN -0.55 AND -0.45
        GROUP BY aspect_code, polarity_score
        ORDER BY polarity_score
    """)
    print("  Near-identical polarity, different emotion profile:")
    for row in cur.fetchall():
        print(f"    {row[0]:20s} polarity={row[1]}  sadness={row[2]}  disgust={row[3]}  "
              f"anger={row[4]}  fear={row[5]}")
        print(f"      \"{row[6]}\"")

    cur.execute("SELECT COUNT(*) FROM TRANSFORMED_OBSERVATIONS WHERE polarity_score < -0.1")
    neg_total = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM TRANSFORMED_OBSERVATIONS
        WHERE polarity_score < -0.1
          AND sadness_score = 0 AND disgust_score = 0 AND anger_score = 0 AND fear_score = 0
    """)
    neg_no_emotion = cur.fetchone()[0]
    print(f"\n  Negative observations (polarity < -0.1): {neg_total}")
    print(f"  With no negative emotion detected: {neg_no_emotion} ({neg_no_emotion/neg_total:.1%})")
    print("  (a coverage limitation of the NRC Emotion Lexicon, documented in Section 7.6)")
    print()


def main():
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()

    print("=" * 60)
    print("SECTION 7.6 - Comparative Analysis Against Simpler Representations")
    print("=" * 60 + "\n")

    star_rating_comparison(cur)
    review_average_comparison(cur)
    polarity_vs_emotion_comparison(cur)

    conn.close()


if __name__ == "__main__":
    main()
