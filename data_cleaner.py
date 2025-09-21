# data_cleaner.py

import pandas as pd
from datetime import datetime
from config import CLEANED_DATA_DIR
import numpy as np

def clean_data(sales_df, exchange_rates):
    """
    Cleans the sales data and converts all prices to USD.
    Handles missing columns gracefully and ensures numeric conversion.
    """
    df = sales_df.copy()

    # 1. Handle missing columns by creating them if they don't exist
    required_columns = ['order_id', 'date', 'product', 'price', 'currency', 'quantity', 'customer_id']
    for col in required_columns:
        if col not in df.columns:
            if col == 'customer_id':
                df[col] = 'UNKNOWN'  # Fill missing customer_id with default
            else:
                df[col] = None  # Fill other missing columns with None
                print(f"⚠️ Warning: Missing column '{col}' filled with None")

    # 2. Convert numeric columns to proper numeric types
    print("Converting numeric columns...")
    numeric_columns = ['price', 'quantity']
    for col in numeric_columns:
        if col in df.columns:
            # Convert to numeric, forcing errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # Fill NaN values appropriately
            if col == 'price':
                df[col] = df[col].fillna(0)
            elif col == 'quantity':
                df[col] = df[col].fillna(1)  # Assume 1 if quantity is missing

    # 3. Handle duplicates
    print("Removing duplicates...")
    initial_count = len(df)
    df = df.drop_duplicates()
    print(f"Removed {initial_count - len(df)} duplicates")

    # 4. Standardize date format (handle mixed formats)
    print("Standardizing date format...")
    if df['date'].notna().any():  # Only process if there are dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce') # 'coerce' invalid dates become NaT
    else:
        print("⚠️ Warning: No valid dates found in 'date' column")

    # 5. Handle missing prices with mean by product
    print("Handling missing prices...")
    if df['price'].notna().any():
        # Calculate mean price for each product
        product_means = df.groupby('product')['price'].transform('mean')
        # Fill missing prices with product mean, then with overall mean, then with 0
        df['price'] = df['price'].fillna(product_means)
        df['price'] = df['price'].fillna(df['price'].mean())
        df['price'] = df['price'].fillna(0)
    else:
        print("⚠️ Warning: No valid prices found, filling with 0")
        df['price'] = 0

    # 6. Handle missing customer_id
    df['customer_id'] = df['customer_id'].fillna('UNKNOWN')

    # 7. Remove rows with invalid quantities (e.g., negative or NaN)
    print("Removing invalid quantities...")
    initial_count = len(df)
    # Ensure quantity is numeric and positive
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
    df = df[df['quantity'] > 0]
    df = df[df['quantity'].notna()]
    print(f"Removed {initial_count - len(df)} rows with invalid quantities")

    # 8. Convert all prices to USD
    print("Converting currencies to USD...")
    conversion_rates = {currency: rate for currency, rate in exchange_rates.items()}
    
    def convert_to_usd(row):
        try:
            currency = str(row['currency']).upper().strip() if pd.notna(row['currency']) else 'USD'
            price = float(row['price']) if pd.notna(row['price']) else 0
            
            if currency == 'USD':
                return price
            
            if currency in conversion_rates:
                return price / conversion_rates[currency]
            else:
                print(f"Warning: Currency code '{currency}' not found in exchange rates. Using 0.")
                return 0
        except (ValueError, TypeError) as e:
            print(f"Warning: Error converting price: {e}. Using 0.")
            return 0

    df['price_usd'] = df.apply(convert_to_usd, axis=1)
    
    # Ensure price_usd is numeric
    df['price_usd'] = pd.to_numeric(df['price_usd'], errors='coerce').fillna(0)
    
    # Calculate total sale
    df['total_sale_usd'] = df['price_usd'] * df['quantity']
    
    # Ensure total_sale_usd is numeric
    df['total_sale_usd'] = pd.to_numeric(df['total_sale_usd'], errors='coerce').fillna(0)

    # 9. Save the cleaned data
    print("Saving cleaned data...")
    today_str = datetime.now().strftime("%Y%m%d")
    output_filename = f"cleaned_sales_data_{today_str}.csv"
    output_path = f"{CLEANED_DATA_DIR}/{output_filename}"
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned data saved to: {output_path}")

    # Show data types for debugging
    print("Final data types:")
    print(df.dtypes)

    return df

# Test the function
if __name__ == "__main__":
    from data_fetcher import fetch_csv_data, fetch_exchange_rates
    sales_df = fetch_csv_data()
    rates = fetch_exchange_rates()
    if sales_df is not None and rates is not None:
        cleaned_df = clean_data(sales_df, rates)
        print(cleaned_df.head(10))
        print(f"total_sale_usd dtype: {cleaned_df['total_sale_usd'].dtype}")