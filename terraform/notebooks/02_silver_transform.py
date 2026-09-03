# Databricks notebook source
# CAPA SILVER — limpieza + MERGE idempotente (evita duplicados en reprocesos)

dbutils.widgets.text("environment", "dev")
dbutils.widgets.text("process_date", "2026-09-01")

environment = dbutils.widgets.get("environment")
process_date = dbutils.widgets.get("process_date")

catalog = f"medallion_{environment}"
bronze_table = f"{catalog}.bronze.trips_raw"
silver_table = f"{catalog}.silver.trips_clean"
rejected_table = f"{catalog}.silver.trips_rejected"

try:
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.silver")
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {silver_table} (
            trip_id STRING,
            pickup_datetime TIMESTAMP,
            dropoff_datetime TIMESTAMP,
            fare_amount DOUBLE,
            process_date STRING
        ) USING DELTA
    """)
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {rejected_table} (
            trip_id STRING,
            reason STRING,
            process_date STRING
        ) USING DELTA
    """)

    df = spark.table(bronze_table)

    # Validación simple: separamos filas inválidas en vez de que rompan el pipeline entero
    valid_df = df.filter("fare_amount > 0 AND tpep_pickup_datetime IS NOT NULL")
    rejected_df = df.filter("fare_amount <= 0 OR tpep_pickup_datetime IS NULL")

    valid_df.selectExpr(
        "trip_id",
        "tpep_pickup_datetime AS pickup_datetime",
        "tpep_dropoff_datetime AS dropoff_datetime",
        "fare_amount",
        "ingestion_date AS process_date"
    ).createOrReplaceTempView("valid_trips")

    # MERGE por clave (trip_id + process_date): correr dos veces no duplica filas
    spark.sql(f"""
        MERGE INTO {silver_table} AS target
        USING valid_trips AS source
        ON target.trip_id = source.trip_id AND target.process_date = source.process_date
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

    if rejected_df.count() > 0:
        rejected_df.selectExpr(
            "trip_id", "'fare_amount_or_datetime_invalid' AS reason", f"'{process_date}' AS process_date"
        ).write.mode("append").saveAsTable(rejected_table)

    print(f"[silver_transform] OK — {valid_df.count()} válidas, {rejected_df.count()} rechazadas")

except Exception as e:
    print(f"[silver_transform] ERROR: {e}")
    raise
