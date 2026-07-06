import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from utils import load_config

# Page config
st.set_page_config(
    page_title="Cat Bakery Analytics",
    page_icon="🐱",
    layout="wide"
)

# Load config
config = load_config()

# Database connection
@st.cache_resource
def get_connection():
    db_config = config['database']
    connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    return create_engine(connection_string)

engine = get_connection()

# Loaded data functions
@st.cache_data(ttl=300)
def load_data():
    with engine.connect() as conn:
        customers = pd.read_sql("SELECT * FROM dim_customer", conn)
        products = pd.read_sql("SELECT * FROM dim_product", conn)
        orders = pd.read_sql("SELECT * FROM fact_orders", conn)
        
        metrics = pd.read_sql("""
            SELECT 
                COUNT(DISTINCT customer_id) as total_customers,
                COUNT(DISTINCT order_id) as total_orders,
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value,
                AVG(order_rating) as avg_rating
            FROM fact_orders
        """, conn)
        
        monthly_trend = pd.read_sql("""
            SELECT 
                DATE_TRUNC('month', order_date) as month,
                COUNT(DISTINCT order_id) as orders,
                SUM(total_amount) as revenue
            FROM fact_orders
            GROUP BY DATE_TRUNC('month', order_date)
            ORDER BY month
        """, conn)
        
        top_products = pd.read_sql("""
            SELECT 
                p.product_name,
                SUM(f.total_amount) as revenue,
                SUM(f.quantity) as quantity
            FROM fact_orders f
            JOIN dim_product p ON f.product_id = p.product_id
            GROUP BY p.product_name
            ORDER BY revenue DESC
            LIMIT 10
        """, conn)
        
        tier_analysis = pd.read_sql("""
            SELECT 
                c.customer_tier,
                COUNT(DISTINCT c.customer_id) as customers,
                SUM(f.total_amount) as revenue,
                AVG(f.total_amount) as avg_order
            FROM dim_customer c
            JOIN fact_orders f ON c.customer_id = f.customer_id
            GROUP BY c.customer_tier
        """, conn)
        
    return customers, products, orders, metrics, monthly_trend, top_products, tier_analysis

# Main dashboard
st.title("Cat Bakery Data Analytics Dashboard")
st.markdown("---")

try:
    customers, products, orders, metrics, monthly_trend, top_products, tier_analysis = load_data()
    
    # Metrics
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
    
    # Charts 
    #Row 1
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
    yaxis=dict(title='Revenue ($)'),
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
        fig.update_layout(height=400, yaxis_title='', xaxis_title='Revenue ($)')
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2
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
    
    # Raw data section
    st.markdown("---")
    st.subheader("Raw Data Preview")
    
    tab1, tab2, tab3 = st.tabs(["Orders", "Customers", "Products"])
    
    with tab1:
        st.dataframe(orders.head(100), use_container_width=True)
    
    with tab2:
        st.dataframe(customers.head(100), use_container_width=True)
    
    with tab3:
        st.dataframe(products.head(100), use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Make sure you've run the ETL pipeline first!")



    
