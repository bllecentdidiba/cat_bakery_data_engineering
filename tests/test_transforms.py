import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add the scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from utils import standardize_date, clean_string_column, validate_ids
from transform import fix_invalid_ratings, clean_product_names_early

# TESTS FOR UTILITY FUNCTIONS

def test_standardize_date():
    """Test date standardization"""
    date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%A, %B %d, %Y']
    
    # Valid dates
    assert standardize_date('2024-11-21', date_formats) == '2024-11-21'
    assert standardize_date('11/21/2024', date_formats) == '2024-11-21'
    assert standardize_date('Tuesday, April 21, 2020', date_formats) == '2020-04-21'
    
    # Invalid dates
    assert standardize_date('invalid', date_formats) is None
    assert standardize_date(np.nan, date_formats) is None
    assert standardize_date('', date_formats) is None
    assert standardize_date('NULL', date_formats) is None

def test_clean_string_column():
    """Test string cleaning"""
    df = pd.DataFrame({'test': ['  Hello  ', 'NULL', '  World  ', 'None', '']})
    df = clean_string_column(df, 'test')
    
    assert df['test'].iloc[0] == 'Hello'
    assert df['test'].iloc[1] == '' 
    assert df['test'].iloc[2] == 'World'
    assert df['test'].iloc[3] == '' 
    assert df['test'].iloc[4] == ''

def test_validate_ids():
    """Test ID validation - only positive integers should remain"""
    df = pd.DataFrame({
        'id': [1, -5, 10, 0, 3.5, 'invalid', 7, -2]
    })
    df = validate_ids(df, 'id')
    
    # Only 1, 10, 3.5 (converts to 3), and 7 should remain
    assert len(df) == 4
    assert all(df['id'] > 0)
    assert df['id'].tolist() == [1, 10, 3, 7]  # 3.5 becomes 3

# TESTS FOR RATING FIX

def test_fix_invalid_ratings():
    """Test fixing invalid ratings by taking first digit"""
    
    # Test data 
    df = pd.DataFrame({
        'order_rating': [5, 43, 4, 58, 3, 31, 2, 45, 1, 52]
    })
    
    df = fix_invalid_ratings(df, 'order_rating')

    expected = [5.0, 4.0, 4.0, 5.0, 3.0, 3.0, 2.0, 4.0, 1.0, 5.0]
    assert df['order_rating'].tolist() == expected
    
    # Test with no invalid ratings
    df = pd.DataFrame({'order_rating': [5, 4, 3, 2, 1]})
    df = fix_invalid_ratings(df, 'order_rating')
    assert df['order_rating'].tolist() == [5.0, 4.0, 3.0, 2.0, 1.0]
    
    # Test with NaN values
    df = pd.DataFrame({'order_rating': [5, np.nan, 43, 4]})
    df = fix_invalid_ratings(df, 'order_rating')

    assert df['order_rating'].iloc[0] == 5.0
    assert df['order_rating'].iloc[2] == 4.0
    assert not pd.isna(df['order_rating'].iloc[1])
    
    # Test with first digit > 5
    df = pd.DataFrame({'order_rating': [67, 89, 4, 5]})
    df = fix_invalid_ratings(df, 'order_rating')
    median = 4.5  # median of 4 and 5
    assert df['order_rating'].iloc[0] == median
    assert df['order_rating'].iloc[1] == median

