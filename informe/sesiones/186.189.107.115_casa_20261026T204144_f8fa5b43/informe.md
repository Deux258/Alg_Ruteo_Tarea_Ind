## Path Discovery: comparación de Scamper y RIPE Atlas

Tarea individual - Algoritmos de Ruteo. Fuente del enunciado: Tarea Individual.docx, conservada con hash. Fecha de elaboración en UTC: 2026-10-26T12:40:13.179926+00:00.

Estado de campaña al generar: 51/153; esta edición analiza 51 ejecuciones principales válidas; 5 pilotos conservados y separados; 0/3 grafos públicos registrados. El documento es de avance mientras queden evidencias pendientes.

## Entorno, adaptación de destinos y trazabilidad

Banda ancha fija domiciliaria en Quilicura, proveedor comercial WOM confirmado por el estudiante. IPv4 pública 186.189.107.115; prefijo 186.189.107.0/24; ASN AS52341. La salida se contrastó con dos servicios y se verificó antes y después de cada ejecución. Interfaz wlan0; sincronización horaria yes.

La presencia de 100.88.0.1 y direcciones privadas en el recorrido es compatible con NAT del operador. No se verificó la dirección WAN del router y no se confirma CGNAT. La falta de respuesta inversa no permite atribuir una causa por sí sola.

| Caso | IP del enunciado / sonda | IP activa / sonda |
| --- | --- | --- |
| Valparaíso | 138.204.228.2 / 31416 | 138.204.230.242 / 6652 |
| Habana | 200.14.48.134 / 12734 | 200.14.48.134 / 12734 |
| Rusia | 37.79.153.66 / 870 | 90.150.251.81 / 870 |

El estudiante autorizó reemplazar 31416, cuyo estado público es Abandoned desde 2025-12-14. Se eligió 6652, conectada y del mismo AS61506, con ubicación declarada en Valparaíso a aproximadamente 0,29 km de la original. Cambia el extremo y el prefijo; no se afirma que sean el mismo equipo o edificio. No se atribuye esta decisión al docente ni se interpreta la indisponibilidad como un fallo de RIPE o del ISP.

Para Rusia se autorizó actualizar la IPv4 de la misma sonda 870. La API se consulta antes de medir para evitar pares incoherentes. Los cambios están documentados en docs/CAMBIOS_DESTINOS.md y la configuración original permanece en config/campana_enunciado.json.

Se trabajan tres destinos, conforme a la tabla del enunciado. Las menciones a cuatro IP y al punto 4 como origen de los pares se interpretan como errores de edición. Las motivaciones sobre velocidad y censura no son hipótesis demostradas por estos traceroutes.

Revisión gráfica adicional de la campaña: 14 PCAP inspeccionados en Wireshark gráfico real, con capturas y procedencia en resultados/revision_wireshark_gui.json.

## Diseño de la campaña y controles

El diseño prevé tres rondas completas, separadas por al menos treinta minutos desde el cierre de la anterior. Cada ronda: 18 trace, 15 tracelb, 9 RIPE de ida y 9 de vuelta. Las duraciones informadas son tiempos de ejecución de pared, incluyendo espera y procesamiento; el envío remoto no se reconstruye desde una captura local inversa. Se ejecuta una sola medición local por vez; Scamper tiene límite global de 20 paquetes/s. TCP usa puerto 80; UDP usa base 33435. RIPE conserva los demás parámetros predeterminados y selecciona IDs exactos de sonda.

## Incidentes y límites temporales de la campaña

La ronda 1 comenzó el 26-10-2026 a las 01:30:20 UTC y sufrió dos interrupciones. La primera fue un error de acceso a un servicio externo antes de enviar una solicitud RIPE; se comprobó que no existía POST y se reanudó esa celda sin duplicarla. La segunda produjo un intervalo extendido durante la noche; no se establece su causa a partir de los registros disponibles.

El tracelb UDP-dport ruso scamper_20261026T024854_fb1d5630 abarcó desde las 02:48:54 hasta las 11:36:02 UTC. Se conserva íntegro y se excluye de la comparación por calidad temporal. El intento TCP-sport scamper_20261026T114443_ad95de92 perdió su controlador y solo dejó 70 bytes WARTS sin registro final; se conserva como intento interrumpido, no como medición válida. Se detuvo su captura residual antes de reanudar. Las decisiones, estados anterior y posterior y hashes están sellados en datos/originales/incidente_interrupcion_20261026T114921_f34fd3cb. Las dos celdas se repiten explícitamente; los otros resultados se conservan.

La ronda 1 no constituye una ventana continua. Las comparaciones que la incorporan deben mostrar sus horas reales y advertir que cambios entre métodos pueden reflejar cambios temporales. Las rondas siguientes se separan al menos treinta minutos desde el cierre efectivo anterior. No se reconstruyen tiempos ni se cambia la fecha de los originales para ocultar esta limitación.

En TCP se observaron respuestas ICMP en PCAP que no fueron incorporadas por Scamper a WARTS. Se contrastan por destino, direcciones, IPID, puertos y tiempo en resultados/correlacion_tcp_captura.json. Esta discrepancia de captura y detección impide atribuir automáticamente los ceros de Scamper a un firewall o a ausencia de respuesta en la red. Los resultados de la herramienta y las observaciones de paquetes se presentan por separado.

Scamper 20260902 se construyó con verificación SHA-256. Las herramientas y la sonda se gestionan con Docker Compose; la imagen de la sonda está fijada por digest, con red del host e identidad persistente. La sonda local es 1018487. Se habilitaron créditos y una API key de permiso limitado, almacenada fuera de Git y de la entrega.

La validación del piloto incluyó WARTS, JSON, PCAPNG, puertos, citas ICMP y correlación temporal. La inspección reproducible se realizó con TShark, componente de Wireshark; no se declaró revisión de su interfaz gráfica. Se conservan los intentos fallidos e inválidos y no cuentan como campaña.

Ronda 1: 51/51 ejecuciones válidas. Inicio observado: 2026-10-26T01:30:20.377856+00:00; cierre observado: 2026-10-26T12:12:04.404627+00:00.

Ronda 2: 0/51 ejecuciones válidas. Inicio observado: pendiente; cierre observado: pendiente.

Ronda 3: 0/51 ejecuciones válidas. Inicio observado: pendiente; cierre observado: pendiente.

La unidad normalizada es una respuesta por intento y TTL. Se preservan respuestas múltiples, errores y timeouts. Un TTL 255 separado de los anteriores se conserva como registro, sin inventar los TTL intermedios ni enlaces entre capas no consecutivas. Los ASN son asociaciones IP-prefijo obtenidas con RIPEstat y no una ruta BGP observada.

## 1. Path Discovery Scamper

## Valparaiso - 138.204.230.242

| Método | Rondas | Mediana IP únicas | Cobertura | Jaccard entre rondas | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| icmp | 1 | 9 | 100.0% | No contrastado | 9 | 4.0 | 1 |
| icmp-paris | 1 | 9 | 100.0% | No contrastado | 9 | 3.9 | 1 |
| udp | 1 | 9 | 100.0% | No contrastado | 9 | 4.3 | 1 |
| udp-paris | 1 | 9 | 100.0% | No contrastado | 10 | 4.5 | 1 |
| tcp | 1 | 0 | 0.0% | No contrastado | 10 | 53.4 | 0 |
| tcp-ack | 1 | 0 | 0.0% | No contrastado | 10 | 53.8 | 0 |

