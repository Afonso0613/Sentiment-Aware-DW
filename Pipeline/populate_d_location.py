"""
Populates D_LOCATION from municipality_data.py.

"""

import sqlite3
from municipality_data import DISTRICT_MUNICIPALITIES

DISTRICT_REGION = {
    "Aveiro": "Centro",
    "Beja": "Alentejo",
    "Braga": "Norte",
    "Bragança": "Norte",
    "Castelo Branco": "Centro",
    "Coimbra": "Centro",
    "Évora": "Alentejo",
    "Faro": "Algarve",
    "Guarda": "Centro",
    "Leiria": "Centro",
    "Lisboa": "Lisboa",
    "Portalegre": "Alentejo",
    "Porto": "Norte",
    "Santarém": "Centro",  
    "Viana do Castelo": "Norte",
    "Vila Real": "Norte",
    "Viseu": "Centro",
    "Azores": "Região Autónoma dos Açores",
    "Madeira": "Região Autónoma da Madeira",
}

SETUBAL_TO_LISBOA = {
    "Alcochete", "Almada", "Barreiro", "Moita", "Montijo",
    "Palmela", "Seixal", "Sesimbra", "Setúbal",
}
SETUBAL_TO_ALENTEJO = {
    "Alcácer do Sal", "Grândola", "Santiago do Cacém", "Sines",
}


def resolve_region(district, municipality):
    if district == "Setúbal":
        if municipality in SETUBAL_TO_LISBOA:
            return "Lisboa"
        if municipality in SETUBAL_TO_ALENTEJO:
            return "Alentejo"
        raise ValueError(f"Unhandled Setúbal municipality: {municipality}")
    return DISTRICT_REGION[district]


def build_rows():
    rows = []
    location_key = 1
    code_counter = 1
    for district in sorted(DISTRICT_MUNICIPALITIES):
        for municipality in sorted(DISTRICT_MUNICIPALITIES[district]):
            region = resolve_region(district, municipality)
            # synthetic code: zero-padded sequential, not an official
            # INE/DICOFRE identifier, see module docstring
            municipality_code = f"{code_counter:03d}"
            rows.append((location_key, municipality_code, region, district, municipality))
            location_key += 1
            code_counter += 1
    return rows


def main():
    conn = sqlite3.connect("warehouse.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    rows = build_rows()
    conn.executemany(
        """INSERT INTO D_LOCATION
           (location_key, municipality_code, region, district, municipality)
           VALUES (?,?,?,?,?)""",
        rows,
    )
    conn.commit()

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM D_LOCATION;")
    print("D_LOCATION populated:", cur.fetchone()[0], "rows (expected 308).")

    cur.execute("SELECT region, COUNT(*) FROM D_LOCATION GROUP BY region ORDER BY region;")
    print("\nRows per region:")
    for region, count in cur.fetchall():
        print(f"  {region:35s} {count}")

    cur.execute("SELECT * FROM D_LOCATION WHERE municipality = 'Setúbal';")
    print("\nSetúbal itself (should be Lisboa region):", cur.fetchone())

    cur.execute("SELECT * FROM D_LOCATION WHERE municipality = 'Sines';")
    print("Sines (should be Alentejo region):", cur.fetchone())

    cur.execute("SELECT * FROM D_LOCATION WHERE municipality = 'Braga';")
    print("Braga (should be Norte region):", cur.fetchone())

    conn.close()


if __name__ == "__main__":
    main()
