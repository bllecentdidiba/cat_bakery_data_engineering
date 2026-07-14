# 🐱 Bakery Sales Data Engineering Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **End-to-end ETL pipeline processing 110 000+ bakery transactions from messy CSV files to an interactive dashboard.**

---

## 📊 Overview

This project is a complete data engineering platform built for a bakery business. It extracts raw data from multiple CSV files, cleans and transforms inconsistent data, loads it into a PostgreSQL star schema and visualizes business insights through an interactive dashboard.

**The Problem:** The bakery had messy data spread across multiple CSV files with inconsistent date formats, thousands of missing values and no proper way to analyze performance.

**The Solution:** An automated ETL pipeline that handles data cleaning, validation and loading — delivering clean, analysis-ready data in minutes instead of hours.

---

## Architecture

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

## Tech Stack

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
| **Total Orders Processed** | 110 000 |
| **Orders After Cleaning** | 109 981 |
| **Data Quality** | 99.98% |
| **Total Customers** | 8 967 |
| **Total Revenue** | R3 278 320.49 |
| **Average Order Value** | R332.93 |

---

## Key Features

- ✅ **ETL Pipeline** — Automated extract, transform, load process
- ✅ **Data Cleaning** — Handles 3+ date formats, imputes missing values (10 000+)
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

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/bllecentdidiba/cat_bakery_data_engineering.git
   cd cat_bakery_data_engineering
   
2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv\Scripts\activate

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

4. **Configure the database**

   -Edit config/config.yaml with your PostgreSQL credentials

   -Default: postgres / postgres123 on localhost:5432

5. **Run the ETL pipeline**
   ```bash
   py scripts/run_pipeline.py
6. **Launch dashboard**
   ```bash
   py -m streamlit run scripts/05_dashboard.py
   
7. **Docker Setup**
   ```bash
   docker-compose up -d
8. Start the scheduler 
   ```bash
   py scripts/email_report.py
   send the email immediately: py scripts/email_report.py --send-now
9. Email config
    under config/yaml.py
   
  email:
  smtp_host: "smtp.gmail.com"
  smtp_port: 587
  sender_email: "your_email@gmail.com"
  sender_password: "your_app_password"
  recipient_email: "recipient@email.com"
  subject: "Bakery Daily Sales Report"

10. **Testing**
    ```# Run all tests
    pytest tests/ -v
    pytest tests/test_transforms.py -v
    pytest --cov=scripts tests/


## Main Dashboard 📊 ##
<img width="1258" height="555" alt="image" src="https://github.com/user-attachments/assets/8b4ba627-c806-457d-ba85-bf30a5b81bc6" />

## Tier Analysis Dashboard ##

<img width="935" height="425" alt="image" src="https://github.com/user-attachments/assets/223e646d-5195-4257-8054-830314e93509" />

## 📧 Automated Email Reports

**The pipeline includes an automated email reporting system:**

Daily Reports: Sends HTML-formatted reports at 9:00 AM

Summary Metrics: Revenue, orders, customers, ratings

Trend Analysis: Monthly revenue trends (last 6 months)

Customer Insights: Tier analysis with revenue breakdown

👨‍🎓 About the Author
BCom Statistics and Data Science student at the University of Pretoria.