Métodos con mayor información según mediana de IP únicas, cobertura y estabilidad: icmp, icmp-paris, udp, udp-paris. Empate en estos criterios. Selección provisional: faltan rondas. La ausencia de llegada se conserva y no invalida automáticamente una medición.

Tabla tipo 1, ronda 1. Las rondas 2 y 3 y todos los intentos están en los anexos CSV de este análisis. Se conserva más de una IP por TTL cuando corresponde.

| HOP | udp | icmp | udp-paris | icmp-paris | tcp | tcp-ack |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | ? not_recorded | ? not_recorded |
| 2 | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | ? not_recorded | ? not_recorded |
| 3 | 10.87.0.3 [non_global] | 10.87.0.2 [non_global] | 10.87.0.3 [non_global] | 10.87.0.2 [non_global] | ? not_recorded | ? not_recorded |
| 4 | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | ? not_recorded | ? not_recorded |
| 5 | 45.68.16.129 [unknown] | 45.68.16.129 [unknown] | 10.87.0.46 [non_global] | 45.68.16.129 [unknown] | ? not_recorded | ? not_recorded |
| 6 | 10.100.154.1 [non_global] | 10.100.154.1 [non_global] | 45.68.16.129 [unknown] | 10.100.154.1 [non_global] | NO_MEDIDO | NO_MEDIDO |
| 7 | 138.204.228.164 [AS61506] | 138.204.228.164 [AS61506] | 10.100.154.1 [non_global] | 138.204.228.164 [AS61506] | NO_MEDIDO | NO_MEDIDO |
| 8 | 138.204.228.162 [AS61506] | 138.204.228.162 [AS61506] | 138.204.228.164 [AS61506] | 138.204.228.162 [AS61506] | NO_MEDIDO | NO_MEDIDO |
| 9 | 138.204.230.242 [AS61506] | 138.204.230.242 [AS61506] | 138.204.228.162 [AS61506] | 138.204.230.242 [AS61506] | NO_MEDIDO | NO_MEDIDO |
| 10 | NO_MEDIDO | NO_MEDIDO | 138.204.230.242 [AS61506] | NO_MEDIDO | NO_MEDIDO | NO_MEDIDO |

| tracelb | Ronda | IP adicionales frente a unión de 6 trace | Sondas tracelb | Sondas de referencia |
| --- | --- | --- | --- | --- |
| udp-dport | 1 | Ninguna | 98 | 57 |
| icmp-echo | 1 | Ninguna | 44 | 57 |
| udp-sport | 1 | Ninguna | 38 | 57 |
| tcp-sport | 1 | Ninguna | 38 | 57 |
| tcp-ack-sport | 1 | Ninguna | 27 | 57 |

Las IP adicionales se comparan contra la unión de los seis trace de la misma ronda. Más IP con más paquetes se interpreta como una relación entre cobertura y costo, sin atribuir superioridad independiente del presupuesto de sondas.

## Habana - 200.14.48.134

| Método | Rondas | Mediana IP únicas | Cobertura | Jaccard entre rondas | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| icmp | 1 | 14 | 77.8% | No contrastado | 22 | 46.4 | 1 |
| udp-paris | 1 | 14 | 76.2% | No contrastado | 27 | 64.2 | 1 |
| icmp-paris | 1 | 13 | 72.2% | No contrastado | 23 | 56.9 | 1 |
| udp | 1 | 9 | 76.9% | No contrastado | 17 | 40.4 | 0 |
| tcp | 1 | 0 | 0.0% | No contrastado | 10 | 54.6 | 0 |
| tcp-ack | 1 | 0 | 0.0% | No contrastado | 10 | 54.7 | 0 |

Métodos con mayor información según mediana de IP únicas, cobertura y estabilidad: icmp. Selección provisional: faltan rondas. La ausencia de llegada se conserva y no invalida automáticamente una medición.

Tabla tipo 1, ronda 1. Las rondas 2 y 3 y todos los intentos están en los anexos CSV de este análisis. Se conserva más de una IP por TTL cuando corresponde.

| HOP | udp | icmp | udp-paris | icmp-paris | tcp | tcp-ack |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | ? not_recorded | ? not_recorded |
| 2 | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | ? not_recorded | ? not_recorded |
| 3 | 10.87.0.3 [non_global] | 10.87.0.2 [non_global] | 10.87.0.3 [non_global] | 10.87.0.2 [non_global] | ? not_recorded | ? not_recorded |
| 4 | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | ? not_recorded | ? not_recorded |
| 5 | ? not_recorded | ? not_recorded | 10.87.0.46 [non_global] | ? not_recorded | ? not_recorded | ? not_recorded |
| 6 | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] | ? not_recorded | 154.54.92.41 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 7 | ? not_recorded | 154.54.29.157 [AS174] | 154.54.92.41 [AS174] | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 8 | 154.54.167.185 [AS174] | 154.54.167.185 [AS174] | 154.54.3.29 [AS174] | 154.54.167.185 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 9 | 38.104.94.178 [AS174] | 38.104.94.178 [AS174] | 154.54.168.85 [AS174] | 38.104.94.178 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 10 | ? not_recorded | ? not_recorded | 38.88.57.26 [AS174] | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 11 | 190.242.168.37 [AS23520] | 190.242.168.39 [AS23520] | ? not_recorded | 190.242.168.39 [AS23520] | NO_MEDIDO | NO_MEDIDO |
| 12 | 200.0.16.16 [AS11960] | 200.0.16.16 [AS11960] | ? not_recorded | 200.0.16.16 [AS11960] | NO_MEDIDO | NO_MEDIDO |
| 13 | 190.242.168.37 [AS23520] | 200.0.16.21 [AS11960] | ? not_recorded | 200.0.16.21 [AS11960] | NO_MEDIDO | NO_MEDIDO |
| 14 | NO_MEDIDO | 200.0.16.29 [AS11960] | 190.242.168.39 [AS23520] | 200.0.16.29 [AS11960] | NO_MEDIDO | NO_MEDIDO |
| 15 | NO_MEDIDO | ? not_recorded | 200.0.16.16 [AS11960] | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 16 | NO_MEDIDO | ? not_recorded | 200.0.16.21 [AS11960] | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 17 | NO_MEDIDO | 200.14.48.178 [AS27725] | 200.0.16.29 [AS11960] | 200.14.48.178 [AS27725] | NO_MEDIDO | NO_MEDIDO |
| 18 | NO_MEDIDO | 200.14.48.134 [AS27725] | 200.0.16.29 [AS11960] | 200.14.48.134 [AS27725] | NO_MEDIDO | NO_MEDIDO |
| 19 | NO_MEDIDO | NO_MEDIDO | ? not_recorded | NO_MEDIDO | NO_MEDIDO | NO_MEDIDO |
| 20 | NO_MEDIDO | NO_MEDIDO | 200.14.48.178 [AS27725] | NO_MEDIDO | NO_MEDIDO | NO_MEDIDO |
| 21 | NO_MEDIDO | NO_MEDIDO | 200.14.48.134 [AS27725] | NO_MEDIDO | NO_MEDIDO | NO_MEDIDO |

