# database.py
# This file's job is to take our clean data and store it
# in a proper database that can be queried quickly
# Think of it like moving from a messy pile of papers
# into a proper organised filing system

import pandas as pd
import sqlite3
import os

# Our database will be stored as a single file called health.db
DATABASE_PATH = 'health.db'

def get_connection():
    """
    Opens a connection to our database
    Think of this like opening the filing cabinet
    """
    return sqlite3.connect(DATABASE_PATH)

def create_tables(conn):
    """
    Creates the structure of our database — like drawing the
    columns and rows of an empty spreadsheet before filling it in
    """
    print("  Creating database tables...")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS facilities (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id         TEXT,
            state               TEXT,
            facility_type       TEXT,
            urban_rural         TEXT,
            accepts_insurance   INTEGER,
            operating_months    INTEGER,
            year                INTEGER
        )
    """)
    # INTEGER PRIMARY KEY = a unique number for every row
    # TEXT = stores words/letters
    # INTEGER = stores whole numbers

    conn.execute("""
        CREATE TABLE IF NOT EXISTS capacity (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id         TEXT,
            patients_served     REAL,
            staff_count         REAL,
            bed_count           REAL,
            patients_per_staff  REAL,
            num_services        INTEGER,
            is_overburdened     INTEGER,
            year                INTEGER
        )
    """)
    # REAL = stores decimal numbers
    # We split into 2 tables — facilities info and capacity info
    # This is called database normalisation — a key engineering concept

    conn.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_id         TEXT,
            service_name        TEXT,
            year                INTEGER
        )
    """)
    # This table stores each service as its own row
    # Much easier to query than a comma separated text column

    conn.commit()
    print("  Tables created successfully!")

def load_data(conn):
    """
    Reads our clean combined CSV and loads it into the database
    Think of this like taking organised papers and filing them
    into the correct folders in our filing cabinet
    """
    print("  Loading clean data into database...")

    df = pd.read_csv('cleaned_data/nmhss_all_years.csv')
    print(f"  Read {len(df)} rows from cleaned data")

    # ── Clear existing data before reloading ─────────────────────
    # This means we can run the pipeline multiple times safely
    # without getting duplicate records in the database
    conn.execute("DELETE FROM facilities")
    conn.execute("DELETE FROM capacity")
    conn.execute("DELETE FROM services")
    conn.commit()
    print("  Cleared existing database records")

    # ── Load FACILITIES table ─────────────────────────────────────
    facilities_df = df[[
        'facility_id', 'state', 'facility_type',
        'urban_rural', 'accepts_insurance',
        'operating_months', 'year'
    ]].copy()

    facilities_df.to_sql(
        'facilities',       # table name
        conn,               # our database connection
        if_exists='append', # add to existing table (don't replace it)
        index=False         # don't add pandas row numbers as a column
    )
    print(f"  Loaded {len(facilities_df)} rows into facilities table")

    # ── Load CAPACITY table ───────────────────────────────────────
    capacity_cols = [
        'facility_id', 'patients_served', 'staff_count',
        'bed_count', 'patients_per_staff',
        'num_services', 'is_overburdened', 'year'
    ]
    # Only include columns that actually exist in our dataframe
    capacity_cols = [c for c in capacity_cols if c in df.columns]
    capacity_df   = df[capacity_cols].copy()

    capacity_df.to_sql('capacity', conn, if_exists='append', index=False)
    print(f"  Loaded {len(capacity_df)} rows into capacity table")

    # ── Load SERVICES table ───────────────────────────────────────
    # Remember services is stored as "Therapy, Medication, Crisis"
    # We split it into individual rows — one row per service
    print("  Expanding services into individual rows...")

    services_rows = []
    for _, row in df.iterrows():
        if pd.notna(row.get('services')):
            for service in str(row['services']).split(','):
                services_rows.append({
                    'facility_id' : row['facility_id'],
                    'service_name': service.strip(),
                    'year'        : row['year']
                })

    services_df = pd.DataFrame(services_rows)
    services_df.to_sql('services', conn, if_exists='append', index=False)
    print(f"  Loaded {len(services_df)} service records")

    conn.commit()

def run_test_queries(conn):
    """
    Runs a few test questions against our database
    to confirm everything loaded correctly
    This is like opening the filing cabinet and checking
    a few folders to make sure everything is in the right place
    """
    print("\n  Running test queries...")

    # Query 1 — total facilities per year
    result = pd.read_sql("""
        SELECT year, COUNT(*) as total_facilities
        FROM facilities
        GROUP BY year
        ORDER BY year
    """, conn)
    print("\n  Facilities per year:")
    print(result.to_string(index=False))

    # Query 2 — average patients per state (top 5)
    result = pd.read_sql("""
        SELECT f.state,
               ROUND(AVG(c.patients_served), 0) as avg_patients
        FROM facilities f
        JOIN capacity c
          ON f.facility_id = c.facility_id
         AND f.year        = c.year
        GROUP BY f.state
        ORDER BY avg_patients DESC
        LIMIT 5
    """, conn)
    print("\n  Top 5 states by average patients served:")
    print(result.to_string(index=False))

    # Query 3 — most common facility type
    result = pd.read_sql("""
        SELECT facility_type,
               COUNT(*) as count
        FROM facilities
        GROUP BY facility_type
        ORDER BY count DESC
    """, conn)
    print("\n  Facility types breakdown:")
    print(result.to_string(index=False))

    # Query 4 — overburdened facilities
    result = pd.read_sql("""
        SELECT f.year,
               COUNT(*) as overburdened_count
        FROM capacity c
        JOIN facilities f
          ON c.facility_id = f.facility_id
         AND c.year        = f.year
        WHERE c.is_overburdened = 1
        GROUP BY f.year
        ORDER BY f.year
    """, conn)
    print("\n  Overburdened facilities per year:")
    print(result.to_string(index=False))

def build_database():
    """Master function — runs all database steps in order"""
    print("\n" + "="*50)
    print("STEP 3: BUILDING DATABASE")
    print("="*50)

    conn = get_connection()

    create_tables(conn)
    load_data(conn)
    run_test_queries(conn)

    conn.close()

    size = os.path.getsize(DATABASE_PATH) / 1024
    print(f"\n  Database saved: {DATABASE_PATH} ({size:.1f} KB)")
    print("  Database build complete!")

if __name__ == '__main__':
    build_database()