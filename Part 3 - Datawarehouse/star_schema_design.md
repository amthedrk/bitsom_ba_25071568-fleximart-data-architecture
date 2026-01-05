Star Schema Design Documentation
Section 1: Schema Overview
FACT TABLE: fact_sales

    Grain: One row per individual product line item in a sales order.

    Business Process: Sales transactions and revenue realization.

    Measures (Numeric Facts):

        quantity_sold: The number of units of a specific product sold.

        unit_price: The price per unit at the specific moment of sale (historical accuracy).

        total_amount: The calculated revenue line item (quantity * unit_price).

    Foreign Keys:

        date_key → Links to dim_date

        product_key → Links to dim_product

        customer_key → Links to dim_customer

DIMENSION TABLE: dim_date

    Purpose: Provides a detailed time-based hierarchy for analysis.

    Type: Conformed Dimension.

    Attributes:

        date_key (PK): Surrogate key (Integer, format: YYYYMMDD, e.g., 20240115).

        full_date: The actual Date object (e.g., 2024-01-15).

        day_of_week: String (Monday, Tuesday...).

        month: Integer (1-12).

        month_name: String (January, February...).

        quarter: String (Q1, Q2, Q3, Q4).

        year: Integer (2023, 2024...).

        is_weekend: Boolean (True/False).

DIMENSION TABLE: dim_product

    Purpose: Stores catalog details to allow slicing sales by product attributes.

    Type: Slowly Changing Dimension (Type 1 for corrections, Type 2 if tracking history).

    Attributes:

        product_key (PK): System-generated Surrogate Key (Auto-increment Integer).

        product_id_nk: Natural Key from the source system (e.g., 'ELEC001').

        product_name: Descriptive name of the item.

        category: High-level grouping (e.g., 'Electronics').

        current_price: The current list price in the catalog.

        stock_quantity: Current inventory level.

DIMENSION TABLE: dim_customer

    Purpose: Stores customer demographics to analyze who is buying what.

    Type: Standard Dimension.

    Attributes:

        customer_key (PK): System-generated Surrogate Key (Auto-increment Integer).

        customer_id_nk: Natural Key from the source system (e.g., 'C001').

        full_name: Combined First and Last name.

        email: Customer contact email.

        city: Customer's city for geographic analysis.

        registration_date: Date the customer joined.

Section 2: Design Decisions

1. Granularity (Transaction Line-Item Level) We chose the finest level of granularity (one row per product per order) rather than aggregating data at the "Order" level. This maximizes analytical flexibility. It allows the business to answer complex questions like "Which specific products are frequently bought together?" or "What is the revenue contribution of 'Electronics' versus 'Fashion'?"—questions that would be impossible if we only stored the total order amount.

2. Surrogate Keys vs. Natural Keys We utilize Integer-based Surrogate Keys (e.g., product_key) as Primary Keys in the Data Warehouse instead of the original text-based Natural Keys (e.g., product_id 'ELEC001').

    Performance: Joining on Integers is significantly faster than joining on Strings.

    Independence: If the source system changes its ID format (e.g., from 'ELEC001' to 'E-001'), our Data Warehouse keys remain stable, preventing broken historical links.

3. Drill-Down and Roll-Up Capabilities The design supports hierarchical analysis through its dimensions:

    Time Hierarchy: Users can "Roll Up" from Daily Sales → Monthly → Quarterly → Yearly trends.

    Product Hierarchy: Users can "Drill Down" from a Category level (e.g., 'Electronics') to specific Products (e.g., 'Samsung S21') to identify underperforming items within successful categories.

Section 3: Sample Data Flow

Source Transaction:

    Order: #T101

    Date: 2024-01-15

    Customer: "Rahul Sharma" (ID: C001, City: Bangalore)

    Product: "Samsung Galaxy S21" (ID: ELEC001, Category: Electronics)

    Qty: 1

    Price: 45,999.00

Becomes in Data Warehouse:

1. dim_date:
JSON

{
  "date_key": 20240115,
  "full_date": "2024-01-15",
  "month_name": "January",
  "quarter": "Q1",
  "year": 2024,
  "is_weekend": false
}

2. dim_customer:
JSON

{
  "customer_key": 101,  // Generated Surrogate Key
  "customer_id_nk": "C001",
  "full_name": "Rahul Sharma",
  "city": "Bangalore"
}

3. dim_product:
JSON

{
  "product_key": 55,    // Generated Surrogate Key
  "product_id_nk": "ELEC001",
  "product_name": "Samsung Galaxy S21",
  "category": "Electronics"
}

4. fact_sales (The Link):
JSON

{
  "date_key": 20240115,  // Points to dim_date
  "product_key": 55,     // Points to dim_product
  "customer_key": 101,   // Points to dim_customer
  "quantity_sold": 1,
  "unit_price": 45999.00,
  "total_amount": 45999.00
}