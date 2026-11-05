import json
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "data/processed/firms_mexico_limpio.parquet"
SALIDA = RAIZ / "report/evidencias/evaluacion_kmeans.json"

spark = (
    SparkSession.builder
    .appName("Evaluacion independiente KMeans")
    .master("local[2]")
    .config("spark.driver.memory", "2g")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    columnas = [
        "latitude",
        "longitude",
        "brightness",
        "frp",
        "confidence_num",
        "daynight_num"
    ]

    datos = spark.read.parquet(DATOS.as_uri())

    # Muestra reproducible para reducir el tiempo de evaluación
    muestra = (
        datos.select(columnas)
        .dropna()
        .sample(False, 0.03, seed=42)
    )

    # Separación antes del entrenamiento
    entrenamiento, prueba = muestra.randomSplit(
        [0.8, 0.2],
        seed=42
    )

    n_entrenamiento = entrenamiento.count()
    n_prueba = prueba.count()

    if n_entrenamiento < 3 or n_prueba < 3:
        raise RuntimeError("No hay suficientes registros.")

    assembler = VectorAssembler(
        inputCols=columnas,
        outputCol="features"
    )

    train_vector = assembler.transform(entrenamiento)
    test_vector = assembler.transform(prueba)

    # El escalador se ajusta solo con entrenamiento
    scaler = StandardScaler(
        inputCol="features",
        outputCol="scaled_features",
        withStd=True,
        withMean=True
    )

    scaler_model = scaler.fit(train_vector)

    train_scaled = scaler_model.transform(train_vector)
    test_scaled = scaler_model.transform(test_vector)

    evaluator = ClusteringEvaluator(
        featuresCol="scaled_features",
        predictionCol="prediction",
        metricName="silhouette",
        distanceMeasure="squaredEuclidean"
    )

    resultados = {}

    # K=2 como línea base; K=3 como configuración del proyecto
    for k in [2, 3]:
        algoritmo = KMeans(
            featuresCol="scaled_features",
            predictionCol="prediction",
            k=k,
            seed=42
        )

        modelo = algoritmo.fit(train_scaled)
        predicciones = modelo.transform(test_scaled)

        puntuacion = evaluator.evaluate(predicciones)
        resultados[f"k_{k}"] = round(float(puntuacion), 6)

    reporte = {
        "algoritmo": "K-Means Spark MLlib",
        "muestra": "3% aleatorio del dataset procesado",
        "seed": 42,
        "entrenamiento_registros": n_entrenamiento,
        "prueba_registros": n_prueba,
        "metrica": "Silhouette en conjunto de prueba",
        "resultados": resultados,
        "linea_base": "K-Means con k=2",
        "modelo_evaluado": "K-Means con k=3",
        "nota": (
            "Evaluacion independiente de la configuracion; "
            "no sustituye el modelo original del dashboard."
        )
    }

    SALIDA.parent.mkdir(parents=True, exist_ok=True)

    SALIDA.write_text(
        json.dumps(reporte, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nEVALUACION K-MEANS - PROTOTIPO v0.2")
    print("-----------------------------------")
    print("Entrenamiento:", n_entrenamiento)
    print("Prueba:", n_prueba)
    print("Silhouette linea base k=2:", resultados["k_2"])
    print("Silhouette modelo k=3:", resultados["k_3"])
    print("-----------------------------------")
    print("Reporte guardado en:", SALIDA)

finally:
    spark.stop()
