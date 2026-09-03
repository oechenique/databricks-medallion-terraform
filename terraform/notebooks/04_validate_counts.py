# Databricks notebook source
# VALIDACIÓN — no es un afterthought, es una task explícita del Job.
# Compara bronze vs silver+rejected para detectar pérdida silenciosa de filas.

dbutils.widgets.text("environment", "dev")
dbutils.widgets.text("process_date", "2026-09-01")

environment = dbutils.widgets.get("environment")
process_date = dbutils.widgets.get("process_date")

catalog = f"medallion_{environment}"
bronze_table = f"{catalog}.bronze.trips_raw"
silver_table = f"{catalog}.silver.trips_clean"
rejected_table = f"{catalog}.silver.trips_rejected"

bronze_count = spark.table(bronze_table).count()
silver_count = spark.table(silver_table).where(f"process_date = '{process_date}'").count()
rejected_count = spark.table(rejected_table).where(f"process_date = '{process_date}'").count()

print(f"[validate_counts] bronze={bronze_count} silver={silver_count} rejected={rejected_count}")

# Regla: silver + rejected debe explicar el 100% de bronze. Si no, algo se perdió en el camino.
if silver_count + rejected_count != bronze_count:
    raise ValueError(
        f"Conteos no cuadran: bronze={bronze_count} vs silver+rejected={silver_count + rejected_count}. "
        f"Revisar lógica de silver_transform."
    )

print("[validate_counts] OK — conteos consistentes")
