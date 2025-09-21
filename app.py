# app.py

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from data_fetcher import fetch_exchange_rates
from data_cleaner import clean_data
from report_generator import generate_html_report
import tempfile

# Page configuration
st.set_page_config(
    page_title="Sales Data Processor",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("📊 Sales Data Automation Dashboard")
st.markdown("""
Upload your sales data CSV file, and we'll automatically clean it, 
add exchange rates, and generate a beautiful report!
""")

# Sidebar for configuration
st.sidebar.header("Configuration")

# File upload section
uploaded_file = st.sidebar.file_uploader(
    "📁 Upload Sales Data CSV",
    type="csv",
    help="Upload your sales data in CSV format"
)

# # Date format selection
# date_format = st.sidebar.selectbox(
#     "Date Format in your CSV",
#     ["YYYY-MM-DD", "YYYY/MM/DD", "MM/DD/YYYY", "DD/MM/YYYY"],
#     help="Select the date format used in your CSV file"
# )

# # Currency options
# base_currency = st.sidebar.selectbox(
#     "Base Currency for Conversion",
#     ["USD", "EUR", "GBP", "JPY", "CAD"],
#     index=0,
#     help="Select the base currency for exchange rate conversion"
# )

# Main content area
if uploaded_file is not None:
    # Display file info
    st.success("✅ File uploaded successfully!")
    file_details = {
        "Filename": uploaded_file.name,
        "File size": f"{uploaded_file.size / 1024:.2f} KB",
        "File type": uploaded_file.type
    }
    st.write(file_details)
    
    # Preview the raw data
    st.subheader("📋 Raw Data Preview")
    try:
        raw_df = pd.read_csv(uploaded_file)
        st.dataframe(raw_df.head(), use_container_width=True)
        
        # Show data statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", len(raw_df))
        with col2:
            st.metric("Total Columns", len(raw_df.columns))
        with col3:
            st.metric("Missing Values", raw_df.isnull().sum().sum())
            
    except Exception as e:
        st.error(f"❌ Error reading CSV file: {e}")
        st.stop()
    
    # Process data when user clicks the button
    if st.button("🚀 Process Data & Generate Report", type="primary"):
        with st.spinner("Processing your data... This may take a few seconds."):
            try:
                # Create a temporary file for processing
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_file_path = tmp_file.name
                
                # Step 1: Fetch exchange rates
                st.info("🌍 Fetching latest exchange rates...")
                exchange_rates = fetch_exchange_rates()
                if exchange_rates is None:
                    st.error("Failed to fetch exchange rates. Please check your internet connection.")
                    st.stop()
                
                # Step 2: Clean and process data
                st.info("🧹 Cleaning and processing data...")
                cleaned_df = clean_data(raw_df, exchange_rates)
                
                # Display cleaned data preview
                st.subheader("✅ Cleaned Data Preview")
                st.dataframe(cleaned_df.head(), use_container_width=True)
                
                # Show cleaning results
                st.subheader("📈 Cleaning Results")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Rows Processed", len(cleaned_df))
                with col2:
                    st.metric("Duplicates Removed", len(raw_df) - len(cleaned_df.drop_duplicates()))
                with col3:
                    st.metric("Missing Values Fixed", raw_df.isnull().sum().sum() - cleaned_df.isnull().sum().sum())
                with col4:
                    total_sales = cleaned_df['total_sale_usd'].sum()
                    st.metric("Total Sales (USD)", f"${total_sales:,.2f}")
                
                # Step 3: Generate report
                st.info("📊 Generating report...")
                report_path = generate_html_report(cleaned_df)
                
                # Step 4: Provide download links
                st.success("🎉 Report generated successfully!")
                
                # Create download buttons
                st.subheader("📥 Download Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Download cleaned CSV
                    csv_data = cleaned_df.to_csv(index=False)
                    st.download_button(
                        label="📄 Download Cleaned CSV",
                        data=csv_data,
                        file_name=f"cleaned_sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        help="Download the cleaned data as CSV"
                    )
                
                with col2:
                    # Download HTML report
                    with open(report_path, "rb") as f:
                        html_data = f.read()
                    st.download_button(
                        label="📋 Download HTML Report",
                        data=html_data,
                        file_name=os.path.basename(report_path),
                        mime="text/html",
                        help="Download the complete HTML report"
                    )
                
                # Display the report inline
                st.subheader("👀 Report Preview")
                st.components.v1.html(open(report_path, 'r').read(), height=1000, scrolling=True)
                
                # Clean up temporary file
                os.unlink(temp_file_path)
                
            except Exception as e:
                st.error(f"❌ Error processing data: {e}")
                import traceback
                st.code(traceback.format_exc())
else:
    # Show instructions when no file is uploaded
    st.info("👈 Please upload a CSV file using the sidebar to get started!")
    
    # Example data format
    st.subheader("📋 Expected CSV Format")
    example_data = {
        'order_id': [1001, 1002, 1003],
        'date': ['2023-10-25', '2023-10-25', '2023-10-26'],
        'product': ['Widget A', 'Gadget B', 'Widget A'],
        'price': [15.99, 24.50, 15.99],
        'currency': ['USD', 'EUR', 'USD'],
        'quantity': [2, 1, 1],
        'customer_id': ['C101', 'C102', 'C103']
    }
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True)
    
    # Download sample template
    csv_example = example_df.to_csv(index=False)
    st.download_button(
        label="📄 Download Sample Template",
        data=csv_example,
        file_name="sales_data_template.csv",
        mime="text/csv",
        help="Download a sample CSV template to get started"
    )