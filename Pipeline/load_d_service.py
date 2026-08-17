"""
Loads D_SERVICE from TRANSFORMED_OBSERVATIONS.

Applies the four transformation rules specified in Section 5.7.3:
  Rule 1: Standardise descriptive and classification attributes.
          service_name is preserved; platform_service_id is the raw
          source identifier kept for traceability; raw service_type
          is mapped onto controlled service_category and
          service_subcategory values; star_rating and price_tier_raw
          are validated and standardised.
  Rule 2: Resolve geographic reference. municipality_name is matched
          against D_LOCATION (already populated) to produce
          location_key. This avoids repeating geographic attributes
          in D_SERVICE and ensures the hierarchy-consistent location
          reference documented in 4.5.3.
  Rule 3: Apply SCD Type 2 versioning logic. Services are grouped by
          their distinct (star_rating, price_tier) combinations, each
          such combination becoming one version, ordered by the
          earliest date that combination was observed. For a service
          with only one version, that version is open-ended
          (valid_to = SCD2_OPEN, is_current = 1). For a service with
          more than one version, in this instance the three services
          listed in service_data.py's SCD2_CHANGES, each earlier
          version is closed the day before the next version begins
          (valid_to = next_valid_from - 1 day, is_current = 0), and
          only the most recent version remains open. This is what
          allows a temporally scoped lookup, such as the one performed
          during the fact table load (Section 5.7.8), to resolve the
          correct version of a service for any given review date.
  Rule 4: Generate surrogate key service_key and load the record.

SCD Type 2 sentinel: valid_to = '9999-12-31' for the current row,
consistent with Kimball convention and the warehouse schema.
"""

import sqlite3
from datetime import date, timedelta

SCD2_OPEN = "9999-12-31"

# Rule 1: map raw service_type onto controlled service_category and
# service_subcategory. The raw labels come from platform_data.py and
# service_data.py; the target values are the three controlled categories
# defined in the D_SERVICE CHECK constraint.
SERVICE_CATEGORY_MAP = {
    # Accommodation
    "Hotel":          ("Accommodation", "Hotel"),
    "Boutique Hotel": ("Accommodation", "Boutique Hotel"),
    "Guesthouse":     ("Accommodation", "Guesthouse"),
    "Hostel":         ("Accommodation", "Hostel"),
    "Inn":            ("Accommodation", "Inn"),
    "Resort":         ("Accommodation", "Resort"),
    # Restaurant/Bar
    "Restaurant":     ("Restaurant/Bar", "Restaurant"),
    "Bar":            ("Restaurant/Bar", "Bar"),
    # Tourist Site
    "Historical Monument": ("Tourist Site", "Historical Monument"),
    "Cultural Attraction": ("Tourist Site", "Cultural Attraction"),
    "Religious Site":      ("Tourist Site", "Religious Site"),
    "Nature Reserve":      ("Tourist Site", "Nature Reserve"),
}

# Rule 1: validate star_rating (only meaningful for Accommodation)
def validate_star_rating(star_rating, service_category):
    if service_category != "Accommodation":
        return None
    if star_rating is None:
        return None
    try:
        val = int(star_rating)
        return val if 1 <= val <= 5 else None
    except (TypeError, ValueError):
        return None

# Rule 1: standardise price_tier from raw label to controlled values
PRICE_TIER_MAP = {
    "budget":    "Low",
    "mid-range": "Medium",
    "premium":   "High",
    "luxury":    "Luxury",
}

def standardise_price_tier(raw):
    if raw is None:
        return None
    return PRICE_TIER_MAP.get(raw.lower().strip())


