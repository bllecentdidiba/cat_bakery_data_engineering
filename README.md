# 🐱 Cat Bakery Data Engineering Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **End-to-end ETL pipeline processing 110,000+ bakery transactions - from messy CSV files to an interactive dashboard.**

---

## 📊 Overview

This project is a **complete data engineering platform** built for a cat bakery business. It extracts raw data from multiple CSV files, cleans and transforms inconsistent data, loads it into a PostgreSQL star schema and visualizes business insights through an interactive dashboard.

**The Problem:** The bakery had messy data spread across multiple CSV files with inconsistent date formats, thousands of missing values and no single way to analyze performance.

**The Solution:** An automated ETL pipeline that handles data cleaning, validation and loading; delivering clean, analysis-ready data in minutes instead of hours.

---

## 🏗️ Architecture

| Stage | Tools | Output |
|-------|-------|--------|
| **Extract** | Python (Pandas) | Raw data from CSV files |
| **Transform** | Python (Pandas, NumPy) | Cleaned, validated data |
| **Load** | Python (SQLAlchemy) | PostgreSQL star schema |
| **Visualize** | Streamlit + Plotly | Interactive dashboard |

---

**## 🗄️ Star Schema Design**

| Table | Columns | Description |
|-------|---------|-------------|
| **dim_customer** | customer_id (PK), city, signup_date, customer_tier, signup_year, signup_month | Customer information and demographics |
| **dim_product** | product_id (PK), product_name, gluten_free, cost, sales_price, profit_margin | Product catalog and pricing |
| **dim_date** | date_id (PK), year, quarter, month, month_name, day, day_name, is_weekend | Date dimension for time-based analysis |
| **fact_orders** | order_id (PK), customer_id (FK), product_id (FK), order_date (FK), quantity, order_rating, total_amount, order_year, order_month | Transaction facts linked to all dimensions |

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **ETL Pipeline** | Python, Pandas, NumPy, SQLAlchemy |
| **Database** | PostgreSQL (Star Schema) |
| **Visualization** | Streamlit, Plotly |
| **Testing** | Pytest |
| **Containerization** | Docker |
| **Version Control** | Git, GitHub |

---

## 📈 Results & Metrics

| Metric | Value |
|--------|-------|
| **Total Orders Processed** | 110,000 |
| **Orders After Cleaning** | 109,981 |
| **Data Quality** | 99.98% |
| **Total Customers** | 58,955 |
| **Total Revenue** | $626,474 |
| **Average Order Value** | $5.50 |

---

## 🔧 Key Features

- ✅ **ETL Pipeline** — Automated extract, transform, load process
- ✅ **Data Cleaning** — Handles 3+ date formats, imputes missing values (10,000+)
- ✅ **Star Schema** — Optimized for analytical queries
- ✅ **Interactive Dashboard** — Streamlit + Plotly visualizations
- ✅ **Docker Containerization** — Portable and reproducible
- ✅ **Unit Tests** — Pytest coverage for critical functions
- ✅ **Logging** — Full audit trail of every pipeline run
- ✅ **Configuration** — YAML-based settings for reusability

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Docker

### Installation

1. **Clone the repository**
   git clone https://github.com/bllecentdidiba/cat_bakery_data_engineering.git
   cd cat_bakery_data_engineering
2. **Install dependencies**
   pip install -r requirements.txt
3. Configure PostgreSQL

      -Create a database named cat_bakery

      -Update config/config.yaml with your credentials

4. Run the ETL Pipeline
5. 
   py scripts/run_pipeline.py
   
7. Launch the Dashboard
   
   py -m streamlit run scripts/05_dashboard.py
   
   Open http://localhost:8501 in your browser

**📊 Dashboard Preview:**
The dashboard provides real-time insights into:

📈 Monthly Revenue and Orders Trends

🏆 Top 10 Products by Revenue

👥 Customer Tier Analysis (Bronze/Silver/Gold)

⭐ Order Rating Distribution

📊 Raw Data Preview



**💡 Business Insights**
Insight                            	Finding
Average Order Value	                $5.50 per order
Top Customer Tier	                  Gold customers generate 40% of revenue
Best-Selling Product	              Almond Croissant (gluten-free)
Seasonal Trend	                    December sales spike 40%
Revenue Growth    	                Consistent year-over-year increase


pytest tests/ -v

**🔮 Future Improvements**

Add CI/CD pipeline (GitHub Actions)

Deploy to cloud (AWS/GCP)

Add more data sources

Implement real-time streaming

Add machine learning predictions

**👤 Author**
**Thanyani Bllecent Didiba**
**BCom Statistics and Data Science** | University of Pretoria

GitHub: @bllecentdidiba

LinkedIn: Thanyani Didiba

Email: bllecentdidiba@gmail.com

**📄 License**
This project is licensed under the MIT License — see the LICENSE file for details.


**🙏 Acknowledgements**
University of Pretoria — BCom Statistics and Data Science

Open-source libraries: Pandas, SQLAlchemy, Streamlit, Plotly
