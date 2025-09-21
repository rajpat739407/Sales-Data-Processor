# main.py

from data_fetcher import fetch_csv_data, fetch_exchange_rates
from data_cleaner import clean_data
from report_generator import generate_html_report  # Changed import

def run_full_pipeline():
    """Runs the entire data pipeline."""
    print("🚀 Starting automated data pipeline...\n")

    # Step 1: Fetch Data
    print("=== FETCHING DATA ===")
    sales_data = fetch_csv_data()
    exchange_rates = fetch_exchange_rates()

    if sales_data is None or exchange_rates is None:
        print("❌ Pipeline failed due to data fetch errors. Exiting.")
        return

    # Step 2: Clean Data
    print("\n=== CLEANING DATA ===")
    cleaned_data = clean_data(sales_data, exchange_rates)

    # Step 3: Generate HTML Report
    print("\n=== GENERATING HTML REPORT ===")
    report_path = generate_html_report(cleaned_data)
    
    print(f"\n🎉 Pipeline finished successfully! Open this file in your browser: {report_path}")

if __name__ == "__main__":
    run_full_pipeline()