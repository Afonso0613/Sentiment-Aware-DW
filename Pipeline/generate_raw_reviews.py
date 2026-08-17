"""
Assembles RAW_REVIEW from service_data, platform_data and
fragment_library.

"""

import random
import sqlite3
from datetime import date, timedelta

from service_data import SERVICES, SCD2_CHANGES
from platform_data import PLATFORMS
from fragment_library import FRAGMENTS

random.seed(42)

DATE_START = date(2022, 1, 1)
DATE_END = date(2025, 12, 31)
DATE_SPAN_DAYS = (DATE_END - DATE_START).days


NEGATIVE_SERVICES = {
    "SVC_005", "SVC_017", "SVC_013", "SVC_045", "SVC_047", "SVC_059",  # accommodation (6)
    "SVC_030", "SVC_029", "SVC_065", "SVC_067",                        # restaurant/bar (4)
    "SVC_038", "SVC_076",                                              # tourist site (2)
}
MIXED_SERVICES = {
    "SVC_003", "SVC_007", "SVC_010", "SVC_018", "SVC_014",
    "SVC_042", "SVC_043", "SVC_046", "SVC_055", "SVC_057",             # accommodation (10)
    "SVC_023", "SVC_028", "SVC_025", "SVC_062", "SVC_066", "SVC_070",  # restaurant/bar (6)
    "SVC_035", "SVC_040", "SVC_074", "SVC_078",                        # tourist site (4)
}
# everything else is mostly_positive (48 services)

SENTIMENT_WEIGHTS = {
    "mostly_positive": {"strong_positive": 0.40, "mild_positive": 0.35, "neutral": 0.15, "mild_negative": 0.08, "strong_negative": 0.02},
    "mixed":           {"strong_positive": 0.20, "mild_positive": 0.20, "neutral": 0.20, "mild_negative": 0.20, "strong_negative": 0.20},
    "mostly_negative": {"strong_positive": 0.03, "mild_positive": 0.07, "neutral": 0.15, "mild_negative": 0.35, "strong_negative": 0.40},
}

STAR_RATING_BY_PROFILE = {
    "mostly_positive": [3.5, 4.0, 4.0, 4.5, 4.5, 4.5, 5.0, 5.0],
    "mixed":           [2.0, 2.5, 3.0, 3.0, 3.5, 4.0, 4.5],
    "mostly_negative": [1.0, 1.5, 1.5, 2.0, 2.0, 2.5, 3.0],
}

# ---------------------------------------------------------------------
ACCOMMODATION_ASPECTS = [
    "LOCATION", "VIEW", "ACCESSIBILITY", "PARKING", "SAFETY",
    "CLEANLINESS", "ROOM_QUALITY", "NOISE_LEVEL", "FACILITIES_CONDITION", "TEMPERATURE_CONTROL",
    "STAFF_QUALITY", "CHECK_IN_EXPERIENCE", "COMMUNICATION",
    "BREAKFAST_QUALITY", "WIFI_CONNECTIVITY", "AMENITIES_VARIETY",
    "VALUE_FOR_MONEY", "HIDDEN_COSTS", "BOOKING_PROCESS",
    "OVERALL_EXPERIENCE", "ATMOSPHERE", "FAMILY_FRIENDLINESS", "DECOR_AND_DESIGN",
]
RESTAURANT_ASPECTS = [
    "LOCATION", "ACCESSIBILITY", "PARKING", "SAFETY",
    "CLEANLINESS", "NOISE_LEVEL",
    "STAFF_QUALITY", "SERVICE_EFFICIENCY", "COMMUNICATION",
    "FOOD_QUALITY", "MENU_VARIETY", "WIFI_CONNECTIVITY",
    "VALUE_FOR_MONEY", "HIDDEN_COSTS", "BOOKING_PROCESS",
    "OVERALL_EXPERIENCE", "ATMOSPHERE", "CROWDING", "ENTERTAINMENT_OPTIONS",
    "FAMILY_FRIENDLINESS", "DECOR_AND_DESIGN",
]
TOURIST_SITE_ASPECTS = [
    "LOCATION", "VIEW", "ACCESSIBILITY", "PARKING", "SAFETY",
    "CLEANLINESS", "PRESERVATION_STATE", "FACILITIES_CONDITION",
    "STAFF_QUALITY", "COMMUNICATION",
    "INFORMATIONAL_VALUE",
    "VALUE_FOR_MONEY", "BOOKING_PROCESS",
    "OVERALL_EXPERIENCE", "ATMOSPHERE", "CROWDING", "ENTERTAINMENT_OPTIONS",
    "FAMILY_FRIENDLINESS", "DECOR_AND_DESIGN",
]

