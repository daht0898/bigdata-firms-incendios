import csv
import json
from pathlib import Path
from datetime import date
from copy import deepcopy

# Archivos
ORIGEN = Path("data/raw/fire_archive_SV-C2_764880.csv")
SALIDA = Path("report/evidencias")
SALIDA.mkdir(parents=True, exist_ok=True)


def validar_registro(fila):
    errores = []

    # Validar coordenadas
    try:
        lat = float(fila["latitude"])
        lon = float(fila["longitude"])

        if not (14 <= lat <= 33):
            errores.append("Latitud fuera de rango")

        if not (-119 <= lon <= -86):
            errores.append("Longitud fuera de rango")

    except (ValueError, TypeError, KeyError):
        errores.append("Coordenadas invalidas")

    # Validar FRP
    try:
        frp = float(fila["frp"])

        if not (0 <= frp < float("inf")):
            errores.append("FRP invalido")

    except (ValueError, TypeError, KeyError):
        errores.append("FRP no numerico")

    # Validar brillo
    try:
        brillo = float(fila["brightness"])

        if not (0 < brillo < float("inf")):
            errores.append("Brillo invalido")

    except (ValueError, TypeError, KeyError):
        errores.append("Brillo no numerico")

    # Validar fecha
    try:
        date.fromisoformat(fila["acq_date"])
    except (ValueError, TypeError, KeyError):
        errores.append("Fecha invalida")

    # Validar periodo
    if fila.get("daynight") not in ("D", "N"):
        errores.append("Periodo dia/noche invalido")

    # Validar confianza
    if fila.get("confidence") not in ("l", "n", "h"):
        errores.append("Confianza invalida")

    return errores


# Leer tres registros reales del dataset
with open(ORIGEN, encoding="utf-8", newline="") as archivo:
    lector = csv.DictReader(archivo)
    reales = [next(lector) for _ in range(3)]

casos = []

# Registros originales
for i, fila in enumerate(reales, start=1):
    casos.append((f"Real_{i}", fila))

# Crear registros invalidos intencionalmente
latitud_invalida = deepcopy(reales[0])
latitud_invalida["latitude"] = "99"
casos.append(("Latitud_invalida", latitud_invalida))

frp_invalido = deepcopy(reales[1])
frp_invalido["frp"] = "-10"
casos.append(("FRP_invalido", frp_invalido))

fecha_invalida = deepcopy(reales[2])
fecha_invalida["acq_date"] = "2026-99-99"
casos.append(("Fecha_invalida", fecha_invalida))

confianza_invalida = deepcopy(reales[0])
confianza_invalida["confidence"] = "X"
casos.append(("Confianza_invalida", confianza_invalida))


resultados = []

print("\nPRUEBA DE VALIDACION DE INGESTA")
print("--------------------------------")

for nombre, fila in casos:
    errores = validar_registro(fila)

    estado = "RECHAZADO" if errores else "ACEPTADO"

    resultados.append({
        "caso": nombre,
        "estado": estado,
        "errores": errores
    })

    print(f"{nombre}: {estado}")

    if errores:
        print(" Motivo:", ", ".join(errores))


aceptados = sum(
    r["estado"] == "ACEPTADO"
    for r in resultados
)

rechazados = sum(
    r["estado"] == "RECHAZADO"
    for r in resultados
)

print("--------------------------------")
print("Total de casos:", len(resultados))
print("Aceptados:", aceptados)
print("Rechazados:", rechazados)

ruta = SALIDA / "prueba_ingesta.json"

ruta.write_text(
    json.dumps(resultados, indent=4, ensure_ascii=False),
    encoding="utf-8"
)

print("Reporte guardado:", ruta)
