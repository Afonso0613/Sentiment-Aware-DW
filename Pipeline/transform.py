"""
Transformation step: text fragmentation, aspect identification and
sentiment derivation.

Takes each row from RAW_REVIEW, splits review_text into sentences via
NLTK's sentence tokeniser, matches each sentence against RAW_ASPECT_KEYWORD
to assign an aspect code, then derives the full set of sentiment measures
per matched sentence using the three tools specified in the thesis:
  - VADER (vaderSentiment): polarity_score
  - TextBlob: subjectivity_score
  - NRC Emotion Lexicon (nrclex): eight Plutchik-aligned emotion scores

The output of this step is the staging table TRANSFORMED_OBSERVATIONS,
which the loading scripts (built next) use to populate the five remaining
warehouse tables: D_SERVICE, D_PLATFORM, D_TRAVEL_SEGMENT, D_REVIEW
and F_ASPECT_SENTIMENT_OBSERVATION.

Design choices documented here since they are not specified at this
level of detail in the thesis:

  Sentence splitting: NLTK sent_tokenize. More robust than naive
  full-stop splitting, handles abbreviations and edge cases correctly.

  Keyword matching: case-insensitive substring search of each sentence
  against RAW_ASPECT_KEYWORD.keyword. Multi-word phrases (e.g.
  "air conditioning", "check-in") are matched before single words to
  avoid partial matches swallowing the longer, more specific signal.

  Disambiguation: two keywords map to multiple aspects ("facilities"
  -> FACILITIES_CONDITION and AMENITIES_VARIETY; "queue" ->
  CHECK_IN_EXPERIENCE and CROWDING). Where a sentence matches more than
  one aspect via a shared keyword, the aspect with the most total
  keyword hits in that sentence wins. Ties are broken by alphabetical
  order of aspect_code for determinism.

  Unmatched sentences: sentences that match no keyword are not loaded
  into the warehouse. This is intentional and consistent with the
  aspect-level grain: a sentence with no identifiable aspect contributes
  nothing to the analytical model and should not inflate fact counts.

  polarity_score: VADER compound score, range [-1, 1].

  subjectivity_score: TextBlob subjectivity, range [0, 1].

  Emotion scores: NRC raw emotion counts normalised to [0, 1] by
  dividing each emotion's count by the total number of emotion-bearing
  words in the sentence. Where NRC detects no emotion at all and the
  sentence is already independently confirmed negative by VADER
  (polarity < -0.1), a small supplementary keyword lexicon is
  consulted as a fallback (see SUPPLEMENTARY_NEGATIVE_EMOTION_KEYWORDS
  below), addressing a documented coverage gap in NRC's general-
  purpose vocabulary (Section 7.6.3) without overriding NRC's own
  judgement when it has one. A sentence with no match in either NRC
  or the supplementary lexicon still produces 0.0 for all eight
  emotions, which remains a valid and expected outcome.

  sentiment_strength: |polarity_score| x subjectivity_score, as
  defined in Section 4.7.5 of the thesis. Absolute value of polarity
  is used so that strongly negative, highly subjective text produces
  a high strength value rather than a near-zero one.

  model_confidence: NULL throughout. VADER does not produce a
  confidence estimate; nor does TextBlob's sentiment API. NULL is
  the correct representation per Table 17's nullable definition.
"""

import sqlite3
import re
from collections import defaultdict

import nltk
nltk.download("punkt_tab", quiet=True)
from nltk.tokenize import sent_tokenize

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from nrclex import NRCLex

VADER = SentimentIntensityAnalyzer()


# ---- helpers --------------------------------------------------------

def derive_polarity(text):
    return round(VADER.polarity_scores(text)["compound"], 4)


def derive_subjectivity(text):
    return round(TextBlob(text).sentiment.subjectivity, 4)


