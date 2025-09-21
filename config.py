# config.py

import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths for data and outputs
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw_sales_data.csv")
CLEANED_DATA_DIR = os.path.join(BASE_DIR, "outputs", "cleaned_data")
REPORT_DIR = os.path.join(BASE_DIR, "outputs", "reports")

# Ensure output directories exist
os.makedirs(CLEANED_DATA_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# API Configuration (We'll use a free fake API for this example)
API_URL = "https://api.exchangerate-api.com/v4/latest/USD"  # Gets USD-based exchange rates