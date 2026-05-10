# cleaner.py
# This file's job is to take the raw messy data from each year
# and turn it into clean consistent data
# Think of it as a translator that speaks all 3 years' "dialects"

import pandas as pd
import numpy as np
import zipfile
import os

os.makedirs('cleaned_data', exist_ok=True)

def extract_and_load(zip_path, year):
    """
    Opens a zip file and loads the CSV inside it
    Like opening a package and taking out what's inside
    """
    print(f"  Loading {year} raw data...")

    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Get the name of the CSV file inside the zip
        csv_name = [f for f in zf.namelist() if f.endswith('.csv')][0]

        with zf.open(csv_name) as f:
            df = pd.read_csv(f)

    print(f"  Raw shape: {df.shape[0]} rows × {df.shape[1]} columns")
    return df

def standardise_columns(df, year):
    """
    Each year uses different column names for the same data
    This function translates everything to one standard name
    Like hiring one translator who speaks all 3 dialects
    """
    print(f"  Standardising {year} column names...")

    # Patients column has 3 different names across years
    # We find whichever one exists and rename it to 'patients_served'
    patient_cols = ['patients_served', 'total_patients', 'num_patients']
    for col in patient_cols:
        if col in df.columns:
            df = df.rename(columns={col: 'patients_served'})
            break

    return df

def standardise_states(df, year):
    """
    2021 data has lowercase state codes — we uppercase everything
    AL, al, Al all become AL
    """
    print(f"  Standardising {year} state formats...")
    df['state'] = df['state'].str.upper().str.strip()
    return df

def standardise_insurance(df, year):
    """
    Insurance column uses 3 different formats:
    2020: Yes/No
    2021: 1/0
    2022: Y/N
    We convert everything to a simple True/False
    """
    print(f"  Standardising {year} insurance column...")

    col = df['accepts_insurance'].astype(str).str.strip().str.upper()

    df['accepts_insurance'] = col.map(
        lambda x: True if x in ['YES', '1', 'Y', 'TRUE'] else False
    )
    return df

def handle_missing_values(df, year):
    """
    Fills in missing values sensibly
    Think of it like a form where some fields were left blank
    We fill them with the most reasonable default value
    """
    print(f"  Handling {year} missing values...")

    before = df.isnull().sum().sum()

    # For numeric columns fill with median
    # Median is better than average when data has extreme outliers
    for col in ['patients_served', 'staff_count', 'bed_count']:
        if col in df.columns:
            median_val = df[col].median()
            df[col]    = df[col].fillna(median_val)

    after = df.isnull().sum().sum()
    print(f"  Missing values: {before} → {after}")
    return df

def remove_duplicates(df, year):
    """
    Removes duplicate rows — we added 5% duplicates on purpose
    to simulate real data messiness
    """
    before = len(df)
    df     = df.drop_duplicates(subset=['facility_id'])
    after  = len(df)
    print(f"  Duplicates removed: {before - after} rows ({before} → {after})")
    return df

def add_derived_columns(df, year):
    """
    Creates new useful columns from existing ones
    This is called feature engineering — making the data richer
    Think of it like a chef who takes raw ingredients
    and prepares them into something more useful
    """
    print(f"  Adding {year} derived columns...")

    # Patients per staff member — a quality/capacity indicator
    if 'staff_count' in df.columns and 'patients_served' in df.columns:
        df['patients_per_staff'] = (
            df['patients_served'] / df['staff_count'].replace(0, np.nan)
        ).round(1)

    # Count how many services each facility offers
    if 'services' in df.columns:
        df['num_services'] = df['services'].str.split(',').str.len()

    # Flag facilities that are likely overburdened
    # More than 50 patients per staff member = high pressure
    if 'patients_per_staff' in df.columns:
        df['is_overburdened'] = df['patients_per_staff'] > 50

    return df

def clean_year(year):
    """
    Master function — runs ALL cleaning steps for one year
    in the correct order
    Think of it like a car wash — each step builds on the last
    """
    print(f"\n{'='*50}")
    print(f"CLEANING {year} DATA")
    print(f"{'='*50}")

    zip_path = f'raw_data/nmhss_{year}.zip'

    if not os.path.exists(zip_path):
        print(f"  ERROR: {zip_path} not found!")
        return None

    # Run each cleaning step in order
    df = extract_and_load(zip_path, year)
    df = standardise_columns(df, year)
    df = standardise_states(df, year)
    df = standardise_insurance(df, year)
    df = handle_missing_values(df, year)
    df = remove_duplicates(df, year)
    df = add_derived_columns(df, year)

    # Add year column so we know which year each row came from
    df['year'] = year

    # Save cleaned version
    output_path = f'cleaned_data/nmhss_{year}_clean.csv'
    df.to_csv(output_path, index=False, encoding='utf-8')

    print(f"\n  DONE: {len(df)} clean rows saved to {output_path}")
    return df

def clean_all():
    """Cleans all 3 years and combines them into one master dataset"""
    print("\n" + "="*50)
    print("STEP 2: CLEANING ALL RAW DATA")
    print("="*50)

    all_years = []

    for year in [2020, 2021, 2022]:
        df = clean_year(year)
        if df is not None:
            all_years.append(df)

    if not all_years:
        print("ERROR: No data was cleaned!")
        return None

    # Stack all 3 years into one big table
    # This is like gluing 3 spreadsheets into one
    combined = pd.concat(all_years, ignore_index=True)

    # Save the combined master file
    combined.to_csv('cleaned_data/nmhss_all_years.csv',
                    index=False, encoding='utf-8')

    print(f"\n{'='*50}")
    print(f"CLEANING COMPLETE")
    print(f"Total records: {len(combined)}")
    print(f"Years covered: {sorted(combined['year'].unique())}")
    print(f"States covered: {combined['state'].nunique()}")
    print(f"{'='*50}")

    return combined

if __name__ == '__main__':
    clean_all()