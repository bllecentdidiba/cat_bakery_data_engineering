import pandas as pd
import numpy as np
from utils import load_config, setup_logging, standardize_date, clean_string_column, validate_ids

# Load config and setup logging
config = load_config()
logger = setup_logging(config)


# HELPER FUNCTIONS FOR DATA CLEANING

def fix_invalid_ratings(df, rating_col='order_rating'):
    """
    Fix invalid ratings by taking the first digit.
    
    Logic: If someone typed '43', they probably meant '4'
           If they typed '58', they meant '5'
           If they typed '31', they meant '3'
    """
    logger.info(f"🔧 Fixing invalid ratings in {rating_col}")
    
    # Identify invalid ratings (not between 1-5)
    invalid_mask = ~df[rating_col].between(1, 5)
    invalid_count = invalid_mask.sum()
    
    if invalid_count == 0:
        logger.info("✅ All ratings are valid")
        return df
    
    logger.warning(f"⚠️ Found {invalid_count} invalid ratings")
        
    invalid_examples = df[invalid_mask][rating_col].head(10).tolist()
    logger.info(f"📝 Sample invalid ratings: {invalid_examples}")
    
    # Take the first digit, I did this because i saw mistakes were less than 60(I assumed users just mistakenly seleceted a second digit)
    def extract_first_digit(value):
        if pd.isna(value):
            return None
        
        try:
            # Converted to string and take first character
            str_val = str(int(float(value)))
            first_digit = int(str_val[0])
            
            # I confirmed if it's between 1-5 now
            if 1 <= first_digit <= 5:
                return float(first_digit)
            else:
                # If first digit is invalid (e.g., 6,7,8,9) then fallback to median
                return None
        except (ValueError, TypeError):
            return None
    
    # Apply the fix
    df['rating_fixed'] = df[rating_col].apply(extract_first_digit)
    
    # Fill any remaining nulls with median
    median_rating = df[df[rating_col].between(1, 5)][rating_col].median()
    if pd.isna(median_rating):
        median_rating = 3.0  # Default fallback
    
    df['rating_fixed'] = df['rating_fixed'].fillna(median_rating)
    
    # Replace original column
    df[rating_col] = df['rating_fixed'].round(1)
    df = df.drop('rating_fixed', axis=1)
    
    # Log results
    fixed_count = invalid_count - (~df[rating_col].between(1, 5)).sum()
    logger.info(f"✅ Fixed {fixed_count} invalid ratings")
    logger.info(f"📊 Rating range after fix: {df[rating_col].min()} - {df[rating_col].max()}")
    
    return df

def clean_product_names_early(df):
    """Clean product names - basic cleaning before database load"""
    logger.info("Cleaning product names...")
    
    if 'product_name' not in df.columns:
        logger.warning("product_name column not found")
        return df
    
    # Basic cleaning: strip whitespace and handle empty values
    df['product_name'] = df['product_name'].fillna('').astype(str).str.strip()
    
    # Replace empty strings with 'Unknown Product'
    df['product_name'] = df['product_name'].replace('', 'Unknown Product')
    
    logger.info(f"✅ Product names cleaned")
    return df

# TRANSFORM CUSTOMERS

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
    
    logger.info(f"✅ Customers transformed: {len(df)} rows")
    return df

# TRANSFORM ORDERS

def transform_orders(df):
    """Transform orders data with rating fixes"""
    logger.info("Starting orders transformation")
    df = df.copy()
    
    logger.info(f"📊 Orders BEFORE any changes: {len(df)} rows")
    
    # Rename columns to lowercase
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    
    # Check for required columns
    required_cols = ['customer_id', 'product_id', 'order_id', 'quantity', 'order_date']
    for col in required_cols:
        if col not in df.columns:
            logger.error(f"❌ Required column '{col}' not found in orders data!")
            return df
    
    # Standardize dates
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
    
    if valid_dates == 0:
        logger.error("❌ ALL DATES FAILED!")
        return df
    
    # FIX INVALID RATINGS
    if 'order_rating' in df.columns:
        logger.info("🔧 Fixing invalid ratings (taking first digit)...")
        df = fix_invalid_ratings(df, 'order_rating')
    else:
        logger.warning("⚠️ order_rating column not found, creating default")
        df['order_rating'] = 3.0
    
    # Handle missing ratings
    df['order_rating'] = df['order_rating'].fillna(
        config['cleaning']['imputation']['order_rating']
    )
    
    # Convert types
    df['customer_id'] = df['customer_id'].astype(int)
    df['product_id'] = df['product_id'].astype(str).str.strip()
    df['order_id'] = df['order_id'].astype(int)
    df['quantity'] = df['quantity'].astype(int)
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    # Add derived columns
    df['order_year'] = df['order_date'].dt.year
    df['order_month'] = df['order_date'].dt.month
    df['order_quarter'] = df['order_date'].dt.quarter
    df['order_day_of_week'] = df['order_date'].dt.day_name()
    
    # Filter valid rows
    df = df.dropna(subset=['order_date', 'order_id'])
    
    logger.info(f"✅ Orders transformed: {len(df)} rows")
    logger.info(f"📊 Rating range: {df['order_rating'].min()} - {df['order_rating'].max()}")
    
    return df


# TRANSFORM PRODUCTS

def transform_products(df):
    """Transform products data with basic cleaning"""
    logger.info("Starting products transformation")
    df = df.copy()
    
    # 1. Rename columns
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    
    # 2. Clean product names (basic cleaning)
    df = clean_product_names_early(df)
    
    # 3. Clean string columns
    df = clean_string_column(df, 'gluten_free')
    
    # 4. Clean product_id
    df['product_id'] = df['product_id'].astype(str).str.strip()
    
    # 5. Handle missing values
    df['gluten_free'] = df['gluten_free'].fillna(
        config['cleaning']['imputation']['gluten_free']
    )
    
    # 6. Fill numeric missing with median
    numeric_cols = ['quantity', 'cost', 'sales_price']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    
    # 7. Ensure proper types
    df['quantity'] = df['quantity'].astype(int)
    df['cost'] = df['cost'].astype(float)
    df['sales_price'] = df['sales_price'].astype(float)
    
    # 8. Add derived columns
    df['profit_margin'] = ((df['sales_price'] - df['cost']) / df['sales_price'] * 100).round(2)
    df['total_value'] = (df['quantity'] * df['sales_price']).round(2)
    
    # 9. Mark gluten-free as boolean for analysis
    df['is_gluten_free'] = df['gluten_free'].map({'Y': 1, 'N': 0, '': 0}).fillna(0)
    
    logger.info(f"✅ Products transformed: {len(df)} rows")
    return df

# RUNNING ALL TRANSFORMATIONS NOW

def run_all_transformations(raw_data):
    """Run all transformations"""
    logger.info("=" * 60)
    logger.info("Starting full transformation pipeline")
    logger.info("=" * 60)
    
    # Transform customers
    customers = transform_customers(raw_data['customers'])
    
    # Transform products
    products = transform_products(raw_data['products'])
    
    # Transform orders
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
        logger.info(f"✅ Saved {name} to {filepath}")
    
    logger.info("=" * 60)
    logger.info("✅ Transformation pipeline complete")
    logger.info("=" * 60)
    
    return transformed

if __name__ == "__main__":
    from extract import extract_all_raw
    raw = extract_all_raw()
    transformed = run_all_transformations(raw)
    print("✅ Transformation complete!")
    print(f"📊 Customers: {len(transformed['customers'])}")
    print(f"📊 Orders: {len(transformed['orders'])}")
    print(f"📊 Products: {len(transformed['products'])}")
