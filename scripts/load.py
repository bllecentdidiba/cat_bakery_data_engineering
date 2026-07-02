import pandas as pd
from sqlalchemy import create_engine, text
from utils import load_config, setup_logging
import os

config = load_config()
logger = setup_logging(config)

def create_db_connection():
    """Create database connection"""
    db_config = config['database']
    connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    return create_engine(connection_string)

def create_star_schema(engine):
    """Create star schema tables"""
    logger.info("Creating star schema tables")
    
    sql_commands = [
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
            conn.execute(text(cmd))
            conn.commit()
    logger.info("Star schema tables created")

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
    logger.info(f"Loaded {len(date_data)} dates")

def load_dimensions(engine, transformed_data):
    """Load dimension tables"""
    logger.info("Loading dimension tables")
    
    # Drop tables with CASCADE to handle dependencies
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS dim_customer CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS dim_product CASCADE"))
        conn.commit()
    
    customers = transformed_data['customers']
    customers.to_sql('dim_customer', engine, if_exists='append', index=False)
    logger.info(f"Loaded {len(customers)} customers")
    
    products = transformed_data['products']
    products.to_sql('dim_product', engine, if_exists='append', index=False)
    logger.info(f"Loaded {len(products)} products")

def load_fact_table(engine, transformed_data):
    """Load fact table"""
    logger.info("Loading fact orders")
    
    orders = transformed_data['orders']
    customers = transformed_data['customers']
    products = transformed_data['products']
    
    fact_orders = orders.merge(
        customers[['customer_id']], 
        on='customer_id', 
        how='inner'
    ).merge(
        products[['product_id']], 
        on='product_id', 
        how='inner'
    )
    
    if 'total_amount' not in fact_orders.columns:
        fact_orders['total_amount'] = fact_orders['quantity'] * 1.0
    
    fact_cols = ['order_id', 'customer_id', 'product_id', 'order_date', 
                 'quantity', 'order_rating', 'total_amount', 'order_year',
                 'order_month', 'order_quarter', 'order_day_of_week']
    
    fact_orders = fact_orders[fact_cols]
    
    fact_orders.to_sql('fact_orders', engine, if_exists='replace', index=False)
    logger.info(f"Loaded {len(fact_orders)} orders")

def run_full_load(transformed_data):
    """Run full load process"""
    logger.info("Starting full load process")
    
    engine = create_db_connection()
    
    create_star_schema(engine)
    load_dim_date(engine)
    load_dimensions(engine, transformed_data)
    load_fact_table(engine, transformed_data)
    
    logger.info("Load complete")
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
    print("Database load complete!")