| tracelb | Ronda | IP adicionales frente a unión de 6 trace | Sondas tracelb | Sondas de referencia |
| --- | --- | --- | --- | --- |
| udp-dport | 1 | 69.79.104.1 | 230 | 109 |
| icmp-echo | 1 | Ninguna | 101 | 109 |
| udp-sport | 1 | Ninguna | 38 | 109 |
| tcp-sport | 1 | Ninguna | 38 | 109 |
| tcp-ack-sport | 1 | Ninguna | 27 | 109 |

Las IP adicionales se comparan contra la unión de los seis trace de la misma ronda. Más IP con más paquetes se interpreta como una relación entre cobertura y costo, sin atribuir superioridad independiente del presupuesto de sondas.

## Rusia - 90.150.251.81

| Método | Rondas | Mediana IP únicas | Cobertura | Jaccard entre rondas | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| icmp | 1 | 10 | 62.5% | No contrastado | 22 | 69.2 | 0 |
| udp | 1 | 10 | 62.5% | No contrastado | 22 | 68.1 | 0 |
| icmp-paris | 1 | 9 | 56.2% | No contrastado | 23 | 76.2 | 0 |
| udp-paris | 1 | 9 | 56.2% | No contrastado | 23 | 76.8 | 0 |
| tcp | 1 | 0 | 0.0% | No contrastado | 10 | 54.4 | 0 |
| tcp-ack | 1 | 0 | 0.0% | No contrastado | 10 | 55.0 | 0 |

Métodos con mayor información según mediana de IP únicas, cobertura y estabilidad: icmp, udp. Empate en estos criterios. Selección provisional: faltan rondas. La ausencia de llegada se conserva y no invalida automáticamente una medición.

Tabla tipo 1, ronda 1. Las rondas 2 y 3 y todos los intentos están en los anexos CSV de este análisis. Se conserva más de una IP por TTL cuando corresponde.

| HOP | udp | icmp | udp-paris | icmp-paris | tcp | tcp-ack |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | ? not_recorded | ? not_recorded |
| 2 | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | ? not_recorded | ? not_recorded |
| 3 | 10.87.0.3 [non_global] | 10.87.0.3 [non_global] | 10.87.0.3 [non_global] | 10.87.0.3 [non_global] | ? not_recorded | ? not_recorded |
| 4 | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | ? not_recorded | ? not_recorded |
| 5 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded |
| 6 | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 7 | 154.54.29.157 [AS174] | 154.54.29.157 [AS174] | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 8 | 154.54.168.85 [AS174] | 154.54.167.185 [AS174] | 154.54.167.185 [AS174] | 154.54.167.185 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 9 | 154.54.10.210 [AS174] | 154.54.10.210 [AS174] | 154.54.10.210 [AS174] | 154.54.10.210 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 10 | 195.22.211.209 [AS6762] | 195.22.211.61 [AS6762] | 195.22.211.209 [AS6762] | 195.22.211.61 [AS6762] | NO_MEDIDO | NO_MEDIDO |
| 11 | 195.22.214.161 [AS6762] | 195.22.214.161 [AS6762] | 195.22.214.161 [AS6762] | 195.22.214.161 [AS6762] | NO_MEDIDO | NO_MEDIDO |
| 12 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 13 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 14 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 15 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 16 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |

| tracelb | Ronda | IP adicionales frente a unión de 6 trace | Sondas tracelb | Sondas de referencia |
| --- | --- | --- | --- | --- |
| icmp-echo | 1 | Ninguna | 112 | 110 |
| udp-sport | 1 | Ninguna | 38 | 110 |
| udp-dport | 1 | 154.54.3.29 | 182 | 110 |
| tcp-sport | 1 | Ninguna | 38 | 110 |
| tcp-ack-sport | 1 | 90.150.251.81 | 27 | 110 |

Las IP adicionales se comparan contra la unión de los seis trace de la misma ronda. Más IP con más paquetes se interpreta como una relación entre cobertura y costo, sin atribuir superioridad independiente del presupuesto de sondas.

## 2. Path Discovery RIPE

La definición efectiva, la solicitud, el ID, la sonda participante y los tiempos reales se conservan para cada medición. La aceptación de una solicitud no se contó como ejecución: se esperó un resultado con el ID y sonda correctos. Las capturas locales de ida permiten contar solicitudes; las de vuelta son parciales y no permiten reconstruir todo el tráfico remoto.

## Valparaiso - protocolos RIPE de ida

| Protocolo | Rondas | Mediana IP únicas | Cobertura | Jaccard | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ICMP | 1 | 9 | 100.0% | No contrastado | 27 | 9.8 | 1 |
| TCP | 1 | 9 | 100.0% | No contrastado | 27 | 9.9 | 1 |
| UDP | 1 | 9 | 100.0% | No contrastado | 27 | 9.4 | 1 |

Protocolos con mayor información en la comparación disponible: ICMP, TCP, UDP. Empate en estos criterios. Resultado provisional.

| HOP | UDP | ICMP | TCP |
| --- | --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] |
| 2 | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] |
| 3 | 10.87.0.3 [non_global] | 10.87.0.2 [non_global] | 10.87.0.3 [non_global] |
| 4 | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] |
| 5 | 45.68.16.129 [unknown] | 45.68.16.129 [unknown] | 45.68.16.129 [unknown] |
| 6 | 10.100.154.1 [non_global] | 10.100.154.1 [non_global] | 10.100.154.1 [non_global] |
| 7 | 138.204.228.164 [AS61506] | 138.204.228.164 [AS61506] | 138.204.228.164 [AS61506] |
| 8 | 138.204.228.162 [AS61506] | 138.204.228.162 [AS61506] | 138.204.228.162 [AS61506] |
| 9 | 138.204.230.242 [AS61506] | 138.204.230.242 [AS61506] | 138.204.230.242 [AS61506] |

## Habana - protocolos RIPE de ida

| Protocolo | Rondas | Mediana IP únicas | Cobertura | Jaccard | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TCP | 1 | 15 | 75.0% | No contrastado | 60 | 78.8 | 1 |
| ICMP | 1 | 14 | 77.8% | No contrastado | 54 | 65.6 | 1 |
| UDP | 1 | 14 | 73.7% | No contrastado | 57 | 133.4 | 1 |

Protocolos con mayor información en la comparación disponible: TCP. Resultado provisional.