ACCOMMODATION_TYPES = {"Hotel", "Boutique Hotel", "Guesthouse", "Hostel", "Inn", "Resort"}
RESTAURANT_TYPES = {"Restaurant", "Bar"}
SITE_TYPES = {"Historical Monument", "Cultural Attraction", "Religious Site", "Nature Reserve"}


def category_for(service_type):
    if service_type in ACCOMMODATION_TYPES:
        return "accommodation"
    if service_type in RESTAURANT_TYPES:
        return "restaurant"
    if service_type in SITE_TYPES:
        return "tourist_site"
    raise ValueError(f"Unclassified service_type: {service_type}")


ASPECTS_BY_CATEGORY = {
    "accommodation": ACCOMMODATION_ASPECTS,
    "restaurant": RESTAURANT_ASPECTS,
    "tourist_site": TOURIST_SITE_ASPECTS,
}

# fragment lookup: (aspect_code, tier) -> text
FRAGMENT_LOOKUP = {(code, tier): text for code, tier, text in FRAGMENTS}


def profile_for(service_source_id):
    if service_source_id in NEGATIVE_SERVICES:
        return "mostly_negative"
    if service_source_id in MIXED_SERVICES:
        return "mixed"
    return "mostly_positive"


def pick_tier(profile, available_tiers):
    weights_full = SENTIMENT_WEIGHTS[profile]
    weights = {t: weights_full[t] for t in available_tiers}
    total = sum(weights.values())
    weights = {t: w / total for t, w in weights.items()}
    return random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]


def build_review_text(category, profile, exclude_aspects=None):
    candidate_aspects = ASPECTS_BY_CATEGORY[category]
    if exclude_aspects:
        candidate_aspects = [a for a in candidate_aspects if a not in exclude_aspects]
    n_aspects = random.randint(2, 4)
    chosen_aspects = random.sample(candidate_aspects, k=min(n_aspects, len(candidate_aspects)))

    pairs = []
    for aspect in chosen_aspects:
        available_tiers = sorted({tier for (code, tier) in FRAGMENT_LOOKUP if code == aspect})
        tier = pick_tier(profile, available_tiers)
        pairs.append((aspect, tier))

    text = " ".join(FRAGMENT_LOOKUP[p] for p in pairs)
    return text, pairs


def build_edit_text(category, profile, original_pairs):
    pairs = list(original_pairs)

    if random.random() < 0.6 and pairs:
        # change opinion on one existing aspect
        idx = random.randrange(len(pairs))
        aspect, _old_tier = pairs[idx]
        available_tiers = sorted({tier for (code, tier) in FRAGMENT_LOOKUP if code == aspect})
        new_tier = pick_tier(profile, available_tiers)
        pairs[idx] = (aspect, new_tier)
    else:
        # add one new aspect not already mentioned
        existing_aspects = {a for a, _ in pairs}
        candidate_aspects = [a for a in ASPECTS_BY_CATEGORY[category] if a not in existing_aspects]
        if candidate_aspects:
            aspect = random.choice(candidate_aspects)
            available_tiers = sorted({tier for (code, tier) in FRAGMENT_LOOKUP if code == aspect})
            tier = pick_tier(profile, available_tiers)
            pairs.append((aspect, tier))

    text = " ".join(FRAGMENT_LOOKUP[p] for p in pairs)
    return text, pairs


def review_volume_for_service(service):
    """Derive a thread count from photo_count and overall_ranking as a
    popularity proxy. Returns a raw (unnormalised) weight; normalised
    to sum to TARGET_THREADS across all services afterwards."""
    overall_ranking = service[6]
    photo_count = service[7]
    return photo_count / max(overall_ranking, 1)


