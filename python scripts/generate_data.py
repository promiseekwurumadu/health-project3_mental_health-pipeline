# generate_data.py
# Since SAMHSA's website blocks automated access, we generate
# realistic synthetic data that mirrors the actual N-MHSS survey structure
# This is a standard data engineering practice when sources are unavailable

import pandas as pd
import numpy as np
import os
import zipfile

# Make results reproducible — same random numbers every time
np.random.seed(42)
os.makedirs('raw_data', exist_ok=True)

# ── Real US states ───────────────────────────────────────────────
STATES = [
    'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA',
    'HI','ID','IL','IN','IA','KS','KY','LA','ME','MD',
    'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
    'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC',
    'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC'
]

# ── Real facility types from actual N-MHSS survey ────────────────
FACILITY_TYPES = [
    'Psychiatric Hospital',
    'Community Mental Health Center',
    'Residential Treatment Center',
    'Outpatient Clinic',
    'Veterans Affairs Medical Center',
    'State Mental Hospital',
    'Private Practice',
    'School Based Program'
]

# ── Services that facilities can offer ──────────────────────────
SERVICES = [
    'Individual Therapy',
    'Group Therapy',
    'Medication Management',
    'Crisis Intervention',
    'Substance Abuse Treatment',
    'Child and Adolescent Services',
    'Telehealth Services',
    'Case Management'
]

def generate_year_data(year, n_facilities=800):
    """
    Generates one year of messy mental health facility data
    Each year has slightly different column names — 
    that's the real engineering challenge we have to fix
    """
    print(f"  Generating {year} data ({n_facilities} facilities)...")
    np.random.seed(year)  # different seed per year = different data

    facility_ids = [f'FAC{year}{str(i).zfill(5)}' for i in range(n_facilities)]
    states       = np.random.choice(STATES, n_facilities)
    facility_types = np.random.choice(FACILITY_TYPES, n_facilities)

    # ── Patients served — with realistic missing values ──────────
    patients = np.random.randint(50, 5000, n_facilities).astype(float)
    # Randomly blank out 15% of patient counts (realistic missingness)
    missing_mask = np.random.random(n_facilities) < 0.15
    patients[missing_mask] = np.nan

    # ── Staff counts ─────────────────────────────────────────────
    staff = np.random.randint(5, 200, n_facilities).astype(float)
    staff[np.random.random(n_facilities) < 0.10] = np.nan

    # ── Bed counts (not all facilities have beds) ────────────────
    beds = np.random.randint(0, 300, n_facilities).astype(float)
    beds[np.random.random(n_facilities) < 0.20] = np.nan

    # ── Services offered — stored as messy comma separated text ──
    def random_services():
        n = np.random.randint(1, len(SERVICES))
        return ', '.join(np.random.choice(SERVICES, n, replace=False))

    services_list = [random_services() for _ in range(n_facilities)]

    # ── Accepts insurance — stored differently each year ─────────
    if year == 2020:
        # 2020 uses Yes/No text
        insurance = np.random.choice(['Yes', 'No'], n_facilities)
    elif year == 2021:
        # 2021 uses 1/0 numbers — inconsistent!
        insurance = np.random.choice([1, 0], n_facilities)
    else:
        # 2022 uses Y/N — yet another format!
        insurance = np.random.choice(['Y', 'N'], n_facilities)

    # ── Introduce duplicate records (5%) — real data problem ─────
    df = pd.DataFrame({
        # Column names differ per year — the core engineering challenge
        'facility_id'    : facility_ids,
        'state'          : states if year != 2021 else [s.lower() for s in states],
        # 2021 has lowercase states — messy!
        'facility_type'  : facility_types,
        'patients_served': patients if year == 2020 else None,
        'total_patients' : patients if year == 2021 else None,
        'num_patients'   : patients if year == 2022 else None,
        # same data, three different column names across years!
        'staff_count'    : staff,
        'bed_count'      : beds,
        'services'       : services_list,
        'accepts_insurance': insurance,
        'year'           : year,
        'urban_rural'    : np.random.choice(
                            ['Urban', 'Rural', 'Suburban'], n_facilities
                           ),
        'operating_months': np.random.randint(1, 13, n_facilities)
    })

    # Remove the two None columns per year cleanly
    df = df.dropna(axis=1, how='all')

    # Add 5% duplicate rows to simulate real data messiness
    n_dupes = int(n_facilities * 0.05)
    dupes   = df.sample(n_dupes, random_state=year)
    df      = pd.concat([df, dupes], ignore_index=True)

    return df

def save_as_zip(df, year):
    """Saves dataframe as CSV inside a zip file — same format as real SAMHSA data"""
    csv_path = f'raw_data/nmhss_{year}.csv'
    zip_path = f'raw_data/nmhss_{year}.zip'

    df.to_csv(csv_path, index=False)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(csv_path, f'nmhss_{year}.csv')

    os.remove(csv_path)  # remove the loose CSV, keep only the zip
    print(f"  Saved: {zip_path} ({len(df)} rows)")

def generate_all():
    print("=" * 50)
    print("GENERATING SYNTHETIC N-MHSS STYLE DATA")
    print("(SAMHSA site returned 403 — using realistic")
    print(" synthetic data with same structure & messiness)")
    print("=" * 50)

    for year in [2020, 2021, 2022]:
        df = generate_year_data(year)
        save_as_zip(df, year)

    print("\nAll 3 years generated successfully!")
    print("Files saved in raw_data/ folder")

if __name__ == '__main__':
    generate_all()