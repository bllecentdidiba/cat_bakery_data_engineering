import pandas as pd
import numpy as np
from utils import load_config, setup_logging, standardize_date, clean_string_column, validate_ids

# Load config and setup logging
config = load_config()
logger = setup_logging(config)

# ----------------------------------------------------------------------------
# TRANSFORM CUSTOMERS
# ----------------------------------------------------------------------------
def transform_customers(df):
    """Transform customers data"""
    logger.info("Starting customers transformation")
    df = df.copy()
    
    # 1. Rename columns
    df.columns = [col.lower().replace(' ', '_').replace('prefered', 'preferred') 
                  for col in df.columns]
    
    # 2. Clean string columns
    string_cols = ['city', 'customer_tier', 'preferred_contact_method']
    for col in string_cols:
        if col in df.columns:
            df = clean_string_column(df, col)
    
    # 3. Standardize dates
    logger.info("Standardizing signup dates")
    df['signup_date'] = df['signup_date'].apply(
        lambda x: standardize_date(x, config['cleaning']['date_formats'])
    )
    
    # 4. Validate IDs
    df = validate_ids(df, 'customer_id')
    
    # 5. Handle missing values
    missing_config = config['cleaning']['imputation']
    df['city'] = df['city'].fillna(missing_config['city'])
    df['customer_tier'] = df['customer_tier'].fillna(missing_config['customer_tier'])
    df['preferred_contact_method'] = df['preferred_contact_method'].fillna(
        missing_config['preferred_contact_method']
    )
    
    # 6. Convert to proper types
    df['customer_id'] = df['customer_id'].astype(int)
    df['signup_date'] = pd.to_datetime(df['signup_date'])
    
    # 7. Add derived columns
    df['signup_year'] = df['signup_date'].dt.year
    df['signup_month'] = df['signup_date'].dt.month
    df['signup_quarter'] = df['signup_date'].dt.quarter
    
    logger.info(f"Customers transformed: {len(df)} rows")
    return df

# ----------------------------------------------------------------------------
# TRANSFORM ORDERS - FIXED VERSION WITH DEBUGGING
# ----------------------------------------------------------------------------
def transform_orders(df):
    """Transform orders data"""
    logger.info("Starting orders transformation")
    df = df.copy()
    
    # 🔍 DEBUG: Check the data BEFORE any changes
    logger.info(f"📊 Orders BEFORE any changes: {len(df)} rows")
    logger.info(f"📊 Columns: {df.columns.tolist()}")
    
    # Rename columns to lowercase
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    logger.info(f"📊 Columns after rename: {df.columns.tolist()}")
    
    # Check for required columns
    required_cols = ['customer_id', 'product_id', 'order_id', 'quantity', 'order_date']
    for col in required_cols:
        if col not in df.columns:
            logger.error(f"❌ Required column '{col}' not found in orders data!")
            logger.info(f"📊 Available columns: {df.columns.tolist()}")
            return df  # Return empty df to prevent crash
    
    # 🔍 DEBUG: Check sample data
    logger.info(f"📊 Sample customer_id: {df['customer_id'].head(5).tolist()}")
    logger.info(f"📊 Sample product_id: {df['product_id'].head(5).tolist()}")
    logger.info(f"📊 Sample order_date: {df['order_date'].head(5).tolist()}")
    
    # 🔴 TEMPORARILY COMMENT OUT VALIDATION TO TEST
    # This will help us see if validation is dropping all rows
    # df = validate_ids(df, 'customer_id')
    # df = validate_ids(df, 'product_id')
    # df = validate_ids(df, 'order_id')
    # df = validate_ids(df, 'quantity')
    logger.info("📊 SKIPPING validation to test...")
    
    # 3. Standardize dates - with error handling
    logger.info("Standardizing order dates...")
    try:
        df['order_date'] = df['order_date'].apply(
            lambda x: standardize_date(x, config['cleaning']['date_formats'])
        )
        logger.info(f"✅ Dates standardized successfully")
    except Exception as e:
        logger.error(f"❌ Error standardizing dates: {str(e)}")
        return df
    
    # Check how many dates were parsed
    valid_dates = df['order_date'].notna().sum()
    logger.info(f"📊 {valid_dates} / {len(df)} rows have valid dates")
    
    # If all dates failed, show sample
    if valid_dates == 0:
        logger.error("❌ ALL DATES FAILED! Sample raw dates:")
        logger.error(df['order_date'].head(10).tolist())
        return df
    
    # 4. Handle missing ratings
    df['order_rating'] = df['order_rating'].fillna(
        config['cleaning']['imputation']['order_rating']
    )
    
    # 5. Convert types
    df['customer_id'] = df['customer_id'].astype(int)
    df['product_id'] = df['product_id'].astype(str)
    df['order_id'] = df['order_id'].astype(int)
    df['quantity'] = df['quantity'].astype(int)
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # 6. Add derived columns
    df['order_year'] = df['order_date'].dt.year
    df['order_month'] = df['order_date'].dt.month
    df['order_quarter'] = df['order_date'].dt.quarter
    df['order_day_of_week'] = df['order_date'].dt.day_name()
    
    # 7. Filter valid rows
    df = df.dropna(subset=['order_date', 'order_id'])
    logger.info(f"Orders transformed: {len(df)} rows")
    return df

