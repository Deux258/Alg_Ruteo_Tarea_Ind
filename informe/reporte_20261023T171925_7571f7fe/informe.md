# Informe de avance de Path Discovery

Generado en UTC: 2026-10-23T17:19:25.592777+00:00

Campaña principal: 0 de 153 combinaciones con evidencia válida. Pilotos válidos: 0.

La tarea sigue abierta hasta completar las mediciones, el análisis de paquetes y las tres publicaciones públicas.

El usuario confirmó que está conectado a la universidad. Las mediciones académicas están pendientes hasta conectarse a la banda ancha fija de casa; la sonda Docker fue detenida. El preflight inicial es diagnóstico de la red universitaria.

## Entorno y metodología

IPv4 pública observada: 152.230.71.234

Prefijo: 152.230.0.0/16. ASN: ['14259'].

ISP comercial: pendiente de confirmar por el usuario. NAT/CGNAT: posible NAT; CGNAT requiere comprobar la WAN del router.

Tres destinos y tres rondas. Scamper 20260902, seis métodos trace y cinco tracelb; RIPE UDP/ICMP/TCP en ambos sentidos.

Se conservan las IP del enunciado. Las referencias a cuatro IP y al punto 4 se interpretan como errores de edición; se requiere aclaración docente para sustituir sondas.

## Dependencias pendientes

Sonda 31416 no conectada: Abandoned

Sonda 870: IP actual 90.151.87.167 difiere de 37.79.153.66

Falta registrar y configurar local_probe_id

Falta validar udp_base_port desde piloto RIPE/PCAP

Falta RIPE_ATLAS_API_KEY en el entorno local

## 1 Path Discovery Scamper

Comparación prevista: IP únicas, cobertura de saltos, llegada al destino y estabilidad entre rondas. Las rutas incompletas se conservan.

Los pilotos y los intentos fallidos se identifican explícitamente y no se cuentan dentro de las 153 combinaciones.

El análisis más reciente contiene pilotos de diagnóstico. Sus métricas no acreditan resultados de la campaña principal ni corresponden a una BAF domiciliaria validada.

Análisis reproducible disponible en resultados/analisis_20261023T171909_df7994fd.

200.14.48.134 scamper trace udp ida: mediana IP únicas 16, cobertura 76.2%, rondas 1.

## 2 Path Discovery RIPE

Requiere sonda local registrada, créditos, API key y sondas remotas consistentes con el enunciado.

Las solicitudes conservarán los parámetros predeterminados salvo protocolo, extremos y puerto TCP 80. Los ASN por IP se consultarán en RIPEstat con fecha y respuesta original.

## 3 Path way RIPE

Se requieren nueve pares por ronda: tres destinos por tres protocolos. Cada par debe compartir IPv4 pública, ronda y protocolo.

Las tablas preservan TTL desde cada origen. Una diferencia entre IP de interfaces no prueba por sí sola que los routers sean diferentes.

La captura en el equipo local de una medición inversa es parcial; el resultado RIPE remoto es la evidencia del recorrido.

## 4 Public Path

Grafos públicos registrados: 0.

Cada grafo debe citar los dos IDs RIPE de su par de ida y vuelta. Se preservarán los huecos y los saltos ambiguos; no se crearán conexiones físicas no observadas.

## Análisis de transporte y payload

Las exportaciones TShark conservan encabezados, bytes completos, payloads y citas ICMP. Las reglas constantes e incrementales aprendidas en ronda 1 se contrastan con las rondas 2 y 3.

Los candidatos de respuesta selectiva requieren pruebas dirigidas y revisión de PCAP. La ausencia de una IP en un traceroute no demuestra una regla de firewall.

La correlación de resultados y capturas está implementada. El análisis completo de catorce métodos permanece pendiente hasta disponer de sus mediciones.

## Referencias

Enunciado original conservado con hash en datos/originales/enunciado/.

https://www.caida.org/catalog/software/scamper/

https://atlas.ripe.net/docs/

https://stat.ripe.net/docs/data-api/api-endpoints/network-info

https://www.ndexbio.org/rest/swagger/index.html
