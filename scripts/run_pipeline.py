import sys
import os
import importlib.util
from pathlib import Path

scripts_path = os.path.dirname(__file__)
parent_path = os.path.dirname(scripts_path)

sys.path.insert(0, scripts_path)
sys.path.insert(0, parent_path)

# Manually loaded modules using the file names
spec = importlib.util.spec_from_file_location("extract", os.path.join(scripts_path, "extract.py"))
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)

spec2 = importlib.util.spec_from_file_location("transform", os.path.join(scripts_path, "transform.py"))
transform = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(transform)

spec3 = importlib.util.spec_from_file_location("load", os.path.join(scripts_path, "load.py"))
load = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(load)

# Import utils normally
from utils import load_config, setup_logging
import pandas as pd

# Assigning the functions
extract_all_raw = extract.extract_all_raw
run_all_transformations = transform.run_all_transformations
run_full_load = load.run_full_load

def main():
    # Setup logging
    config = load_config()
    logger = setup_logging(config)
    
    logger.info("=" * 60)
    logger.info("STARTING BAKERY ETL PIPELINE")
    logger.info("=" * 60)
    
    # Extract
    logger.info("STEP 1: Extracting raw data...")
    raw_data = extract_all_raw()
    logger.info(f"Extracted: {len(raw_data['customers'])} customers, "
               f"{len(raw_data['orders'])} orders, "
               f"{len(raw_data['products'])} products")
    
    # Transform
    logger.info("STEP 2: Transforming data...")
    transformed_data = run_all_transformations(raw_data)
    logger.info("Transformation complete")
    
    # Load
    logger.info("STEP 3: Loading data to database...")
    engine = run_full_load(transformed_data)
    logger.info("Load complete")
    
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
    logger.info("=" * 60)
    
    logger.info("\nTo view dashboard, run:")
    logger.info("streamlit run scripts/05_dashboard.py")

if __name__ == "__main__":
    main()