def derive_emotions(text, polarity):
    emotions = ["joy", "trust", "fear", "surprise",
                "sadness", "disgust", "anger", "anticipation"]
    nrc = NRCLex()
    nrc.load_raw_text(text)
    raw = nrc.affect_frequencies
    # affect_frequencies already normalises by word count inside NRCLex,
    # but the values can exceed 1.0 when multiple emotion words stack.
    # We clamp to [0, 1] to stay within the CHECK constraint on the fact
    # table.
    scores = {e: min(round(raw.get(e, 0.0), 4), 1.0) for e in emotions}

    # Fallback: only consulted when NRC detects no negative emotion at
    # all (sadness, disgust, anger, fear all zero) and the sentence is
    # already independently confirmed negative by VADER. Checking only
    # the four negative-leaning emotions, rather than requiring all
    # eight to be zero, matters here: NRC can register a spurious
    # positive-leaning emotion such as anticipation on an otherwise
    # negative sentence, which would incorrectly block this fallback
    # from ever firing if all eight were required to be zero. This
    # never overrides a genuine NRC result, it only fills a documented
    # coverage gap (Section 7.6.3) for sentences NRC's lexicon has no
    # negative-emotion signal for.
    negative_emotions = ["sadness", "disgust", "anger", "fear"]
    if all(scores[e] == 0.0 for e in negative_emotions) and polarity < -0.1:
        supplement = apply_supplementary_emotion_lexicon(text)
        if supplement:
            scores.update(supplement)

    return scores


# Supplementary negative-emotion keyword lexicon, used only as the
# fallback described above. Built from real vocabulary gaps identified
# during evaluation (Section 7.6.3): NRC's general-purpose lexicon does
# not recognise several common negative words in this domain, such as
# "failed", "poor" or "deceptive", confirmed individually against NRC
# before inclusion here. Weights are deliberately modest (0.2-0.5)
# since this is a fallback contributing partial signal, not a
# replacement for NRC's own judgement.
SUPPLEMENTARY_NEGATIVE_EMOTION_KEYWORDS = {
    "failed":      [("anger", 0.3), ("sadness", 0.2)],
    "poor":        [("disgust", 0.3)],
    "stained":     [("disgust", 0.4)],
    "undercooked": [("disgust", 0.4)],
    "lacking":     [("sadness", 0.2)],
    "frustrating": [("anger", 0.5)],
    "struggled":   [("sadness", 0.2), ("fear", 0.1)],
    "deceptive":   [("anger", 0.5), ("disgust", 0.3)],
    "repetitive":  [("sadness", 0.2)],
    "confusing":   [("fear", 0.2), ("sadness", 0.1)],
    "unusable":    [("anger", 0.3), ("disgust", 0.2)],
}


def apply_supplementary_emotion_lexicon(text):
    """Word-boundary match against SUPPLEMENTARY_NEGATIVE_EMOTION_KEYWORDS.
    Returns a dict of emotion scores if any keyword matched, else None."""
    lower = text.lower()
    found = {}
    for word, emotion_pairs in SUPPLEMENTARY_NEGATIVE_EMOTION_KEYWORDS.items():
        if re.search(r"\b" + re.escape(word) + r"\b", lower):
            for emotion, weight in emotion_pairs:
                found[emotion] = max(found.get(emotion, 0.0), weight)
    return found if found else None


def derive_sentiment_strength(polarity, subjectivity):
    return round(abs(polarity) * subjectivity, 4)


def load_keywords(conn):
    """Returns sorted list of (keyword, aspect_code) pairs, multi-word
    phrases first so they are matched before their component words."""
    cur = conn.cursor()
    cur.execute("SELECT keyword, aspect_code FROM RAW_ASPECT_KEYWORD")
    rows = cur.fetchall()
    # sort: longer (multi-word) phrases first, then alphabetical
    return sorted(rows, key=lambda r: (-len(r[0].split()), r[0]))


