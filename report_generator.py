# report_generator.py

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
from config import REPORT_DIR, BASE_DIR

def generate_visualizations(cleaned_df):
    """Generates plots and returns their filenames."""
    print("Generating visualizations...")
    
    # Ensure output directory exists
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    plot_filenames = []
    
    try:
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)

        # 1. Sales by Product (Bar Chart) - only if we have numeric data
        if 'total_sale_usd' in cleaned_df.columns and pd.api.types.is_numeric_dtype(cleaned_df['total_sale_usd']):
            sales_by_product = cleaned_df.groupby('product')['total_sale_usd'].sum().sort_values(ascending=False)
            
            if not sales_by_product.empty and sales_by_product.sum() > 0:
                plt.figure()
                sales_by_product.plot(kind='bar', color='skyblue')
                plt.title('Total Sales by Product (USD)')
                plt.ylabel('Total Sales (USD)')
                plt.xticks(rotation=45)
                plot_filename_1 = 'sales_by_product.png'
                plot_path_1 = os.path.join(REPORT_DIR, plot_filename_1)
                plt.tight_layout()
                plt.savefig(plot_path_1, dpi=100, bbox_inches='tight')
                plt.close()
                plot_filenames.append(plot_filename_1)
                print("✅ Sales by product chart generated")
            else:
                print("⚠️ No valid sales data for product chart")
                plot_filenames.append(None)
        else:
            print("⚠️ total_sale_usd column missing or not numeric")
            plot_filenames.append(None)

        # 2. Daily Sales Trend (Line Chart) - only if we have date and numeric data
        if 'date' in cleaned_df.columns and 'total_sale_usd' in cleaned_df.columns:
            # Ensure date is datetime type
            daily_df = cleaned_df.copy()
            daily_df['date'] = pd.to_datetime(daily_df['date'], errors='coerce')
            daily_df = daily_df.dropna(subset=['date'])
            
            if not daily_df.empty:
                daily_sales = daily_df.groupby('date')['total_sale_usd'].sum()
                
                if not daily_sales.empty and daily_sales.sum() > 0:
                    plt.figure()
                    daily_sales.plot(kind='line', marker='o', color='green')
                    plt.title('Daily Sales Trend (USD)')
                    plt.ylabel('Total Sales (USD)')
                    plot_filename_2 = 'daily_trend.png'
                    plot_path_2 = os.path.join(REPORT_DIR, plot_filename_2)
                    plt.tight_layout()
                    plt.savefig(plot_path_2, dpi=100, bbox_inches='tight')
                    plt.close()
                    plot_filenames.append(plot_filename_2)
                    print("✅ Daily trend chart generated")
                else:
                    print("⚠️ No valid data for daily trend chart")
                    plot_filenames.append(None)
            else:
                print("⚠️ No valid dates for daily trend chart")
                plot_filenames.append(None)
        else:
            print("⚠️ Date or total_sale_usd column missing")
            plot_filenames.append(None)

    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")
        # Return None for both plots if there's an error
        return None, None

    # Ensure we return exactly two values
    while len(plot_filenames) < 2:
        plot_filenames.append(None)
    
    return plot_filenames[0], plot_filenames[1]

def generate_html_report(cleaned_df):
    """Generates a standalone HTML report."""
    print("Generating HTML report...")
    
    # Generate visualizations
    plot1_filename, plot2_filename = generate_visualizations(cleaned_df)

    # Calculate Summary Statistics
    total_sales = 0
    total_orders = 0
    aov = 0
    
    if 'total_sale_usd' in cleaned_df.columns:
        # Ensure total_sale_usd is numeric
        cleaned_df['total_sale_usd'] = pd.to_numeric(cleaned_df['total_sale_usd'], errors='coerce').fillna(0)
        total_sales = cleaned_df['total_sale_usd'].sum()
    
    if 'order_id' in cleaned_df.columns:
        total_orders = cleaned_df['order_id'].nunique()
    
    aov = total_sales / total_orders if total_orders > 0 else 0

    # Create a DataFrame for the top 5 orders if we have the data
    if 'total_sale_usd' in cleaned_df.columns and pd.api.types.is_numeric_dtype(cleaned_df['total_sale_usd']):
        try:
            # Ensure the column is numeric before using nlargest
            cleaned_df['total_sale_usd'] = pd.to_numeric(cleaned_df['total_sale_usd'], errors='coerce')
            top_orders = cleaned_df.nlargest(5, 'total_sale_usd')
            # Select only available columns
            available_columns = [col for col in ['order_id', 'date', 'product', 'quantity', 'total_sale_usd'] 
                               if col in top_orders.columns]
            top_orders = top_orders[available_columns]
            top_orders_html = top_orders.to_html(index=False, float_format='${:,.2f}'.format)
        except Exception as e:
            print(f"⚠️ Error getting top orders: {e}")
            # Fallback: just show the first 5 rows
            available_columns = [col for col in ['order_id', 'date', 'product', 'quantity', 'total_sale_usd'] 
                               if col in cleaned_df.columns]
            top_orders = cleaned_df.head(5)[available_columns]
            top_orders_html = top_orders.to_html(index=False, float_format='${:,.2f}'.format)
    else:
        top_orders_html = "<p>No sales data available for top orders</p>"

    # Set up Jinja2 environment and template
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report_template.html')

    # Get today's date for the report
    today = datetime.now().strftime("%Y-%m-%d")

    # Render HTML with variables
    html_out = template.render(
        date=today,
        total_sales=total_sales,
        total_orders=total_orders,
        aov=aov,
        sales_by_product_plot=plot1_filename,
        daily_trend_plot=plot2_filename,
        top_orders_table=top_orders_html
    )

    # Write HTML to a file
    html_path = f"{REPORT_DIR}/sales_report_{today}.html"
    with open(html_path, "w", encoding='utf-8') as f:
        f.write(html_out)
    print(f"✅ HTML report generated: {html_path}")
    return html_path

# Test the function
if __name__ == "__main__":
    from data_cleaner import clean_data
    from data_fetcher import fetch_csv_data, fetch_exchange_rates

    sales_df = fetch_csv_data()
    rates = fetch_exchange_rates()
    if sales_df is not None and rates is not None:
        cleaned_df = clean_data(sales_df, rates)
        generate_html_report(cleaned_df)