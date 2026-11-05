from pathlib import Path
import pandas as pd
import math

# Archivo con nuestras 110 peticiones reales
ARCHIVO = Path("report/evidencias/finops_registros.csv")
SALIDA = Path("report/evidencias/costo_unitario_finops.md")

# Tarifas publicadas de Google Cloud Run
CPU_USD_SEG = 0.000024
RAM_USD_GIB_SEG = 0.0000025
SOLICITUD_USD = 0.40 / 1_000_000

# Configuracion de referencia
VCPU = 1
RAM_GIB = 0.5

# Tipo de cambio FIX de referencia
MXN_POR_USD = 18.6285

# Leer las mediciones existentes
datos = pd.read_csv(ARCHIVO)

datos = datos[
    (datos["estado_http"] == 200) &
    (datos["endpoint"] == "/api/clusters")
].copy()

if datos.empty:
    raise SystemExit("No hay peticiones validas.")

# Modelo simplificado:
# un bloque minimo de 100 ms facturables por solicitud
def segundos_facturables(ms):
    return max(1, math.ceil(ms / 100)) * 0.1

datos["segundos_facturables"] = datos["tiempo_ms"].apply(
    segundos_facturables
)

# Costo estimado por solicitud
datos["costo_usd"] = (
    datos["segundos_facturables"] * VCPU * CPU_USD_SEG
    + datos["segundos_facturables"] * RAM_GIB * RAM_USD_GIB_SEG
    + SOLICITUD_USD
)

total = len(datos)
costo_total_usd = datos["costo_usd"].sum()
costo_unitario_usd = costo_total_usd / total

costo_total_mxn = costo_total_usd * MXN_POR_USD
costo_unitario_mxn = costo_unitario_usd * MXN_POR_USD

print("\nCOSTO UNITARIO FINOPS - PROTOTIPO v0.2")
print("--------------------------------------")
print(f"Peticiones analizadas: {total}")
print(f"Tiempo API promedio: {datos['tiempo_ms'].mean():.3f} ms")
print(f"Costo total estimado: ${costo_total_usd:.9f} USD")
print(f"Costo unitario: ${costo_unitario_usd:.9f} USD")
print(f"Costo unitario: ${costo_unitario_mxn:.8f} MXN")
print(f"Costo de las {total} consultas: ${costo_total_mxn:.6f} MXN")
print("--------------------------------------")
print("Modelo: Google Cloud Run, us-central1")
print("Ambiente medido: Ubuntu local")
print("Resultado: ESTIMACION, no gasto real")

reporte = f"""# Costo unitario FinOps - Prototipo v0.2

## Mediciones
- Endpoint: `/api/clusters`
- Peticiones exitosas: {total}
- Tiempo promedio medido: {datos['tiempo_ms'].mean():.3f} ms
- Ambiente de medicion: Ubuntu local.

## Supuestos de infraestructura
- Proveedor de referencia: Google Cloud Run.
- Region de referencia: us-central1.
- CPU: 1 vCPU.
- Memoria: 512 MiB.
- Facturacion simplificada: minimo 100 ms por solicitud.
- Tarifa CPU: USD {CPU_USD_SEG} por vCPU-segundo.
- Tarifa RAM: USD {RAM_USD_GIB_SEG} por GiB-segundo.
- Tarifa por solicitud: USD {SOLICITUD_USD:.9f}.
- Tipo de cambio: {MXN_POR_USD} MXN/USD.
- Nivel gratuito: no aplicado.

## Resultados
- Costo total estimado: USD {costo_total_usd:.9f}.
- Costo unitario estimado: USD {costo_unitario_usd:.9f}.
- Costo unitario estimado: MXN {costo_unitario_mxn:.8f}.
- Costo total estimado: MXN {costo_total_mxn:.6f}.

## Limitaciones
Este resultado es una simulacion de costo de infraestructura
basada en mediciones locales.

No representa una factura real de Google Cloud.

El redondeo de 100 ms por solicitud es una simplificacion
conservadora; la facturacion real depende del tiempo
facturable de las instancias y de la concurrencia.

No incluye procesamiento PySpark, entrenamiento K-Means,
almacenamiento administrado, transferencias de red,
arranque de instancias ni costos operativos fijos.

No debe reemplazar directamente el costo total de
3 MXN por consulta del modelo financiero.

## Fuentes
Google Cloud Run:
https://cloud.google.com/run/pricing

Banco de Mexico:
https://www.banxico.org.mx/tipcamb/tipCamMIAction.do?idioma=sp
"""

SALIDA.write_text(reporte, encoding="utf-8")

print("\nReporte guardado en:", SALIDA)
