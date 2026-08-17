"""
Populates D_ASPECT 

"""

import sqlite3

# (aspect_code, aspect_name, aspect_category, aspect_description)
ASPECTS = [
    # Location
    ("LOCATION", "Location",
     "Location",
     "Evaluation of the service's geographic position, proximity to points of interest and ease of reaching it."),
    ("VIEW", "View",
     "Location",
     "Evaluation of the visual outlook from rooms, terraces or seating areas, such as sea, city or garden views."),
    ("ACCESSIBILITY", "Accessibility",
     "Location",
     "Evaluation of physical access to the service, including suitability for visitors with reduced mobility."),
    ("PARKING", "Parking",
     "Location",
     "Evaluation of parking availability, convenience and cost at or near the service."),
    ("SAFETY", "Safety",
     "Location",
     "Evaluation of perceived personal safety and security of the surrounding area or premises."),

    # Physical Environment
    ("CLEANLINESS", "Cleanliness",
     "Physical Environment",
     "Perceived cleanliness of rooms, facilities or common areas."),
    ("ROOM_QUALITY", "Room Quality",
     "Physical Environment",
     "Evaluation of room comfort, furnishing and overall condition."),
    ("NOISE_LEVEL", "Noise Level",
     "Physical Environment",
     "Evaluation of ambient noise from neighbouring rooms, the street or nearby establishments."),
    ("PRESERVATION_STATE", "Preservation State",
     "Physical Environment",
     "Evaluation of the physical conservation and upkeep of a tourist site or historical attraction."),
    ("FACILITIES_CONDITION", "Facilities Condition",
     "Physical Environment",
     "Evaluation of the maintenance and working condition of shared facilities such as pools, lifts or restrooms."),
    ("TEMPERATURE_CONTROL", "Temperature Control",
     "Physical Environment",
     "Evaluation of heating, cooling or ventilation adequacy within rooms or indoor spaces."),

    # Staff and Service
    ("STAFF_QUALITY", "Staff Quality",
     "Staff and Service",
     "Evaluation of staff behaviour, friendliness and professionalism."),
    ("SERVICE_EFFICIENCY", "Service Efficiency",
     "Staff and Service",
     "Evaluation of the speed and effectiveness with which service requests or orders are handled."),
    ("CHECK_IN_EXPERIENCE", "Check-in Experience",
     "Staff and Service",
     "Evaluation of the arrival, check-in or seating process and any associated waiting time."),
    ("COMMUNICATION", "Communication",
     "Staff and Service",
     "Evaluation of the clarity and responsiveness of communication from staff before, during or after the visit."),

    # Core Offering
    ("FOOD_QUALITY", "Food Quality",
     "Core Offering",
     "Evaluation of the taste, presentation and quality of food served."),
    ("BREAKFAST_QUALITY", "Breakfast Quality",
     "Core Offering",
     "Evaluation of breakfast options, quality and service where offered as part of accommodation."),
    ("MENU_VARIETY", "Menu Variety",
     "Core Offering",
     "Evaluation of the range and diversity of options available on a restaurant or bar menu."),
    ("INFORMATIONAL_VALUE", "Informational Value",
     "Core Offering",
     "Evaluation of the educational or informational content provided at a tourist site, such as signage or guided commentary."),
    ("WIFI_CONNECTIVITY", "Wifi Connectivity",
     "Core Offering",
     "Evaluation of the availability and reliability of wireless internet access."),
    ("AMENITIES_VARIETY", "Amenities Variety",
     "Core Offering",
     "Evaluation of the range of additional amenities offered, such as a pool, gym or spa."),

    # Value and Pricing
    ("VALUE_FOR_MONEY", "Value for Money",
     "Value and Pricing",
     "Evaluation of whether the price paid was considered justified relative to the experience or quality received."),
    ("HIDDEN_COSTS", "Hidden Costs",
     "Value and Pricing",
     "Evaluation of unexpected or undisclosed charges encountered during or after the visit."),
    ("BOOKING_PROCESS", "Booking Process",
     "Value and Pricing",
     "Evaluation of the ease, transparency and reliability of the reservation or booking process."),

    # Experience and Atmosphere
    ("OVERALL_EXPERIENCE", "Overall Experience",
     "Experience and Atmosphere",
     "General evaluation of the visit as a whole, not attributable to a single specific aspect."),
    ("ATMOSPHERE", "Atmosphere",
     "Experience and Atmosphere",
     "Evaluation of the ambience, mood or character of the environment."),
    ("CROWDING", "Crowding",
     "Experience and Atmosphere",
     "Evaluation of how busy or congested the service felt during the visit."),
    ("ENTERTAINMENT_OPTIONS", "Entertainment Options",
     "Experience and Atmosphere",
     "Evaluation of entertainment, activities or events available during the visit."),
    ("FAMILY_FRIENDLINESS", "Family Friendliness",
     "Experience and Atmosphere",
     "Evaluation of suitability for travelling with children or as a family group."),
    ("DECOR_AND_DESIGN", "Decor and Design",
     "Experience and Atmosphere",
     "Evaluation of interior or exterior visual design, decoration and styling."),
]


def main():
    conn = sqlite3.connect("warehouse.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    rows = [
        (key, code, name, category, description)
        for key, (code, name, category, description) in enumerate(ASPECTS, start=1)
    ]

    conn.executemany(
        """INSERT INTO D_ASPECT
           (aspect_key, aspect_code, aspect_name, aspect_category, aspect_description)
           VALUES (?,?,?,?,?)""",
        rows,
    )
    conn.commit()

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM D_ASPECT;")
    print("D_ASPECT populated:", cur.fetchone()[0], "rows.")

    cur.execute("SELECT aspect_category, COUNT(*) FROM D_ASPECT GROUP BY aspect_category ORDER BY aspect_category;")
    print("\nRows per category:")
    for category, count in cur.fetchall():
        print(f"  {category:30s} {count}")

    cur.execute("SELECT * FROM D_ASPECT WHERE aspect_code = 'CLEANLINESS';")
    print("\nCLEANLINESS (matches existing thesis example):", cur.fetchone())

    cur.execute("SELECT * FROM D_ASPECT WHERE aspect_code = 'STAFF_QUALITY';")
    print("STAFF_QUALITY (matches existing thesis example):", cur.fetchone())

    conn.close()


if __name__ == "__main__":
    main()
