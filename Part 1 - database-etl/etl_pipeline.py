import pandas as pd
from sqlalchemy import create_engine, text
import re
import warnings

# --- CONFIGURATION ---
DB_USER = 'root'
DB_PASSWORD = 'password'  # <--- ENTER YOUR REAL PASSWORD HERE
DB_HOST = 'localhost'
DB_NAME = 'fleximart'

# --- SUPPRESS WARNINGS ---
warnings.filterwarnings("ignore", category=UserWarning)

# --- HELPER FUNCTIONS ---

def clean_id(id_val):
    """Converts IDs like 'C001' or 'P-100' to pure integers (1, 100)."""
    if pd.isna(id_val):
        return None
    # Remove all non-numeric characters (letters, hyphens, etc.)
    clean_str = re.sub(r'\D', '', str(id_val))
    try:
        return int(clean_str)
    except ValueError:
        return None

def clean_phone(phone):
    """Standardizes phone numbers to +91-XXXXXXXXXX format."""
    if pd.isna(phone):
        return None
    digits = re.sub(r'\D', '', str(phone))
    if len(digits) == 10:
        return f"+91-{digits}"
    elif len(digits) > 10:
        return f"+{digits[:2]}-{digits[2:]}"
    return None

def standardize_date(date_str):
    """Safely converts dates to YYYY-MM-DD."""
    try:
        return pd.to_datetime(date_str, dayfirst=True, errors='coerce').strftime('%Y-%m-%d')
    except:
        return None

# --- ETL PROCESS ---

