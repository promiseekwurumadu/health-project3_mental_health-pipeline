# pipeline.py
# This is the master file that runs the entire pipeline
# from raw data to clean database in one single command
# Think of it like a factory manager who tells each
# station exactly when to start working

import time
from generate_data import generate_all
from cleaner      import clean_all
from database     import build_database, get_connection

def run_pipeline():
    """
    Runs the complete data pipeline end to end
    Step 1 → Generate/Download raw data
    Step 2 → Clean and standardise it
    Step 3 → Load into database
    """

    start_time = time.time()

    print("\n" + "🏥 " * 20)
    print("  MENTAL HEALTH SERVICES DATA PIPELINE")
    print("🏥 " * 20)
    print("Starting full pipeline run...\n")

    # ── STEP 1 ────────────────────────────────────────────────────
    print("STEP 1 of 3: Generating raw data...")
    generate_all()
    print("✓ Step 1 complete\n")

    # ── STEP 2 ────────────────────────────────────────────────────
    print("STEP 2 of 3: Cleaning data...")
    combined_df = clean_all()
    print("✓ Step 2 complete\n")

    # ── STEP 3 ────────────────────────────────────────────────────
    print("STEP 3 of 3: Loading into database...")
    build_database()
    print("✓ Step 3 complete\n")

    # ── PIPELINE SUMMARY ──────────────────────────────────────────
    end_time     = time.time()
    elapsed      = round(end_time - start_time, 2)

    conn         = get_connection()
    import pandas as pd
    total        = pd.read_sql(
                    "SELECT COUNT(*) as total FROM facilities", conn
                   ).iloc[0]['total']
    conn.close()

    print("\n" + "="*50)
    print("  PIPELINE COMPLETE")
    print("="*50)
    print(f"  Total facilities in database : {int(total)}")
    print(f"  Years covered                : 2020, 2021, 2022")
    print(f"  Time taken                   : {elapsed} seconds")
    print(f"  Database location            : health.db")
    print(f"  Dashboard command            : streamlit run dashboard.py")
    print("="*50)

if __name__ == '__main__':
    run_pipeline()