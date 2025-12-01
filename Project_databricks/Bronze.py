# Databricks notebook source
df = spark.table("workspace.default.customer_shopping_fraud_clean_ids_no_fraud_column")
display(df)