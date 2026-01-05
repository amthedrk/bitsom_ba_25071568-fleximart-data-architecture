NoSQL Justification Report
Section A: Limitations of RDBMS

Relational Database Management Systems (RDBMS) like MySQL are designed around rigid, tabular structures that struggle with the variability of modern e-commerce catalogs.

    The "Sparse Data" Problem: In an RDBMS, every row in a table must follow the same column structure. If FlexiMart sells Laptops (requiring RAM, CPU) and Shoes (requiring Size, Color), we would need to create a products table with all possible columns. This results in a "sparse" table where a Shoe record has NULL values for RAM and CPU, wasting storage and complicating queries.

    Schema Rigidity: Adding a new product category (e.g., "Food" with ExpiryDate) requires an ALTER TABLE command. On large datasets, this operation locks the table, potentially causing downtime or performance degradation for the live website.

    Complex Relationships: Storing customer reviews in an RDBMS requires a separate reviews table linked by Foreign Keys. Retrieving a product with its reviews requires a JOIN operation, which becomes computationally expensive and slower as the data volume grows.

Section B: NoSQL Benefits (MongoDB)

MongoDB, a Document-Oriented NoSQL database, offers specific architectural advantages that resolve the friction points of RDBMS for product catalogs.

    Flexible Schema (Polymorphism): MongoDB stores data as BSON (Binary JSON) documents. This allows each document in the same collection to have a completely different structure. A "Laptop" document can hold technical specifications, while a "Shoe" document in the same collection holds style attributes. No schema changes or downtime are required to introduce new product types.

Embedded Data Models: Instead of splitting data across tables, MongoDB allows embedding related data directly into the parent document. Customer reviews can be stored as an array inside the Product document. This allows the application to fetch a product and all its reviews in a single read operation, significantly boosting read performance.

Horizontal Scalability: MongoDB is built for "Sharding"—distributing data across multiple cheap servers. Unlike RDBMS, which typically scales "Vertically" (requiring bigger, expensive hardware), MongoDB can handle massive catalogs by simply adding more nodes to the cluster.

Section C: Trade-offs

While MongoDB excels at content management, replacing MySQL comes with distinct disadvantages:

    Weaker Transactional Guarantees: MySQL ensures strict ACID (Atomicity, Consistency, Isolation, Durability) compliance, which is critical for financial transactions (like the orders table). While MongoDB supports transactions, they are more complex to implement and performance-heavy compared to the mature transaction engines of RDBMS.

    Data Integrity Responsibility: MySQL enforces integrity constraints (e.g., Foreign Keys, Data Types) at the database level. MongoDB is schema-less, meaning the database does not validate data by default. The responsibility for ensuring that email fields actually contain emails, or that mandatory fields exist, shifts entirely to the application code, increasing the risk of "dirty" data.