| HOP | UDP | ICMP | TCP |
| --- | --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] |
| 2 | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] |
| 3 | 10.87.0.3 [non_global] | 10.87.0.2 [non_global] | 10.87.0.3 [non_global] |
| 4 | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] |
| 5 | * | * | * |
| 6 | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] |
| 7 | *; 154.54.3.29 [AS174] | *; 154.54.29.157 [AS174] | 154.54.29.157 [AS174] |
| 8 | 154.54.168.85 [AS174] | 154.54.167.185 [AS174] | 154.54.167.185 [AS174] |
| 9 | 38.104.94.178 [AS174] | 38.104.94.178 [AS174] | 38.88.57.26 [AS174] |
| 10 | * | * | * |
| 11 | 190.242.168.39 [AS23520] | 190.242.168.39 [AS23520] | 69.79.104.1 [AS23520] |
| 12 | 200.0.16.16 [AS11960] | 200.0.16.16 [AS11960] | * |
| 13 | 200.0.16.21 [AS11960] | 200.0.16.21 [AS11960] | 190.242.168.39 [AS23520] |
| 14 | 200.0.16.25 [AS11960] | 200.0.16.29 [AS11960] | 200.0.16.16 [AS11960] |
| 15 | * | * | 200.0.16.21 [AS11960] |
| 16 | * | * | 200.0.16.29 [AS11960] |
| 17 | * | 200.14.48.178 [AS27725] | * |
| 18 | 200.14.48.178 [AS27725] | 200.14.48.134 [AS27725] | * |
| 19 | 200.14.48.134 [AS27725] | NO_MEDIDO | 200.14.48.178 [AS27725] |
| 20 | NO_MEDIDO | NO_MEDIDO | *; 200.14.48.134 [AS27725] |

## Rusia - protocolos RIPE de ida

| Protocolo | Rondas | Mediana IP únicas | Cobertura | Jaccard | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UDP | 1 | 10 | 61.1% | No contrastado | 54 | 142.8 | 0 |
| ICMP | 1 | 10 | 58.8% | No contrastado | 51 | 106.4 | 0 |
| TCP | 1 | 9 | 56.2% | No contrastado | 48 | 96.1 | 0 |

Protocolos con mayor información en la comparación disponible: UDP. Resultado provisional.

| HOP | UDP | ICMP | TCP |
| --- | --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] |
| 2 | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] |
| 3 | 10.87.0.3 [non_global] | 10.87.0.3 [non_global] | 10.87.0.3 [non_global] |
| 4 | 10.87.0.3 [non_global]; 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] |
| 5 | 10.87.0.46 [non_global] | * | * |
| 6 | * | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] |
| 7 | 154.54.92.41 [AS174] | *; 154.54.29.157 [AS174] | 154.54.29.157 [AS174] |
| 8 | 154.54.29.157 [AS174] | 154.54.167.185 [AS174] | 154.54.167.185 [AS174] |
| 9 | 154.54.167.185 [AS174] | 154.54.10.210 [AS174] | 154.54.10.210 [AS174] |
| 10 | 154.54.10.210 [AS174] | 195.22.211.61 [AS6762] | 195.22.211.61 [AS6762] |
| 11 | *; 195.22.211.61 [AS6762] | *; 195.22.214.161 [AS6762] | * |
| 12 | *; 195.22.214.161 [AS6762] | * | * |
| 13 | * | * | * |
| 14 | * | * | * |
| 15 | * | * | * |
| 16 | * | * | NO_MEDIDO |
| 17 | * | NO_MEDIDO | NO_MEDIDO |
| 255 | * | * | * |

## Transporte, payload y respuesta selectiva

Se inspeccionan seis métodos trace, cinco tracelb y tres protocolos RIPE. Las fichas conservan TTL, tamaño, IPID, protocolo, puertos, flags TCP, secuencia/ACK, campos ICMP, checksums, payload hexadecimal y encabezados originales citados. Los campos no presentes en un protocolo se consideran no aplicables.

## ripe / traceroute / ICMP

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 90; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Incremento 1 cada 3 sondas; base propia de cada ejecución; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Variable; rango observado 13806 a 14027; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 76; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 1; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 58487 a 60756; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| icmp.type | Constante: 8; n=27 | Pendiente: aún no hay otra ronda contrastada |
| icmp.code | Constante: 0; n=27 | Pendiente: aún no hay otra ronda contrastada |
| icmp.ident | Constante: 36864; n=27 | Pendiente: aún no hay otra ronda contrastada |
| icmp.seq | Incremento 1 por sonda; base propia de cada ejecución; n=27 | Pendiente: aún no hay otra ronda contrastada |
| icmp.checksum | Constante: 0x0001; n=27 | Pendiente: aún no hay otra ronda contrastada |
| data.data | Variable; longitudes observadas [48] bytes; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [48] bytes. Bytes iniciales: d4dc687474703a2f2f61746c61732e726970652e6e65742041746c617320736179732048692100000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Segmento ASCII constante desde offset 2: http://atlas.ripe.net Atlas says Hi!

Restricción observada: la suma de payload_word0_BE, icmp.checksum, icmp.ident, icmp.seq módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## ripe / traceroute / TCP

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 102; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Incremento 1 cada 3 sondas; base propia de cada ejecución; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Variable; rango observado 52408 a 52700; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 88; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 6; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 19797 a 22137; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| tcp.srcport | Constante: 20480; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.dstport | Constante: 80; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.flags | Constante: 0x0002; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.seq_raw | Incremento 1 por sonda; base propia de cada ejecución; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.ack_raw | Constante: 0; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.len | Constante: 48; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.checksum | Incremento -1 por sonda; base propia de cada ejecución; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.payload | Constante: 687474703a2f2f61746c61732e726970652e6e65742041746c6173207361797320486921000000000000000000000000; n=27 | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [48] bytes. Bytes iniciales: 687474703a2f2f61746c61732e726970652e6e65742041746c6173207361797320486921000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [].

Segmento ASCII constante desde offset 0: http://atlas.ripe.net Atlas says Hi!

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## ripe / traceroute / UDP

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 90; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Incremento 1 cada 3 sondas; base propia de cada ejecución; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Variable; rango observado 57690 a 57939; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 76; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 17; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 14559 a 16856; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| udp.srcport | Constante: 20480; n=27 | Pendiente: aún no hay otra ronda contrastada |
| udp.dstport | Constante: 33435; n=27 | Pendiente: aún no hay otra ronda contrastada |
| udp.length | Constante: 56; n=27 | Pendiente: aún no hay otra ronda contrastada |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=27 | Pendiente: aún no hay otra ronda contrastada |
| udp.payload | Variable; longitudes observadas [48] bytes; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| data.data | Variable; longitudes observadas [48] bytes; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [48] bytes. Bytes iniciales: 0352687474703a2f2f61746c61732e726970652e6e65742041746c617320736179732048692100000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Segmento ASCII constante desde offset 2: http://atlas.ripe.net Atlas says Hi!

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / icmp

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 44; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 1; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Incremento -257 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| icmp.type | Constante: 8; n=9 | Pendiente: aún no hay otra ronda contrastada |
| icmp.code | Constante: 0; n=9 | Pendiente: aún no hay otra ronda contrastada |
| icmp.ident | Constante: 32769; n=9 | Pendiente: aún no hay otra ronda contrastada |
| icmp.seq | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| icmp.checksum | Incremento -1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| data.data | Constante: 00000000000000000000000000000000; n=9 | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [16] bytes. Bytes iniciales: 00000000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [].

