# downloader.py
# This file's only job is to download the raw data files from SAMHSA
# Think of it like an automatic shopping delivery — 
# you tell it what you want and it goes and gets it

import requests  # lets Python make web requests (like a browser)
import os        # lets Python interact with your file system

# Create a folder to store raw downloaded files
# exist_ok=True means don't crash if folder already exists
os.makedirs('raw_data', exist_ok=True)

# These are the direct download links for SAMHSA N-MHSS data
# Each link is one year of mental health services survey data
DOWNLOAD_LINKS = {
    '2020': 'https://www.samhsa.gov/data/sites/default/files/reports/rpt35248/2020_NMHSS_CSV.zip',
    '2021': 'https://www.samhsa.gov/data/sites/default/files/reports/rpt39443/2021_NMHSS_CSV.zip',
    '2022': 'https://www.samhsa.gov/data/sites/default/files/reports/rpt42288/2022_NMHSS_CSV.zip'
}

def download_file(year, url):
    """
    Downloads one file for a given year
    Think of this like a function = a reusable instruction set
    You give it a year and a link, it downloads the file
    """
    filename = f'raw_data/nmhss_{year}.zip'

    # Don't re-download if file already exists
    # This saves time if you run the pipeline more than once
    if os.path.exists(filename):
        print(f"  {year} file already exists, skipping download")
        return filename

    print(f"  Downloading {year} data...")

    try:
        # stream=True means download in chunks (good for large files)
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()  # crash loudly if download failed

        # Write the file to disk chunk by chunk
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"  {year} downloaded successfully!")
        return filename

    except Exception as e:
        print(f"  ERROR downloading {year}: {e}")
        return None

def download_all():
    """Downloads all years of data"""
    print("=" * 50)
    print("STEP 1: DOWNLOADING RAW DATA FILES")
    print("=" * 50)

    downloaded = {}
    for year, url in DOWNLOAD_LINKS.items():
        result = download_all_files = download_file(year, url)
        if result:
            downloaded[year] = result

    print(f"\nDownloaded {len(downloaded)} out of {len(DOWNLOAD_LINKS)} files")
    return downloaded

# This means: only run download_all() if we run THIS file directly
# If another file imports this, it won't auto-run
if __name__ == '__main__':
    download_all()