"""
Populates D_DATE for the 2022-2026 window.

"""

import sqlite3
from datetime import date, timedelta

START = date(2022, 1, 1)
END = date(2026, 12, 31)

SEASON_BY_MONTH = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Autumn", 10: "Autumn", 11: "Autumn",
}


def build_rows():
    rows = []
    current = START
    while current <= END:
        date_key = int(current.strftime("%Y%m%d"))
        full_date = current.isoformat()
        day_of_month = current.day
        day_name = current.strftime("%A")
        month = current.month
        month_name = current.strftime("%B")
        quarter = (month - 1) // 3 + 1
        year = current.year
        season = SEASON_BY_MONTH[month]

        rows.append((
            date_key, full_date, day_of_month, day_name,
            month, month_name, quarter, year, season,
        ))
        current += timedelta(days=1)
    return rows


def main():
    conn = sqlite3.connect("warehouse.db")
    conn.execute("PRAGMA foreign_keys = ON;")

    rows = build_rows()
    conn.executemany(
        """INSERT INTO D_DATE
           (date_key, full_date, day_of_month, day_name,
            month, month_name, quarter, year, season)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    conn.commit()

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM D_DATE;")
    total = cur.fetchone()[0]
    print(f"D_DATE populated: {total} rows.")

    cur.execute("SELECT MIN(full_date), MAX(full_date) FROM D_DATE;")
    print("Range:", cur.fetchone())

    cur.execute("SELECT * FROM D_DATE WHERE date_key = 20240215;")
    print("Spot check (2024-02-15):", cur.fetchone())

    cur.execute("SELECT * FROM D_DATE WHERE date_key = 20240229;")
    print("Leap day check (2024-02-29):", cur.fetchone())

    cur.execute("SELECT season, COUNT(*) FROM D_DATE GROUP BY season ORDER BY season;")
    print("Season distribution:", cur.fetchall())

    conn.close()


if __name__ == "__main__":
    main()