Restricción observada: la suma de payload_word0_BE, icmp.checksum, icmp.ident, icmp.seq módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / icmp-paris

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 44; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 1; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Incremento -257 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| icmp.type | Constante: 8; n=9 | Pendiente: aún no hay otra ronda contrastada |
| icmp.code | Constante: 0; n=9 | Pendiente: aún no hay otra ronda contrastada |
| icmp.ident | Constante: 32769; n=9 | Pendiente: aún no hay otra ronda contrastada |
| icmp.seq | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| icmp.checksum | Constante: 0x8001; n=9 | Pendiente: aún no hay otra ronda contrastada |
| data.data | Variable; longitudes observadas [16] bytes; n=9. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [16] bytes. Bytes iniciales: f7fc0000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, icmp.checksum, icmp.ident, icmp.seq módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / tcp

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 54; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Incremento 1 cada 2 sondas; base propia de cada ejecución; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 40; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 6; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 57175 a 58208; n=10. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| tcp.srcport | Constante: 32769; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.dstport | Constante: 80; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.flags | Constante: 0x0002; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.seq_raw | Constante: 0; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.ack_raw | Constante: 0; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.len | Constante: 0; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.checksum | Constante: 0x9922; n=10 | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [0] bytes. Sin payload de aplicación en estas sondas.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / tcp-ack

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 54; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Incremento 1 cada 2 sondas; base propia de cada ejecución; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 40; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 6; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 57175 a 58208; n=10. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| tcp.srcport | Constante: 32769; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.dstport | Constante: 80; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.flags | Constante: 0x0010; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.seq_raw | Constante: 0; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.ack_raw | Constante: 0; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.len | Constante: 0; n=10 | Pendiente: aún no hay otra ronda contrastada |
| tcp.checksum | Constante: 0x9914; n=10 | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [0] bytes. Sin payload de aplicación en estas sondas.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / udp

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 44; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 17; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Incremento -257 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| udp.srcport | Constante: 32769; n=9 | Pendiente: aún no hay otra ronda contrastada |
| udp.dstport | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| udp.length | Constante: 24; n=9 | Pendiente: aún no hay otra ronda contrastada |
| udp.checksum | Incremento -1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| udp.payload | Constante: 00000000000000000000000000000000; n=9 | Pendiente: aún no hay otra ronda contrastada |
| data.data | Constante: 00000000000000000000000000000000; n=9 | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [16] bytes. Bytes iniciales: 00000000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [].

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / udp-paris

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Incremento 1 por sonda; base propia de cada ejecución; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 44; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 17; n=10 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Incremento -257 por sonda; base propia de cada ejecución; n=10 | Pendiente: aún no hay otra ronda contrastada |
| udp.srcport | Constante: 32769; n=10 | Pendiente: aún no hay otra ronda contrastada |
| udp.dstport | Constante: 33435; n=10 | Pendiente: aún no hay otra ronda contrastada |
| udp.length | Constante: 24; n=10 | Pendiente: aún no hay otra ronda contrastada |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=10 | Pendiente: aún no hay otra ronda contrastada |
| udp.payload | Variable; longitudes observadas [16] bytes; n=10. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| data.data | Variable; longitudes observadas [16] bytes; n=10. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [16] bytes. Bytes iniciales: 66b10000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / icmp-echo

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=44 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=44 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=44 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Variable; rango observado 1 a 9; n=44. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Constante: 0x0000; n=44 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 44; n=44 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 1; n=44 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 56162 a 58210; n=44. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| icmp.type | Constante: 8; n=44 | Pendiente: aún no hay otra ronda contrastada |
| icmp.code | Constante: 0; n=44 | Pendiente: aún no hay otra ronda contrastada |
| icmp.ident | Constante: 32769; n=44 | Pendiente: aún no hay otra ronda contrastada |
| icmp.seq | Incremento 1 por sonda; base propia de cada ejecución; n=44 | Pendiente: aún no hay otra ronda contrastada |
| icmp.checksum | Variable; rango observado 1 a 6; n=44. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| data.data | Variable; longitudes observadas [16] bytes; n=44. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [16] bytes. Bytes iniciales: 77fd0000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, icmp.checksum, icmp.ident, icmp.seq módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / tcp-ack-sport

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 54; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Variable; rango observado 1 a 4; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 40; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 6; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 57414 a 58208; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| tcp.srcport | Variable; rango observado 32769 a 32774; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| tcp.dstport | Constante: 80; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.flags | Constante: 0x0010; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.seq_raw | Constante: 0; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.ack_raw | Constante: 0; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.len | Constante: 0; n=27 | Pendiente: aún no hay otra ronda contrastada |
| tcp.checksum | Variable; rango observado 39183 a 39188; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [0] bytes. Sin payload de aplicación en estas sondas.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / tcp-sport

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 54; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Variable; rango observado 1 a 4; n=38. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 40; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 6; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 57403 a 58208; n=38. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| tcp.srcport | Variable; rango observado 32769 a 32774; n=38. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| tcp.dstport | Constante: 80; n=38 | Pendiente: aún no hay otra ronda contrastada |
| tcp.flags | Constante: 0x0002; n=38 | Pendiente: aún no hay otra ronda contrastada |
| tcp.seq_raw | Constante: 0; n=38 | Pendiente: aún no hay otra ronda contrastada |
| tcp.ack_raw | Constante: 0; n=38 | Pendiente: aún no hay otra ronda contrastada |
| tcp.len | Constante: 0; n=38 | Pendiente: aún no hay otra ronda contrastada |
| tcp.checksum | Variable; rango observado 39197 a 39202; n=38. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [0] bytes. Sin payload de aplicación en estas sondas.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / udp-dport

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=98 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=98 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=98 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Variable; rango observado 1 a 9; n=98. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=98 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 44; n=98 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 17; n=98 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 56048 a 58193; n=98. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| udp.srcport | Constante: 32769; n=98 | Pendiente: aún no hay otra ronda contrastada |
| udp.dstport | Variable; rango observado 33435 a 33461; n=98. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| udp.length | Constante: 24; n=98 | Pendiente: aún no hay otra ronda contrastada |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=98 | Pendiente: aún no hay otra ronda contrastada |
| udp.payload | Variable; longitudes observadas [16] bytes; n=98. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| data.data | Variable; longitudes observadas [16] bytes; n=98. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [16] bytes. Bytes iniciales: 66b10000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / udp-sport

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Variable; rango observado 1 a 4; n=38. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 44; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 17; n=38 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 57388 a 58193; n=38. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| udp.srcport | Variable; rango observado 32769 a 32774; n=38. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| udp.dstport | Constante: 33435; n=38 | Pendiente: aún no hay otra ronda contrastada |
| udp.length | Constante: 24; n=38 | Pendiente: aún no hay otra ronda contrastada |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=38 | Pendiente: aún no hay otra ronda contrastada |
| udp.payload | Variable; longitudes observadas [16] bytes; n=38. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| data.data | Variable; longitudes observadas [16] bytes; n=38. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [16] bytes. Bytes iniciales: 66b10000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

