"""
Loads D_TRAVEL_SEGMENT from TRANSFORMED_OBSERVATIONS.

Applies the three transformation rules specified in Section 5.7.5:
  Rule 1: Extract and standardise segment attributes. Raw trip labels
          such as "Travelled with family" are normalised into controlled
          travel_party_type values. Null values are preserved where
          source data is unavailable, per the thesis's explicit note
          that imputation is not applied.
  Rule 2: Generate a stable travel_segment_code from the standardised
          combination. The format documented in 5.7.5 is illustrated
          as FR_25_34_FAMILY_LEISURE; we follow that pattern exactly,
          using ISO 3166-1 alpha-2 nationality codes where possible,
          with NULL attributes represented as UNKNOWN in the code so
          the code remains a non-null, stable natural key even for
          partially unknown segments.
  Rule 3: Resolve surrogate key. If a code already exists in
          D_TRAVEL_SEGMENT the existing key is reused; if not, a new
          record is inserted. This ensures the dimension contains only
          combinations observed in the actual dataset.
"""

import sqlite3

# Rule 1: normalise raw trip type labels -> controlled travel_party_type
TRIP_TYPE_MAP = {
    "Travelled solo":         "Solo",
    "Travelled as a couple":  "Couple",
    "Travelled with family":  "Family",
    "Travelled with friends": "Friends",
}

# Rule 1: normalise raw trip purpose -> controlled trip_purpose
TRIP_PURPOSE_MAP = {
    "Leisure":  "Leisure",
    "Business": "Business",
}

# Rule 2: nationality -> short code for segment key.
# Common nationalities in the dataset; others fall through to UNKNOWN.
NATIONALITY_CODE = {
    "Portugal":        "PT",
    "Spain":           "ES",
    "France":          "FR",
    "Germany":         "DE",
    "United Kingdom":  "UK",
    "Brazil":          "BR",
    "United States":   "US",
    "Italy":           "IT",
    "Netherlands":     "NL",
    "Ireland":         "IE",
}


def make_segment_code(nationality, age_group, gender, travel_party_type, trip_purpose):
    """Generates a stable natural key from the standardised attributes.
    NULL attributes contribute 'UNKNOWN' so the code is always non-null
    and always unique to its combination."""
    parts = [
        NATIONALITY_CODE.get(nationality, "UNKNOWN") if nationality else "UNKNOWN",
        age_group.replace("-", "_") if age_group else "UNKNOWN",
        gender.upper().replace("/", "_").replace(" ", "_") if gender else "UNKNOWN",
        travel_party_type.upper() if travel_party_type else "UNKNOWN",
        trip_purpose.upper() if trip_purpose else "UNKNOWN",
    ]
    return "_".join(parts)


def load_d_travel_segment(conn):
    cur = conn.cursor()

    # Rule 1: collect distinct raw reviewer/trip attribute combinations
    cur.execute("""
        SELECT DISTINCT
            reviewer_nationality,
            reviewer_age_group,
            reviewer_gender,
            trip_type_raw,
            trip_purpose_raw
        FROM TRANSFORMED_OBSERVATIONS
        ORDER BY reviewer_nationality, reviewer_age_group,
                 reviewer_gender, trip_type_raw, trip_purpose_raw
    """)
    raw_segments = cur.fetchall()

    segment_key = 1
    code_to_key = {}
    rows = []

    for (nationality, age_group, gender, trip_type_raw, trip_purpose_raw) in raw_segments:

        # Rule 1: standardise
        travel_party_type = TRIP_TYPE_MAP.get(trip_type_raw) if trip_type_raw else None
        trip_purpose = TRIP_PURPOSE_MAP.get(trip_purpose_raw) if trip_purpose_raw else None

        # Rule 2: generate code
        code = make_segment_code(nationality, age_group, gender,
                                  travel_party_type, trip_purpose)

        # Rule 3: reuse existing key if code already seen
        if code in code_to_key:
            continue

        code_to_key[code] = segment_key
        rows.append((
            segment_key,
            code,
            nationality,
            age_group,
            gender,
            travel_party_type,
            trip_purpose,
        ))
        segment_key += 1

    conn.executemany(
        """INSERT INTO D_TRAVEL_SEGMENT
           (travel_segment_key, travel_segment_code, nationality,
            age_group, gender, travel_party_type, trip_purpose)
           VALUES (?,?,?,?,?,?,?)""",
        rows,
    )
    conn.commit()
    return len(rows), code_to_key


def main():
    conn = sqlite3.connect("warehouse.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    n, code_to_key = load_d_travel_segment(conn)
    print(f"D_TRAVEL_SEGMENT loaded: {n} rows.")

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM D_TRAVEL_SEGMENT WHERE travel_party_type IS NULL")
    print("Rows with null travel_party_type:", cur.fetchone()[0])

    cur.execute("SELECT COUNT(*) FROM D_TRAVEL_SEGMENT")
    total = cur.fetchone()[0]
    print("Total segment combinations:", total)

    # verify the code format matches the thesis example pattern
    cur.execute("SELECT travel_segment_code FROM D_TRAVEL_SEGMENT WHERE nationality='France' AND age_group='25-34' AND travel_party_type='Family' AND trip_purpose='Leisure' LIMIT 1")
    row = cur.fetchone()
    print(f"\nCode for French/25-34/Family/Leisure: {row[0] if row else 'NOT FOUND'}")
    print("Expected pattern from 5.7.5: FR_25_34_FAMILY_LEISURE")

    # spot check a few codes
    cur.execute("SELECT travel_segment_key, travel_segment_code, nationality, travel_party_type FROM D_TRAVEL_SEGMENT LIMIT 5")
    print("\nSample rows:")
    for row in cur.fetchall():
        print(f"  {row}")

    conn.close()


if __name__ == "__main__":
    main()
