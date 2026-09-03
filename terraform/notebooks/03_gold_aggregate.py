# Databricks notebook source
# CAPA GOLD — agregados de negocio, también vía MERGE para idempotencia

dbutils.widgets.text("environment", "dev")
dbutils.widgets.text("process_date", "2026-09-01")

environment = dbutils.widgets.get("environment")
process_date = dbutils.widgets.get("process_date")

catalog = f"medallion_{environment}"
silver_table = f"{catalog}.silver.trips_clean"
gold_table = f"{catalog}.gold.daily_revenue"

try:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.gold")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {gold_table} (
            process_date STRING,
            total_trips LONG,
            total_revenue DOUBLE,
            avg_fare DOUBLE
        ) USING DELTA
    """)

    spark.sql(f"""
        CREATE OR REPLACE TEMP VIEW daily_agg AS
        SELECT
            '{process_date}' AS process_date,
            COUNT(*) AS total_trips,
            SUM(fare_amount) AS total_revenue,
            AVG(fare_amount) AS avg_fare
        FROM {silver_table}
        WHERE process_date = '{process_date}'
    """)

    spark.sql(f"""
        MERGE INTO {gold_table} AS target
        USING daily_agg AS source
        ON target.process_date = source.process_date
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

    print(f"[gold_aggregate] OK — gold actualizado para {process_date}")

except Exception as e:
    print(f"[gold_aggregate] ERROR: {e}")
    raise
