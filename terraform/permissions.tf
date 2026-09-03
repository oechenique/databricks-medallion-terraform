# resource "databricks_permissions" "medallion_job_permissions" {
#  job_id = databricks_job.medallion_pipeline.id
#
#  access_control {
#    group_name       = "users"
#    permission_level = "CAN_VIEW"
#  }
#
#  # Agregá acá tu usuario/grupo con CAN_MANAGE_RUN o CAN_MANAGE según necesites
#}
