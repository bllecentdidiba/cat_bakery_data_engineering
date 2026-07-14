"""
Bakery Dashboard - Quick and dirty analytics
Created for the 2026 sales review
TODO: Add more filters and make it dynamic
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from utils import load_config
from datetime import datetime

# Page setup - copied this from the docs
st.set_page_config(
    page_title="Bakery Sales Analytics",
    page_icon="🐱",  # The team loves cats
    layout="wide"
)

# Load config
config = load_config()

# Database connection - reused from other scripts
@st.cache_resource
def get_connection():
    db_config = config['database']

    # I always forget the connection string format 🤣
    connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    return create_engine(connection_string)

engine = get_connection()

# This loads the data 
# Cached for 5 minutes to avoid hitting the DB too hard
@st.cache_data(ttl=300)
def load_data():
    # HACK: Hardcoded for 2026, need to make this dynamic
    # The boss wants 2026 only for now
    start_date = '2026-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    with engine.connect() as conn:
        # Had to add COALESCE because of NULL values
        # The data quality isn't great
        metrics = pd.read_sql(f"""
            SELECT 
                COUNT(DISTINCT customer_id) as total_customers,
                COUNT(DISTINCT order_id) as total_orders,
                COALESCE(SUM(total_amount), 0) as total_revenue,
                COALESCE(AVG(total_amount), 0) as avg_order_value,
                COALESCE(AVG(order_rating), 0) as avg_rating
            FROM fact_orders
            WHERE order_date >= '{start_date}' 
            AND order_date <= '{end_date}'
        """, conn)
        
        # Monthly trend 
        monthly_trend = pd.read_sql(f"""
            SELECT 
                DATE_TRUNC('month', order_date) as month,
                COUNT(DISTINCT order_id) as orders,
                COALESCE(SUM(total_amount), 0) as revenue
            FROM fact_orders
            WHERE order_date >= '{start_date}' 
            AND order_date <= '{end_date}'
            GROUP BY DATE_TRUNC('month', order_date)
            ORDER BY month
        """, conn)
        
        # Top products - used for the marketing team
        top_products = pd.read_sql(f"""
            SELECT 
                p.product_name,
                COALESCE(SUM(f.total_amount), 0) as revenue,
                COALESCE(SUM(f.quantity), 0) as quantity
            FROM fact_orders f
            JOIN dim_product p ON f.product_id = p.product_id
            WHERE f.order_date >= '{start_date}' 
            AND f.order_date <= '{end_date}'
            GROUP BY p.product_name
            ORDER BY revenue DESC
            LIMIT 10
        """, conn)
        
        # Customer tiers - copied from the analytics SQL
        tier_analysis = pd.read_sql(f"""
            SELECT 
                c.customer_tier,
                COUNT(DISTINCT c.customer_id) as customers,
                COALESCE(SUM(f.total_amount), 0) as revenue,
                COALESCE(AVG(f.total_amount), 0) as avg_order
            FROM dim_customer c
            JOIN fact_orders f ON c.customer_id = f.customer_id
            WHERE f.order_date >= '{start_date}' 
            AND f.order_date <= '{end_date}'
            GROUP BY c.customer_tier
        """, conn)
        
    return metrics, monthly_trend, top_products, tier_analysis

# --- Dashboard starts here ---

st.title("🐱 Bakery Data Analytics Dashboard")
st.markdown("---")

# Quick info for the user
current_year = datetime.now().year
st.info(f"📊 Showing data for **{current_year}** only (Jan 1 - {datetime.now().strftime('%b %d, %Y')})")

try:
    # Load the data
    metrics, monthly_trend, top_products, tier_analysis = load_data()
    
    # Check if we have data
    if metrics['total_orders'].iloc[0] == 0:
        st.warning("⚠️ No orders found for 2026 yet")
        st.info("The data will appear here once orders are placed.")
    else:
        # Display metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Customers", f"{metrics['total_customers'].iloc[0]:,}")
        with col2:
            st.metric("Total Orders", f"{metrics['total_orders'].iloc[0]:,}")
        with col3:
            st.metric("Total Revenue", f"${metrics['total_revenue'].iloc[0]:,.2f}")
        with col4:
            st.metric("Avg Order Value", f"${metrics['avg_order_value'].iloc[0]:.2f}")
        with col5:
            st.metric("Avg Rating", f"{metrics['avg_rating'].iloc[0]:.2f} ⭐")
        
        st.markdown("---")
        
        # First row of charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Monthly Revenue & Orders")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly_trend['month'],
                y=monthly_trend['revenue'],
                name='Revenue',
                yaxis='y1',
                line=dict(color='blue')
            ))
            fig.add_trace(go.Bar(
                x=monthly_trend['month'],
                y=monthly_trend['orders'],
                name='Orders',
                yaxis='y2',
                marker_color='orange',
                opacity=0.7
            ))
            fig.update_layout(
                yaxis=dict(title='Revenue (R)'),
                yaxis2=dict(title='Orders', overlaying='y', side='right'),
                hovermode='x unified',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Top 10 Products by Revenue")
            fig = px.bar(
                top_products,
                x='revenue',
                y='product_name',
                orientation='h',
                color='revenue',
                color_continuous_scale='Viridis',
                text=top_products['revenue'].apply(lambda x: f'${x:,.0f}')
            )
            fig.update_layout(height=400, yaxis_title='', xaxis_title='Revenue (R)')
            st.plotly_chart(fig, use_container_width=True)
        
        # Second row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Customer Tier Analysis")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=tier_analysis['customer_tier'],
                y=tier_analysis['customers'],
                name='Customers',
                marker_color='lightblue',
                text=tier_analysis['customers'],
                textposition='outside'
            ))
            fig.add_trace(go.Scatter(
                x=tier_analysis['customer_tier'],
                y=tier_analysis['revenue'],
                name='Revenue',
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='red', width=3),
                marker=dict(size=10)
            ))
            fig.update_layout(
                yaxis=dict(title='Customers'),
                yaxis2=dict(title='Revenue ($)', overlaying='y', side='right'),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Footer
        st.markdown("---")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

except Exception as e:
    # Something went wrong
    st.error(f"Error loading data: {str(e)}")
    st.info("Make sure you've run the ETL pipeline first")

# TODO: Add better error handling
