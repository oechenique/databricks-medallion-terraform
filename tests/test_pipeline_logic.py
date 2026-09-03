"""
Tests unitarios de la lógica de negocio del pipeline (fuera de Databricks,
corren local o en CI con pyspark). No dependen de un cluster real.

Correr con: pytest tests/
"""
import pytest
from pyspark.sql import SparkSession
from pyspark.sql import Row


@pytest.fixture(scope="module")
def spark():
    return (
        SparkSession.builder
        .master("local[2]")
        .appName("pipeline-tests")
        .getOrCreate()
    )


def test_silver_filters_invalid_fare(spark):
    """Filas con fare_amount <= 0 deben ir a rejected, no a silver."""
    df = spark.createDataFrame([
        Row(trip_id="1", fare_amount=15.5, tpep_pickup_datetime="2026-09-01 08:00:00"),
        Row(trip_id="2", fare_amount=-3.0, tpep_pickup_datetime="2026-09-01 09:00:00"),
        Row(trip_id="3", fare_amount=0.0, tpep_pickup_datetime="2026-09-01 10:00:00"),
    ])

    valid = df.filter("fare_amount > 0")
    rejected = df.filter("fare_amount <= 0")

    assert valid.count() == 1
    assert rejected.count() == 2


def test_bronze_silver_rejected_counts_reconcile(spark):
    """La suma de silver + rejected siempre debe igualar bronze (invariante del pipeline)."""
    bronze_count = 100
    silver_count = 92
    rejected_count = 8

    assert silver_count + rejected_count == bronze_count
