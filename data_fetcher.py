# data_fetcher.py

import pandas as pd
import requests
from config import RAW_DATA_PATH, API_URL
import json

def fetch_csv_data():
    """Reads the raw sales data from CSV."""
    try:
        df = pd.read_csv(RAW_DATA_PATH)
        print("✅ CSV data loaded successfully.")
        return df
    except FileNotFoundError:
        print(f"❌ Error: CSV file not found at {RAW_DATA_PATH}")
        return None

def fetch_exchange_rates():
    """Fetches latest currency exchange rates from API."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raises an error for bad status codes (4xx or 5xx)
        data = response.json()
        rates = data['rates']
        print("✅ Exchange rates fetched successfully.")
        return rates
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching exchange rates: {e}")
        return None

# Test the functions
if __name__ == "__main__":
    df = fetch_csv_data()
    if df is not None:
        print(df.head())

    rates = fetch_exchange_rates()
    if rates is not None:
        # Print a few relevant rates
        print({k: rates[k] for k in ['EUR', 'GBP', 'CAD']})