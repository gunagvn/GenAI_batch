# Databricks notebook source
from pyspark.sql import functions as F

# --- CONFIGURATION ---
SILVER_TABLE_NAME = "default.silver_no_negative_qty"
SALES_GOLD_TABLE_NAME = "default.gold_sales_performance"
CUSTOMER_GOLD_TABLE_NAME = "default.gold_customer_behavior"

print(f"Loading data from Silver Layer table: {SILVER_TABLE_NAME}")

# --- Load the Silver DataFrame ---
try:
    df_silver = spark.table(SILVER_TABLE_NAME)
    print(f"Silver DataFrame loaded with {df_silver.count()} rows.")
except Exception as e:
    print(f"Error loading Silver table {SILVER_TABLE_NAME}: {e}")
    raise



# COMMAND ----------

spark.sql("SHOW TABLES IN default").show()


# COMMAND ----------



# Assuming 'df_silver' is the DataFrame from Step 1

print("\n--- Creating Gold Table: Sales Performance ---")

# 1. Feature Engineering: Extract time components and calculate total sales price
df_enriched = df_silver.withColumn("sales_price", F.col("price")) \
                       .withColumn("year", F.year(F.col("invoice_date"))) \
                       .withColumn("month", F.month(F.col("invoice_date"))) \
                       .withColumn("day_of_year", F.dayofyear(F.col("invoice_date")))

# 2. Aggregation: Group by Date (Year, Month) and Mall to get key KPIs
df_sales_gold = df_enriched.groupBy("year", "month", "shopping_mall").agg(
    F.countDistinct("invoice_no").alias("Total_Transactions"),
    F.sum("sales_price").alias("Total_Revenue"),
    F.sum("quantity").alias("Total_Quantity_Sold"),
    F.avg("sales_price").alias("Avg_Transaction_Value")
).orderBy("year", "month")

# 3. Save to Gold Layer
print(f"Saving Sales Gold data to: {SALES_GOLD_TABLE_NAME}")
df_sales_gold.write \
    .option("overwriteSchema", "true") \
    .mode("overwrite") \
    .saveAsTable(SALES_GOLD_TABLE_NAME)

print(f"Gold table saved. Final row count: {df_sales_gold.count()}")

# Display the result of this step (First Gold Table)
display(df_sales_gold)

# COMMAND ----------



# Assuming 'df_silver' is the DataFrame from Step 1

print("\n--- Creating Gold Table: Customer Behavior (RFM Features) ---")

# 1. Determine the latest date in the dataset to calculate Recency
# We use a literal date one day after the max date as the "snapshot date"
max_date = df_silver.select(F.max("invoice_date")).collect()[0][0]
SNAPSHOT_DATE = F.lit(max_date).cast("timestamp") + F.expr("interval 1 day")

# 2. Calculate RFM metrics per customer
df_customer_gold = df_silver.groupBy("customer_id").agg(
    # Recency: Days since last purchase
    F.datediff(SNAPSHOT_DATE, F.max("invoice_date")).alias("Recency_Days"),
    
    # Frequency: Total number of unique invoices (transactions)
    F.countDistinct("invoice_no").alias("Frequency_Transactions"),
    
    # Monetary: Total spent by the customer over the entire period
    F.sum("price").alias("Monetary_Value_Total"),
    
    # Other useful features
    F.avg("age").alias("Avg_Age"), # Average age (useful for consistency check)
    F.count("*").alias("Total_Items_Purchased_Count") # Total count of line items
)

# 3. Save to Gold Layer
print(f"Saving Customer Gold data to: {CUSTOMER_GOLD_TABLE_NAME}")
df_customer_gold.write \
    .option("overwriteSchema", "true") \
    .mode("overwrite") \
    .saveAsTable(CUSTOMER_GOLD_TABLE_NAME)

print(f"Gold table saved. Final row count: {df_customer_gold.count()}")

