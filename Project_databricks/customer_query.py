# Databricks notebook source
# MAGIC %sql
# MAGIC
# MAGIC -- Customer Loyalty by Category (Gold Layer Analysis)
# MAGIC -- Uses Silver Layer table: default.customer_shopping_silver
# MAGIC
# MAGIC SELECT
# MAGIC     category,
# MAGIC
# MAGIC     -- 1. Average Spend per Transaction (Monetary Value)
# MAGIC     SUM(T1.quantity * T1.price) / COUNT(DISTINCT T1.invoice_no) AS Avg_Transaction_Value,
# MAGIC
# MAGIC     -- 2. Average Purchase Frequency per Customer
# MAGIC     COUNT(DISTINCT T1.invoice_no) / COUNT(DISTINCT T1.customer_id) AS Avg_Transactions_Per_Customer,
# MAGIC
# MAGIC     -- 3. Number of Distinct Customers
# MAGIC     COUNT(DISTINCT T1.customer_id) AS Unique_Customers_Count,
# MAGIC
# MAGIC     -- 4. Total Revenue for that Category
# MAGIC     SUM(T1.quantity * T1.price) AS Category_Total_Revenue
# MAGIC
# MAGIC FROM default.silver_no_negative_qty AS T1
# MAGIC GROUP BY category
# MAGIC ORDER BY Avg_Transaction_Value DESC;
# MAGIC