Control de recepción TCP: {"reviewed_scamper_tcp_runs": 12, "runs_with_matching_icmp_quotes": 12, "runs_with_pcap_warts_discrepancy": 12, "interpretation": "Correlación estricta por direcciones, IPID, puertos y orden temporal. Presencia en PCAP no implica aceptación por Scamper. Causa de la diferencia no establecida; no demuestra bloqueo TCP de los routers."}. Las respuestas presentes en PCAP y ausentes en WARTS se informan por separado; no prueban filtrado de red. Detalle reproducible en resultados/correlacion_tcp_captura.json.

Candidatos de respuesta selectiva detectados: 346. La ausencia de una IP en un método no demuestra una regla de firewall: puede deberse a carga, balanceo, pérdida o rutas diferentes. Se requiere corroboración entre rondas y pruebas dirigidas acotadas para cada herramienta.

Pruebas dirigidas de respuesta selectiva pendientes. Este requisito no se da por cerrado por la mera lista de candidatos.

## Control adicional de recepción TCP

Prueba fuera de las 153 celdas. Se compara el envío predeterminado y la opción oficial rawtcp, conservando o cambiando explícitamente el puerto de origen. Los resultados principales mantienen sus parámetros originales.

| rawtcp | Puerto origen | IP únicas | Sondas | Parada | Run |
| --- | --- | --- | --- | --- | --- |
| False | 32769 | 0 | 10 | GAPLIMIT | scamper_20261026T121333_d9eba637 |
| True | 32769 | 0 | 10 | GAPLIMIT | scamper_20261026T121430_512d36cb |
| True | 20480 | 0 | 10 | GAPLIMIT | scamper_20261026T121527_6f5fa7b5 |

Diagnóstico adicional; excluido de la comparación principal y del entrenamiento de patrones. Una diferencia no identifica por sí sola la regla de firewall o causa local.

## 3. Path way RIPE: ida y vuelta

Cada comparación conserva la numeración desde cada origen y también compara el orden inverso de la vuelta. Las IP corresponden a interfaces observadas; direcciones distintas no demuestran routers distintos ni se asume alias entre interfaces. Las secuencias AS tampoco prueban una ruta BGP.

## Valparaiso - comparación de sentidos

| Protocolo | Ronda | IDs ida / vuelta | IP únicas ida / vuelta | Jaccard IP intermedias | Observación incompleta |
| --- | --- | --- | --- | --- | --- |
| UDP | 1 | 227487299 / 227487390 | 9 / 7 | 0.071 | True |
| ICMP | 1 | 227487554 / 227487571 | 9 / 7 | 0.077 | False |
| TCP | 1 | 227487577 / 227487604 | 9 / 6 | 0.077 | True |

Tabla tipo 2: UDP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 138.204.230.193 [AS61506] |
| 2 | 100.88.0.1 [non_global] | 138.204.228.164 [AS61506] |
| 3 | 10.87.0.3 [non_global] | 10.100.163.1 [non_global] |
| 4 | 10.87.0.46 [non_global] | 10.100.154.2 [non_global] |
| 5 | 45.68.16.129 [unknown] | 45.68.16.231 [unknown] |
| 6 | 10.100.154.1 [non_global] | 192.168.113.5 [non_global] |
| 7 | 138.204.228.164 [AS61506] | * |
| 8 | 138.204.228.162 [AS61506] | * |
| 9 | 138.204.230.242 [AS61506] | * |
| 10 | NO_MEDIDO | *; 138.204.228.163 [AS61506]; 138.204.230.193 [AS61506] |
| 11 | NO_MEDIDO | * |
| 255 | NO_MEDIDO | * |

Tabla tipo 2: ICMP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 138.204.230.193 [AS61506] |
| 2 | 100.88.0.1 [non_global] | 138.204.228.164 [AS61506] |
| 3 | 10.87.0.2 [non_global] | 10.100.163.1 [non_global] |
| 4 | 10.87.0.46 [non_global] | 10.100.154.2 [non_global] |
| 5 | 45.68.16.129 [unknown] | 45.68.16.231 [unknown] |
| 6 | 10.100.154.1 [non_global] | 192.168.113.5 [non_global] |
| 7 | 138.204.228.164 [AS61506] | 186.189.107.115 [AS52341] |
| 8 | 138.204.228.162 [AS61506] | NO_MEDIDO |
| 9 | 138.204.230.242 [AS61506] | NO_MEDIDO |

Tabla tipo 2: TCP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 138.204.230.193 [AS61506] |
| 2 | 100.88.0.1 [non_global] | 138.204.228.164 [AS61506] |
| 3 | 10.87.0.3 [non_global] | 10.100.163.1 [non_global] |
| 4 | 10.87.0.46 [non_global] | 10.100.154.2 [non_global] |
| 5 | 45.68.16.129 [unknown] | 45.68.16.231 [unknown] |
| 6 | 10.100.154.1 [non_global] | 192.168.113.5 [non_global] |
| 7 | 138.204.228.164 [AS61506] | * |
| 8 | 138.204.228.162 [AS61506] | * |
| 9 | 138.204.230.242 [AS61506] | * |
| 10 | NO_MEDIDO | * |
| 11 | NO_MEDIDO | * |
| 255 | NO_MEDIDO | * |