# ----------------------------------------------------------------------------
# TRANSFORM PRODUCTS
# ----------------------------------------------------------------------------
def transform_products(df):
    """Transform products data"""
    logger.info("Starting products transformation")
    df = df.copy()
    
    # 1. Rename columns
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    
    # 2. Clean string columns
    df = clean_string_column(df, 'product_name')
    df = clean_string_column(df, 'gluten_free')
    
    # 3. Clean product_id
    df['product_id'] = df['product_id'].astype(str).str.strip()
    
    # 4. Handle missing values
    df['product_name'] = df['product_name'].fillna('Unknown Product')
    df['gluten_free'] = df['gluten_free'].fillna(
        config['cleaning']['imputation']['gluten_free']
    )
    
    # 5. Fill numeric missing with median
    numeric_cols = ['quantity', 'cost', 'sales_price']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    
    # 6. Ensure proper types
    df['quantity'] = df['quantity'].astype(int)
    df['cost'] = df['cost'].astype(float)
    df['sales_price'] = df['sales_price'].astype(float)
    
    # 7. Add derived columns
    df['profit_margin'] = ((df['sales_price'] - df['cost']) / df['sales_price'] * 100).round(2)
    df['total_value'] = (df['quantity'] * df['sales_price']).round(2)
    
    # 8. Mark gluten-free as boolean for analysis
    df['is_gluten_free'] = df['gluten_free'].map({'Y': 1, 'N': 0, '': 0}).fillna(0)
    
    logger.info(f"Products transformed: {len(df)} rows")
    return df

# ----------------------------------------------------------------------------
# RUN ALL TRANSFORMATIONS
# ----------------------------------------------------------------------------
def run_all_transformations(raw_data):
    """Run all transformations"""
    logger.info("Starting full transformation pipeline")
    
    # First transform customers and products
    customers = transform_customers(raw_data['customers'])
    products = transform_products(raw_data['products'])
    
    # Now transform orders
    orders = transform_orders(raw_data['orders'])
    
    transformed = {
        'customers': customers,
        'orders': orders,
        'products': products
    }
    
    # Save processed data
    processed_path = config['paths']['processed_data']
    for name, df in transformed.items():
        filepath = f"{processed_path}{name}_processed.csv"
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {name} to {filepath}")
    
    return transformed

if __name__ == "__main__":
    # For testing: run this file directly
    from scripts import extract_all_raw
    raw = extract_all_raw()
    transformed = run_all_transformations(raw)
    print("Transformation complete!")