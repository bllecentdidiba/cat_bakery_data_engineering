import pandas as pd
import numpy as np
import logging
import yaml
from datetime import datetime
import os
import re

def load_config():
    """Load configuration from YAML file"""
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # The config folder is in the same directory as utils.py
    config_path = os.path.join(current_dir, 'config', 'config.yaml')
    print(f"Loading config from: {config_path}")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def setup_logging(config):
    """Setup logging configuration"""
    log_dir = config['paths'].get('logs', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = f"{log_dir}/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=config['logging']['level'],
        format=config['logging']['format'],
        handlers=[
            logging.FileHandler(log_file),
             logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def standardize_date(date_str, date_formats):
    """Standardize date to YYYY-MM-DD format"""
    if pd.isna(date_str) or date_str in ['', 'NULL', 'None']:
        return None
    
    date_str = str(date_str).strip()
    
    for fmt in date_formats:
        try:
            return pd.to_datetime(date_str, format=fmt).strftime('%Y-%m-%d')
        except:
            continue
    
    try:
        return pd.to_datetime(date_str).strftime('%Y-%m-%d')
    except:
        return None

def clean_string_column(df, col):
    """Clean string column: strip whitespace, uppercase first letter"""
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].str.replace('NULL', '')
        df[col] = df[col].str.replace('None', '')
        df[col] = df[col].str.title()
        df[col] = df[col].replace(['', 'Nan', 'NAN'], np.nan)
    return df

def validate_ids(df, id_col):
    """Validate ID columns are positive integers"""
    if id_col in df.columns:
        df[id_col] = pd.to_numeric(df[id_col], errors='coerce')
        df = df[df[id_col] > 0]
    return df

def save_to_csv(df, filepath, index=False):
    """Save DataFrame to CSV with proper formatting"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=index)
    return filepath

def calculate_missing_stats(df):
    """Calculate missing value statistics"""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    stats = pd.DataFrame({
        'Missing_Count': missing,
        'Missing_Percentage': missing_pct
    })
    return stats[stats['Missing_Count'] > 0].sort_values('Missing_Percentage', ascending=False)
