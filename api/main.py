from pathlib import Path
from datetime import datetime
import sqlite3
import time

from fastapi import FastAPI, Request, Query, HTTPException

# Ubicación de nuestra base de datos
RAIZ = Path(__file__).resolve().parents[1]
BD = RAIZ / "data" / "firms.sqlite3"

app = FastAPI(
    title="API Big Data - Incendios Forestales México",
    description="Consulta de resultados NASA FIRMS, PySpark y K-Means",
    version="0.2"
)


def consultar(sql, parametros=()):
    """Ejecuta una consulta y devuelve los registros."""
    with sqlite3.connect(BD) as conexion:
        conexion.row_factory = sqlite3.Row
        filas = conexion.execute(sql, parametros).fetchall()
        return [dict(fila) for fila in filas]


# Tabla para registrar el uso de la API
with sqlite3.connect(BD) as conexion:
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS uso_api (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cliente TEXT,
            endpoint TEXT,
            tiempo_ms REAL,
            cpu_ms REAL,
            proyecto TEXT,
            ambiente TEXT,
            componente TEXT,
            estado_http INTEGER,
            facturable INTEGER
        )
    """)


# Registrar peticiones y tiempos de procesamiento
@app.middleware("http")
async def registrar_uso(request: Request, call_next):
    inicio = time.perf_counter()
    inicio_cpu = time.process_time()

    respuesta = await call_next(request)

    tiempo_ms = (time.perf_counter() - inicio) * 1000
    cpu_ms = (time.process_time() - inicio_cpu) * 1000

    ruta = request.url.path

    if ruta.startswith("/api/"):
        cliente = request.headers.get("X-Client-ID", "cliente_demo")
        cliente = cliente[:64]

        rutas_facturables = {
            "/api/summary",
            "/api/years",
            "/api/clusters",
            "/api/points"
        }

        facturable = int(
            ruta in rutas_facturables
            and 200 <= respuesta.status_code < 300
        )

        with sqlite3.connect(BD) as conexion:
            conexion.execute("""
                INSERT INTO uso_api (
                    fecha, cliente, endpoint, tiempo_ms,
                    cpu_ms, proyecto, ambiente, componente,
                    estado_http, facturable
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().astimezone().isoformat(),
                cliente,
                ruta,
                round(tiempo_ms, 3),
                round(cpu_ms, 3),
                "BigData-FIRMS",
                "local",
                "FastAPI",
                respuesta.status_code,
                facturable
            ))

    respuesta.headers["X-Tiempo-API-ms"] = str(round(tiempo_ms, 3))
    return respuesta


@app.get("/health")
def health():
    return {
        "estado": "funcionando",
        "base_datos": BD.exists(),
        "version": "0.2"
    }


@app.get("/api/summary")
def obtener_resumen():
    datos = consultar("SELECT * FROM resumen LIMIT 1")

    if not datos:
        raise HTTPException(404, "No se encontró el resumen")

    return datos[0]


@app.get("/api/years")
def obtener_anios():
    return consultar("SELECT * FROM anios")


@app.get("/api/clusters")
def obtener_clusters():
    return consultar("SELECT * FROM clusters")


@app.get("/api/points")
def obtener_puntos(
    limit: int = Query(default=1000, ge=1, le=50000)
):
    return consultar(
        "SELECT * FROM puntos LIMIT ?",
        (limit,)
    )


@app.get("/api/usage")
def consultar_uso(cliente: str = "cliente_demo"):
    return consultar("""
        SELECT *
        FROM uso_api
        WHERE cliente = ?
        ORDER BY id DESC
        LIMIT 20
    """, (cliente,))


@app.get("/api/billing")
def generar_estado_cuenta(
    cliente: str = "cliente_demo",
    mes: str = None
):
    if mes is None:
        mes = datetime.now().astimezone().strftime("%Y-%m")

    resultados = consultar("""
        SELECT COUNT(*) AS consultas
        FROM uso_api
        WHERE cliente = ?
          AND substr(fecha, 1, 7) = ?
          AND facturable = 1
    """, (cliente, mes))

    total = resultados[0]["consultas"]

    tarifa_base = 7900
    incluidas = 100
    precio_extra = 10

    extras = max(0, total - incluidas)
    importe = tarifa_base + extras * precio_extra

    return {
        "cliente": cliente,
        "mes": mes,
        "consultas_realizadas": total,
        "consultas_incluidas": incluidas,
        "consultas_adicionales": extras,
        "tarifa_base_mxn": tarifa_base,
        "precio_consulta_extra_mxn": precio_extra,
        "total_mxn": importe,
        "tipo": "Estado de cuenta simulado"
    }
