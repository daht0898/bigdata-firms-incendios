from fastapi.testclient import TestClient
from api.main import app

cliente = TestClient(app)


def test_api_funciona():
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json()["base_datos"] is True


def test_resumen_real():
    respuesta = cliente.get(
        "/api/summary",
        headers={"X-Client-ID": "cliente_test"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["total_incendios"] == 934712


def test_clusters():
    respuesta = cliente.get(
        "/api/clusters",
        headers={"X-Client-ID": "cliente_test"}
    )

    assert respuesta.status_code == 200

    clusters = respuesta.json()

    assert len(clusters) == 3
    assert sum(c["total_incendios"] for c in clusters) == 934712
