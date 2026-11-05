from pathlib import Path
import sqlite3
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "data" / "output"
BD = RAIZ / "data" / "firms.sqlite3"

ARCHIVOS = {
    "resumen": "resumen_general_final.csv",
    "anios": "incendios_por_anio_final.csv",
    "clusters": "resumen_clusters_final.csv",
    "puntos": "puntos_cluster_dashboard_sample.csv"
}

with sqlite3.connect(BD) as conexion:
    for tabla, nombre in ARCHIVOS.items():
        ruta = SALIDA / nombre

        if not ruta.exists():
            raise FileNotFoundError(f"No existe: {ruta}")

        datos = pd.read_csv(ruta)
        datos.to_sql(tabla, conexion, if_exists="replace", index=False)

        print(f"{tabla}: {len(datos):,} registros importados")

print(f"\nBase de datos creada correctamente: {BD}")