def test_fix_invalid_ratings_edge_cases():
    """Test edge cases for rating fixing"""
    
    # Test with all invalid ratings
    df = pd.DataFrame({'order_rating': [45, 58, 31, 42]})
    df = fix_invalid_ratings(df, 'order_rating')
    expected = [4.0, 5.0, 3.0, 4.0]  # Taking first digit
    assert df['order_rating'].tolist() == expected
    
    # Test with ratings that are already valid
    df = pd.DataFrame({'order_rating': [1, 2, 3, 4, 5]})
    df = fix_invalid_ratings(df, 'order_rating')
    assert df['order_rating'].tolist() == [1.0, 2.0, 3.0, 4.0, 5.0]
    
    # Test with negative values (should be handled)
    df = pd.DataFrame({'order_rating': [-1, 0, 43, 4]})
    df = fix_invalid_ratings(df, 'order_rating')
    # -1 and 0 should be fixed to median
    assert df['order_rating'].iloc[2] == 4.0
    assert df['order_rating'].iloc[3] == 4.0

# TESTS FOR PRODUCT NAME CLEANING

def test_clean_product_names_early():
    """Test basic product name cleaning"""
    
    df = pd.DataFrame({
        'product_name': ['  Almond Croissant  ', '', '  Ciabatta  ', None, '  ']
    })
    
    df = clean_product_names_early(df)
    
    assert df['product_name'].iloc[0] == 'Almond Croissant'
    assert df['product_name'].iloc[1] == 'Unknown Product'  
    assert df['product_name'].iloc[2] == 'Ciabatta'
    assert df['product_name'].iloc[3] == 'Unknown Product' 
    assert df['product_name'].iloc[4] == 'Unknown Product' 
    
    # Test with no product_name column
    df = pd.DataFrame({'other_col': [1, 2, 3]})
    df = clean_product_names_early(df)
    assert 'product_name' not in df.columns 

def test_clean_product_names_with_mixed_cases():
    """Test product name cleaning with mixed cases"""
    
    df = pd.DataFrame({
        'product_name': ['  ALMOND CROISSANT  ', '  ciabatta  ', '  RYE BREAD  ']
    })
    
    df = clean_product_names_early(df)
    
    # clean_product_names_early only strips whitespace, doesn't change case
    assert df['product_name'].iloc[0] == 'ALMOND CROISSANT'
    assert df['product_name'].iloc[1] == 'ciabatta'
    assert df['product_name'].iloc[2] == 'RYE BREAD'

# TEST FOR ENTIRE TRANSFORM PIPELINE

def test_complete_transform_flow():
    """Test the entire transform flow with real data"""
    from transform import transform_customers, transform_orders, transform_products
    
    # Create sample data
    customers_df = pd.DataFrame({
        'customer_id': [1, 2, 3],
        'city': ['  New York  ', '  Los Angeles  ', '  Chicago  '],
        'signup_date': ['2024-01-15', '2024-02-20', '2024-03-25'],
        'customer_tier': ['Gold', 'Silver', 'Bronze'],
        'preferred_contact_method': ['Email', 'Phone', 'Email']
    })
    
    orders_df = pd.DataFrame({
        'order_id': [101, 102, 103],
        'customer_id': [1, 2, 1],
        'product_id': ['P001', 'P002', 'P001'],
        'quantity': [2, 1, 3],
        'order_date': ['2024-01-15', '2024-02-20', '2024-03-25'],
        'order_rating': [5, 43, 4] 
    })
    
    products_df = pd.DataFrame({
        'product_id': ['P001', 'P002'],
        'product_name': ['  Almond Croissant  ', '  Ciabatta  '],
        'gluten_free': ['N', 'Y'],
        'quantity': [100, 50],
        'cost': [10.0, 8.0],
        'sales_price': [15.0, 12.0]
    })
    
    # Transform each
    customers = transform_customers(customers_df)
    orders = transform_orders(orders_df)
    products = transform_products(products_df)
    
    # Check customers
    assert len(customers) == 3
    assert customers['city'].iloc[0] == 'New York'
    
    # Check orders - rating 43 should become 4
    assert len(orders) == 3
    assert orders['order_rating'].iloc[1] == 4.0 
    
    # Check products
    assert len(products) == 2
    assert products['product_name'].iloc[0] == 'Almond Croissant'
    assert products['product_name'].iloc[1] == 'Ciabatta'

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