def resolve_service_attrs_at(service_source_id, base_star_rating, base_price_tier, review_date):
    change = SCD2_CHANGES.get(service_source_id)
    if change is None:
        return base_star_rating, base_price_tier

    change_date = date.fromisoformat(change["change_date"])
    attrs = change["changed"] if review_date >= change_date else change["original"]

    star_rating = attrs.get("star_rating", base_star_rating)
    price_tier = attrs.get("price_tier_raw", base_price_tier)
    return star_rating, price_tier


TARGET_THREADS = 900
TARGET_EDITS = 100

REVIEWER_NATIONALITIES = [
    "Portugal", "Spain", "France", "Germany", "United Kingdom",
    "Brazil", "United States", "Italy", "Netherlands", "Ireland",
]
AGE_GROUPS = ["<18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
GENDERS = ["Female", "Male", "Other/Unknown"]
TRIP_TYPE_LABELS = [
    "Travelled solo", "Travelled as a couple",
    "Travelled with family", "Travelled with friends",
]
TRIP_PURPOSES = ["Leisure", "Business"]
LANGUAGES_WEIGHTED = (["en"] * 7) + (["pt"] * 2) + (["es"] * 1) + (["fr"] * 1) + (["de"] * 1)

REVIEW_TITLES = [
    "Great stay", "Would recommend", "Mixed feelings", "Not what we expected",
    "Lovely experience", "Decent but unremarkable", "Worth a visit",
    "Disappointing", "Exceeded expectations", "Average at best",
]


def maybe_null(value, p_null=0.18):
    return None if random.random() < p_null else value


def random_date():
    offset = random.randint(0, DATE_SPAN_DAYS)
    return DATE_START + timedelta(days=offset)


def build_threads():
    weights = [review_volume_for_service(s) for s in SERVICES]
    total_weight = sum(weights)
    raw_counts = [w / total_weight * TARGET_THREADS for w in weights]

    counts = [min(max(round(c), 6), 20) for c in raw_counts]

    n = len(counts)
    while sum(counts) < TARGET_THREADS:
        candidates = [i for i in range(n) if counts[i] < 20]
        if not candidates:
            break
        i = max(candidates, key=lambda i: raw_counts[i] - counts[i])
        counts[i] += 1
    while sum(counts) > TARGET_THREADS:
        candidates = [i for i in range(n) if counts[i] > 6]
        if not candidates:
            break
        i = min(candidates, key=lambda i: raw_counts[i] - counts[i])
        counts[i] -= 1

    threads = []
    thread_seq = 1
    for service, count in zip(SERVICES, counts):
        service_source_id = service[0]
        category = category_for(service[2])
        profile = profile_for(service_source_id)
        for _ in range(count):
            threads.append({
                "thread_id": f"THREAD_{thread_seq:04d}",
                "service": service,
                "category": category,
                "profile": profile,
                "captured_at": random_date(),
            })
            thread_seq += 1
    return threads


def build_rows(threads):
    rows = []
    capture_seq = 1

    platform_lookup = {p[0]: p for p in PLATFORMS}
    platform_ids = list(platform_lookup.keys())

    edit_threads = random.sample(threads, k=min(TARGET_EDITS, len(threads)))
    edit_thread_ids = {t["thread_id"] for t in edit_threads}

    for thread in threads:
        service = thread["service"]
        service_source_id, service_name, service_type, municipality_name, \
            star_rating_official, price_tier_raw, overall_ranking, photo_count = service

        platform = platform_lookup[random.choice(platform_ids)]
        platform_id, platform_name, platform_url, country_scope = platform

        nationality = maybe_null(random.choice(REVIEWER_NATIONALITIES))
        age_group = maybe_null(random.choice(AGE_GROUPS))
        gender = maybe_null(random.choice(GENDERS))
        trip_type_raw = maybe_null(random.choice(TRIP_TYPE_LABELS))
        trip_purpose_raw = maybe_null(random.choice(TRIP_PURPOSES))
        language_raw = random.choice(LANGUAGES_WEIGHTED)

        star_rating = random.choice(STAR_RATING_BY_PROFILE[thread["profile"]])
        review_text, original_pairs = build_review_text(thread["category"], thread["profile"])
        review_title = random.choice(REVIEW_TITLES)

        # resolve this capture's service attributes as they would
        # genuinely have been reported on this specific date
        capture_star_rating_official, capture_price_tier_raw = resolve_service_attrs_at(
            service_source_id, star_rating_official, price_tier_raw, thread["captured_at"]
        )

        rows.append((
            f"CAP_{capture_seq:05d}", thread["thread_id"], thread["captured_at"].isoformat(),
            platform_id, platform_name, platform_url, country_scope,
            service_source_id, service_name, service_type, municipality_name,
            capture_star_rating_official, capture_price_tier_raw, overall_ranking, photo_count,
            review_title, review_text, star_rating, language_raw,
            nationality, age_group, gender, trip_type_raw, trip_purpose_raw,
        ))
        capture_seq += 1

        if thread["thread_id"] in edit_thread_ids:
            edit_offset = random.randint(1, 60)
            edit_date = min(thread["captured_at"] + timedelta(days=edit_offset), DATE_END)
            edit_star = max(1.0, min(5.0, star_rating + random.choice([-1.0, -0.5, 0.5, 1.0])))
            edit_text, _ = build_edit_text(thread["category"], thread["profile"], original_pairs)

            # the edit is a separate capture on a separate date, so its
            # service attributes are resolved independently: if the
            # edit falls on the other side of a service's change_date
            # from the original, it should reflect the new attributes
            edit_star_rating_official, edit_price_tier_raw = resolve_service_attrs_at(
                service_source_id, star_rating_official, price_tier_raw, edit_date
            )

            rows.append((
                f"CAP_{capture_seq:05d}", thread["thread_id"], edit_date.isoformat(),
                platform_id, platform_name, platform_url, country_scope,
                service_source_id, service_name, service_type, municipality_name,
                edit_star_rating_official, edit_price_tier_raw, overall_ranking, photo_count,
                review_title, edit_text, edit_star, language_raw,
                nationality, age_group, gender, trip_type_raw, trip_purpose_raw,
            ))
            capture_seq += 1

    return rows


def main():
    threads = build_threads()
    print(f"Generated {len(threads)} review threads.")

    rows = build_rows(threads)
    print(f"Generated {len(rows)} total RAW_REVIEW rows (threads + edits).")

    conn = sqlite3.connect("warehouse.db")
    conn.executemany(
        """INSERT INTO RAW_REVIEW (
               raw_capture_id, raw_thread_id, captured_at,
               platform_id, platform_name, platform_url, country_scope,
               service_source_id, service_name, service_type, municipality_name,
               star_rating_official, price_tier_raw, overall_ranking, photo_count,
               review_title, review_text, star_rating_reviewer, language_raw,
               reviewer_nationality, reviewer_age_group, reviewer_gender,
               trip_type_raw, trip_purpose_raw
           ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    conn.commit()

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM RAW_REVIEW;")
    print("\nRAW_REVIEW row count in database:", cur.fetchone()[0])

    cur.execute("SELECT COUNT(DISTINCT raw_thread_id) FROM RAW_REVIEW;")
    print("Distinct threads:", cur.fetchone()[0])

    cur.execute("""
        SELECT raw_thread_id, COUNT(*) c FROM RAW_REVIEW
        GROUP BY raw_thread_id HAVING c > 1
    """)
    edited = cur.fetchall()
    print("Threads with more than one capture (edits):", len(edited))

    cur.execute("SELECT MIN(captured_at), MAX(captured_at) FROM RAW_REVIEW;")
    print("Date range:", cur.fetchone())

    cur.execute("""
        SELECT service_source_id, COUNT(*) FROM RAW_REVIEW
        GROUP BY service_source_id ORDER BY COUNT(*) DESC LIMIT 5
    """)
    print("Top 5 most-reviewed services:", cur.fetchall())

    cur.execute("""
        SELECT service_source_id, COUNT(*) FROM RAW_REVIEW
        GROUP BY service_source_id ORDER BY COUNT(*) ASC LIMIT 5
    """)
    print("Bottom 5 least-reviewed services:", cur.fetchall())

    conn.close()


if __name__ == "__main__":
    main()
