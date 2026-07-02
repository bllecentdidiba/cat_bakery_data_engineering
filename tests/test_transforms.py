import pytest
import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from utils import standardize_date, clean_string_column, validate_ids

def test_standardize_date():
    """Test date standardization"""
    assert standardize_date('2024-11-21', ['%Y-%m-%d']) == '2024-11-21'
    assert standardize_date('11/21/2024', ['%m/%d/%Y']) == '2024-11-21'
    assert standardize_date('Tuesday, April 21, 2020', ['%A, %B %d, %Y']) == '2020-04-21'
    assert standardize_date('invalid', ['%Y-%m-%d']) is None
    assert standardize_date(np.nan, ['%Y-%m-%d']) is None

def test_clean_string_column():
    """Test string cleaning"""
    df = pd.DataFrame({'test': ['  Hello  ', 'NULL', '  World  ']})
    df = clean_string_column(df, 'test')
    assert df['test'].iloc[0] == 'Hello'
    assert df['test'].iloc[1] == ''
    assert df['test'].iloc[2] == 'World'

def test_validate_ids():
    """Test ID validation"""
    df = pd.DataFrame({'id': [1, -5, 10, 0, 3.5, 'invalid']})
    df = validate_ids(df, 'id')
    assert len(df) == 3  # Only 1, 10, 3.5 should remain


    