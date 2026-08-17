"""
Populates RAW_ASPECT_KEYWORD.

Keywords are derived from the fragment library (fragment_library.py)
rather than hand-authored independently: the fragment texts are
aspect-tagged by construction, so the vocabulary that naturally
appears in each aspect's fragments is the right source for keywords
the ETL step will later match against review text.

Selection principle: kept keywords are genuinely discriminative for
their aspect, appearing naturally in the fragment vocabulary for that
aspect and unlikely to dominate fragments of unrelated aspects. Generic
sentiment words (great, poor, disappointing) are excluded even if they
appear in the fragments, since they carry no aspect signal on their own.

Multi-word phrases (e.g. "check-in", "air conditioning") are included
where a single word would be ambiguous: "check" alone would match too
broadly, but "check-in" is specific.

This dictionary is an ETL-time lookup structure only, per Section 5.7.4
of the thesis. It is not loaded into the warehouse, it lives in
RAW_ASPECT_KEYWORD and is used during the transformation phase to
identify which aspect a text fragment belongs to.
"""

import sqlite3

# (keyword, aspect_code)
KEYWORDS = [
    # LOCATION
    ("location", "LOCATION"),
    ("located", "LOCATION"),
    ("city centre", "LOCATION"),
    ("attractions", "LOCATION"),
    ("central", "LOCATION"),
    ("transport", "LOCATION"),
    ("public transport", "LOCATION"),

    # VIEW
    ("view", "VIEW"),
    ("overlooking", "VIEW"),
    ("terrace", "VIEW"),
    ("courtyard", "VIEW"),
    ("outlook", "VIEW"),

    # ACCESSIBILITY
    ("accessibility", "ACCESSIBILITY"),
    ("accessible", "ACCESSIBILITY"),
    ("wheelchair", "ACCESSIBILITY"),
    ("ramps", "ACCESSIBILITY"),
    ("stairs", "ACCESSIBILITY"),
    ("stroller", "ACCESSIBILITY"),
    ("mobility", "ACCESSIBILITY"),

    # PARKING
    ("parking", "PARKING"),
    ("park", "PARKING"),
    ("car park", "PARKING"),

    # SAFETY
    ("safety", "SAFETY"),
    ("safe", "SAFETY"),
    ("unsafe", "SAFETY"),
    ("police", "SAFETY"),
    ("security", "SAFETY"),
    ("night", "SAFETY"),

    # CLEANLINESS
    ("cleanliness", "CLEANLINESS"),
    ("clean", "CLEANLINESS"),
    ("dirty", "CLEANLINESS"),
    ("spotless", "CLEANLINESS"),
    ("hygiene", "CLEANLINESS"),
    ("dust", "CLEANLINESS"),
    ("grime", "CLEANLINESS"),
    ("bathroom", "CLEANLINESS"),
    ("housekeeping", "CLEANLINESS"),

    # ROOM_QUALITY
    ("room", "ROOM_QUALITY"),
    ("bed", "ROOM_QUALITY"),
    ("mattress", "ROOM_QUALITY"),
    ("furnished", "ROOM_QUALITY"),
    ("furniture", "ROOM_QUALITY"),
    ("wardrobe", "ROOM_QUALITY"),
    ("comfortable", "ROOM_QUALITY"),
    ("cramped", "ROOM_QUALITY"),

    # NOISE_LEVEL
    ("noise", "NOISE_LEVEL"),
    ("noisy", "NOISE_LEVEL"),
    ("quiet", "NOISE_LEVEL"),
    ("loud", "NOISE_LEVEL"),
    ("traffic", "NOISE_LEVEL"),
    ("relax", "NOISE_LEVEL"),
    ("nightlife", "NOISE_LEVEL"),

    # PRESERVATION_STATE
    ("preservation", "PRESERVATION_STATE"),
    ("preserved", "PRESERVATION_STATE"),
    ("restoration", "PRESERVATION_STATE"),
    ("disrepair", "PRESERVATION_STATE"),
    ("neglected", "PRESERVATION_STATE"),
    ("medieval", "PRESERVATION_STATE"),
    ("heritage", "PRESERVATION_STATE"),
    ("historic", "PRESERVATION_STATE"),
    ("conservation", "PRESERVATION_STATE"),

    # FACILITIES_CONDITION
    ("facilities", "FACILITIES_CONDITION"),
    ("pool", "FACILITIES_CONDITION"),
    ("gym", "FACILITIES_CONDITION"),
    ("lift", "FACILITIES_CONDITION"),
    ("maintenance", "FACILITIES_CONDITION"),
    ("maintained", "FACILITIES_CONDITION"),
    ("broken", "FACILITIES_CONDITION"),
    ("out of order", "FACILITIES_CONDITION"),

    # TEMPERATURE_CONTROL
    ("temperature", "TEMPERATURE_CONTROL"),
    ("air conditioning", "TEMPERATURE_CONTROL"),
    ("heating", "TEMPERATURE_CONTROL"),
    ("ventilation", "TEMPERATURE_CONTROL"),
    ("cool", "TEMPERATURE_CONTROL"),
    ("warm", "TEMPERATURE_CONTROL"),
    ("hot", "TEMPERATURE_CONTROL"),
    ("cold", "TEMPERATURE_CONTROL"),

    # STAFF_QUALITY
    ("staff", "STAFF_QUALITY"),
    ("receptionist", "STAFF_QUALITY"),
    ("rude", "STAFF_QUALITY"),
    ("friendly", "STAFF_QUALITY"),
    ("helpful", "STAFF_QUALITY"),
    ("professional", "STAFF_QUALITY"),
    ("attentive", "STAFF_QUALITY"),
    ("dismissive", "STAFF_QUALITY"),

    # SERVICE_EFFICIENCY
    ("service", "SERVICE_EFFICIENCY"),
    ("slow", "SERVICE_EFFICIENCY"),
    ("prompt", "SERVICE_EFFICIENCY"),
    ("wait", "SERVICE_EFFICIENCY"),
    ("waiting", "SERVICE_EFFICIENCY"),
    ("order", "SERVICE_EFFICIENCY"),
    ("orders", "SERVICE_EFFICIENCY"),
    ("efficient", "SERVICE_EFFICIENCY"),
    ("speed", "SERVICE_EFFICIENCY"),

    # CHECK_IN_EXPERIENCE
    ("check-in", "CHECK_IN_EXPERIENCE"),
    ("check in", "CHECK_IN_EXPERIENCE"),
    ("arrival", "CHECK_IN_EXPERIENCE"),
    ("queue", "CHECK_IN_EXPERIENCE"),
    ("reception", "CHECK_IN_EXPERIENCE"),

    # COMMUNICATION
    ("communication", "COMMUNICATION"),
    ("email", "COMMUNICATION"),
    ("responded", "COMMUNICATION"),
    ("response", "COMMUNICATION"),
    ("messages", "COMMUNICATION"),
    ("confirmed", "COMMUNICATION"),
    ("confirmation", "COMMUNICATION"),

    # FOOD_QUALITY
    ("food", "FOOD_QUALITY"),
    ("meal", "FOOD_QUALITY"),
    ("dish", "FOOD_QUALITY"),
    ("dishes", "FOOD_QUALITY"),
    ("taste", "FOOD_QUALITY"),
    ("overcooked", "FOOD_QUALITY"),
    ("fresh", "FOOD_QUALITY"),
    ("bland", "FOOD_QUALITY"),
    ("flavour", "FOOD_QUALITY"),

    # BREAKFAST_QUALITY
    ("breakfast", "BREAKFAST_QUALITY"),
    ("morning meal", "BREAKFAST_QUALITY"),
    ("buffet", "BREAKFAST_QUALITY"),

    # MENU_VARIETY
    ("menu", "MENU_VARIETY"),
    ("variety", "MENU_VARIETY"),
    ("options", "MENU_VARIETY"),
    ("dietary", "MENU_VARIETY"),
    ("vegetarian", "MENU_VARIETY"),
    ("choice", "MENU_VARIETY"),

    # INFORMATIONAL_VALUE
    ("information", "INFORMATIONAL_VALUE"),
    ("signage", "INFORMATIONAL_VALUE"),
    ("guided", "INFORMATIONAL_VALUE"),
    ("educational", "INFORMATIONAL_VALUE"),
    ("panels", "INFORMATIONAL_VALUE"),
    ("commentary", "INFORMATIONAL_VALUE"),
    ("historical", "INFORMATIONAL_VALUE"),

    # WIFI_CONNECTIVITY
    ("wifi", "WIFI_CONNECTIVITY"),
    ("wi-fi", "WIFI_CONNECTIVITY"),
    ("internet", "WIFI_CONNECTIVITY"),
    ("connection", "WIFI_CONNECTIVITY"),
    ("connectivity", "WIFI_CONNECTIVITY"),
    ("broadband", "WIFI_CONNECTIVITY"),

    # AMENITIES_VARIETY
    ("amenities", "AMENITIES_VARIETY"),
    ("amenity", "AMENITIES_VARIETY"),
    ("spa", "AMENITIES_VARIETY"),
    ("sauna", "AMENITIES_VARIETY"),
    ("facilities", "AMENITIES_VARIETY"),

    # VALUE_FOR_MONEY
    ("value", "VALUE_FOR_MONEY"),
    ("price", "VALUE_FOR_MONEY"),
    ("worth", "VALUE_FOR_MONEY"),
    ("overpriced", "VALUE_FOR_MONEY"),
    ("affordable", "VALUE_FOR_MONEY"),
    ("expensive", "VALUE_FOR_MONEY"),
    ("cost", "VALUE_FOR_MONEY"),

    # HIDDEN_COSTS
    ("hidden", "HIDDEN_COSTS"),
    ("fees", "HIDDEN_COSTS"),
    ("charges", "HIDDEN_COSTS"),
    ("unexpected", "HIDDEN_COSTS"),
    ("checkout", "HIDDEN_COSTS"),
    ("surcharge", "HIDDEN_COSTS"),
    ("tax", "HIDDEN_COSTS"),

    # BOOKING_PROCESS
    ("booking", "BOOKING_PROCESS"),
    ("reservation", "BOOKING_PROCESS"),
    ("booked", "BOOKING_PROCESS"),
    ("online booking", "BOOKING_PROCESS"),
    ("website", "BOOKING_PROCESS"),

    # OVERALL_EXPERIENCE
    ("overall", "OVERALL_EXPERIENCE"),
    ("experience", "OVERALL_EXPERIENCE"),
    ("trip", "OVERALL_EXPERIENCE"),
    ("visit", "OVERALL_EXPERIENCE"),
    ("recommend", "OVERALL_EXPERIENCE"),
    ("return", "OVERALL_EXPERIENCE"),

    # ATMOSPHERE
    ("atmosphere", "ATMOSPHERE"),
    ("ambience", "ATMOSPHERE"),
    ("vibe", "ATMOSPHERE"),
    ("mood", "ATMOSPHERE"),
    ("welcoming", "ATMOSPHERE"),
    ("character", "ATMOSPHERE"),

    # CROWDING
    ("crowded", "CROWDING"),
    ("crowding", "CROWDING"),
    ("busy", "CROWDING"),
    ("congested", "CROWDING"),
    ("queue", "CROWDING"),
    ("packed", "CROWDING"),
    ("overcrowded", "CROWDING"),

    # ENTERTAINMENT_OPTIONS
    ("entertainment", "ENTERTAINMENT_OPTIONS"),
    ("live music", "ENTERTAINMENT_OPTIONS"),
    ("activities", "ENTERTAINMENT_OPTIONS"),
    ("events", "ENTERTAINMENT_OPTIONS"),
    ("performance", "ENTERTAINMENT_OPTIONS"),
    ("shows", "ENTERTAINMENT_OPTIONS"),

    # FAMILY_FRIENDLINESS
    ("family", "FAMILY_FRIENDLINESS"),
    ("children", "FAMILY_FRIENDLINESS"),
    ("kids", "FAMILY_FRIENDLINESS"),
    ("child", "FAMILY_FRIENDLINESS"),
    ("family-friendly", "FAMILY_FRIENDLINESS"),

    # DECOR_AND_DESIGN
    ("decor", "DECOR_AND_DESIGN"),
    ("design", "DECOR_AND_DESIGN"),
    ("interior", "DECOR_AND_DESIGN"),
    ("decoration", "DECOR_AND_DESIGN"),
    ("styling", "DECOR_AND_DESIGN"),
    ("aesthetic", "DECOR_AND_DESIGN"),
]


def main():
    conn = sqlite3.connect("warehouse.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.executemany(
        "INSERT OR IGNORE INTO RAW_ASPECT_KEYWORD (keyword, aspect_code) VALUES (?,?)",
        KEYWORDS,
    )
    conn.commit()

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM RAW_ASPECT_KEYWORD;")
    print("RAW_ASPECT_KEYWORD rows:", cur.fetchone()[0])

    cur.execute("SELECT aspect_code, COUNT(*) FROM RAW_ASPECT_KEYWORD GROUP BY aspect_code ORDER BY aspect_code;")
    print("\nKeywords per aspect:")
    for code, count in cur.fetchall():
        print(f"  {code:25s} {count}")

    # quick spot check: do core fragment keywords appear as expected?
    test_words = ["cleanliness", "breakfast", "staff", "parking", "wifi", "decor"]
    print("\nSpot checks:")
    for w in test_words:
        cur.execute("SELECT aspect_code FROM RAW_ASPECT_KEYWORD WHERE keyword=?", (w,))
        result = cur.fetchall()
        print(f"  '{w}' -> {[r[0] for r in result]}")

    conn.close()


if __name__ == "__main__":
    main()