# Display the result of this step (Second Gold Table)
display(df_customer_gold)

# COMMAND ----------



# Assuming 'df_silver' is the DataFrame loaded in Step 1

print("\n--- Creating Gold Table: Product Performance ---")

df_product_gold = df_silver.groupBy("category", "shopping_mall").agg(
    # Aggregations
    F.countDistinct("invoice_no").alias("Total_Transactions"),
    F.sum("quantity").alias("Total_Quantity_Sold"),
    F.sum("price").alias("Total_Revenue"),
    F.avg("price").alias("Avg_Price_Per_Transaction"),
    
    # Feature: Identify the number of unique customers who bought this category/mall combination
    F.countDistinct("customer_id").alias("Unique_Customers")
).orderBy(F.desc("Total_Revenue"))

# Save to Gold Layer
OUTPUT_TABLE_NAME = "default.gold_product_performance"
print(f"Saving Product Gold data to: {OUTPUT_TABLE_NAME}")

df_product_gold.write \
    .option("overwriteSchema", "true") \
    .mode("overwrite") \
    .saveAsTable(OUTPUT_TABLE_NAME)

print(f"Gold table saved. Final row count: {df_product_gold.count()}")

# Display the result of this step (Third Gold Table)
display(df_product_gold)

# COMMAND ----------

from pyspark.sql import functions as F

# Load Gold Sales & Customer tables
sales_df = spark.table("default.gold_sales_performance")
customer_df = spark.table("default.gold_customer_behavior")

# 1. Sales Summary: Total Revenue & Total Transactions
sales_summary = (
    sales_df
    .agg(
        F.sum("Total_Revenue").alias("Total_Revenue"),
        F.sum("Total_Transactions").alias("Total_Transactions")
    )
)

# 2. Customer Summary: Avg Recency
customer_summary = (
    customer_df
    .agg(
        F.avg("Recency_Days").alias("Avg_Customer_Recency")
    )
)

# 3. Cross join - combine both
kpi_df = sales_summary.crossJoin(customer_summary)

display(kpi_df)

# COMMAND ----------

from pyspark.sql import functions as F

sales_df = spark.table("default.gold_sales_performance")

monthly_df = (
    sales_df
    .withColumn(
        "Year_Month",
        F.concat_ws(
            "-",
            F.col("year").cast("string"),
            F.lpad(F.col("month").cast("string"), 2, "0")
        )
    )
    .groupBy("Year_Month")
    .agg(
        F.sum("Total_Revenue").alias("Total_Revenue"),
        F.sum("Total_Transactions").alias("Total_Transactions")
    )
    .orderBy("Year_Month")
)

display(monthly_df)

# COMMAND ----------

product_df = spark.table("default.gold_product_performance")

category_revenue_df = (
    product_df
    .groupBy("category")
    .agg(
        F.sum("Total_Revenue").alias("Category_Total_Revenue")
    )
    .orderBy(F.col("Category_Total_Revenue").desc())
)

display(category_revenue_df)

# COMMAND ----------

silver_df = spark.table("default.silver_no_negative_qty")

loyalty_df = (
    silver_df
    .groupBy("category")
    .agg(
        # Avg Transaction Value = SUM(qty * price) / COUNT(DISTINCT invoice)
        (F.sum(F.col("quantity") * F.col("price")) /
         F.countDistinct("invoice_no")).alias("Avg_Transaction_Value"),

        # Avg Transactions per Customer = Count(distinct invoices) / Count(distinct customers)
        (F.countDistinct("invoice_no") /
         F.countDistinct("customer_id")).alias("Avg_Transactions_Per_Customer"),

        # Total unique customers
        F.countDistinct("customer_id").alias("Unique_Customers_Count"),

        # Total revenue for category
        F.sum(F.col("quantity") * F.col("price")).alias("Category_Total_Revenue")
    )
    .orderBy(F.col("Avg_Transaction_Value").desc())
)

display(loyalty_df)