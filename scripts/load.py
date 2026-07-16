import pandas as pd
from sqlalchemy import create_engine, text
from utils import load_config, setup_logging
import os

config = load_config()
logger = setup_logging(config)

def clean_product_names_for_db(df):
    """Clean product names based on actual products.csv data"""
    logger.info("Cleaning product names for database...")
    
    # Show original unique products
    original_products = df['product_name'].unique().tolist()
    logger.info(f"📊 Original unique products: {len(original_products)}")
    logger.info(f"📊 Original products: {original_products}")
    
    product_name_mapping = {
        # Almond Croissant variations
        'Almond Croissant GF': 'Almond Croissant GF',
        'Almon Croissant GF': 'Almond Croissant GF',
        
        # Ciabatta variations (typos)
        'Ciabatta': 'Ciabatta',
        'Ciabater': 'Ciabatta',
        'Ciabattar': 'Ciabatta',
        
        # Sourdough variations
        'Sourcedough Loaf': 'Sourdough Loaf',
        'Sourcedogh Loaf': 'Sourdough Loaf',
        'ASourcedough Loaf': 'Sourdough Loaf',
        
        # Rye Bread variations
        'Rye Bread': 'Rye Bread',
        'RRye Bread': 'Rye Bread',
        
        # Blueberry Muffin
        'Blueberry Muffin GF': 'Blueberry Muffin GF',
        
        # Red Velvet Cupcake
        'Red Velvet Cupcake': 'Red Velvet Cupcake',
        
        # Empty product names
        '': 'Unknown Product',
        'NULL': 'Unknown Product',
        None: 'Unknown Product',
    }
    
    # Clean and standardize product names
    df['product_name_clean'] = df['product_name'].fillna('').str.strip()
    
    # Apply mapping
    df['product_name_clean'] = df['product_name_clean'].replace(product_name_mapping)
    
    # Log the cleaned names
    unique_names = df['product_name_clean'].unique().tolist()
    logger.info(f"✅ Cleaned product names: {len(unique_names)} unique products")
    logger.info(f"📊 Products: {unique_names}")
    
    # Replace the product_name column
    df['product_name'] = df['product_name_clean']
    df = df.drop('product_name_clean', axis=1)
    
    return df

def create_db_connection():
    """Create database connection"""
    db_config = config['database']
    connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    return create_engine(connection_string)

def create_star_schema(engine):
    """Create star schema tables"""
    logger.info("Creating star schema tables")
    
    sql_commands = [
        """DROP TABLE IF EXISTS fact_orders CASCADE""",
        """DROP TABLE IF EXISTS dim_customer CASCADE""",
        """DROP TABLE IF EXISTS dim_product CASCADE""",
        """DROP TABLE IF EXISTS dim_date CASCADE""",
        
        """
        CREATE TABLE IF NOT EXISTS dim_customer (
            customer_id INTEGER PRIMARY KEY,
            city VARCHAR(100),
            signup_date DATE,
            signup_year INTEGER,
            signup_month INTEGER,
            signup_quarter INTEGER,
            customer_tier VARCHAR(50),
            preferred_contact_method VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dim_product (
            product_id VARCHAR(20) PRIMARY KEY,
            product_name VARCHAR(200),
            gluten_free VARCHAR(5),
            is_gluten_free INTEGER,
            quantity INTEGER,
            cost DECIMAL(10,2),
            sales_price DECIMAL(10,2),
            profit_margin DECIMAL(10,2),
            total_value DECIMAL(10,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dim_date (
            date_id DATE PRIMARY KEY,
            year INTEGER,
            quarter INTEGER,
            month INTEGER,
            month_name VARCHAR(20),
            day INTEGER,
            day_name VARCHAR(20),
            day_of_week INTEGER,
            is_weekend BOOLEAN
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS fact_orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER REFERENCES dim_customer(customer_id),
            product_id VARCHAR(20) REFERENCES dim_product(product_id),
            order_date DATE,
            quantity INTEGER,
            order_rating DECIMAL(3,2),
            total_amount DECIMAL(10,2),
            order_year INTEGER,
            order_month INTEGER,
            order_quarter INTEGER,
            order_day_of_week VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_fact_customer ON fact_orders(customer_id);
        CREATE INDEX IF NOT EXISTS idx_fact_product ON fact_orders(product_id);
        CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_orders(order_date);
        """
    ]
    
    with engine.connect() as conn:
        for cmd in sql_commands:
            try:
                conn.execute(text(cmd))
                conn.commit()
            except Exception as e:
                logger.error(f"Error executing: {cmd[:50]}... Error: {str(e)}")
                raise
    
    logger.info("✅ Star schema tables created")