def identify_aspect(sentence, keyword_pairs):
    """Returns the best-matching aspect_code for a sentence, or None
    if no keyword matches. Where a sentence hits multiple aspects, the
    aspect with the most keyword hits wins; ties broken alphabetically."""
    lower = sentence.lower()
    hits = defaultdict(int)
    for keyword, aspect_code in keyword_pairs:
        if keyword in lower:
            hits[aspect_code] += 1
    if not hits:
        return None
    max_hits = max(hits.values())
    candidates = sorted(k for k, v in hits.items() if v == max_hits)
    return candidates[0]


def create_staging_table(conn):
    conn.executescript("""
        DROP TABLE IF EXISTS TRANSFORMED_OBSERVATIONS;
        CREATE TABLE TRANSFORMED_OBSERVATIONS (
            obs_id              INTEGER PRIMARY KEY,
            raw_capture_id       TEXT NOT NULL,
            raw_thread_id        TEXT NOT NULL,
            captured_at           TEXT NOT NULL,
            is_edit              INTEGER NOT NULL,  -- 1 if not earliest capture in thread
            platform_id          TEXT NOT NULL,
            platform_name         TEXT NOT NULL,
            platform_url          TEXT,
            service_source_id    TEXT NOT NULL,
            service_name          TEXT NOT NULL,
            service_type           TEXT NOT NULL,
            municipality_name     TEXT,
            star_rating_official  REAL,
            price_tier_raw        TEXT,
            review_group_id       TEXT NOT NULL,
            review_text            TEXT NOT NULL,
            star_rating_reviewer  REAL,
            language_raw            TEXT,
            reviewer_nationality  TEXT,
            reviewer_age_group     TEXT,
            reviewer_gender         TEXT,
            trip_type_raw            TEXT,
            trip_purpose_raw       TEXT,
            sentence               TEXT NOT NULL,
            aspect_code             TEXT NOT NULL,
            polarity_score          REAL NOT NULL,
            subjectivity_score      REAL NOT NULL,
            joy_score               REAL NOT NULL,
            trust_score             REAL NOT NULL,
            fear_score              REAL NOT NULL,
            surprise_score          REAL NOT NULL,
            sadness_score           REAL NOT NULL,
            disgust_score           REAL NOT NULL,
            anger_score             REAL NOT NULL,
            anticipation_score      REAL NOT NULL,
            sentiment_strength      REAL NOT NULL,
            model_confidence        REAL          -- always NULL (VADER/TextBlob produce none)
        );
    """)


