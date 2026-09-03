resource "databricks_job" "medallion_pipeline" {
  name = "medallion-pipeline-${var.environment}"

  # Parametrización: estos valores llegan a cada notebook como dbutils.widgets
  parameter {
    name    = "environment"
    default = var.environment
  }
  parameter {
    name    = "process_date"
    default = var.process_date
  }
  parameter {
    name    = "source_table"
    default = var.source_table
  }

  task {
    task_key = "bronze_ingest"

    notebook_task {
      notebook_path = databricks_notebook.bronze.path
    }

    max_retries               = 2
    min_retry_interval_millis = 60000
    retry_on_timeout           = true
  }

  task {
    task_key = "silver_transform"

    depends_on {
      task_key = "bronze_ingest"
    }

    notebook_task {
      notebook_path = databricks_notebook.silver.path
    }

    max_retries               = 2
    min_retry_interval_millis = 60000
    retry_on_timeout           = true
  }

  task {
    task_key = "gold_aggregate"

    depends_on {
      task_key = "silver_transform"
    }

    notebook_task {
      notebook_path = databricks_notebook.gold.path
    }

    max_retries      = 2
    retry_on_timeout = true
  }

  task {
    task_key = "validate_counts"

    depends_on {
      task_key = "gold_aggregate"
    }

    notebook_task {
      notebook_path = databricks_notebook.validation.path
    }
  }

  # Alertas: si falla cualquier task, avisa por email
  email_notifications {
    on_failure = var.notification_email != "" ? [var.notification_email] : []
  }

  webhook_notifications {}

  tags = {
    project     = "medallion-pipeline"
    environment = var.environment
    managed_by  = "terraform"
  }
}