def load_d_service(conn):
    cur = conn.cursor()

    # Rule 2: build municipality -> location_key lookup from D_LOCATION
    cur.execute("SELECT municipality, location_key FROM D_LOCATION")
    location_lookup = {row[0]: row[1] for row in cur.fetchall()}

    # collect distinct (service, attribute-combination) pairs from the
    # staging table. A service with a genuine attribute change (see
    # SCD2_CHANGES) produces more than one row here, one per distinct
    # (star_rating_official, price_tier_raw) combination it carries.
    cur.execute("""
        SELECT
            service_source_id,
            service_name,
            service_type,
            municipality_name,
            star_rating_official,
            price_tier_raw,
            MIN(captured_at) AS first_seen
        FROM TRANSFORMED_OBSERVATIONS
        GROUP BY service_source_id, service_name, service_type,
                 municipality_name, star_rating_official, price_tier_raw
        ORDER BY service_source_id, first_seen
    """)
    raw_rows = cur.fetchall()

    # group by service_source_id, preserving chronological order
    # within each service (the query above already orders by first_seen)
    from collections import OrderedDict
    versions_by_service = OrderedDict()
    for row in raw_rows:
        service_source_id = row[0]
        versions_by_service.setdefault(service_source_id, []).append(row)

    rows = []
    service_key = 1

    for service_source_id, versions in versions_by_service.items():
        n_versions = len(versions)

        for i, (svc_id, service_name, service_type, municipality_name,
                star_rating_official, price_tier_raw, first_seen) in enumerate(versions):

            # Rule 1: classify
            category_pair = SERVICE_CATEGORY_MAP.get(service_type)
            if category_pair is None:
                raise ValueError(f"Unmapped service_type: '{service_type}'")
            service_category, service_subcategory = category_pair

            star_rating = validate_star_rating(star_rating_official, service_category)
            price_tier = standardise_price_tier(price_tier_raw)

            # Rule 2: resolve location
            location_key = location_lookup.get(municipality_name)
            if location_key is None:
                raise ValueError(f"Municipality not found in D_LOCATION: '{municipality_name}'")

            # Rule 3: SCD Type 2. valid_from is this version's first
            # observed date. If this is not the most recent version,
            # valid_to closes the day before the next version begins
            # and is_current is 0; the most recent version stays open.
            valid_from = first_seen[:10]

            if i < n_versions - 1:
                next_first_seen = versions[i + 1][6][:10]
                next_valid_from = date.fromisoformat(next_first_seen)
                valid_to = (next_valid_from - timedelta(days=1)).isoformat()
                is_current = 0
            else:
                valid_to = SCD2_OPEN
                is_current = 1

            # Rule 4: load
            rows.append((
                service_key,
                svc_id,
                location_key,
                service_name,
                service_category,
                service_subcategory,
                star_rating,
                price_tier,
                is_current,
                valid_from,
                valid_to,
            ))
            service_key += 1

    conn.executemany(
        """INSERT INTO D_SERVICE (
               service_key, platform_service_id, location_key, service_name,
               service_category, service_subcategory, star_rating, price_tier,
               is_current, valid_from, valid_to
           ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    conn.commit()
    return len(rows)


def main():
    conn = sqlite3.connect("warehouse.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    n = load_d_service(conn)
    print(f"D_SERVICE loaded: {n} rows.")

    cur = conn.cursor()

    cur.execute("SELECT service_category, COUNT(*) FROM D_SERVICE GROUP BY service_category")
    print("\nRows per service_category:", cur.fetchall())

    cur.execute("SELECT COUNT(*) FROM D_SERVICE WHERE is_current = 1")
    print("Current rows (is_current=1):", cur.fetchone()[0])

    cur.execute("SELECT COUNT(*) FROM D_SERVICE WHERE valid_to = '9999-12-31'")
    print("Open-ended rows (valid_to=9999-12-31):", cur.fetchone()[0])

    cur.execute("""
        SELECT platform_service_id, COUNT(*) AS n_versions
        FROM D_SERVICE GROUP BY platform_service_id HAVING n_versions > 1
    """)
    multi = cur.fetchall()
    print("Services with more than one version:", multi or "none")

    # verify FK integrity: every service references a real location_key
    cur.execute("""
        SELECT COUNT(*) FROM D_SERVICE s
        LEFT JOIN D_LOCATION l ON s.location_key = l.location_key
        WHERE l.location_key IS NULL
    """)
    orphan_fks = cur.fetchone()[0]
    print("Services with invalid location_key:", orphan_fks or "none")

    # detailed view of the three SCD2-flagged services
    print("\nSCD2 version detail for SVC_002, SVC_015, SVC_033:")
    cur.execute("""
        SELECT platform_service_id, star_rating, price_tier, valid_from, valid_to, is_current
        FROM D_SERVICE WHERE platform_service_id IN ('SVC_002','SVC_015','SVC_033')
        ORDER BY platform_service_id, valid_from
    """)
    for row in cur.fetchall():
        print(f"  {row}")

    conn.close()


if __name__ == "__main__":
    main()
