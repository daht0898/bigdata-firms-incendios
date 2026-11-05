import csv
import time
from pathlib import Path

import numpy as np
import requests

# Configuración de la prueba
URL = "http://127.0.0.1:8000/api/clusters"
CLIENTE = "cliente_prueba_latencia"
TOTAL = 110

SALIDA = Path("report/evidencias")
SALIDA.mkdir(parents=True, exist_ok=True)

registros = []

print("Iniciando prueba de latencia...\n")

with requests.Session() as sesion:

    sesion.headers.update({
        "X-Client-ID": CLIENTE
    })

    for numero in range(1, TOTAL + 1):

        inicio = time.perf_counter()

        respuesta = sesion.get(URL, timeout=30)

        tiempo_cliente = (
            time.perf_counter() - inicio
        ) * 1000

        respuesta.raise_for_status()

        tiempo_servidor = float(
            respuesta.headers["X-Tiempo-API-ms"]
        )

        registros.append({
            "peticion": numero,
            "estado_http": respuesta.status_code,
            "latencia_cliente_ms": round(tiempo_cliente, 3),
            "latencia_servidor_ms": tiempo_servidor
        })

        if numero % 10 == 0:
            print(f"Peticiones completadas: {numero}/{TOTAL}")


# Cálculo estadístico
cliente = np.array([
    r["latencia_cliente_ms"] for r in registros
])

servidor = np.array([
    r["latencia_servidor_ms"] for r in registros
])

resumen = f"""
RESULTADOS DE LATENCIA - PROTOTIPO v0.2

Endpoint: {URL}
Cliente de prueba: {CLIENTE}
Peticiones exitosas: {len(registros)}

LATENCIA DESDE EL CLIENTE
p50: {np.percentile(cliente, 50):.3f} ms
p95: {np.percentile(cliente, 95):.3f} ms
Promedio: {np.mean(cliente):.3f} ms

LATENCIA REGISTRADA POR FASTAPI
p50: {np.percentile(servidor, 50):.3f} ms
p95: {np.percentile(servidor, 95):.3f} ms
Promedio: {np.mean(servidor):.3f} ms

Ambiente: Ubuntu / ejecución local
"""

# Guardar resultados individuales
with open(
    SALIDA / "latencia_110.csv",
    "w",
    newline="",
    encoding="utf-8"
) as archivo:

    escritor = csv.DictWriter(
        archivo,
        fieldnames=registros[0].keys()
    )

    escritor.writeheader()
    escritor.writerows(registros)


# Guardar resumen
(SALIDA / "resumen_latencia.txt").write_text(
    resumen,
    encoding="utf-8"
)

print(resumen)
print("Archivos guardados en report/evidencias/")