def etl_process():
    print("--- Starting ETL Process ---")
    report_lines = ["--- Data Quality Report ---\n"]
    
    # ---------------------------------------------------------
    # 1. EXTRACT
    # ---------------------------------------------------------
    print("Step 1: Extracting data...")
    try:
        df_cust = pd.read_csv('customers_raw.csv')
        df_prod = pd.read_csv('products_raw.csv')
        df_sales = pd.read_csv('sales_raw.csv')
        report_lines.append(f"Files Read: Customers({len(df_cust)}), Products({len(df_prod)}), Sales({len(df_sales)})")
    except FileNotFoundError as e:
        print(f"❌ CRITICAL ERROR: File not found - {e}")
        return

    # ---------------------------------------------------------
    # 2. TRANSFORM
    # ---------------------------------------------------------
    print("Step 2: Transforming data...")

    # --- Cleaning Customers ---
    initial_cust = len(df_cust)
    
    # FIX: Convert 'C001' -> 1
    df_cust['customer_id'] = df_cust['customer_id'].apply(clean_id)
    # Drop rows where ID became None (invalid)
    df_cust.dropna(subset=['customer_id'], inplace=True)
    
    df_cust.drop_duplicates(subset=['customer_id'], inplace=True) 
    df_cust.dropna(subset=['email'], inplace=True)
    df_cust['phone'] = df_cust['phone'].apply(clean_phone)
    df_cust['registration_date'] = df_cust['registration_date'].apply(standardize_date)
    
    report_lines.append(f"Customers: Removed {initial_cust - len(df_cust)} duplicates/invalid rows.")

    # --- Cleaning Products ---
    # FIX: Convert 'P001' -> 1
    df_prod['product_id'] = df_prod['product_id'].apply(clean_id)
    df_prod.dropna(subset=['product_id'], inplace=True)
    
    df_prod.drop_duplicates(subset=['product_id'], inplace=True)
    df_prod['category'] = df_prod['category'].str.title()
    df_prod['stock_quantity'] = df_prod['stock_quantity'].fillna(0).astype(int)
    df_prod['price'] = pd.to_numeric(df_prod['price'], errors='coerce')
    df_prod.dropna(subset=['price'], inplace=True)
    
    report_lines.append(f"Products: Processed {len(df_prod)} valid products.")

    # --- Cleaning Sales ---
    # FIX: Clean all IDs in sales table too so they match the other tables
    df_sales['transaction_id'] = df_sales['transaction_id'].apply(clean_id)
    df_sales['customer_id'] = df_sales['customer_id'].apply(clean_id)
    df_sales['product_id'] = df_sales['product_id'].apply(clean_id)
    
    # Calculate Amount
    if 'quantity' in df_sales.columns and 'unit_price' in df_sales.columns:
        df_sales['quantity'] = pd.to_numeric(df_sales['quantity'], errors='coerce').fillna(0)
        df_sales['unit_price'] = pd.to_numeric(df_sales['unit_price'], errors='coerce').fillna(0.0)
        df_sales['amount'] = df_sales['quantity'] * df_sales['unit_price']
        print("   -> Calculated missing 'amount' column.")
    else:
        print("❌ CRITICAL ERROR: sales_raw.csv is missing 'quantity' or 'unit_price' columns.")
        return

    df_sales.drop_duplicates(inplace=True)
    df_sales['transaction_date'] = df_sales['transaction_date'].apply(standardize_date)
    df_sales.dropna(subset=['transaction_date'], inplace=True)
    
    # Filter valid Foreign Keys (Ensure customer 1 exists in customer table)
    valid_cust_ids = set(df_cust['customer_id'])
    valid_prod_ids = set(df_prod['product_id'])
    
    df_sales = df_sales[
        df_sales['customer_id'].isin(valid_cust_ids) & 
        df_sales['product_id'].isin(valid_prod_ids)
    ]
    
    # PREPARE ORDERS TABLE
    orders_df = df_sales.groupby('transaction_id').agg({
        'customer_id': 'first',
        'transaction_date': 'first',
        'amount': 'sum'
    }).reset_index()
    
    orders_df.rename(columns={
        'transaction_id': 'order_id', 
        'transaction_date': 'order_date', 
        'amount': 'total_amount'
    }, inplace=True)
    orders_df['status'] = 'Completed'

    # PREPARE ORDER_ITEMS TABLE
    order_items_df = df_sales.copy()
    order_items_df['subtotal'] = order_items_df['amount']
    order_items_df.rename(columns={'transaction_id': 'order_id'}, inplace=True)
    order_items_df = order_items_df[['order_id', 'product_id', 'quantity', 'unit_price', 'subtotal']]

    report_lines.append(f"Sales: Cleaned and split into {len(orders_df)} Orders.")

    # ---------------------------------------------------------
    # 3. LOAD (MySQL)
    # ---------------------------------------------------------
    print("Step 3: Loading into MySQL...")
    
    # Connect to Server
    server_conn = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}"
    try:
        engine_server = create_engine(server_conn)
        with engine_server.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("Check if your MySQL Server is running and the password is correct.")
        return

    # Connect to Database
    db_conn = f"{server_conn}/{DB_NAME}"
    engine = create_engine(db_conn)
    
    with engine.connect() as conn:
        # Reset Tables
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        conn.execute(text("DROP TABLE IF EXISTS order_items, orders, products, customers;"))
        
        # Schema
        conn.execute(text("""
            CREATE TABLE customers (
                customer_id INT PRIMARY KEY,  -- Removed AUTO_INCREMENT so we can use CSV IDs
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                city VARCHAR(50),
                registration_date DATE
            );
        """))
        conn.execute(text("""
            CREATE TABLE products (
                product_id INT PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                stock_quantity INT DEFAULT 0
            );
        """))
        conn.execute(text("""
            CREATE TABLE orders (
                order_id INT PRIMARY KEY,
                customer_id INT NOT NULL,
                order_date DATE NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'Pending',
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            );
        """))
        conn.execute(text("""
            CREATE TABLE order_items (
                order_item_id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
        """))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

        # Insert Data
        print("   -> Inserting customers...")
        df_cust.to_sql('customers', con=conn, if_exists='append', index=False)
        
        print("   -> Inserting products...")
        df_prod.to_sql('products', con=conn, if_exists='append', index=False)
        
        print("   -> Inserting orders...")
        orders_df.to_sql('orders', con=conn, if_exists='append', index=False)
        
        print("   -> Inserting order items...")
        order_items_df.to_sql('order_items', con=conn, if_exists='append', index=False)
        
        report_lines.append("Database Load: Success.")

    # Save Report
    with open('data_quality_report.txt', 'w') as f:
        f.writelines([line + '\n' for line in report_lines])
    
    print("✅ ETL Pipeline Completed Successfully!")

if __name__ == "__main__":
    etl_process()