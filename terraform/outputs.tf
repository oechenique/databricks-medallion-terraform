output "job_id" {
  description = "ID del Job creado — buscalo en Workflows dentro de Databricks"
  value       = databricks_job.medallion_pipeline.id
}

output "job_url" {
  description = "URL directa al Job en la consola de Databricks"
  value       = "${var.databricks_host}/#job/${databricks_job.medallion_pipeline.id}"
}
