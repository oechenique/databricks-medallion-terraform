# Databricks notebook source
# CAPA BRONZE — ingesta cruda, patrón CTAS (reproducible: correr N veces = mismo resultado)

dbutils.widgets.text("environment", "dev")
dbutils.widgets.text("process_date", "2026-09-01")
dbutils.widgets.text("source_table", "samples.nyctaxi.trips")

environment = dbutils.widgets.get("environment")
process_date = dbutils.widgets.get("process_date")
source_table = dbutils.widgets.get("source_table")

catalog = f"medallion_{environment}"
bronze_table = f"{catalog}.bronze.trips_raw"

try:
    spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog}")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.bronze")

    # samples.nyctaxi.trips no trae un ID de viaje propio, así que generamos
    # uno sintético (hash determinístico) para poder hacer MERGE por clave en silver.
    # CTAS: recrea la tabla entera a partir de la fuente. Idempotente por diseño.
    spark.sql(f"""
        CREATE OR REPLACE TABLE {bronze_table} AS
        SELECT
            sha2(concat_ws('|', tpep_pickup_datetime, tpep_dropoff_datetime, fare_amount, pickup_zip), 256) AS trip_id,
            *,
            '{process_date}' AS ingestion_date
        FROM {source_table}
        WHERE CAST(tpep_pickup_datetime AS DATE) = '{process_date}'
    """)

    row_count = spark.table(bronze_table).count()
    print(f"[bronze_ingest] OK — {row_count} filas en {bronze_table}")

    if row_count == 0:
        raise ValueError(f"Bronze vacío para process_date={process_date}. Revisar fuente.")

except Exception as e:
    print(f"[bronze_ingest] ERROR: {e}")
    raise  # re-lanzar para que el Job marque la task como failed y dispare el retry/alerta
