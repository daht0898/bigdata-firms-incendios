# Pipeline Big Data para análisis de incendios forestales en México

Proyecto final de Big Data enfocado en el análisis de detecciones de incendios activos en México usando datos satelitales de NASA FIRMS.

El pipeline usa PySpark para procesamiento, Parquet para almacenamiento, Spark SQL para análisis exploratorio, SparkML para clustering K-Means y Streamlit para el dashboard final.

## Objetivo

Diseñar e implementar un pipeline de Big Data para analizar detecciones de incendios forestales en México, identificar patrones temporales y espaciales, y agrupar zonas de riesgo mediante K-Means.

## Dataset

Fuente: NASA FIRMS  
Producto usado: VIIRS S-NPP  
Región: México  
Periodo: 2023-01-01 a 2025-12-31  
Formato original: CSV comprimido en ZIP  

Archivo incluido:

    data/raw/DL_FIRE_SV-C2_764880.zip

Al descomprimirlo debe generarse:

    data/raw/fire_archive_SV-C2_764880.csv

## Herramientas usadas

- Python 3.12
- PySpark
- Spark SQL
- SparkML
- Pandas
- Streamlit
- Plotly
- PyDeck
- Parquet

## Instalación

En Ubuntu:

    sudo apt update
    sudo apt install -y python3.12-venv python3-full unzip

Crear entorno virtual:

    python3 -m venv venv
    source venv/bin/activate

Instalar dependencias:

    pip install --upgrade pip
    pip install -r requirements.txt

## Preparar dataset

Descomprimir el dataset:

    cd data/raw
    unzip DL_FIRE_SV-C2_764880.zip
    cd ../..

Debe quedar este archivo:

    data/raw/fire_archive_SV-C2_764880.csv

## Ejecutar pipeline

Probar Spark:

    python src/00_prueba_spark.py

Procesar dataset:

    python src/01_procesamiento_firms.py

Ejecutar análisis exploratorio:

    python src/02_analisis_exploratorio.py

Entrenar modelo K-Means:

    python src/03_modelo_kmeans.py

Preparar CSV finales:

    python src/04_preparar_csv_finales.py

Crear muestra para dashboard:

    python src/05_crear_muestra_dashboard.py

## Ejecutar dashboard

    streamlit run dashboard/app.py

Abrir en navegador:

    http://localhost:8501

## Resultados principales

- Total de detecciones: 934,712
- Periodo: 2023-01-01 a 2025-12-31
- FRP promedio: 8.93
- FRP máximo: 1282.13
- Silhouette Score del modelo K-Means: 0.4636

Detecciones por año:

- 2023: 327,657
- 2024: 330,134
- 2025: 276,921

Clusters interpretados:

- Cluster 1: Riesgo Alto
- Cluster 2: Riesgo Medio
- Cluster 0: Riesgo Bajo

## Dashboard

El dashboard muestra métricas generales, detecciones por año y mes, distribución día/noche, nivel de confianza, clusters de riesgo, mapa con puntos de incendio y zonas aproximadas con más detecciones.

## Nota

El archivo completo de puntos con clusters no se sube porque es más pesado. Se puede regenerar ejecutando el pipeline.

---

# Prototipo avanzado v0.2

## Descripción

Sistema informático basado en Big Data para apoyar el análisis
histórico de detecciones satelitales de actividad térmica en México.

Utiliza datos de NASA FIRMS, procesamiento mediante PySpark,
agrupamiento K-Means y visualización interactiva.

El sistema no realiza predicciones de incendios en tiempo real
ni genera alertas oficiales.

## Arquitectura

NASA FIRMS
    |
    v
PySpark + K-Means
    |
    v
Archivos CSV procesados
    |
    v
SQLite
    |
    v
FastAPI
    |
    v
Dashboard Streamlit

El procesamiento y entrenamiento se realizan por lotes.
La API consulta resultados previamente generados.

## Tecnologías

- Python
- PySpark y Spark MLlib
- Streamlit
- FastAPI
- SQLite
- Docker Compose
- Pandas y Plotly

## Ejecución mediante Docker

Requisitos:

- Docker
- Docker Compose

Desde la carpeta principal del proyecto ejecutar:

    docker compose up --build -d

Comprobar los contenedores:

    docker compose ps

Acceder a:

- Dashboard: http://localhost:8502
- API: http://localhost:8001/docs

Si no existe data/firms.sqlite3, el servicio API ejecuta
el importador para generarla desde los CSV incluidos.

Para detener los servicios:

    docker compose down

## Pruebas automatizadas

Con las dependencias de desarrollo instaladas:

    python -m pytest -v tests/test_api.py tests/test_modelo.py

## Evaluación y mediciones

Se incluyen scripts para:

- Evaluación comparativa K-Means.
- Medición de latencia p50 y p95.
- Registro y análisis FinOps.
- Estimación de costo unitario.
- Validación de datos.

Las mediciones de latencia corresponden a consultas
de resultados almacenados, no al entrenamiento de K-Means.

Los costos de Cloud Run son estimaciones basadas en
mediciones locales, no gastos reales de infraestructura.

## Datos y reproducibilidad

La carpeta data/output incluye los resultados necesarios
para iniciar el dashboard y reconstruir SQLite.

Los datos originales de NASA FIRMS y los archivos
intermedios Parquet no se incluyen en el repositorio.

Para reproducir el procesamiento y entrenamiento originales
es necesario obtener el dataset correspondiente y ejecutar
los scripts de src.

La evaluación comparativa incluida utiliza una muestra
y no sustituye el modelo original del dashboard.

## Cambios respecto al primer parcial

- Integración de una base de datos SQLite.
- Implementación de API con FastAPI.
- Dashboard conectado a la API.
- Registro de consultas por cliente.
- Generación de estado de cuenta simulado.
- Medición de latencia.
- Instrumentación y estimación de costos FinOps.
- Auditoría automatizada de dependencias.
- Pruebas automatizadas.
- Despliegue mediante Docker Compose.

## Versión

v0.2 - Prototipo avanzado del segundo parcial.

