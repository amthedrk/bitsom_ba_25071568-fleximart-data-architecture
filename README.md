# bitsom_ba_25071568-fleximart-data-architecture

# FlexiMart Data Architecture Project

**Student Name**: Ameya Kale

**Student ID**: bitsom_ba_25071568

**Email**: drameyakale.sm@gmail.com

**Date**: 04-01-2026


## Project Overview

This project implements a complete end-to-end data architecture for "FlexiMart," a fictional e-commerce platform. The system features a Hybrid Database Architecture comprising:

    Relational ETL Pipeline: Cleaning raw CSV data using Python/Pandas and loading it into a normalized MySQL database (3NF).

    NoSQL Catalog: Using MongoDB to manage diverse product schemas and embedded customer reviews.

    Data Warehouse: Implementing a Star Schema (OLAP) to facilitate high-performance historical sales analysis and drill-down reporting.

## Repository Structure

├── part1-database-etl/  
│   ├── etl_pipeline.py  
│   ├── schema_documentation.md  
│   ├── business_queries.sql  
│   └── data_quality_report.txt  
├── part2-nosql/  
│   ├── nosql_analysis.md  
│   ├── mongodb_operations.js  
│   └── products_catalog.json  
├── part3-datawarehouse/  
│   ├── star_schema_design.md  
│   ├── warehouse_schema.sql  
│   ├── warehouse_data.sql  
│   └── analytics_queries.sql  
└── README.md  

## Technologies Used

    Languages: Python 3.x, SQL, JavaScript (MongoDB Shell)

    Libraries: pandas, sqlalchemy, mysql-connector-python

    Databases: MySQL 8.0 (OLTP & OLAP), MongoDB 6.0 (NoSQL)

    Tools: VS Code, DBeaver / MySQL Workbench

## Setup Instructions
### Database Setup
Bash

# 1. Create databases in MySQL
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS fleximart;"
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS fleximart_dw;"

# 2. Run Part 1 - ETL Pipeline (Loads data into 'fleximart')
python part1-database-etl/etl_pipeline.py

# 3. Run Part 1 - Business Queries (Analysis on 3NF Schema)
mysql -u root -p fleximart < part1-database-etl/business_queries.sql

# 4. Run Part 3 - Data Warehouse (Setup Star Schema)
mysql -u root -p fleximart_dw < part3-datawarehouse/warehouse_schema.sql
mysql -u root -p fleximart_dw < part3-datawarehouse/warehouse_data.sql
mysql -u root -p fleximart_dw < part3-datawarehouse/analytics_queries.sql

### MongoDB Setup
Bash

# Run Part 2 - NoSQL Operations
mongosh fleximart_nosql < part2-nosql/mongodb_operations.js

## Key Learnings

    ETL Complexity: Learned how to robustly handle dirty data, specifically calculating missing derived fields (like total_amount) and standardizing inconsistent date formats during the transformation phase.

    Schema Design: Understood the trade-offs between a normalized 3NF schema (great for data integrity in transactions) versus a Star Schema (optimized for read-heavy analytical queries).

    Polyglot Persistence: Gained practical experience in choosing the right tool for the job using MySQL for structured orders and MongoDB for semi-structured product catalogs with embedded reviews.

## Challenges Faced

    Missing Data in Source Files: The raw sales_raw.csv file was missing the total_amount column.

        Solution: Implemented a calculation logic in etl_pipeline.py to derive amount = quantity * unit_price automatically before loading.

    Schema Evolution in NoSQL: The provided MongoDB dataset changed the review structure from user to user_id/username.

        Solution: Updated the mongodb_operations.js script to dynamically handle the new schema structure and ensure data consistency during updates.

    Date Parsing Errors: Python initially threw warnings/errors for mixed date formats (DD/MM/YYYY vs MM/DD/YYYY).

        Solution: Implemented a standardize_date function with dayfirst=True and error coercion to handle all formats gracefully.



        
