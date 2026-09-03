terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.60"
    }
  }

  # Backend remoto recomendado para no dejar el state (con secretos) en tu máquina.
  # Descomentar y configurar cuando tengas el bucket/tabla listos:
  #
  # backend "s3" {
  #   bucket         = "tu-bucket-tfstate"
  #   key            = "databricks-medallion/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "databricks" {
  host  = var.databricks_host
  token = var.databricks_token
}
