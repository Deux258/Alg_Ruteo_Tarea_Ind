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

Las tres rondas de la selección actual terminaron con **153/153 mediciones válidas**. Valparaíso, La Habana y Rusia tienen grafos definitivos públicos y recibos de comprobación anónima. Los 14 métodos cuentan con revisión gráfica en Wireshark y capturas de la sesión seleccionada; los dos casos de respuesta selectiva se corroboraron con repeticiones.

El análisis final es `resultados/analisis_20261027T151549_92fa68e2`. El informe se genera en LaTeX desde esa selección sellada: [fuentes y reproducción](informe/latex/README.md). El origen es WOM, 186.189.89.115, AS52341. Los destinos vigentes son 138.204.230.242 / 6652, 200.14.48.134 / 12734 y 37.79.226.46 / 3959, alternativas admitidas por el enunciado actualizado. Las sesiones anteriores permanecen como antecedentes y no se mezclan con estas 153 ejecuciones.

## Organización

- `config/`: campaña original y ajustes locales ignorados por Git.
- `path_discovery/`: CLI, adquisición, normalización, paquetes y entrega.
- `datos/originales/`: enunciado, preflight, mediciones y consultas ASN; nunca se sobrescriben después del sellado.
- `resultados/`: análisis regenerables, tablas, diagnósticos y exportaciones de paquetes.
- `grafos/`: constancias de publicación NDEx.
- `informe/`: proyecto LaTeX, PDF final y versiones históricas; `compose.latex.yaml` permite compilar sin red.
- `tests/`: fixtures sintéticos separados de los datos medidos.

Los originales y capturas quedan fuera de Git y se incluyen en la entrega local con `bundle`. No se publica automáticamente ningún cambio en Git.
