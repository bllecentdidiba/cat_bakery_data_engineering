"""
Extract script - reads raw CSV files
This is simple, just loads the data from the raw folder
"""

import pandas as pd 
import os
from utils import load_config, setup_logging

# Load config
config = load_config()
logger = setup_logging(config)

# Quick check to make sure paths exist

def extract_csv(file_path):
    """Extract data from CSV with error handling"""
    try:
        logger.info(f"Extracting data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"✅ Extracted {len(df)} rows from {os.path.basename(file_path)}")
        return df
    except FileNotFoundError:
        logger.error(f"❌ File not found: {file_path}")
        print(f"❌ File not found: {file_path}")
        print("💡 Make sure the raw data files exist in the data/raw/ folder")
        raise
    except Exception as e:
        logger.error(f"❌ Error extracting {file_path}: {str(e)}")
        print(f"❌ Error: {str(e)}")
        raise

def extract_all_raw():
    """Extract all raw data files"""
    raw_path = config['paths']['raw_data']
    
    # I could make this more dynamic, but because there is only 3 files for now
    customers = extract_csv(os.path.join(raw_path, 'customers.csv'))
    orders = extract_csv(os.path.join(raw_path, 'orders.csv'))
    products = extract_csv(os.path.join(raw_path, 'products.csv'))
    
    return {
        'customers': customers,
        'orders': orders,
        'products': products
    }

# This runs when the script is executed directly
if __name__ == "__main__":
    print("🐱 Bakery ETL - Extraction Phase")
    print("=" * 40)
    
    raw_data = extract_all_raw()
    
    print("\n✅ Extraction complete!")
    print(f"📊 Customers: {len(raw_data['customers']):,} rows")
    print(f"📊 Orders: {len(raw_data['orders']):,} rows")
    print(f"📊 Products: {len(raw_data['products']):,} rows")
    print("\n💡 Ready for transformation phase")
