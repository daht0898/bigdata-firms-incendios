import sqlite3
from pathlib import Path
import pandas as pd

BD = Path("data/firms.sqlite3")
SALIDA = Path("report/evidencias")
SALIDA.mkdir(parents=True, exist_ok=True)

# Consultar registros del cliente utilizado en las pruebas
with sqlite3.connect(BD) as conexion:
    datos = pd.read_sql_query("""
        SELECT
            fecha,
            cliente,
            endpoint,
            tiempo_ms,
            cpu_ms,
            proyecto,
            ambiente,
            componente,
            estado_http,
            facturable
        FROM uso_api
        WHERE cliente = 'cliente_prueba_latencia'
          AND endpoint = '/api/clusters'
        ORDER BY id
    """, conexion)

if datos.empty:
    raise SystemExit("No se encontraron registros de prueba.")

# Guardar todos los registros
datos.to_csv(
    SALIDA / "finops_registros.csv",
    index=False
)

# Calcular estadísticas
total = len(datos)
exitosas = int((datos["estado_http"] == 200).sum())

tiempo_promedio = datos["tiempo_ms"].mean()
tiempo_total = datos["tiempo_ms"].sum()

cpu_promedio = datos["cpu_ms"].mean()
cpu_total = datos["cpu_ms"].sum()

print("\nREPORTE FINOPS - PROTOTIPO v0.2")
print("--------------------------------")
print(f"Peticiones registradas: {total}")
print(f"Peticiones exitosas: {exitosas}")
print(f"Tiempo promedio API: {tiempo_promedio:.3f} ms")
print(f"Tiempo acumulado API: {tiempo_total:.3f} ms")
print(f"Tiempo CPU registrado promedio: {cpu_promedio:.3f} ms")
print(f"Tiempo CPU registrado acumulado: {cpu_total:.3f} ms")
print("Proyecto: BigData-FIRMS")
print("Ambiente: local")
print("Componente: FastAPI")
print("--------------------------------")
print("Archivo generado: report/evidencias/finops_registros.csv")

resumen = (
    f"Peticiones: {total}\n"
    f"Exitosas: {exitosas}\n"
    f"Tiempo promedio API: {tiempo_promedio:.3f} ms\n"
    f"Tiempo acumulado API: {tiempo_total:.3f} ms\n"
    f"Tiempo CPU proceso promedio: {cpu_promedio:.3f} ms\n"
    f"Tiempo CPU proceso acumulado: {cpu_total:.3f} ms\n"
    "Ambiente: local\n"
    "Costo monetario: pendiente de tarifa verificable\n"
)

(SALIDA / "finops_resumen.txt").write_text(
    resumen,
    encoding="utf-8"
)
