-- 1. Monthly Revenue Trend
SELECT 
    DATE_TRUNC('month', order_date) as month,
    COUNT(DISTINCT order_id) as total_orders,
    SUM(total_amount) as total_revenue,
    SUM(quantity) as total_items_sold,
    ROUND(AVG(total_amount), 2) as avg_order_value
FROM fact_orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month DESC;

-- 2. Customer Tier Analysis
SELECT 
    c.customer_tier,
    COUNT(DISTINCT c.customer_id) as customer_count,
    COUNT(DISTINCT f.order_id) as total_orders,
    ROUND(SUM(f.total_amount), 2) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_order_value,
    ROUND(SUM(f.total_amount) / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2) as revenue_per_customer
FROM dim_customer c
JOIN fact_orders f ON c.customer_id = f.customer_id
GROUP BY c.customer_tier
ORDER BY total_revenue DESC;

-- 3. Top 10 Products by Revenue
SELECT 
    p.product_name,
    COUNT(DISTINCT f.order_id) as order_count,
    SUM(f.quantity) as total_quantity_sold,
    ROUND(SUM(f.total_amount), 2) as total_revenue,
    p.profit_margin,
    ROUND(AVG(f.order_rating), 2) as avg_rating
FROM dim_product p
JOIN fact_orders f ON p.product_id = f.product_id
GROUP BY p.product_id, p.product_name, p.profit_margin
ORDER BY total_revenue DESC
LIMIT 10;

-- 4. Customer Lifetime Value (CLV)
WITH customer_orders AS (
    SELECT 
        c.customer_id,
        c.city,
        c.customer_tier,
        c.signup_date,
        COUNT(DISTINCT f.order_id) as order_count,
        SUM(f.total_amount) as total_spent,
        AVG(f.total_amount) as avg_order_value,
        MIN(f.order_date) as first_order,
        MAX(f.order_date) as last_order,
        EXTRACT(DAY FROM (MAX(f.order_date) - MIN(f.order_date))) as days_active
    FROM dim_customer c
    JOIN fact_orders f ON c.customer_id = f.customer_id
    GROUP BY c.customer_id, c.city, c.customer_tier, c.signup_date
)
SELECT 
    customer_tier,
    COUNT(*) as customer_count,
    ROUND(AVG(total_spent), 2) as avg_clv,
    ROUND(AVG(order_count), 2) as avg_orders,
    ROUND(AVG(days_active), 0) as avg_days_active,
    ROUND(AVG(avg_order_value), 2) as avg_order_value
FROM customer_orders
GROUP BY customer_tier
ORDER BY avg_clv DESC;

-- 5. Seasonal Patterns
SELECT 
    EXTRACT(MONTH FROM order_date) as month,
    COUNT(DISTINCT order_id) as orders,
    ROUND(SUM(total_amount), 2) as revenue,
    ROUND(AVG(order_rating), 2) as avg_rating
FROM fact_orders
GROUP BY EXTRACT(MONTH FROM order_date)
ORDER BY month;

-- 6. City Performance
SELECT 
    c.city,
    COUNT(DISTINCT c.customer_id) as customer_count,
    COUNT(DISTINCT f.order_id) as order_count,
    ROUND(SUM(f.total_amount), 2) as total_revenue,
    ROUND(AVG(f.total_amount), 2) as avg_order_value,
    ROUND(AVG(f.order_rating), 2) as avg_rating
FROM dim_customer c
JOIN fact_orders f ON c.customer_id = f.customer_id
GROUP BY c.city
HAVING COUNT(DISTINCT f.order_id) > 10
ORDER BY total_revenue DESC;

-- 7. Gluten-Free Analysis
SELECT 
    CASE WHEN p.is_gluten_free = 1 THEN 'Gluten Free' ELSE 'Regular' END as product_type,
    COUNT(DISTINCT f.order_id) as order_count,
    SUM(f.quantity) as total_quantity,
    ROUND(SUM(f.total_amount), 2) as total_revenue,
    ROUND(AVG(f.order_rating), 2) as avg_rating,
    ROUND(AVG(p.profit_margin), 2) as avg_profit_margin
FROM dim_product p
JOIN fact_orders f ON p.product_id = f.product_id
GROUP BY p.is_gluten_free;

-- 8. Customer Retention Analysis
WITH customer_activity AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', order_date) as order_month,
        COUNT(*) as monthly_orders
    FROM fact_orders
    GROUP BY customer_id, DATE_TRUNC('month', order_date)
),
retention AS (
    SELECT 
        order_month,
        COUNT(DISTINCT customer_id) as active_customers,
        LAG(COUNT(DISTINCT customer_id), 1) OVER (ORDER BY order_month) as prev_month_customers
    FROM customer_activity
    GROUP BY order_month
)
SELECT 
    order_month,
    active_customers,
    prev_month_customers,
    ROUND(100.0 * active_customers / NULLIF(prev_month_customers, 0), 2) as retention_rate
FROM retention
ORDER BY order_month DESC;

-- 9. High-Value Customers (Top 20%)
WITH customer_ranking AS (
    SELECT 
        c.customer_id,
        c.customer_tier,
        SUM(f.total_amount) as total_spent,
        NTILE(5) OVER (ORDER BY SUM(f.total_amount) DESC) as percentile_rank
    FROM dim_customer c
    JOIN fact_orders f ON c.customer_id = f.customer_id
    GROUP BY c.customer_id, c.customer_tier
)
SELECT 
    customer_tier,
    COUNT(*) as customer_count,
    ROUND(AVG(total_spent), 2) as avg_spent,
    MIN(total_spent) as min_spent,
    MAX(total_spent) as max_spent
FROM customer_ranking
WHERE percentile_rank = 1
GROUP BY customer_tier
ORDER BY avg_spent DESC;

-- 10. Product Affinity (Frequently Bought Together)
WITH order_products AS (
    SELECT 
        order_id,
        product_id
    FROM fact_orders
),
product_pairs AS (
    SELECT 
        a.product_id as product_a,
        b.product_id as product_b,
        COUNT(*) as frequency
    FROM order_products a
    JOIN order_products b ON a.order_id = b.order_id AND a.product_id < b.product_id
    GROUP BY a.product_id, b.product_id
)
SELECT 
    pa.product_name as product_a_name,
    pb.product_name as product_b_name,
    pp.frequency
FROM product_pairs pp
JOIN dim_product pa ON pp.product_a = pa.product_id
JOIN dim_product pb ON pp.product_b = pb.product_id
ORDER BY pp.frequency DESC
LIMIT 20;