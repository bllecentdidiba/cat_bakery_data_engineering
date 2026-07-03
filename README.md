# 🐱 Cat Bakery Data Engineering Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **End-to-end ETL pipeline processing 110,000+ bakery transactions — from messy CSV files to an interactive dashboard.**

---

## 📊 Overview

This project is a complete data engineering platform built for a cat bakery business. It extracts raw data from multiple CSV files, cleans and transforms inconsistent data, loads it into a PostgreSQL star schema and visualizes business insights through an interactive dashboard.

**The Problem:** The bakery had messy data spread across multiple CSV files with inconsistent date formats, thousands of missing values and no proper way to analyze performance.

**The Solution:** An automated ETL pipeline that handles data cleaning, validation and loading — delivering clean, analysis-ready data in minutes instead of hours.

---

## 🏗️ Architecture

| Stage | Tools | Output |
|-------|-------|--------|
| **Extract** | Python (Pandas) | Raw data from CSV files |
| **Transform** | Python (Pandas, NumPy) | Cleaned, validated data |
| **Load** | Python (SQLAlchemy) | PostgreSQL star schema |
| **Visualize** | Streamlit + Plotly | Interactive dashboard |

---

## 🗄️ Star Schema Design

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
- Windows

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/bllecentdidiba/cat_bakery_data_engineering.git
   cd cat_bakery_data_engineering
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the ETL pipeline**
   ```bash
   py run_pipeline.py 
   ```

5. **Launch the dashboard**
   ```bash
   py -m streamlit run scripts/05_dashboard.py
   ```
### Visualizations

## 📊Visual 1: Executive Dashboard

<img width="1291" height="503" alt="Executive_Dashboard" src="https://github.com/user-attachments/assets/d0f3ca82-abd4-4ee4-b556-bce1bc8b5218" />

## 📊Visual 2: Customer tier analysis

<img width="636" height="310" alt="Customer_tier_ananalysis" src="https://github.com/user-attachments/assets/dad95429-72e2-4721-aa96-f9e970253e60" />