def transform(conn, keyword_pairs):
    cur = conn.cursor()

    # derive is_edit: for each thread, the earliest captured_at is the
    # original; any later capture is an edit. Computed once as a lookup.
    cur.execute("""
        SELECT raw_capture_id,
               captured_at != MIN(captured_at) OVER (PARTITION BY raw_thread_id
                                                      ORDER BY captured_at
                                                      ROWS BETWEEN UNBOUNDED PRECEDING
                                                               AND UNBOUNDED FOLLOWING)
               AS is_edit
        FROM RAW_REVIEW
    """)
    is_edit_map = {row[0]: int(row[1]) for row in cur.fetchall()}

    # review_group_id: we use raw_thread_id as the group identifier,
    # which is what ties original and edit together in RAW_REVIEW.
    # It maps directly onto D_REVIEW.review_group_id per Section 5.7.6.

    cur.execute("SELECT * FROM RAW_REVIEW")
    raw_rows = cur.fetchall()
    col_names = [d[0] for d in cur.description]
    col = {name: idx for idx, name in enumerate(col_names)}

    obs_id = 1
    observations = []
    unmatched_sentences = 0
    total_sentences = 0

    for row in raw_rows:
        capture_id = row[col["raw_capture_id"]]
        thread_id = row[col["raw_thread_id"]]
        captured_at = row[col["captured_at"]]
        review_text = row[col["review_text"]]
        is_edit = is_edit_map[capture_id]

        sentences = sent_tokenize(review_text)
        total_sentences += len(sentences)

        for sentence in sentences:
            aspect_code = identify_aspect(sentence, keyword_pairs)
            if aspect_code is None:
                unmatched_sentences += 1
                continue

            polarity = derive_polarity(sentence)
            subjectivity = derive_subjectivity(sentence)

            # drop structurally neutral sentences: polarity=0 and
            # subjectivity=0 together reliably flags factual statements
            # with no evaluative content ("Breakfast is served at 7am").
            # These contribute no sentiment signal and dilute measures.
            if polarity == 0.0 and subjectivity == 0.0:
                unmatched_sentences += 1
                continue

            emotions = derive_emotions(sentence, polarity)
            strength = derive_sentiment_strength(polarity, subjectivity)

            observations.append((
                obs_id,
                capture_id,
                thread_id,
                captured_at,
                is_edit,
                row[col["platform_id"]],
                row[col["platform_name"]],
                row[col["platform_url"]],
                row[col["service_source_id"]],
                row[col["service_name"]],
                row[col["service_type"]],
                row[col["municipality_name"]],
                row[col["star_rating_official"]],
                row[col["price_tier_raw"]],
                thread_id,           # review_group_id = raw_thread_id
                review_text,
                row[col["star_rating_reviewer"]],
                row[col["language_raw"]],
                row[col["reviewer_nationality"]],
                row[col["reviewer_age_group"]],
                row[col["reviewer_gender"]],
                row[col["trip_type_raw"]],
                row[col["trip_purpose_raw"]],
                sentence,
                aspect_code,
                polarity,
                subjectivity,
                emotions["joy"],
                emotions["trust"],
                emotions["fear"],
                emotions["surprise"],
                emotions["sadness"],
                emotions["disgust"],
                emotions["anger"],
                emotions["anticipation"],
                strength,
                None,                # model_confidence always NULL
            ))
            obs_id += 1

    conn.executemany("""
        INSERT INTO TRANSFORMED_OBSERVATIONS VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, observations)
    conn.commit()

    return len(observations), total_sentences, unmatched_sentences


def main():
    conn = sqlite3.connect("warehouse.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    print("Creating staging table...")
    create_staging_table(conn)

    print("Loading keyword dictionary...")
    keyword_pairs = load_keywords(conn)
    print(f"  {len(keyword_pairs)} keyword-aspect pairs loaded.")

    print("Running transformation...")
    n_obs, n_sent, n_unmatched = transform(conn, keyword_pairs)

    print(f"\nTransformation complete.")
    print(f"  Total sentences processed : {n_sent}")
    print(f"  Sentences matched (observations): {n_obs}")
    print(f"  Sentences unmatched (dropped)   : {n_unmatched}")
    print(f"  Match rate: {n_obs/n_sent:.1%}")

    cur = conn.cursor()
    cur.execute("SELECT aspect_code, COUNT(*) FROM TRANSFORMED_OBSERVATIONS GROUP BY aspect_code ORDER BY COUNT(*) DESC LIMIT 10")
    print("\nTop 10 aspects by observation count:")
    for row in cur.fetchall():
        print(f"  {row[0]:25s} {row[1]}")

    cur.execute("""
        SELECT AVG(polarity_score), AVG(subjectivity_score), AVG(sentiment_strength)
        FROM TRANSFORMED_OBSERVATIONS
    """)
    avg = cur.fetchone()
    print(f"\nMean polarity   : {avg[0]:.4f}")
    print(f"Mean subjectivity: {avg[1]:.4f}")
    print(f"Mean strength   : {avg[2]:.4f}")

    # spot check: one observation in full
    cur.execute("SELECT sentence, aspect_code, polarity_score, subjectivity_score, joy_score, anger_score, sentiment_strength FROM TRANSFORMED_OBSERVATIONS LIMIT 1")
    row = cur.fetchone()
    print(f"\nSample observation:")
    print(f"  Sentence    : {row[0]}")
    print(f"  Aspect      : {row[1]}")
    print(f"  Polarity    : {row[2]}")
    print(f"  Subjectivity: {row[3]}")
    print(f"  Joy         : {row[4]}")
    print(f"  Anger       : {row[5]}")
    print(f"  Strength    : {row[6]}")

    conn.close()


if __name__ == "__main__":
    main()
