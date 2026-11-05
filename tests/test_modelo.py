import json
from pathlib import Path

import pandas as pd


def test_resultados_kmeans():
    ruta = Path(
        "report/evidencias/evaluacion_kmeans.json"
    )

    assert ruta.exists(), "Falta la evaluación del modelo"

    datos = json.loads(ruta.read_text(encoding="utf-8"))

    assert datos["entrenamiento_registros"] > 0
    assert datos["prueba_registros"] > 0

    resultados = datos["resultados"]

    assert -1 <= resultados["k_2"] <= 1
    assert -1 <= resultados["k_3"] <= 1


def test_tres_grupos():
    ruta = Path(
        "data/output/resumen_clusters_final.csv"
    )

    clusters = pd.read_csv(ruta)

    assert len(clusters) == 3
    assert set(clusters["riesgo"]) == {
        "Alto", "Medio", "Bajo"
    }

    assert clusters["total_incendios"].sum() == 934712
