# Diagnóstico TCP de la revisión

Las capturas PCAP históricas contienen respuestas ICMP correlacionadas con solicitudes TCP que no figuran como saltos aceptados en WARTS. La correlación está documentada en `resultados/correlacion_tcp_captura.json`; por sí sola no demuestra filtrado ni identifica la causa de la discrepancia.

El control adicional de `resultados/diagnostico_tcp_rxerr_revision.json` conserva los originales y distingue TCP y TCP-ACK normales de la opción experimental `-O ICMP-rxerr`. La línea base finalizó en GAPLIMIT con 10 sondas y sin IP aceptadas; con ICMP-rxerr Scamper informó «unhandled trace type for icmp-rxerr», `stop_reason=ERROR` y cero sondas. Estos últimos controles no son mediciones de ruta válidas. Los metadatos sellados originales se conservan sin modificar, aunque en ellos figuró inicialmente `completed`: se corrigió la validación para rechazar en adelante `stop_reason=ERROR`.

Para la campaña académica se mantienen los métodos y parámetros originales. Las respuestas ausentes se reportan como no observadas; no se reemplazan por las IP presentes únicamente en PCAP.
