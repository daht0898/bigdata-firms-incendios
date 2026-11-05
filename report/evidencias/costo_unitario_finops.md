# Costo unitario FinOps - Prototipo v0.2

## Mediciones
- Endpoint: `/api/clusters`
- Peticiones exitosas: 110
- Tiempo promedio medido: 1.076 ms
- Ambiente de medicion: Ubuntu local.

## Supuestos de infraestructura
- Proveedor de referencia: Google Cloud Run.
- Region de referencia: us-central1.
- CPU: 1 vCPU.
- Memoria: 512 MiB.
- Facturacion simplificada: minimo 100 ms por solicitud.
- Tarifa CPU: USD 2.4e-05 por vCPU-segundo.
- Tarifa RAM: USD 2.5e-06 por GiB-segundo.
- Tarifa por solicitud: USD 0.000000400.
- Tipo de cambio: 18.6285 MXN/USD.
- Nivel gratuito: no aplicado.

## Resultados
- Costo total estimado: USD 0.000321750.
- Costo unitario estimado: USD 0.000002925.
- Costo unitario estimado: MXN 0.00005449.
- Costo total estimado: MXN 0.005994.

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
