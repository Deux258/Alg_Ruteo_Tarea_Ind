# Tarea individual de Path Discovery

Proyecto independiente para medir rutas de Internet desde banda ancha fija con Scamper 20260902, RIPE Atlas, TShark y NDEx.

La implementación incluye las 153 combinaciones de la campaña, originales con SHA-256, capturas PCAPNG, tablas por salto y ASN, comparación de métodos, grafos CX2, publicación NDEx e informe reproducible. Los resultados académicos se completan con las mediciones reales; el estado se consulta con `./main status`.

```bash
./main plan
./main preflight
./scripts/test.sh
```

Comenzar por [la guía operativa](docs/GUIA_OPERATIVA.md), [la matriz de cumplimiento](docs/MATRIZ_CUMPLIMIENTO.md) y [la consulta docente preparada](docs/CONSULTA_DOCENTE.md).

**Actualizado el 26 de octubre de 2026 (Santiago).** Sonda RIPE [1018487](https://atlas.ripe.net/probes/1018487/) conectada en WOM, IPv4 actual `186.189.89.115`, AS52341. Se reconfirmó la conexión de casa sin VPN. Las credenciales permanecen fuera de Git y de la entrega.

La sesión anterior (`186.189.107.115`) se interrumpió tras reiniciar el equipo. Se conservaron sus 60 resultados completos y el informe de avance como evidencia histórica, sin sumarlos a las nuevas 153 celdas. La campaña activa valida un nuevo piloto y ejecuta tres rondas con la IP vigente. Ver [estado y continuidad](docs/ESTADO_REANUDACION.md) e [incidentes](docs/INCIDENTES_CAMPANA.md).

El servicio finito `path-discovery-casa-20261026-204144.service` mantiene un bloqueo temporal de suspensión y procesa cada ronda. Consultar `./main status` y `systemctl --user status path-discovery-casa-20261026-204144.service`; el log es `resultados/casa_20261026T204144_f8fa5b43_supervisor.log`. No iniciar otra campaña mientras esté activo. Un reinicio o un cambio de IP detiene la ejecución y requiere revisar los intentos pendientes.

Las tres rondas terminaron con **153/153 mediciones principales válidas**; las pruebas adicionales concluyeron. La primera ronda terminó con 51/51 mediciones válidas. Se reprodujo sin red: 59 archivos de tablas, métricas y CX2 idénticos; 2405 archivos del paquete y 163 manifiestos originales verificados. El informe de avance vigente incorpora las dos rondas; las capturas nuevas se indexaron para la próxima regeneración. El servicio finalizó correctamente. Quedan pendientes las corroboraciones entre rondas y tres publicaciones públicas en NDEx.

El usuario autorizó sustituir 31416 por 6652 y actualizar la IP de 870. Se conserva la justificación en [Cambios de destinos](docs/CAMBIOS_DESTINOS.md). Las catorce capturas Wireshark anteriores pertenecen a la sesión histórica. Los 14 métodos nuevos ya tienen revisión gráfica sellada y capturas propias de sesión, más dos imágenes de las citas ICMP. Faltan tres publicaciones públicas en NDEx y el cierre del informe.

## Organización

- `config/`: campaña original y ajustes locales ignorados por Git.
- `path_discovery/`: CLI, adquisición, normalización, paquetes y entrega.
- `datos/originales/`: enunciado, preflight, mediciones y consultas ASN; nunca se sobrescriben después del sellado.
- `resultados/`: análisis regenerables, tablas, diagnósticos y exportaciones de paquetes.
- `grafos/`: constancias de publicación NDEx.
- `informe/`: informes Markdown y PDF cuando ReportLab está disponible.
- `tests/`: fixtures sintéticos separados de los datos medidos.

Los originales y capturas quedan fuera de Git y se incluyen en la entrega local con `bundle`. No se publica automáticamente ningún cambio en Git.
