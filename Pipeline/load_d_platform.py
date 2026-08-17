"""
Loads D_PLATFORM from TRANSFORMED_OBSERVATIONS.

Applies the three transformation rules specified in Section 5.7.7:
  Rule 1: Standardise platform identification - platform_id becomes
          platform_code, platform_name is cleaned to a consistent
          representation.
  Rule 2: Classify platform metadata - assign platform_type from a
          controlled mapping; rename platform_url from the source
          field name (platform_url -> platform_website in D_PLATFORM,
          as documented in 5.7.7). country_scope and other source
          fields are dropped.
  Rule 3: Generate surrogate key platform_key and load the record.

Each distinct platform_id in TRANSFORMED_OBSERVATIONS becomes exactly
one row in D_PLATFORM. D_PLATFORM uses SCD Type 1, no versioning.
"""

import sqlite3

PLATFORM_TYPE_MAP = {
    "TA":  "Review Website",
    "GR":  "Review Website",
    "BK":  "Booking Platform",
    "FB":  "Social Media",
    "PTG": "Other",
}


def load_d_platform(conn):
    cur = conn.cursor()

    # collect distinct platforms from the staging table
    cur.execute("""
        SELECT DISTINCT platform_id, platform_name, platform_url
        FROM TRANSFORMED_OBSERVATIONS
        ORDER BY platform_id
    """)
    raw_platforms = cur.fetchall()

    rows = []
    for platform_key, (platform_id, platform_name, platform_url) in enumerate(raw_platforms, start=1):
        platform_type = PLATFORM_TYPE_MAP.get(platform_id)
        if platform_type is None:
            raise ValueError(f"No platform_type mapping for platform_id '{platform_id}'")

        rows.append((
            platform_key,
            platform_id,          # -> platform_code (Rule 1)
            platform_name,        # -> platform_name (cleaned, already consistent)
            platform_type,        # -> platform_type (Rule 2)
            platform_url,         # -> platform_website (Rule 2, rename)
        ))

    conn.executemany(
        """INSERT INTO D_PLATFORM
           (platform_key, platform_code, platform_name, platform_type, platform_website)
           VALUES (?,?,?,?,?)""",
        rows,
    )
    conn.commit()
    return len(rows)


def main():
    conn = sqlite3.connect("warehouse.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    n = load_d_platform(conn)
    print(f"D_PLATFORM loaded: {n} rows.")

    cur = conn.cursor()
    cur.execute("SELECT * FROM D_PLATFORM ORDER BY platform_key;")
    print("\nD_PLATFORM contents:")
    for row in cur.fetchall():
        print(f"  {row}")

    # verify all four platform_type domain values are represented
    cur.execute("SELECT DISTINCT platform_type FROM D_PLATFORM ORDER BY platform_type")
    types = [r[0] for r in cur.fetchall()]
    print(f"\nplatform_type values present: {types}")
    expected = {"Review Website", "Booking Platform", "Social Media", "Other"}
    missing = expected - set(types)
    print(f"Missing from domain: {missing or 'none'}")

    conn.close()


if __name__ == "__main__":
    main()
