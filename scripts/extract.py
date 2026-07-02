import pandas as pd
import os
from utils import load_config, setup_logging

config = load_config()
logger = setup_logging(config)

def extract_csv(file_path):
    """Extract data from CSV with error handling"""
    try:
        logger.info(f"Extracting data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Extracted {len(df)} rows from {os.path.basename(file_path)}")
        return df
    except Exception as e:
        logger.error(f"Error extracting {file_path}: {str(e)}")
        raise

def extract_all_raw():
    """Extract all raw data files"""
    raw_path = config['paths']['raw_data']
    
    customers = extract_csv(os.path.join(raw_path, 'customers.csv'))
    orders = extract_csv(os.path.join(raw_path, 'orders.csv'))
    products = extract_csv(os.path.join(raw_path, 'products.csv'))
    
    return {
        'customers': customers,
        'orders': orders,
        'products': products
    }

if __name__ == "__main__":
    raw_data = extract_all_raw()
    print("Extraction complete!")
    print(f"Customers: {len(raw_data['customers'])} rows")
    print(f"Orders: {len(raw_data['orders'])} rows")
    print(f"Products: {len(raw_data['products'])} rows")