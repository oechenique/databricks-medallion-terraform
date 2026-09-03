# Medallion Pipeline en Databricks — gestionado con Terraform

Pipeline de datos con arquitectura Medallion (Bronze → Silver → Gold) sobre
Databricks Free Edition, desplegado como Infrastructure as Code con Terraform
y automatizado vía GitHub Actions.

## Arquitectura

```
Bronze (CTAS)  →  Silver (MERGE + validación)  →  Gold (MERGE)  →  Validación de conteos
```

- **Bronze**: `CREATE OR REPLACE TABLE` — reproducible, correr N veces da el mismo resultado. Como `samples.nyctaxi.trips` no trae un ID de viaje propio, se genera un `trip_id` sintético (hash determinístico de pickup/dropoff/fare) para poder mergear por clave más adelante.
- **Silver**: `MERGE INTO` por clave (`trip_id` + `process_date`) — idempotente, no duplica en reprocesos. Las filas inválidas se separan a una tabla de rechazados en vez de romper el pipeline.
- **Gold**: agregados de negocio, también vía `MERGE` sobre `process_date`.
- **Validación**: task explícita que chequea que `silver + rejected == bronze` (detecta pérdida silenciosa de datos).

## Estructura del repo

```
terraform/
  main.tf                    # provider + backend
  variables.tf                # parametrización (env, process_date, source_table, etc.)
  notebooks.tf                 # sube los .py del pipeline como notebooks
  job.tf                        # Job con 4 tasks encadenadas y retries
  outputs.tf                     # URL del Job post-apply
  notebooks/                      # código real de cada capa
  terraform.tfvars.example         # plantilla, sin secrets
.github/workflows/terraform.yml       # CI/CD: plan en PR, apply en merge a main
tests/test_pipeline_logic.py            # unit tests con pyspark local
```

## Setup — correrlo por primera vez (local)

1. Instalá Terraform y el CLI de Databricks.
2. Copiá `terraform/terraform.tfvars.example` a `terraform/terraform.tfvars` (este último está en `.gitignore`, nunca se commitea). Completá `databricks_host` con la URL real de tu workspace y `process_date` con una fecha que exista en el dataset fuente (`samples.nyctaxi.trips` es de enero 2016).
3. Exportá el token en vez de escribirlo en el `.tfvars`:
   ```bash
   export TF_VAR_databricks_token="dapi..."
   ```
4. Desde `terraform/`:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```
5. Entrá a tu workspace de Databricks → **Workflows** y vas a ver el Job `medallion-pipeline-dev` creado. Click en **Run now** para correrlo.

## Setup — automatizado (GitHub Actions)

1. En tu repo de GitHub: **Settings → Secrets and variables → Actions**, agregá:
   - `DATABRICKS_HOST`
   - `DATABRICKS_TOKEN`
   - `NOTIFICATION_EMAIL` (opcional)
2. Cada PR contra `main` que toque `terraform/**` corre `terraform plan` automáticamente.
3. Al mergear a `main`, corre `terraform apply` y aplica los cambios al workspace real.

## Limitaciones conocidas (Free Edition)

- Sin acceso a APIs de cuenta ni a clusters custom — solo cómputo serverless. Por eso las tasks son `notebook_task` sin `environment_key` ni bloque `environment`: ese bloque es para tasks de tipo `spark_python_task` con dependencias de librerías, no hace falta para notebooks en serverless, y de hecho romper esto tira un error de "Invalid platform channel".
- El token del workspace puede no traer el scope `access-management` por default (afecta a `databricks_permissions`, que este proyecto no usa por ser de un solo usuario).
- Para producción con clusters dedicados y control de permisos más fino, se migra a un plan Premium/Enterprise sin cambiar la estructura del código.

## Qué evalúa esto (y por qué está armado así)

| Pregunta típica de entrevista | Dónde está la respuesta |
|---|---|
| ¿Cómo parametrizás? | `job.tf` → `parameter {}`, recibido como widgets en cada notebook |
| ¿Cómo garantizás idempotencia? | Bronze = CTAS, Silver/Gold = MERGE por clave (`trip_id` sintético + `process_date`) |
| ¿Cómo controlás errores? | `try/except` + `raise` en cada notebook, `max_retries` en el Job |
| ¿Cómo encontrás fallos? | `email_notifications { on_failure }`, logs por task en Workflows |
| ¿Cómo testeás? | `tests/` con pytest + task de validación de conteos en el propio pipeline |
| ¿Cómo manejás secrets? | GitHub Secrets → env vars → nunca en el `.tf` ni en el repo |