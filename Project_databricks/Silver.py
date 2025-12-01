# Databricks notebook source
# dklfjlk
from pyspark.sql import functions as F 
Bronze = spark.table("workspace.default.customer_shopping_fraud_clean_ids_no_fraud_column")

Silver_No_Negative_Qty_df =( Bronze.filter(F.col("quantity") > 0))
Silver_No_Negative_Qty_df.write.format("delta").mode("overwrite").saveAsTable(
    "default.silver_no_negative_qty"
)

display(Silver_No_Negative_Qty_df)

# COMMAND ----------

#To Remove duplicate price
Silver_No_Negative_Qty_df =( Bronze.filter(F.col("price") > 0))
display(Silver_No_Negative_Qty_df)

# COMMAND ----------

Silver_No_Negative_Qty_df = Bronze.filter(
    (F.col("age") >= 10) & (F.col("age") <= 100)
)
display(Silver_No_Negative_Qty_df)




# COMMAND ----------

Silver_No_Negative_Qty_df = Bronze.filter(
    (F.col("age") >= 10) & (F.col("age") <= 100)
)
display(Silver_No_Negative_Qty_df)


# COMMAND ----------

Silver_No_Negative_Qty_df = (
    Bronze
        .withColumn("invoice_date", F.to_date("invoice_date", "yyyy-MM-dd"))
        .filter(F.col("invoice_date").isNotNull())
)
display(Silver_No_Negative_Qty_df)


# COMMAND ----------

Silver_No_Negative_Qty_df = (
    Bronze.withColumn("gender", F.initcap(F.col("gender")))
)
display(Silver_No_Negative_Qty_df)



# COMMAND ----------

Silver_No_Negative_Qty_df = (
    Bronze .withColumn("category", F.trim(F.col("category")))
        .withColumn("payment_method", F.trim(F.col("payment_method")))
)
display(Silver_No_Negative_Qty_df)



# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType

# Define the schema to accurately load the raw data
raw_schema = StructType([
    StructField("invoice_no", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("age", StringType(), True),
    StructField("category", StringType(), True),
    StructField("quantity", StringType(), True),
    StructField("price", StringType(), True),
    StructField("payment_method", StringType(), True),
    StructField("invoice_date", StringType(), True),
    StructField("shopping_mall", StringType(), True)
])

# Load the Bronze table. This DataFrame 'df' is used in all following cells.
df = spark.read.table("customer_shopping_fraud_clean_ids_no_fraud_column")

print(f"Bronze DataFrame 'df' loaded successfully with {df.count()} records.")
display(df)

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import LongType, DoubleType

# NOTE: Requires 'df' to be defined in block 1.

print("--- AUDIT: INVALID RECORDS (EXCLUDED DATA) ---")

# --- Preparation: Cast and Define Filters ---
df_casted = df.withColumn("age_num", F.col("age").cast(LongType())) \
              .withColumn("quantity_num", F.col("quantity").cast(LongType())) \
              .withColumn("price_num", F.col("price").cast(DoubleType()))

# 1. Invalid Price/Quantity (non-positive, or nulls)
invalid_transactions = (F.col("quantity_num").isNull()) | (F.col("price_num").isNull()) | \
                       (F.col("quantity_num") <= 0) | (F.col("price_num") <= 0)

# 2. Invalid Age (Age outside 15-100 range, or nulls)
invalid_age = (F.col("age_num").isNull()) | \
              (F.col("age_num") < 15) | (F.col("age_num") > 100)

# --- 3. Filter for all invalid records ---
df_invalid_records_viz = df_casted.filter(invalid_transactions | invalid_age)

# --- Visualization Preparation (Summary Table) ---
df_invalid_summary = df_invalid_records_viz.withColumn(
    "Removal_Reason", 
    F.when(invalid_age, "Invalid Age (Out of Range)").otherwise("Invalid Price/Quantity (<=0)")
).groupBy("Removal_Reason").count().withColumnRenamed("count", "Records_Removed")

print(f"Total Invalid Records Found: {df_invalid_records_viz.count()}")
print("\nSummary of Records Removed by Reason:")
display(df_invalid_summary)

display(df_invalid_records_viz)