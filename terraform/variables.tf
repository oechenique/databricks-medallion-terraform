variable "databricks_host" {
  description = "URL del workspace de Databricks (ej: https://xxx.cloud.databricks.com)"
  type        = string
}

variable "databricks_token" {
  description = "Token de autenticación (PAT u OAuth). Nunca hardcodear, viene de env var o GitHub Secrets."
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Entorno de ejecución (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "process_date" {
  description = "Fecha de procesamiento del pipeline (parametrizable por run)"
  type        = string
  default     = "2016-01-01"
}

variable "source_table" {
  description = "Tabla/dataset fuente para la capa bronze"
  type        = string
  default     = "samples.nyctaxi.trips"
}

variable "notification_email" {
  description = "Email para alertas de fallos en el Job"
  type        = string
  default     = ""
}
