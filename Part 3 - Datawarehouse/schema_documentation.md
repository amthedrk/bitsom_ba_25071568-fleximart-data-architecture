Database Schema Documentation
1. Entity-Relationship Description
ENTITY: customers

    Purpose: Stores distinct profiles for all registered users of the FlexiMart platform.

    Attributes:

        customer_id (INT, PK): Unique surrogate identifier for the customer.

        first_name (VARCHAR): Customer's given name.

        last_name (VARCHAR): Customer's family name.

        email (VARCHAR, Unique): Customer's email address (used for contact/login).

        phone (VARCHAR): Standardized contact number (+91 format).

        city (VARCHAR): Customer's city of residence.

        registration_date (DATE): The date the customer profile was created.

    Relationships:

        1:M with orders: A single customer can place multiple orders over time.

ENTITY: products

    Purpose: Maintains the catalog of items available for sale.

    Attributes:

        product_id (INT, PK): Unique surrogate identifier for the product.

        product_name (VARCHAR): The descriptive name of the item.

        category (VARCHAR): The classification group (e.g., Electronics, Fashion).

        price (DECIMAL): The current listing price per unit.

        stock_quantity (INT): Current inventory count available.

    Relationships:

        1:M with order_items: A single product (e.g., "Laptop") can appear in many different order line items.

ENTITY: orders

    Purpose: Records the high-level details of a transaction event.

    Attributes:

        order_id (INT, PK): Unique surrogate identifier for the transaction.

        customer_id (INT, FK): Reference to the customer who placed the order.

        order_date (DATE): The date the transaction occurred.

        total_amount (DECIMAL): The final calculated value of the entire order.

        status (VARCHAR): The current fulfillment state (e.g., 'Pending', 'Completed').

    Relationships:

        M:1 with customers: Each order belongs to exactly one customer.

        1:M with order_items: A single order is composed of one or more specific line items.

ENTITY: order_items

    Purpose: Acts as a bridge table to resolve the Many-to-Many relationship between Orders and Products, storing specific line-item details.

    Attributes:

        order_item_id (INT, PK): Unique surrogate identifier for the line item.

        order_id (INT, FK): Link to the parent order.

        product_id (INT, FK): Link to the specific product purchased.

        quantity (INT): The number of units of this product purchased in this specific order.

        unit_price (DECIMAL): A snapshot of the product's price at the moment of purchase (preserving historical accuracy even if catalog prices change).

        subtotal (DECIMAL): Calculated value (quantity * unit_price).

    Relationships:

        M:1 with orders: Relates to one specific parent order.

        M:1 with products: Relates to one specific product from the catalog.

2. Normalization Explanation

The FlexiMart database schema is designed to adhere to the Third Normal Form (3NF). This structure ensures data integrity, minimizes redundancy, and facilitates efficient data management.

Why this is in 3NF:

    First Normal Form (1NF): All tables contain atomic values. We do not store multiple products in a single cell (e.g., "Laptop, Mouse" in one row). Instead, we break these out into the order_items table, ensuring every column contains a single value and every record is unique.

    Second Normal Form (2NF): We utilize single-column Primary Keys (surrogate keys like order_id, customer_id) for all tables. This eliminates partial dependencies. For example, in order_items, the subtotal depends on the specific line item defined by the primary key, not just part of a composite key.

    Third Normal Form (3NF): We have removed transitive dependencies. Non-key attributes depend only on the primary key. For instance, we do not store the customer_city inside the orders table. If we did, city would depend on customer_id, which is not the primary key of the orders table. By isolating customer details in the customers table, we ensure strictly direct dependencies.

Functional Dependencies:

    customer_id → {first_name, last_name, email, city...}

    product_id → {product_name, category, price...}

    order_id → {customer_id, order_date, total_amount...}

Avoiding Anomalies:

    Update Anomaly: If a customer changes their email, we update it in one single row in the customers table. We do not need to hunt down every order they ever placed to update the email there, preventing data inconsistencies.

    Insert Anomaly: We can add a new product to our catalog immediately without requiring it to be ordered. If products were nested inside orders, we couldn't create a product until someone bought it.

    Delete Anomaly: If we delete an order record (e.g., a cancelled transaction), we do not lose the customer's personal data or the product's catalog details, as those entities exist independently in their own tables.

    3. Sample Data Representation
Table: customers
customer_id	first_name	last_name	email	phone	city	registration_date
1	Rahul	Sharma	rahul.s@gmail.com	+91-9876543210	Bangalore	2023-01-15
2	Priya	Patel	p.patel@yahoo.com	+91-9988776655	Mumbai	2023-02-20
3	Sneha	Reddy	sneha.r@gmail.com	+91-9123456789	Hyderabad	2023-04-15
Table: products
product_id	product_name	category	price	stock_quantity
1	Samsung Galaxy S21	Electronics	45999.00	150
2	Nike Running Shoes	Fashion	3499.00	80
3	Sony Headphones	Electronics	1999.00	200
Table: orders
order_id	customer_id	order_date	total_amount	status
101	1	2024-01-15	45999.00	Completed
102	2	2024-01-16	5998.00	Completed
103	1	2024-02-10	1999.00	Pending
Table: order_items
order_item_id	order_id	product_id	quantity	unit_price	subtotal
501	101	1	1	45999.00	45999.00
502	102	2	2	2999.00	5998.00
503	103	3	1	1999.00	1999.00