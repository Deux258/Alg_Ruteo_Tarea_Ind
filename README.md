# Tarea individual de Path Discovery

Proyecto independiente para medir rutas de Internet desde banda ancha fija con Scamper 20260902, RIPE Atlas, TShark y NDEx.

La implementación incluye las 153 combinaciones de la campaña, originales con SHA-256, capturas PCAPNG, tablas por salto y ASN, comparación de métodos, grafos CX2, publicación NDEx e informe reproducible. Los resultados académicos se completan con las mediciones reales; el estado se consulta con `./main status`.

```bash
./main plan
./main preflight
./scripts/test.sh
```

Comenzar por [la guía operativa](docs/GUIA_OPERATIVA.md), [la matriz de cumplimiento](docs/MATRIZ_CUMPLIMIENTO.md) y [la consulta docente preparada](docs/CONSULTA_DOCENTE.md).

**Actualizado el 26 de octubre de 2026 (Santiago).** Sonda RIPE [1018487](https://atlas.ripe.net/probes/1018487/) registrada y conectada desde casa en WOM. Se reclamaron 50.000 créditos iniciales y se guardó una API key local con permiso exclusivo para programar mediciones, válida hasta el 24 de noviembre. El valor no se incluye en Git ni en las capturas.

Los pilotos UDP ya tienen originales y capturas: RIPE [ida 227476785](https://atlas.ripe.net/measurements/227476785/results) llegó a Cuba; [vuelta 227477165](https://atlas.ripe.net/measurements/227477165/results) obtuvo una ruta incompleta. Scamper se repitió con la base UDP 33435. La campaña principal se inició tras aceptar la evidencia del piloto. El progreso vigente se obtiene con `./main status`; los pilotos no cuentan.

El usuario autorizó sustituir 31416 por 6652 y actualizar la IP de 870. Se conservan los originales y la justificación en [Cambios de destinos](docs/CAMBIOS_DESTINOS.md). La revisión técnica del piloto se realizó con TShark, sin declarar revisión gráfica. Ver [el estado y las evidencias](docs/ESTADO_REANUDACION.md).

La campaña dispone de un coordinador persistente con pausas de treinta minutos y procesamiento tras cada ronda. El PID vigente está en `.state/continuacion_recuperada.pid` y la salida en `resultados/continuacion_recuperada.log`; no iniciar otra campaña mientras siga activo. Los incidentes y las exclusiones de calidad están documentados en `docs/INCIDENTES_CAMPANA.md`.

Se revisaron los catorce métodos en Wireshark gráfico real, usando un contenedor Compose y PCAP montados en solo lectura. Las capturas, hashes y procedencia están en `capturas/indice.json` y `resultados/revision_wireshark_gui.json`. El informe `informe/path_discovery/informe.pdf` se mantiene como avance hasta completar las rondas, las corroboraciones y tres publicaciones públicas de NDEx.

## Organización

- `config/`: campaña original y ajustes locales ignorados por Git.
- `path_discovery/`: CLI, adquisición, normalización, paquetes y entrega.
- `datos/originales/`: enunciado, preflight, mediciones y consultas ASN; nunca se sobrescriben después del sellado.
- `resultados/`: análisis regenerables, tablas, diagnósticos y exportaciones de paquetes.
- `grafos/`: constancias de publicación NDEx.
- `informe/`: informes Markdown y PDF cuando ReportLab está disponible.
- `tests/`: fixtures sintéticos separados de los datos medidos.

Los originales y capturas quedan fuera de Git y se incluyen en la entrega local con `bundle`. No se publica automáticamente ningún cambio en Git.