def load_dim_date(engine):
    """Generate and load date dimension"""
    logger.info("Loading date dimension")
    
    start_date = pd.to_datetime('2020-01-01')
    end_date = pd.to_datetime('2026-12-31')
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    date_data = pd.DataFrame({
        'date_id': dates,
        'year': dates.year,
        'quarter': dates.quarter,
        'month': dates.month,
        'month_name': dates.month_name(),
        'day': dates.day,
        'day_name': dates.day_name(),
        'day_of_week': dates.dayofweek + 1,
        'is_weekend': (dates.dayofweek >= 5)
    })
    
    date_data.to_sql('dim_date', engine, if_exists='replace', index=False)
    logger.info(f"✅ Loaded {len(date_data)} dates")

def load_dimensions(engine, transformed_data):
    """Load dimension tables with cleaned product names"""
    logger.info("Loading dimension tables")
    
    # Clean product names before loading
    products = transformed_data['products'].copy()
    products = clean_product_names_for_db(products)
    
    # Drop existing tables first
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS dim_customer CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS dim_product CASCADE"))
        conn.commit()
    
    # Load customers - using 'replace' to avoid duplicates
    customers = transformed_data['customers']
    customers.to_sql('dim_customer', engine, if_exists='replace', index=False)
    logger.info(f"✅ Loaded {len(customers)} customers")
    
    # Load products
    products.to_sql('dim_product', engine, if_exists='replace', index=False)
    logger.info(f"✅ Loaded {len(products)} products")
    
    # Log product names for verification
    unique_products = products['product_name'].unique().tolist()
    logger.info(f"📊 Products in database: {unique_products}")
    
    return products

def load_fact_table(engine, transformed_data, products):
    """Load fact table with date validation - 2026 ONLY"""
    logger.info("Loading fact orders")
    
    orders = transformed_data['orders']
    customers = transformed_data['customers']

    # Filter for 2026 ONLY
   
    logger.info("⏰ Filtering orders for 2026 only...")
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    
    # Filter for 2026
    orders_2026 = orders[orders['order_date'].dt.year == 2026]
    logger.info(f"📊 Orders before filter: {len(orders)}")
    logger.info(f"📊 Orders in 2026 only: {len(orders_2026)}")
    logger.info(f"🗑️ Removed {len(orders) - len(orders_2026)} orders from other years")
    
    orders = orders_2026
    
    #alidate and filter out future dates (within 2026)

    logger.info("⏰ Validating order dates...")
    today = pd.Timestamp.today().normalize()
    
    future_orders = orders[orders['order_date'] > today]
    if len(future_orders) > 0:
        logger.warning(f"⚠️ Found {len(future_orders)} orders with future dates!")
        logger.warning(f"📅 Future dates sample: {future_orders['order_date'].unique()[:5].tolist()}")
        orders = orders[orders['order_date'] <= today]
        logger.info(f"🗑️ Removed {len(future_orders)} future-dated orders")
    else:
        logger.info("✅ All orders have valid dates (none in the future)")
    
    logger.info(f"📊 Orders after date validation: {len(orders)} rows")
  
    
    # Use the cleaned products - include sales_price
    fact_orders = orders.merge(
        customers[['customer_id']], 
        on='customer_id', 
        how='inner'
    ).merge(
        products[['product_id', 'sales_price']],
        on='product_id', 
        how='inner'
    )
    
    # Calculate total_amount from quantity * sales_price
    fact_orders['total_amount'] = fact_orders['quantity'] * fact_orders['sales_price']
    
    fact_cols = ['order_id', 'customer_id', 'product_id', 'order_date', 
                 'quantity', 'order_rating', 'total_amount', 'order_year', 
                 'order_month', 'order_quarter', 'order_day_of_week']
    
    fact_orders = fact_orders[fact_cols]
    fact_orders.to_sql('fact_orders', engine, if_exists='replace', index=False)
    
    logger.info(f"✅ Loaded {len(fact_orders)} orders")
    logger.info(f"💰 Total Revenue (2026 only): R{fact_orders['total_amount'].sum():,.2f}")
def run_full_load(transformed_data):
    """Run full load process"""
    logger.info("Starting full load process")
    
    engine = create_db_connection()
    create_star_schema(engine)
    load_dim_date(engine)
    products = load_dimensions(engine, transformed_data)
    load_fact_table(engine, transformed_data, products)
    
    logger.info("✅ Load complete")
    return engine

if __name__ == "__main__":
    config = load_config()
    processed_path = config['paths']['processed_data']
    
    transformed_data = {
        'customers': pd.read_csv(f"{processed_path}customers_processed.csv"),
        'orders': pd.read_csv(f"{processed_path}orders_processed.csv"),
        'products': pd.read_csv(f"{processed_path}products_processed.csv")
    }
    
    engine = run_full_load(transformed_data)
    print("✅ Database load complete!")
    
    # Verify the data
    with engine.connect() as conn:
        result = pd.read_sql("""
            SELECT 
                product_name,
                COUNT(*) as product_count,
                SUM(quantity) as total_quantity,
                ROUND(AVG(sales_price), 2) as avg_price
            FROM dim_product
            GROUP BY product_name
            ORDER BY product_name
        """, conn)
        print("\n📊 Products in database:")
        print(result.to_string(index=False))
