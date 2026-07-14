import pandas as pd
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from sqlalchemy import create_engine
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_config, setup_logging
import schedule
import time

# Load config
config = load_config()
logger = setup_logging(config)

# Quick test to make sure config loaded
# print(config.keys())

def get_db_connection():
    """Create database connection - reused from other scripts"""
    db_config = config['database']
    
    connection_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    return create_engine(connection_string)

def generate_report_data():
    """Generate the report data from PostgreSQL"""
    logger.info("Generating report data...")
    
    engine = get_db_connection()
    
    with engine.connect() as conn:
        # Query 1: Monthly Revenue Trend (Last 6 months)
        # Had to use TO_CHAR because the date formatting was giving me issues
        monthly_revenue = pd.read_sql("""
            SELECT 
                TO_CHAR(DATE_TRUNC('month', order_date), 'YYYY-MM') as month,
                COUNT(DISTINCT order_id) as total_orders,
                ROUND(SUM(total_amount)::numeric, 2) as total_revenue,
                SUM(quantity) as total_items_sold,
                ROUND(AVG(total_amount)::numeric, 2) as avg_order_value
            FROM fact_orders
            GROUP BY DATE_TRUNC('month', order_date)
            ORDER BY DATE_TRUNC('month', order_date) DESC
            LIMIT 6
        """, conn)
        
        # Query 2: Customer Tier Analysis
        
        tier_analysis = pd.read_sql("""
            SELECT 
                c.customer_tier,
                COUNT(DISTINCT c.customer_id) as customer_count,
                COUNT(DISTINCT f.order_id) as total_orders,
                ROUND(SUM(f.total_amount)::numeric, 2) as total_revenue,
                ROUND(AVG(f.total_amount)::numeric, 2) as avg_order_value,
                ROUND(SUM(f.total_amount)::numeric / NULLIF(COUNT(DISTINCT c.customer_id), 0), 2) as revenue_per_customer
            FROM dim_customer c
            JOIN fact_orders f ON c.customer_id = f.customer_id
            GROUP BY c.customer_tier
            ORDER BY total_revenue DESC
        """, conn)
        
        # Summary metrics - quick numbers for the top of the report
        summary = pd.read_sql("""
            SELECT 
                COUNT(DISTINCT customer_id) as total_customers,
                COUNT(DISTINCT order_id) as total_orders,
                ROUND(SUM(total_amount)::numeric, 2) as total_revenue,
                ROUND(AVG(order_rating)::numeric, 2) as avg_rating,
                COUNT(DISTINCT product_id) as unique_products
            FROM fact_orders
        """, conn)
        
    return monthly_revenue, tier_analysis, summary

def create_html_report(monthly_revenue, tier_analysis, summary):
    """Create HTML email content - I should probably use a template instead of this mess"""
    
    today = datetime.now().strftime("%B %d, %Y")
    
    # Get summary values
    total_revenue = summary['total_revenue'].iloc[0]
    total_orders = summary['total_orders'].iloc[0]
    total_customers = summary['total_customers'].iloc[0]
    avg_rating = summary['avg_rating'].iloc[0]
    unique_products = summary['unique_products'].iloc[0]
    
    # Convert to HTML 
    monthly_html = monthly_revenue.to_html(index=False, classes='table table-striped')
    tier_html = tier_analysis.to_html(index=False, classes='table table-striped')
    
    # I copied this CSS from Stack Overflow 🙈
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            .summary {{ 
                background: #f8f9fa; 
                padding: 15px; 
                border-radius: 5px; 
                margin: 20px 0;
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }}
            .summary-item {{
                flex: 1;
                min-width: 150px;
                padding: 10px;
                background: white;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .summary-item .label {{ color: #7f8c8d; font-size: 12px; text-transform: uppercase; }}
            .summary-item .value {{ color: #2c3e50; font-size: 24px; font-weight: bold; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th {{ background-color: #3498db; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
            .footer {{ margin-top: 30px; color: #7f8c8d; font-size: 12px; text-align: center; border-top: 1px solid #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>🐱 Bakery Daily Sales Report</h1>
        <p><strong>Report Date:</strong> {today}</p>
        
        <div class="summary">
            <div class="summary-item">
                <div class="label">Total Revenue</div>
                <div class="value">${total_revenue:,.2f}</div>
            </div>
            <div class="summary-item">
                <div class="label">Total Orders</div>
                <div class="value">{total_orders:,}</div>
            </div>
            <div class="summary-item">
                <div class="label">Total Customers</div>
                <div class="value">{total_customers:,}</div>
            </div>
            <div class="summary-item">
                <div class="label">Avg Rating</div>
                <div class="value">{avg_rating:.2f}</div>
            </div>
            <div class="summary-item">
                <div class="label">Unique Products</div>
                <div class="value">{unique_products:,}</div>
            </div>
        </div>
        
        <h2>📊 Monthly Revenue Trend (Last 6 Months)</h2>
        {monthly_html}
        
        <h2>👥 Customer Tier Analysis</h2>
        {tier_html}
        
        <div class="footer">
            Generated automatically by Cat Bakery ETL Pipeline • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </body>
    </html>
    """
    
    return html

def send_email_report():
    """Send the report via email"""
    logger.info("Preparing to send email report...")
    
    try:
        # Generate report data
        monthly_revenue, tier_analysis, summary = generate_report_data()
        
        # Create HTML content
        html_content = create_html_report(monthly_revenue, tier_analysis, summary)
        
        # Check if email config exists
        if 'email' not in config:
            logger.error("Email configuration not found in config.yaml")
            print("Please add email configuration to config/config.yaml")
            return False
        
        # Get email config
        email_config = config['email']
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = email_config['sender_email']
        msg['To'] = email_config['recipient_email']
        msg['Subject'] = f"{email_config['subject']} - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Attach HTML
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        logger.info(f"Sending email to {email_config['recipient_email']}...")

        with smtplib.SMTP(email_config['smtp_host'], email_config['smtp_port']) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            # This sometimes fails - need to handle better
            server.login(
                email_config['sender_email'],
                email_config['sender_password']
            )
            server.send_message(msg)

        logger.info("Email sent successfully.")

        # Save report locally because this is good for backup
        reports_dir = config['paths'].get('reports', 'reports/daily_reports')
        os.makedirs(reports_dir, exist_ok=True)

        report_file = os.path.join(
            reports_dir,
            f"report_{datetime.now().strftime('%Y%m%d')}.html"
        )

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Report saved to {report_file}")

        print(f"✅ Report sent to {email_config['recipient_email']}")
        return True

    except Exception as e:
        logger.exception("Failed to send email.")
        print(f"❌ Error: {e}")
        # TODO: Add retry logic
        return False

# This is where the script starts
if __name__ == "__main__":
    print("🐱 Bakery Sales Email Report Scheduler")
    print("=" * 40)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--send-now":
        print("Sending report now...")
        send_email_report()
    else:
        print("Starting scheduler...")
        print("Reports will be sent daily at 9:00 AM")
        print("Press Ctrl+C to stop")
        print("")
        
        # Schedule the report to run daily at 9:00 AM
        schedule.every().day.at("09:00").do(send_email_report)
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n👋 Scheduler stopped by user")
