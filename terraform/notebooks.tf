# Sube el código de cada capa como notebook al workspace.
# El contenido real vive en terraform/notebooks/*.py (versionado en git).

resource "databricks_notebook" "bronze" {
  path     = "/Workspace/medallion-${var.environment}/01_bronze_ingest"
  language = "PYTHON"
  source   = "${path.module}/notebooks/01_bronze_ingest.py"
}

resource "databricks_notebook" "silver" {
  path     = "/Workspace/medallion-${var.environment}/02_silver_transform"
  language = "PYTHON"
  source   = "${path.module}/notebooks/02_silver_transform.py"
}

resource "databricks_notebook" "gold" {
  path     = "/Workspace/medallion-${var.environment}/03_gold_aggregate"
  language = "PYTHON"
  source   = "${path.module}/notebooks/03_gold_aggregate.py"
}

resource "databricks_notebook" "validation" {
  path     = "/Workspace/medallion-${var.environment}/04_validate_counts"
  language = "PYTHON"
  source   = "${path.module}/notebooks/04_validate_counts.py"
}