UDP, ronda 1: AS de ida [['unknown'], ['61506']]; AS de vuelta invertida [['unknown'], ['61506'], ['unknown'], ['61506']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

ICMP, ronda 1: AS de ida [['unknown'], ['61506']]; AS de vuelta invertida [['unknown'], ['61506']]. Coincidencia del orden observado de IP: False; de secuencia AS: True. La comparación se limita a las interfaces y sondas utilizadas.

TCP, ronda 1: AS de ida [['unknown'], ['61506']]; AS de vuelta invertida [['unknown'], ['61506']]. Coincidencia del orden observado de IP: False; de secuencia AS: True. No permite afirmar simetría completa por observaciones incompletas.

## Habana - comparación de sentidos

| Protocolo | Ronda | IDs ida / vuelta | IP únicas ida / vuelta | Jaccard IP intermedias | Observación incompleta |
| --- | --- | --- | --- | --- | --- |
| UDP | 1 | 227501050 / 227501582 | 14 / 11 | 0.000 | True |
| ICMP | 1 | 227502138 / 227502539 | 14 / 12 | 0.000 | True |
| TCP | 1 | 227511891 / 227512264 | 15 / 11 | 0.000 | True |

Tabla tipo 2: UDP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 200.14.48.132 [AS27725] |
| 2 | 100.88.0.1 [non_global] | 200.14.48.177 [AS27725] |
| 3 | 10.87.0.3 [non_global] | 192.168.118.89 [non_global] |
| 4 | 10.87.0.46 [non_global] | 172.31.247.241 [non_global] |
| 5 | * | 200.0.16.30 [AS11960] |
| 6 | 154.54.92.41 [AS174] | 200.0.16.18 [AS11960] |
| 7 | *; 154.54.3.29 [AS174] | 200.0.16.20 [AS11960] |
| 8 | 154.54.168.85 [AS174] | 89.221.37.138 [AS6762] |
| 9 | 38.104.94.178 [AS174] | 8.243.236.9 [AS3356] |
| 10 | * | 200.189.207.14 [AS3549] |
| 11 | 190.242.168.39 [AS23520] | 8.243.191.90 [AS3356] |
| 12 | 200.0.16.16 [AS11960] | * |
| 13 | 200.0.16.21 [AS11960] | * |
| 14 | 200.0.16.25 [AS11960] | * |
| 15 | * | * |
| 16 | * | * |
| 17 | * | NO_MEDIDO |
| 18 | 200.14.48.178 [AS27725] | NO_MEDIDO |
| 19 | 200.14.48.134 [AS27725] | NO_MEDIDO |
| 255 | NO_MEDIDO | * |

Tabla tipo 2: ICMP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 200.14.48.132 [AS27725] |
| 2 | 100.88.0.1 [non_global] | 200.14.48.177 [AS27725] |
| 3 | 10.87.0.2 [non_global] | 192.168.118.89 [non_global] |
| 4 | 10.87.0.46 [non_global] | 172.31.247.241 [non_global] |
| 5 | * | 200.0.16.86 [AS11960] |
| 6 | 154.54.92.41 [AS174] | 200.0.16.45 [AS11960] |
| 7 | *; 154.54.29.157 [AS174] | 200.0.16.20 [AS11960] |
| 8 | 154.54.167.185 [AS174] | 89.221.37.180 [AS6762] |
| 9 | 38.104.94.178 [AS174] | 8.243.236.5 [AS3356] |
| 10 | * | 200.189.207.14 [AS3549] |
| 11 | 190.242.168.39 [AS23520] | 8.243.191.90 [AS3356] |
| 12 | 200.0.16.16 [AS11960] | 186.189.107.115 [AS52341] |
| 13 | 200.0.16.21 [AS11960] | NO_MEDIDO |
| 14 | 200.0.16.29 [AS11960] | NO_MEDIDO |
| 15 | * | NO_MEDIDO |
| 16 | * | NO_MEDIDO |
| 17 | 200.14.48.178 [AS27725] | NO_MEDIDO |
| 18 | 200.14.48.134 [AS27725] | NO_MEDIDO |

Tabla tipo 2: TCP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 200.14.48.132 [AS27725] |
| 2 | 100.88.0.1 [non_global] | 200.14.48.177 [AS27725] |
| 3 | 10.87.0.3 [non_global] | 192.168.118.89 [non_global] |
| 4 | 10.87.0.46 [non_global] | 172.31.247.241 [non_global] |
| 5 | * | 200.0.16.86 [AS11960] |
| 6 | 154.54.92.41 [AS174] | 200.0.16.45 [AS11960] |
| 7 | 154.54.29.157 [AS174] | 200.0.16.20 [AS11960] |
| 8 | 154.54.167.185 [AS174] | 89.221.37.138 [AS6762] |
| 9 | 38.88.57.26 [AS174] | 8.243.236.5 [AS3356] |
| 10 | * | 200.189.207.14 [AS3549] |
| 11 | 69.79.104.1 [AS23520] | 8.243.191.90 [AS3356] |
| 12 | * | * |
| 13 | 190.242.168.39 [AS23520] | * |
| 14 | 200.0.16.16 [AS11960] | * |
| 15 | 200.0.16.21 [AS11960] | * |
| 16 | 200.0.16.29 [AS11960] | * |
| 17 | * | NO_MEDIDO |
| 18 | * | NO_MEDIDO |
| 19 | 200.14.48.178 [AS27725] | NO_MEDIDO |
| 20 | *; 200.14.48.134 [AS27725] | NO_MEDIDO |
| 255 | NO_MEDIDO | * |

UDP, ronda 1: AS de ida [['unknown'], ['174'], ['unknown'], ['23520'], ['11960'], ['unknown'], ['27725']]; AS de vuelta invertida [['unknown'], ['3356'], ['3549'], ['3356'], ['6762'], ['11960'], ['unknown'], ['27725']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

ICMP, ronda 1: AS de ida [['unknown'], ['174'], ['unknown'], ['23520'], ['11960'], ['unknown'], ['27725']]; AS de vuelta invertida [['3356'], ['3549'], ['3356'], ['6762'], ['11960'], ['unknown'], ['27725']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

TCP, ronda 1: AS de ida [['unknown'], ['174'], ['unknown'], ['23520'], ['unknown'], ['23520'], ['11960'], ['unknown'], ['27725']]; AS de vuelta invertida [['unknown'], ['3356'], ['3549'], ['3356'], ['6762'], ['11960'], ['unknown'], ['27725']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

## Rusia - comparación de sentidos

| Protocolo | Ronda | IDs ida / vuelta | IP únicas ida / vuelta | Jaccard IP intermedias | Observación incompleta |
| --- | --- | --- | --- | --- | --- |
| UDP | 1 | 227721105 / 227722324 | 10 / 8 | 0.000 | True |
| ICMP | 1 | 227722559 / 227722986 | 10 / 9 | 0.000 | True |
| TCP | 1 | 227723181 / 227724115 | 9 / 7 | 0.000 | True |

Tabla tipo 2: UDP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.19.17 [non_global] |
| 2 | 100.88.0.1 [non_global] | 80.71.208.96 [AS12389] |
| 3 | 10.87.0.3 [non_global] | 87.226.151.154 [AS12389] |
| 4 | 10.87.0.3 [non_global]; 10.87.0.46 [non_global] | 192.168.193.171 [non_global] |
| 5 | 10.87.0.46 [non_global] | *; 172.29.39.125 [non_global] |
| 6 | * | 212.133.1.53 [AS3356] |
| 7 | 154.54.92.41 [AS174] | 200.189.207.14 [AS3549] |
| 8 | 154.54.29.157 [AS174] | 8.243.191.90 [AS3356] |
| 9 | 154.54.167.185 [AS174] | * |
| 10 | 154.54.10.210 [AS174] | * |
| 11 | *; 195.22.211.61 [AS6762] | * |
| 12 | *; 195.22.214.161 [AS6762] | * |
| 13 | * | * |
| 14 | * | NO_MEDIDO |
| 15 | * | NO_MEDIDO |
| 16 | * | NO_MEDIDO |
| 17 | * | NO_MEDIDO |
| 255 | * | * |

Tabla tipo 2: ICMP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.19.17 [non_global] |
| 2 | 100.88.0.1 [non_global] | 80.71.208.96 [AS12389] |
| 3 | 10.87.0.3 [non_global] | 87.226.151.154 [AS12389] |
| 4 | 10.87.0.46 [non_global] | 192.168.193.171 [non_global] |
| 5 | * | *; 172.29.39.179 [non_global] |
| 6 | 154.54.92.41 [AS174] | 212.133.1.53 [AS3356] |
| 7 | *; 154.54.29.157 [AS174] | 200.189.207.14 [AS3549] |
| 8 | 154.54.167.185 [AS174] | 8.243.191.90 [AS3356] |
| 9 | 154.54.10.210 [AS174] | 186.189.107.115 [AS52341] |
| 10 | 195.22.211.61 [AS6762] | NO_MEDIDO |
| 11 | *; 195.22.214.161 [AS6762] | NO_MEDIDO |
| 12 | * | NO_MEDIDO |
| 13 | * | NO_MEDIDO |
| 14 | * | NO_MEDIDO |
| 15 | * | NO_MEDIDO |
| 16 | * | NO_MEDIDO |
| 255 | * | NO_MEDIDO |

Tabla tipo 2: TCP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.19.17 [non_global] |
| 2 | 100.88.0.1 [non_global] | 80.71.208.96 [AS12389] |
| 3 | 10.87.0.3 [non_global] | *; 87.226.151.154 [AS12389] |
| 4 | 10.87.0.46 [non_global] | 192.168.193.171 [non_global] |
| 5 | * | *; 172.29.39.171 [non_global] |
| 6 | 154.54.92.41 [AS174] | * |
| 7 | 154.54.29.157 [AS174] | *; 200.189.207.14 [AS3549] |
| 8 | 154.54.167.185 [AS174] | 8.243.191.90 [AS3356] |
| 9 | 154.54.10.210 [AS174] | * |
| 10 | 195.22.211.61 [AS6762] | * |
| 11 | * | * |
| 12 | * | * |
| 13 | * | * |
| 14 | * | NO_MEDIDO |
| 15 | * | NO_MEDIDO |
| 255 | * | * |

UDP, ronda 1: AS de ida [['unknown'], ['174'], ['6762'], ['unknown']]; AS de vuelta invertida [['unknown'], ['3356'], ['3549'], ['3356'], ['unknown'], ['12389'], ['unknown']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

ICMP, ronda 1: AS de ida [['unknown'], ['174'], ['6762'], ['unknown']]; AS de vuelta invertida [['3356'], ['3549'], ['3356'], ['unknown'], ['12389'], ['unknown']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

TCP, ronda 1: AS de ida [['unknown'], ['174'], ['6762'], ['unknown']]; AS de vuelta invertida [['unknown'], ['3356'], ['3549'], ['unknown'], ['12389'], ['unknown']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

## 4. Public Path

Por destino se selecciona un par RIPE del mismo protocolo, ronda e IPv4 pública. Se maximiza la unión de IP, luego se minimizan saltos sin respuesta y separación temporal. El grafo es dirigido; las adyacencias son inferidas por traceroute, los huecos son explícitos y no se crean enlaces cartesianos entre respuestas múltiples.

Destino 138.204.230.242: mediciones seleccionadas [227487554, 227487571]. Publicación y UUID público pendientes.

Destino 200.14.48.134: mediciones seleccionadas [227502138, 227502539]. Publicación y UUID público pendientes.

Destino 90.150.251.81: mediciones seleccionadas [227722559, 227722986]. Publicación y UUID público pendientes.

## Reproducción, integridad y limitaciones

Análisis utilizado: resultados/analisis_20261026T121332_5bd349cc. Regenerar con ./main analyze después de conservar las consultas ASN; ./main verify comprueba los manifiestos. Exportar PCAP con ./main packet-export y contrastar patrones con ./main patterns. El código, configuración activa y original, capturas, tablas, grafos y originales se reúnen con ./main bundle, excluyendo credenciales y claves privadas.

Reproducción de avance acreditada en reproduccion_ronda_1.json: 51 ejecuciones regeneradas sin nuevas mediciones ni consultas ASN, con tablas, métricas y tres CX2 idénticos. Se verificaron 1253 archivos del paquete. Este control no sustituye la repetición del cierre sobre las tres rondas.

Las mediciones describen las rutas observadas en estos horarios y bajo estos protocolos. No cuantifican por sí solas velocidad de acceso, congestión sostenida, censura o reglas de filtrado. Los timeouts y las rutas incompletas se conservan como resultados con sus límites de interpretación.

## Referencias

https://www.caida.org/catalog/software/scamper/

https://www.wireshark.org/docs/man-pages/tshark.html

https://atlas.ripe.net/docs/

https://stat.ripe.net/docs/data-api/api-endpoints/network-info

https://www.ndexbio.org/docs/using-the-ndex-api/

https://cytoscape.org/cx/cx2/cx2-visual-styles/

## Anexo de capturas

![api_configurada_sin_secreto](../../capturas/api_configurada_sin_secreto.png)

![campana_ronda_1_completa](../../capturas/campana_ronda_1_completa.png)

![creditos_50000](../../capturas/creditos_50000.png)

![mediciones_piloto_ida_vuelta](../../capturas/mediciones_piloto_ida_vuelta.png)

![registro_exitoso](../../capturas/registro_exitoso.png)

![ripe_rusia_udp_ida_227721105](../../capturas/ripe_rusia_udp_ida_227721105.png)

![sonda_1018487_connected](../../capturas/sonda_1018487_connected.png)

![sonda_31416_abandoned](../../capturas/sonda_31416_abandoned.png)

![sonda_6652_connected](../../capturas/sonda_6652_connected.png)

![sonda_870_ipv4_actual](../../capturas/sonda_870_ipv4_actual.png)

![traceroute_ida_21_saltos](../../capturas/traceroute_ida_21_saltos.png)

![traceroute_vuelta_17_registros](../../capturas/traceroute_vuelta_17_registros.png)

![wireshark_cita_icmp_tcp_scamper_r1](../../capturas/wireshark_cita_icmp_tcp_scamper_r1.png)

![wireshark_ripe_traceroute_ICMP_r1](../../capturas/wireshark_ripe_traceroute_ICMP_r1.png)

![wireshark_ripe_traceroute_TCP_r1](../../capturas/wireshark_ripe_traceroute_TCP_r1.png)

![wireshark_ripe_traceroute_UDP_r1](../../capturas/wireshark_ripe_traceroute_UDP_r1.png)

![wireshark_scamper_trace_icmp-paris_r1](../../capturas/wireshark_scamper_trace_icmp-paris_r1.png)

![wireshark_scamper_trace_icmp_r1](../../capturas/wireshark_scamper_trace_icmp_r1.png)

![wireshark_scamper_trace_tcp-ack_r1](../../capturas/wireshark_scamper_trace_tcp-ack_r1.png)

![wireshark_scamper_trace_tcp_r1](../../capturas/wireshark_scamper_trace_tcp_r1.png)

![wireshark_scamper_trace_udp-paris_r1](../../capturas/wireshark_scamper_trace_udp-paris_r1.png)

![wireshark_scamper_trace_udp_r1](../../capturas/wireshark_scamper_trace_udp_r1.png)

![wireshark_scamper_tracelb_icmp-echo_r1](../../capturas/wireshark_scamper_tracelb_icmp-echo_r1.png)

![wireshark_scamper_tracelb_tcp-ack-sport_r1](../../capturas/wireshark_scamper_tracelb_tcp-ack-sport_r1.png)

![wireshark_scamper_tracelb_tcp-sport_r1](../../capturas/wireshark_scamper_tracelb_tcp-sport_r1.png)

![wireshark_scamper_tracelb_udp-dport_r1](../../capturas/wireshark_scamper_tracelb_udp-dport_r1.png)

![wireshark_scamper_tracelb_udp-sport_r1](../../capturas/wireshark_scamper_tracelb_udp-sport_r1.png)
