## Path Discovery: comparación de Scamper y RIPE Atlas

Tarea individual - Algoritmos de Ruteo. Fuente del enunciado: Tarea Individual.docx, conservada con hash. Fecha de elaboración en UTC: 2026-10-27T00:11:47.204251+00:00.

Estado de campaña al generar: 102/153; esta edición analiza 102 ejecuciones principales válidas; 3 pilotos conservados y separados; 0/3 grafos públicos registrados. El documento es de avance mientras queden evidencias pendientes.

## Entorno, adaptación de destinos y trazabilidad

Banda ancha fija domiciliaria en Quilicura, proveedor comercial WOM confirmado por el estudiante. IPv4 pública 186.189.89.115; prefijo 186.189.89.0/24; ASN AS52341. La salida se contrastó con dos servicios y se verificó antes y después de cada ejecución. Interfaz wlan0; sincronización horaria yes.

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

## Sesión histórica 186.189.107.115 (fuera de la campaña activa)

Los siguientes párrafos describen únicamente las mediciones de la sesión anterior, conservadas como anexo histórico. No corresponden a las nuevas rondas de 186.189.89.115.

La ronda 1 comenzó el 26-10-2026 a las 01:30:20 UTC y sufrió dos interrupciones. La primera fue un error de acceso a un servicio externo antes de enviar una solicitud RIPE; se comprobó que no existía POST y se reanudó esa celda sin duplicarla. La segunda produjo un intervalo extendido durante la noche; no se establece su causa a partir de los registros disponibles.

El tracelb UDP-dport ruso scamper_20261026T024854_fb1d5630 abarcó desde las 02:48:54 hasta las 11:36:02 UTC. Se conserva íntegro y se excluye de la comparación por calidad temporal. El intento TCP-sport scamper_20261026T114443_ad95de92 perdió su controlador y solo dejó 70 bytes WARTS sin registro final; se conserva como intento interrumpido, no como medición válida. Se detuvo su captura residual antes de reanudar. Las decisiones, estados anterior y posterior y hashes están sellados en datos/originales/incidente_interrupcion_20261026T114921_f34fd3cb. Las dos celdas se repiten explícitamente; los otros resultados se conservan.

La ronda 1 no constituye una ventana continua. Las comparaciones que la incorporan deben mostrar sus horas reales y advertir que cambios entre métodos pueden reflejar cambios temporales. Las rondas siguientes se separan al menos treinta minutos desde el cierre efectivo anterior. No se reconstruyen tiempos ni se cambia la fecha de los originales para ocultar esta limitación.

En TCP se observaron respuestas ICMP en PCAP que no fueron incorporadas por Scamper a WARTS. Se contrastan por destino, direcciones, IPID, puertos y tiempo en resultados/correlacion_tcp_captura.json. Esta discrepancia de captura y detección impide atribuir automáticamente los ceros de Scamper a un firewall o a ausencia de respuesta en la red. Los resultados de la herramienta y las observaciones de paquetes se presentan por separado.

## Cambio de sesión del 26-10-2026 y campaña activa

El equipo reinició y volvió a suspenderse. El coordinador anterior ya no estaba activo; se conservaron 51 celdas completas de la primera ronda y nueve de la segunda. El intento TCP-sport scamper_20261026T124823_a8e33742 dejó 70 bytes WARTS sin resultado final. Se selló como intento interrumpido con fecha de revisión; su hora real de finalización es desconocida. No se cuenta como medición válida.

La IPv4 pública cambió de 186.189.107.115 a 186.189.89.115, prefijo 186.189.89.0/24, AS52341. El usuario confirmó nuevamente WOM domiciliaria y ausencia de VPN. La API de la sonda 1018487 mostró inicialmente direcciones de AS3549; tras reconectar el contenedor y consultar nuevamente, informó la misma IPv4 WOM que dos servicios externos. La causa de la discrepancia inicial no quedó establecida. No se afirma que el usuario estuviera en otra red ni que hubiera una VPN.

Los estados previos, parámetros públicos, informe y registros del sistema se conservaron en datos/originales/cambio_sesion_20261026T204144_9c115e26 (consultar la ruta exacta en config/reproduccion.json, campo session_archive). Los 60 resultados históricos permanecen disponibles y pueden analizarse mediante ./main analyze --session-ip 186.189.107.115. El contador activo y las comparaciones nuevas filtran la IPv4 de sesión y no mezclan ambos orígenes.

Se preparó un nuevo piloto completo y tres rondas desde la IPv4 vigente. Un servicio transitorio de systemd ejecuta una sola campaña, sin reinicio automático, y mantiene un bloqueo temporal de reposo y suspensión. Antes de cada ejecución se verifica la IPv4 esperada; cualquier cambio detiene las mediciones. El bloqueo se libera al terminar el proceso. Reiniciar o apagar el equipo todavía interrumpe la campaña y exige revisar el intento antes de reanudar.

Scamper 20260902 se construyó con verificación SHA-256. Las herramientas y la sonda se gestionan con Docker Compose; la imagen de la sonda está fijada por digest, con red del host e identidad persistente. La sonda local es 1018487. Se habilitaron créditos y una API key de permiso limitado, almacenada fuera de Git y de la entrega.

La validación del piloto incluyó WARTS, JSON, PCAPNG, puertos, citas ICMP y correlación temporal. La inspección reproducible se realizó con TShark, componente de Wireshark; no se declaró revisión de su interfaz gráfica. Se conservan los intentos fallidos e inválidos y no cuentan como campaña.

Ronda 1: 51/51 ejecuciones válidas. Inicio observado: 2026-10-26T20:46:19.639257+00:00; cierre observado: 2026-10-26T22:11:36.274508+00:00.

Ronda 2: 51/51 ejecuciones válidas. Inicio observado: 2026-10-26T22:41:46.818545+00:00; cierre observado: 2026-10-27T00:08:46.287702+00:00.

Ronda 3: 0/51 ejecuciones válidas. Inicio observado: pendiente; cierre observado: pendiente.

La unidad normalizada es una respuesta por intento y TTL. Se preservan respuestas múltiples, errores y timeouts. Un TTL 255 separado de los anteriores se conserva como registro, sin inventar los TTL intermedios ni enlaces entre capas no consecutivas. Los ASN son asociaciones IP-prefijo obtenidas con RIPEstat y no una ruta BGP observada.

El costo de Scamper se informa con su contador WARTS y el de RIPE de ida con solicitudes clasificadas en PCAP. Se conservan ambos conteos cuando están disponibles. Una diferencia entre contador y captura se documenta sin atribuir automáticamente pérdida, fallo de envío o filtrado. Las capturas inversas locales no permiten contar toda la emisión remota.

| Destino | Método | Ronda | Contador WARTS | Solicitudes PCAP |
| --- | --- | --- | --- | --- |
| 138.204.230.242 | trace / udp-paris | 1 | 10 | 9 |

Se contrastó una ejecución representativa de trace, tracelb y RIPE con sus originales, capturas y revisión GUI real. La evidencia y sus hashes están en datos/originales/revision_familias_20261026T214241_921e52e7. Este control verifica la normalización y la asociación de archivos; el contraste temporal requiere las tres rondas.

## 1. Path Discovery Scamper

## Valparaiso - 138.204.230.242

| Método | Rondas | Mediana IP únicas | Cobertura | Jaccard entre rondas | Mediana sondas WARTS | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| icmp | 2 | 9.0 | 100.0% | 1.000 | 9.0 | 5.3 | 2 |
| icmp-paris | 2 | 9.0 | 100.0% | 1.000 | 9.0 | 5.7 | 2 |
| udp | 2 | 9.0 | 100.0% | 1.000 | 9.0 | 5.1 | 2 |
| udp-paris | 2 | 9.0 | 100.0% | 1.000 | 10.0 | 5.3 | 2 |
| tcp | 2 | 0.0 | 0.0% | 1.000 | 10.0 | 54.9 | 0 |
| tcp-ack | 2 | 0.0 | 0.0% | 1.000 | 10.0 | 54.5 | 0 |

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
| udp-dport | 1 | Ninguna | 93 | 57 |
| icmp-echo | 1 | Ninguna | 44 | 57 |
| udp-sport | 1 | Ninguna | 48 | 57 |
| tcp-sport | 1 | Ninguna | 38 | 57 |
| tcp-ack-sport | 1 | Ninguna | 27 | 57 |
| udp-dport | 2 | Ninguna | 98 | 57 |
| icmp-echo | 2 | Ninguna | 44 | 57 |
| udp-sport | 2 | Ninguna | 38 | 57 |
| tcp-sport | 2 | Ninguna | 38 | 57 |
| tcp-ack-sport | 2 | Ninguna | 27 | 57 |

Las IP adicionales se comparan contra la unión de los seis trace de la misma ronda. Más IP con más paquetes se interpreta como una relación entre cobertura y costo, sin atribuir superioridad independiente del presupuesto de sondas.

## Habana - 200.14.48.134

| Método | Rondas | Mediana IP únicas | Cobertura | Jaccard entre rondas | Mediana sondas WARTS | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| icmp | 2 | 13.0 | 76.5% | 1.000 | 22.0 | 51.6 | 2 |
| udp-paris | 2 | 13.0 | 70.2% | 0.733 | 26.0 | 66.5 | 2 |
| icmp-paris | 2 | 12.5 | 73.5% | 0.923 | 22.5 | 56.5 | 2 |
| udp | 2 | 11.0 | 83.5% | 0.467 | 18.5 | 35.9 | 0 |
| tcp | 2 | 0.0 | 0.0% | 1.000 | 10.0 | 55.7 | 0 |
| tcp-ack | 2 | 0.0 | 0.0% | 1.000 | 10.0 | 55.0 | 0 |

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
| 7 | 154.54.3.29 [AS174] | 154.54.29.157 [AS174] | 154.54.92.41 [AS174] | 154.54.29.157 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 8 | 154.54.167.185 [AS174] | 154.54.167.185 [AS174] | ? not_recorded | 154.54.167.185 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 9 | 38.88.57.26 [AS174] | 38.104.94.178 [AS174] | 154.54.167.185 [AS174] | 38.104.94.178 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 10 | ? not_recorded | ? not_recorded | 38.88.57.26 [AS174] | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 11 | 190.242.168.37 [AS23520] | 190.242.168.37 [AS23520] | ? not_recorded | 190.242.168.37 [AS23520] | NO_MEDIDO | NO_MEDIDO |
| 12 | 200.0.16.21 [AS11960] | 200.0.16.21 [AS11960] | ? not_recorded | 200.0.16.21 [AS11960] | NO_MEDIDO | NO_MEDIDO |
| 13 | 200.0.16.29 [AS11960] | 200.0.16.29 [AS11960] | ? not_recorded | 200.0.16.29 [AS11960] | NO_MEDIDO | NO_MEDIDO |
| 14 | 200.0.16.21 [AS11960] | ? not_recorded | 190.242.168.39 [AS23520] | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 15 | NO_MEDIDO | ? not_recorded | 200.0.16.16 [AS11960] | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 16 | NO_MEDIDO | 200.14.48.178 [AS27725] | 200.0.16.21 [AS11960] | 200.14.48.178 [AS27725] | NO_MEDIDO | NO_MEDIDO |
| 17 | NO_MEDIDO | 200.14.48.134 [AS27725] | 200.0.16.29 [AS11960] | 200.14.48.134 [AS27725] | NO_MEDIDO | NO_MEDIDO |
| 18 | NO_MEDIDO | NO_MEDIDO | ? not_recorded | NO_MEDIDO | NO_MEDIDO | NO_MEDIDO |
| 19 | NO_MEDIDO | NO_MEDIDO | ? not_recorded | NO_MEDIDO | NO_MEDIDO | NO_MEDIDO |
| 20 | NO_MEDIDO | NO_MEDIDO | 200.14.48.178 [AS27725] | NO_MEDIDO | NO_MEDIDO | NO_MEDIDO |
| 21 | NO_MEDIDO | NO_MEDIDO | 200.14.48.134 [AS27725] | NO_MEDIDO | NO_MEDIDO | NO_MEDIDO |

| tracelb | Ronda | IP adicionales frente a unión de 6 trace | Sondas tracelb | Sondas de referencia |
| --- | --- | --- | --- | --- |
| udp-dport | 1 | 154.54.168.85, 69.79.104.1 | 200 | 110 |
| icmp-echo | 1 | Ninguna | 118 | 110 |
| udp-sport | 1 | Ninguna | 38 | 110 |
| tcp-sport | 1 | Ninguna | 38 | 110 |
| tcp-ack-sport | 1 | Ninguna | 27 | 110 |
| udp-dport | 2 | 154.54.3.29, 69.79.104.1 | 252 | 108 |
| icmp-echo | 2 | Ninguna | 118 | 108 |
| udp-sport | 2 | Ninguna | 38 | 108 |
| tcp-sport | 2 | Ninguna | 38 | 108 |
| tcp-ack-sport | 2 | Ninguna | 27 | 108 |

Las IP adicionales se comparan contra la unión de los seis trace de la misma ronda. Más IP con más paquetes se interpreta como una relación entre cobertura y costo, sin atribuir superioridad independiente del presupuesto de sondas.

## Rusia - 90.150.251.81

| Método | Rondas | Mediana IP únicas | Cobertura | Jaccard entre rondas | Mediana sondas WARTS | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| udp-paris | 2 | 10.0 | 62.5% | 0.538 | 22.0 | 67.1 | 0 |
| udp | 2 | 9.5 | 61.3% | 0.727 | 21.5 | 66.5 | 0 |
| icmp-paris | 2 | 9.5 | 59.4% | 0.900 | 23.0 | 73.2 | 0 |
| icmp | 2 | 9.0 | 57.9% | 0.800 | 22.0 | 70.5 | 0 |
| tcp | 2 | 0.0 | 0.0% | 1.000 | 10.0 | 54.5 | 0 |
| tcp-ack | 2 | 0.0 | 0.0% | 1.000 | 10.0 | 55.2 | 0 |

Métodos con mayor información según mediana de IP únicas, cobertura y estabilidad: udp-paris. Selección provisional: faltan rondas. La ausencia de llegada se conserva y no invalida automáticamente una medición.

Tabla tipo 1, ronda 1. Las rondas 2 y 3 y todos los intentos están en los anexos CSV de este análisis. Se conserva más de una IP por TTL cuando corresponde.

| HOP | udp | icmp | udp-paris | icmp-paris | tcp | tcp-ack |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | ? not_recorded | ? not_recorded |
| 2 | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | ? not_recorded | ? not_recorded |
| 3 | 10.87.0.3 [non_global] | 10.87.0.3 [non_global] | 10.87.0.3 [non_global] | 10.87.0.3 [non_global] | ? not_recorded | ? not_recorded |
| 4 | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | ? not_recorded | ? not_recorded |
| 5 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded |
| 6 | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 7 | 154.54.3.29 [AS174] | ? not_recorded | 154.54.29.157 [AS174] | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 8 | 154.54.167.185 [AS174] | 154.54.168.85 [AS174] | 154.54.167.185 [AS174] | 154.54.168.85 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 9 | 154.54.10.210 [AS174] | 154.54.10.210 [AS174] | 154.54.10.210 [AS174] | 154.54.10.210 [AS174] | NO_MEDIDO | NO_MEDIDO |
| 10 | 195.22.211.209 [AS6762] | 195.22.211.61 [AS6762] | 195.22.211.209 [AS6762] | 195.22.211.61 [AS6762] | NO_MEDIDO | NO_MEDIDO |
| 11 | ? not_recorded | ? not_recorded | 195.22.214.161 [AS6762] | 195.22.214.161 [AS6762] | NO_MEDIDO | NO_MEDIDO |
| 12 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 13 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 14 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 15 | ? not_recorded | ? not_recorded | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |
| 16 | NO_MEDIDO | NO_MEDIDO | ? not_recorded | ? not_recorded | NO_MEDIDO | NO_MEDIDO |

| tracelb | Ronda | IP adicionales frente a unión de 6 trace | Sondas tracelb | Sondas de referencia |
| --- | --- | --- | --- | --- |
| udp-dport | 1 | Ninguna | 188 | 109 |
| icmp-echo | 1 | Ninguna | 100 | 109 |
| udp-sport | 1 | Ninguna | 38 | 109 |
| tcp-sport | 1 | Ninguna | 38 | 109 |
| tcp-ack-sport | 1 | 90.150.251.81 | 27 | 109 |
| udp-dport | 2 | Ninguna | 174 | 108 |
| icmp-echo | 2 | Ninguna | 111 | 108 |
| udp-sport | 2 | Ninguna | 38 | 108 |
| tcp-sport | 2 | Ninguna | 38 | 108 |
| tcp-ack-sport | 2 | 90.150.251.81 | 27 | 108 |

Las IP adicionales se comparan contra la unión de los seis trace de la misma ronda. Más IP con más paquetes se interpreta como una relación entre cobertura y costo, sin atribuir superioridad independiente del presupuesto de sondas.

## 2. Path Discovery RIPE

La definición efectiva, la solicitud, el ID, la sonda participante y los tiempos reales se conservan para cada medición. La aceptación de una solicitud no se contó como ejecución: se esperó un resultado con el ID y sonda correctos. Las capturas locales de ida permiten contar solicitudes; las de vuelta son parciales y no permiten reconstruir todo el tráfico remoto.

## Valparaiso - protocolos RIPE de ida

| Protocolo | Rondas | Mediana IP únicas | Cobertura | Jaccard | Mediana sondas PCAP | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ICMP | 2 | 9.0 | 100.0% | 1.000 | 27.0 | 17.5 | 2 |
| TCP | 2 | 9.0 | 100.0% | 1.000 | 27.0 | 11.4 | 2 |
| UDP | 2 | 9.0 | 100.0% | 1.000 | 27.0 | 11.9 | 2 |

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

| Protocolo | Rondas | Mediana IP únicas | Cobertura | Jaccard | Mediana sondas PCAP | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TCP | 2 | 15.0 | 83.7% | 0.875 | 55.5 | 77.0 | 2 |
| UDP | 2 | 14.5 | 76.4% | 0.812 | 57.0 | 74.4 | 2 |
| ICMP | 2 | 13.0 | 76.5% | 1.000 | 51.0 | 71.0 | 2 |

Protocolos con mayor información en la comparación disponible: TCP. Resultado provisional.

| HOP | UDP | ICMP | TCP |
| --- | --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] |
| 2 | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] |
| 3 | 10.87.0.3 [non_global] | 10.87.0.2 [non_global] | 10.87.0.3 [non_global] |
| 4 | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] |
| 5 | * | * | * |
| 6 | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] |
| 7 | *; 154.54.29.157 [AS174] | *; 154.54.29.157 [AS174] | *; 154.54.29.157 [AS174] |
| 8 | 154.54.167.185 [AS174] | 154.54.167.185 [AS174] | 154.54.167.185 [AS174] |
| 9 | 38.104.94.178 [AS174] | *; 38.104.94.178 [AS174] | *; 38.88.57.26 [AS174] |
| 10 | * | * | * |
| 11 | 190.242.168.39 [AS23520] | *; 190.242.168.37 [AS23520] | *; 190.242.168.39 [AS23520] |
| 12 | 200.0.16.16 [AS11960] | 200.0.16.21 [AS11960] | 200.0.16.16 [AS11960] |
| 13 | 200.0.16.21 [AS11960] | 200.0.16.29 [AS11960] | 200.0.16.21 [AS11960] |
| 14 | 200.0.16.29 [AS11960] | * | 200.0.16.25 [AS11960] |
| 15 | * | * | * |
| 16 | * | 200.14.48.178 [AS27725] | 200.14.48.178 [AS27725] |
| 17 | 200.14.48.178 [AS27725] | 200.14.48.134 [AS27725] | 200.14.48.134 [AS27725] |
| 18 | 200.14.48.134 [AS27725] | NO_MEDIDO | NO_MEDIDO |

## Rusia - protocolos RIPE de ida

| Protocolo | Rondas | Mediana IP únicas | Cobertura | Jaccard | Mediana sondas PCAP | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ICMP | 2 | 10.0 | 58.8% | 1.000 | 51.0 | 104.6 | 0 |
| UDP | 2 | 9.5 | 61.1% | 0.727 | 54.0 | 108.0 | 0 |
| TCP | 2 | 9.0 | 54.4% | 0.636 | 49.5 | 107.2 | 0 |

Protocolos con mayor información en la comparación disponible: ICMP. Resultado provisional.

| HOP | UDP | ICMP | TCP |
| --- | --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] |
| 2 | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] |
| 3 | 10.87.0.3 [non_global] | 10.87.0.3 [non_global] | 10.87.0.3 [non_global] |
| 4 | 10.87.0.3 [non_global]; 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] |
| 5 | 10.87.0.46 [non_global] | * | * |
| 6 | *; 100.88.0.1 [non_global]; 192.168.100.1 [non_global] | 154.54.92.41 [AS174] | 154.54.92.41 [AS174] |
| 7 | 154.54.92.41 [AS174] | 154.54.3.29 [AS174] | 154.54.3.29 [AS174] |
| 8 | *; 154.54.29.157 [AS174] | 154.54.168.85 [AS174] | 154.54.168.85 [AS174] |
| 9 | 154.54.167.185 [AS174] | 154.54.10.210 [AS174] | 154.54.10.210 [AS174] |
| 10 | 154.54.10.210 [AS174] | 195.22.211.61 [AS6762] | 195.22.211.61 [AS6762] |
| 11 | 195.22.211.61 [AS6762] | *; 195.22.214.161 [AS6762] | *; 195.22.214.161 [AS6762] |
| 12 | *; 195.22.214.161 [AS6762] | * | * |
| 13 | * | * | * |
| 14 | * | * | * |
| 15 | * | * | * |
| 16 | * | * | * |
| 17 | * | NO_MEDIDO | NO_MEDIDO |
| 255 | * | * | * |

## Transporte, payload y respuesta selectiva

Se inspeccionan seis métodos trace, cinco tracelb y tres protocolos RIPE. Las fichas conservan TTL, tamaño, IPID, protocolo, puertos, flags TCP, secuencia/ACK, campos ICMP, checksums, payload hexadecimal y encabezados originales citados. Los campos no presentes en un protocolo se consideran no aplicables.

## ripe / traceroute / ICMP

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 90; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.ttl | Incremento 1 cada 3 sondas; base propia de cada ejecución; n=27 | Ronda 2: regla corroborada; comprobaciones=26; fallos=0 |
| ip.id | Variable; rango observado 4983 a 5479; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |
| ip.len | Constante: 76; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.proto | Constante: 1; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.checksum | Variable; rango observado 1500 a 4044; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |
| icmp.type | Constante: 8; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| icmp.code | Constante: 0; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| icmp.ident | Constante: 36864; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| icmp.seq | Incremento 1 por sonda; base propia de cada ejecución; n=27 | Ronda 2: regla corroborada; comprobaciones=26; fallos=0 |
| icmp.checksum | Constante: 0x0001; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| data.data | Variable; longitudes observadas [48] bytes; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |

Payload observado: [48] bytes. Bytes iniciales: d4dc687474703a2f2f61746c61732e726970652e6e65742041746c617320736179732048692100000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Segmento ASCII constante desde offset 2: http://atlas.ripe.net Atlas says Hi!

Restricción observada: la suma de payload_word0_BE, icmp.checksum, icmp.ident, icmp.seq módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 27, "word_constraint_stable_in_new_execution": true, "new_execution_base": 25823, "checked_later_packets": 26, "failed_later_packets": 0}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## ripe / traceroute / TCP

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 102; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.ttl | Incremento 1 cada 3 sondas; base propia de cada ejecución; n=27 | Ronda 2: regla corroborada; comprobaciones=26; fallos=0 |
| ip.id | Variable; rango observado 39744 a 39994; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |
| ip.len | Constante: 88; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.proto | Constante: 6; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.checksum | Variable; rango observado 32503 a 34801; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |
| tcp.srcport | Constante: 20480; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| tcp.dstport | Constante: 80; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| tcp.flags | Constante: 0x0002; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| tcp.seq_raw | Incremento 1 por sonda; base propia de cada ejecución; n=27 | Ronda 2: regla corroborada; comprobaciones=26; fallos=0 |
| tcp.ack_raw | Constante: 0; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| tcp.len | Constante: 48; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| tcp.checksum | Incremento -1 por sonda; base propia de cada ejecución; n=27 | Ronda 2: regla corroborada; comprobaciones=26; fallos=0 |
| tcp.payload | Constante: 687474703a2f2f61746c61732e726970652e6e65742041746c6173207361797320486921000000000000000000000000; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |

Payload observado: [48] bytes. Bytes iniciales: 687474703a2f2f61746c61732e726970652e6e65742041746c6173207361797320486921000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [].

Segmento ASCII constante desde offset 0: http://atlas.ripe.net Atlas says Hi!

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 27, "word_constraint_stable_in_new_execution": null, "new_execution_base": null, "checked_later_packets": 0, "failed_later_packets": null}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## ripe / traceroute / UDP

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 90; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.ttl | Incremento 1 cada 3 sondas; base propia de cada ejecución; n=27 | Ronda 2: regla corroborada; comprobaciones=26; fallos=0 |
| ip.id | Variable; rango observado 11144 a 11370; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |
| ip.len | Constante: 76; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.proto | Constante: 17; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.checksum | Variable; rango observado 61128 a 63402; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |
| udp.srcport | Constante: 20480; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| udp.dstport | Constante: 33435; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| udp.length | Constante: 56; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=27 | Ronda 2: regla corroborada; comprobaciones=26; fallos=0 |
| udp.payload | Variable; longitudes observadas [48] bytes; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |
| data.data | Variable; longitudes observadas [48] bytes; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |

Payload observado: [48] bytes. Bytes iniciales: 0352687474703a2f2f61746c61732e726970652e6e65742041746c617320736179732048692100000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Segmento ASCII constante desde offset 2: http://atlas.ripe.net Atlas says Hi!

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 27, "word_constraint_stable_in_new_execution": true, "new_execution_base": 54766, "checked_later_packets": 26, "failed_later_packets": 0}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / icmp

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.ttl | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| ip.len | Constante: 44; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.proto | Constante: 1; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.checksum | Incremento -257 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| icmp.type | Constante: 8; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| icmp.code | Constante: 0; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| icmp.ident | Constante: 32769; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| icmp.seq | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| icmp.checksum | Incremento -1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| data.data | Constante: 00000000000000000000000000000000; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |

Payload observado: [16] bytes. Bytes iniciales: 00000000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [].

Restricción observada: la suma de payload_word0_BE, icmp.checksum, icmp.ident, icmp.seq módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 9, "word_constraint_stable_in_new_execution": true, "new_execution_base": 63487, "checked_later_packets": 8, "failed_later_packets": 0}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / icmp-paris

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.ttl | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| ip.len | Constante: 44; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.proto | Constante: 1; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.checksum | Incremento -257 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| icmp.type | Constante: 8; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| icmp.code | Constante: 0; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| icmp.ident | Constante: 32769; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| icmp.seq | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| icmp.checksum | Constante: 0x8001; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| data.data | Variable; longitudes observadas [16] bytes; n=9. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=9 |

Payload observado: [16] bytes. Bytes iniciales: f7fc0000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, icmp.checksum, icmp.ident, icmp.seq módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 9, "word_constraint_stable_in_new_execution": true, "new_execution_base": 63487, "checked_later_packets": 8, "failed_later_packets": 0}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / tcp

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 54; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.ttl | Incremento 1 cada 2 sondas; base propia de cada ejecución; n=10 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=10 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.len | Constante: 40; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.proto | Constante: 6; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.checksum | Variable; rango observado 57175 a 58208; n=10. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=10 |
| tcp.srcport | Constante: 32769; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.dstport | Constante: 80; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.flags | Constante: 0x0002; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.seq_raw | Constante: 0; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.ack_raw | Constante: 0; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.len | Constante: 0; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.checksum | Constante: 0x9922; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |

Payload observado: [0] bytes. Sin payload de aplicación en estas sondas.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 10, "word_constraint_stable_in_new_execution": null, "new_execution_base": null, "checked_later_packets": 0, "failed_later_packets": null}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / tcp-ack

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 54; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.ttl | Incremento 1 cada 2 sondas; base propia de cada ejecución; n=10 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=10 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.len | Constante: 40; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.proto | Constante: 6; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.checksum | Variable; rango observado 57175 a 58208; n=10. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=10 |
| tcp.srcport | Constante: 32769; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.dstport | Constante: 80; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.flags | Constante: 0x0010; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.seq_raw | Constante: 0; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.ack_raw | Constante: 0; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.len | Constante: 0; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| tcp.checksum | Constante: 0x9914; n=10 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |

Payload observado: [0] bytes. Sin payload de aplicación en estas sondas.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 10, "word_constraint_stable_in_new_execution": null, "new_execution_base": null, "checked_later_packets": 0, "failed_later_packets": null}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / udp

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.ttl | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| ip.len | Constante: 44; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.proto | Constante: 17; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.checksum | Incremento -257 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| udp.srcport | Constante: 32769; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| udp.dstport | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| udp.length | Constante: 24; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| udp.checksum | Incremento -1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=8; fallos=0 |
| udp.payload | Constante: 00000000000000000000000000000000; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| data.data | Constante: 00000000000000000000000000000000; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |

Payload observado: [16] bytes. Bytes iniciales: 00000000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [].

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 9, "word_constraint_stable_in_new_execution": true, "new_execution_base": 26959, "checked_later_packets": 8, "failed_later_packets": 0}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / trace / udp-paris

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=9 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=9 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=9 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.ttl | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| ip.len | Constante: 44; n=9 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.proto | Constante: 17; n=9 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| ip.checksum | Incremento -257 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| udp.srcport | Constante: 32769; n=9 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| udp.dstport | Constante: 33435; n=9 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| udp.length | Constante: 24; n=9 | Ronda 2: regla corroborada; comprobaciones=10; fallos=0 |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Ronda 2: regla corroborada; comprobaciones=9; fallos=0 |
| udp.payload | Variable; longitudes observadas [16] bytes; n=9. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=10 |
| data.data | Variable; longitudes observadas [16] bytes; n=9. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=10 |

Payload observado: [16] bytes. Bytes iniciales: 66b10000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 10, "word_constraint_stable_in_new_execution": true, "new_execution_base": 26959, "checked_later_packets": 9, "failed_later_packets": 0}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / icmp-echo

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=44 | Ronda 2: regla corroborada; comprobaciones=44; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=44 | Ronda 2: regla corroborada; comprobaciones=44; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=44 | Ronda 2: regla corroborada; comprobaciones=44; fallos=0 |
| ip.ttl | Variable; rango observado 1 a 9; n=44. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=44 |
| ip.id | Constante: 0x0000; n=44 | Ronda 2: regla corroborada; comprobaciones=44; fallos=0 |
| ip.len | Constante: 44; n=44 | Ronda 2: regla corroborada; comprobaciones=44; fallos=0 |
| ip.proto | Constante: 1; n=44 | Ronda 2: regla corroborada; comprobaciones=44; fallos=0 |
| ip.checksum | Variable; rango observado 56162 a 58210; n=44. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=44 |
| icmp.type | Constante: 8; n=44 | Ronda 2: regla corroborada; comprobaciones=44; fallos=0 |
| icmp.code | Constante: 0; n=44 | Ronda 2: regla corroborada; comprobaciones=44; fallos=0 |
| icmp.ident | Constante: 32769; n=44 | Ronda 2: regla corroborada; comprobaciones=44; fallos=0 |
| icmp.seq | Incremento 1 por sonda; base propia de cada ejecución; n=44 | Ronda 2: regla corroborada; comprobaciones=43; fallos=0 |
| icmp.checksum | Variable; rango observado 1 a 6; n=44. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=44 |
| data.data | Variable; longitudes observadas [16] bytes; n=44. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=44 |

Payload observado: [16] bytes. Bytes iniciales: 77fd0000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, icmp.checksum, icmp.ident, icmp.seq módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 44, "word_constraint_stable_in_new_execution": true, "new_execution_base": 63487, "checked_later_packets": 43, "failed_later_packets": 0}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / tcp-ack-sport

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 54; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.ttl | Variable; rango observado 1 a 4; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=27 | Ronda 2: regla corroborada; comprobaciones=26; fallos=0 |
| ip.len | Constante: 40; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.proto | Constante: 6; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| ip.checksum | Variable; rango observado 57414 a 58208; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |
| tcp.srcport | Variable; rango observado 32769 a 32774; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |
| tcp.dstport | Constante: 80; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| tcp.flags | Constante: 0x0010; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| tcp.seq_raw | Constante: 0; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| tcp.ack_raw | Constante: 0; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| tcp.len | Constante: 0; n=27 | Ronda 2: regla corroborada; comprobaciones=27; fallos=0 |
| tcp.checksum | Variable; rango observado 39183 a 39188; n=27. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=27 |

Payload observado: [0] bytes. Sin payload de aplicación en estas sondas.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 27, "word_constraint_stable_in_new_execution": null, "new_execution_base": null, "checked_later_packets": 0, "failed_later_packets": null}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / tcp-sport

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 54; n=38 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=38 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=38 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| ip.ttl | Variable; rango observado 1 a 4; n=38. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=38 |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=38 | Ronda 2: regla corroborada; comprobaciones=37; fallos=0 |
| ip.len | Constante: 40; n=38 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| ip.proto | Constante: 6; n=38 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| ip.checksum | Variable; rango observado 57403 a 58208; n=38. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=38 |
| tcp.srcport | Variable; rango observado 32769 a 32774; n=38. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=38 |
| tcp.dstport | Constante: 80; n=38 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| tcp.flags | Constante: 0x0002; n=38 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| tcp.seq_raw | Constante: 0; n=38 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| tcp.ack_raw | Constante: 0; n=38 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| tcp.len | Constante: 0; n=38 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| tcp.checksum | Variable; rango observado 39197 a 39202; n=38. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=38 |

Payload observado: [0] bytes. Sin payload de aplicación en estas sondas.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 38, "word_constraint_stable_in_new_execution": null, "new_execution_base": null, "checked_later_packets": 0, "failed_later_packets": null}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / udp-dport

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=93 | Ronda 2: regla corroborada; comprobaciones=98; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=93 | Ronda 2: regla corroborada; comprobaciones=98; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=93 | Ronda 2: regla corroborada; comprobaciones=98; fallos=0 |
| ip.ttl | Variable; rango observado 1 a 9; n=93. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=98 |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=93 | Ronda 2: regla corroborada; comprobaciones=97; fallos=0 |
| ip.len | Constante: 44; n=93 | Ronda 2: regla corroborada; comprobaciones=98; fallos=0 |
| ip.proto | Constante: 17; n=93 | Ronda 2: regla corroborada; comprobaciones=98; fallos=0 |
| ip.checksum | Variable; rango observado 56053 a 58193; n=93. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=98 |
| udp.srcport | Constante: 32769; n=93 | Ronda 2: regla corroborada; comprobaciones=98; fallos=0 |
| udp.dstport | Variable; rango observado 33435 a 33461; n=93. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=98 |
| udp.length | Constante: 24; n=93 | Ronda 2: regla corroborada; comprobaciones=98; fallos=0 |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=93 | Ronda 2: regla corroborada; comprobaciones=97; fallos=0 |
| udp.payload | Variable; longitudes observadas [16] bytes; n=93. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=98 |
| data.data | Variable; longitudes observadas [16] bytes; n=93. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=98 |

Payload observado: [16] bytes. Bytes iniciales: 66b10000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 98, "word_constraint_stable_in_new_execution": true, "new_execution_base": 26959, "checked_later_packets": 97, "failed_later_packets": 0}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / udp-sport

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=48 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| ip.src | Constante: 192.168.100.7; n=48 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| ip.dst | Constante: 138.204.230.242; n=48 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| ip.ttl | Variable; rango observado 1 a 5; n=48. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=38 |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=48 | Ronda 2: regla corroborada; comprobaciones=37; fallos=0 |
| ip.len | Constante: 44; n=48 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| ip.proto | Constante: 17; n=48 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| ip.checksum | Variable; rango observado 57122 a 58193; n=48. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=38 |
| udp.srcport | Variable; rango observado 32769 a 32774; n=48. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=38 |
| udp.dstport | Constante: 33435; n=48 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| udp.length | Constante: 24; n=48 | Ronda 2: regla corroborada; comprobaciones=38; fallos=0 |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=48 | Ronda 2: regla corroborada; comprobaciones=37; fallos=0 |
| udp.payload | Variable; longitudes observadas [16] bytes; n=48. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=38 |
| data.data | Variable; longitudes observadas [16] bytes; n=48. No se predice valor exacto. | Ronda 2: sin regla exacta contrastable; comprobaciones=38 |

Payload observado: [16] bytes. Bytes iniciales: 66b10000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

Contraste del formato de payload: {"2": {"payload_lengths_match": true, "constant_ascii_segments_match": true, "samples": 38, "word_constraint_stable_in_new_execution": true, "new_execution_base": 26959, "checked_later_packets": 37, "failed_later_packets": 0}}

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

Control de recepción TCP: {"reviewed_scamper_tcp_runs": 24, "runs_with_matching_icmp_quotes": 24, "runs_with_pcap_warts_discrepancy": 24, "interpretation": "Correlación estricta por direcciones, IPID, puertos y orden temporal. Presencia en PCAP no implica aceptación por Scamper. Causa de la diferencia no establecida; no demuestra bloqueo TCP de los routers."}. Las respuestas presentes en PCAP y ausentes en WARTS se informan por separado; no prueban filtrado de red. Detalle reproducible en resultados/correlacion_tcp_captura.json.

Candidatos de respuesta selectiva detectados: 707. La ausencia de una IP en un método no demuestra una regla de firewall: puede deberse a carga, balanceo, pérdida o rutas diferentes. Se requiere corroboración entre rondas y pruebas dirigidas acotadas para cada herramienta.

Pruebas dirigidas de respuesta selectiva pendientes. Este requisito no se da por cerrado por la mera lista de candidatos.

## Control adicional de recepción TCP

Prueba fuera de las 153 celdas. Se compara el envío predeterminado y la opción oficial rawtcp, conservando o cambiando explícitamente el puerto de origen. Los resultados principales mantienen sus parámetros originales.

| rawtcp | Puerto origen | IP únicas | Sondas | Parada | Run |
| --- | --- | --- | --- | --- | --- |
| False | 32769 | 0 | 10 | GAPLIMIT | scamper_20261026T221240_ef87de8b |
| True | 32769 | 0 | 10 | GAPLIMIT | scamper_20261026T221336_6c36ecb2 |
| True | 20480 | 0 | 10 | GAPLIMIT | scamper_20261026T221433_60b0c099 |

Diagnóstico adicional; excluido de la comparación principal y del entrenamiento de patrones. Una diferencia no identifica por sí sola la regla de firewall o causa local.

## 3. Path way RIPE: ida y vuelta

Las respuestas desde la IPv4 pública domiciliaria acreditan la observación de esa dirección. Identificar al equipo que respondió requiere correlación con la captura local y conocimiento del NAT.

La vuelta ICMP 227916578 observó respuestas desde la IP pública de destino. La captura local contiene 0 paquetes con la IP de esa sonda en el encabezado IPv4 exterior; la identidad del respondiente queda sin establecer. Evidencia: datos/originales/revision_vuelta_20261026T220433_32cda63d.

Cada comparación conserva la numeración desde cada origen y también compara el orden inverso de la vuelta. Las IP corresponden a interfaces observadas; direcciones distintas no demuestran routers distintos ni se asume alias entre interfaces. Las secuencias AS tampoco prueban una ruta BGP.

## Valparaiso - comparación de sentidos

| Protocolo | Ronda | IDs ida / vuelta | IP únicas ida / vuelta | Jaccard IP intermedias | Observación incompleta |
| --- | --- | --- | --- | --- | --- |
| UDP | 1 | 227903487 / 227903721 | 9 / 7 | 0.071 | True |
| ICMP | 1 | 227905446 / 227905809 | 9 / 7 | 0.077 | False |
| TCP | 1 | 227905859 / 227905911 | 9 / 6 | 0.077 | True |
| UDP | 2 | 227942660 / 227942705 | 9 / 7 | 0.071 | True |
| ICMP | 2 | 227942829 / 227942832 | 9 / 7 | 0.077 | False |
| TCP | 2 | 227942843 / 227942892 | 9 / 6 | 0.077 | True |

Tabla tipo 2: UDP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 138.204.230.193 [AS61506] |
| 2 | 100.88.0.1 [non_global] | 138.204.228.164 [AS61506] |
| 3 | 10.87.0.3 [non_global] | 10.100.163.1 [non_global] |
| 4 | 10.87.0.46 [non_global] | 10.100.154.2 [non_global] |
| 5 | 45.68.16.129 [unknown] | 45.68.16.231 [unknown] |
| 6 | 10.100.154.1 [non_global] | 192.168.113.5 [non_global] |
| 7 | 138.204.228.164 [AS61506] | *; 138.204.228.163 [AS61506]; 138.204.230.193 [AS61506] |
| 8 | 138.204.228.162 [AS61506] | * |
| 9 | 138.204.230.242 [AS61506] | * |
| 10 | NO_MEDIDO | * |
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
| 7 | 138.204.228.164 [AS61506] | 186.189.89.115 [AS52341] |
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

UDP, ronda 2: AS de ida [['unknown'], ['61506']]; AS de vuelta invertida [['unknown'], ['61506'], ['unknown'], ['61506']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

ICMP, ronda 2: AS de ida [['unknown'], ['61506']]; AS de vuelta invertida [['unknown'], ['61506']]. Coincidencia del orden observado de IP: False; de secuencia AS: True. La comparación se limita a las interfaces y sondas utilizadas.

TCP, ronda 2: AS de ida [['unknown'], ['61506']]; AS de vuelta invertida [['unknown'], ['61506']]. Coincidencia del orden observado de IP: False; de secuencia AS: True. No permite afirmar simetría completa por observaciones incompletas.

## Habana - comparación de sentidos

| Protocolo | Ronda | IDs ida / vuelta | IP únicas ida / vuelta | Jaccard IP intermedias | Observación incompleta |
| --- | --- | --- | --- | --- | --- |
| UDP | 1 | 227915103 / 227916164 | 14 / 11 | 0.000 | True |
| ICMP | 1 | 227916364 / 227916578 | 13 / 12 | 0.000 | True |
| TCP | 1 | 227916610 / 227916694 | 14 / 11 | 0.000 | True |
| UDP | 2 | 227951133 / 227952719 | 15 / 11 | 0.000 | True |
| ICMP | 2 | 227953059 / 227953105 | 13 / 12 | 0.000 | True |
| TCP | 2 | 227953132 / 227953345 | 16 / 10 | 0.000 | True |

Tabla tipo 2: UDP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 200.14.48.132 [AS27725] |
| 2 | 100.88.0.1 [non_global] | 200.14.48.177 [AS27725] |
| 3 | 10.87.0.3 [non_global] | 192.168.118.89 [non_global] |
| 4 | 10.87.0.46 [non_global] | 172.31.247.241 [non_global] |
| 5 | * | 200.0.16.30 [AS11960] |
| 6 | 154.54.92.41 [AS174] | 200.0.16.18 [AS11960] |
| 7 | *; 154.54.29.157 [AS174] | 200.0.16.20 [AS11960] |
| 8 | 154.54.167.185 [AS174] | 89.221.37.138 [AS6762] |
| 9 | 38.104.94.178 [AS174] | 8.243.236.5 [AS3356] |
| 10 | * | 200.189.207.14 [AS3549] |
| 11 | 190.242.168.39 [AS23520] | 8.243.191.90 [AS3356] |
| 12 | 200.0.16.16 [AS11960] | * |
| 13 | 200.0.16.21 [AS11960] | * |
| 14 | 200.0.16.29 [AS11960] | * |
| 15 | * | * |
| 16 | * | * |
| 17 | 200.14.48.178 [AS27725] | NO_MEDIDO |
| 18 | 200.14.48.134 [AS27725] | NO_MEDIDO |
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
| 8 | 154.54.167.185 [AS174] | 89.221.37.138 [AS6762] |
| 9 | *; 38.104.94.178 [AS174] | 8.243.236.5 [AS3356] |
| 10 | * | 200.189.207.14 [AS3549] |
| 11 | *; 190.242.168.37 [AS23520] | 8.243.191.90 [AS3356] |
| 12 | 200.0.16.21 [AS11960] | *; 186.189.89.115 [AS52341] |
| 13 | 200.0.16.29 [AS11960] | NO_MEDIDO |
| 14 | * | NO_MEDIDO |
| 15 | * | NO_MEDIDO |
| 16 | 200.14.48.178 [AS27725] | NO_MEDIDO |
| 17 | 200.14.48.134 [AS27725] | NO_MEDIDO |

Tabla tipo 2: TCP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 200.14.48.132 [AS27725] |
| 2 | 100.88.0.1 [non_global] | 200.14.48.177 [AS27725] |
| 3 | 10.87.0.3 [non_global] | 192.168.118.89 [non_global] |
| 4 | 10.87.0.46 [non_global] | *; 172.31.247.241 [non_global] |
| 5 | * | 200.0.16.86 [AS11960] |
| 6 | 154.54.92.41 [AS174] | 200.0.16.45 [AS11960] |
| 7 | *; 154.54.29.157 [AS174] | 200.0.16.20 [AS11960] |
| 8 | 154.54.167.185 [AS174] | 89.221.37.138 [AS6762] |
| 9 | *; 38.88.57.26 [AS174] | 8.243.236.9 [AS3356] |
| 10 | * | 200.189.207.14 [AS3549] |
| 11 | *; 190.242.168.39 [AS23520] | 8.243.191.90 [AS3356] |
| 12 | 200.0.16.16 [AS11960] | * |
| 13 | 200.0.16.21 [AS11960] | * |
| 14 | 200.0.16.25 [AS11960] | * |
| 15 | * | *; 200.14.48.132 [AS27725]; 200.14.48.177 [AS27725] |
| 16 | 200.14.48.178 [AS27725] | * |
| 17 | 200.14.48.134 [AS27725] | NO_MEDIDO |
| 255 | NO_MEDIDO | * |

UDP, ronda 1: AS de ida [['unknown'], ['174'], ['unknown'], ['23520'], ['11960'], ['unknown'], ['27725']]; AS de vuelta invertida [['unknown'], ['3356'], ['3549'], ['3356'], ['6762'], ['11960'], ['unknown'], ['27725']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

ICMP, ronda 1: AS de ida [['unknown'], ['174'], ['unknown'], ['23520'], ['11960'], ['unknown'], ['27725']]; AS de vuelta invertida [['3356'], ['3549'], ['3356'], ['6762'], ['11960'], ['unknown'], ['27725']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

TCP, ronda 1: AS de ida [['unknown'], ['174'], ['unknown'], ['23520'], ['11960'], ['unknown'], ['27725']]; AS de vuelta invertida [['unknown'], ['27725'], ['unknown'], ['3356'], ['3549'], ['3356'], ['6762'], ['11960'], ['unknown'], ['27725']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

UDP, ronda 2: AS de ida [['unknown'], ['174'], ['unknown'], ['23520'], ['unknown'], ['23520'], ['11960'], ['unknown'], ['27725']]; AS de vuelta invertida [['unknown'], ['27725'], ['unknown'], ['3356'], ['3549'], ['3356'], ['6762'], ['11960'], ['unknown'], ['27725']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

ICMP, ronda 2: AS de ida [['unknown'], ['174'], ['unknown'], ['23520'], ['11960'], ['unknown'], ['27725']]; AS de vuelta invertida [['3356'], ['3549'], ['3356'], ['6762'], ['11960'], ['unknown'], ['27725']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

TCP, ronda 2: AS de ida [['unknown'], ['174'], ['unknown'], ['23520'], ['11960'], ['unknown'], ['11960'], ['unknown'], ['27725']]; AS de vuelta invertida [['unknown'], ['3356'], ['3549'], ['3356'], ['6762'], ['11960'], ['27725'], ['unknown'], ['27725']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

## Rusia - comparación de sentidos

| Protocolo | Ronda | IDs ida / vuelta | IP únicas ida / vuelta | Jaccard IP intermedias | Observación incompleta |
| --- | --- | --- | --- | --- | --- |
| UDP | 1 | 227925416 / 227925724 | 10 / 8 | 0.000 | True |
| ICMP | 1 | 227925939 / 227927183 | 10 / 9 | 0.000 | True |
| TCP | 1 | 227927414 / 227928192 | 10 / 7 | 0.000 | True |
| UDP | 2 | 227961705 / 227962594 | 9 / 8 | 0.000 | True |
| ICMP | 2 | 227962892 / 227964087 | 10 / 9 | 0.000 | True |
| TCP | 2 | 227964166 / 227964896 | 8 / 8 | 0.000 | True |

Tabla tipo 2: UDP, ronda 1. Las otras rondas permanecen en CSV.

| HOP | IP_IDA | IP_VUELTA |
| --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.19.17 [non_global] |
| 2 | 100.88.0.1 [non_global] | 80.71.208.96 [AS12389] |
| 3 | 10.87.0.3 [non_global] | 87.226.151.154 [AS12389] |
| 4 | 10.87.0.3 [non_global]; 10.87.0.46 [non_global] | 192.168.193.171 [non_global] |
| 5 | 10.87.0.46 [non_global] | 172.29.39.131 [non_global] |
| 6 | *; 100.88.0.1 [non_global]; 192.168.100.1 [non_global] | 212.133.1.53 [AS3356] |
| 7 | 154.54.92.41 [AS174] | 200.189.207.14 [AS3549] |
| 8 | *; 154.54.29.157 [AS174] | 8.243.191.90 [AS3356] |
| 9 | 154.54.167.185 [AS174] | * |
| 10 | 154.54.10.210 [AS174] | * |
| 11 | 195.22.211.61 [AS6762] | * |
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
| 5 | * | 172.29.39.185 [non_global] |
| 6 | 154.54.92.41 [AS174] | 212.133.1.53 [AS3356] |
| 7 | 154.54.3.29 [AS174] | 200.189.207.14 [AS3549] |
| 8 | 154.54.168.85 [AS174] | 8.243.191.90 [AS3356] |
| 9 | 154.54.10.210 [AS174] | 186.189.89.115 [AS52341] |
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
| 3 | 10.87.0.3 [non_global] | 87.226.151.154 [AS12389] |
| 4 | 10.87.0.46 [non_global] | 192.168.193.171 [non_global] |
| 5 | * | * |
| 6 | 154.54.92.41 [AS174] | 212.133.1.53 [AS3356] |
| 7 | 154.54.3.29 [AS174] | 200.189.207.14 [AS3549] |
| 8 | 154.54.168.85 [AS174] | 8.243.191.90 [AS3356] |
| 9 | 154.54.10.210 [AS174] | * |
| 10 | 195.22.211.61 [AS6762] | * |
| 11 | *; 195.22.214.161 [AS6762] | * |
| 12 | * | * |
| 13 | * | * |
| 14 | * | NO_MEDIDO |
| 15 | * | NO_MEDIDO |
| 16 | * | NO_MEDIDO |
| 255 | * | * |

UDP, ronda 1: AS de ida [['unknown'], ['174'], ['6762'], ['unknown']]; AS de vuelta invertida [['unknown'], ['3356'], ['3549'], ['3356'], ['unknown'], ['12389'], ['unknown']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

ICMP, ronda 1: AS de ida [['unknown'], ['174'], ['6762'], ['unknown']]; AS de vuelta invertida [['3356'], ['3549'], ['3356'], ['unknown'], ['12389'], ['unknown']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

TCP, ronda 1: AS de ida [['unknown'], ['174'], ['6762'], ['unknown']]; AS de vuelta invertida [['unknown'], ['3356'], ['3549'], ['3356'], ['unknown'], ['12389'], ['unknown']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

UDP, ronda 2: AS de ida [['unknown'], ['174'], ['unknown'], ['174'], ['6762'], ['unknown']]; AS de vuelta invertida [['unknown'], ['3356'], ['3549'], ['3356'], ['unknown'], ['12389'], ['unknown']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

ICMP, ronda 2: AS de ida [['unknown'], ['174'], ['6762'], ['unknown']]; AS de vuelta invertida [['3356'], ['3549'], ['3356'], ['unknown'], ['12389'], ['unknown']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

TCP, ronda 2: AS de ida [['unknown'], ['174'], ['unknown'], ['174'], ['6762'], ['unknown']]; AS de vuelta invertida [['12389'], ['unknown'], ['3356'], ['3549'], ['3356'], ['unknown'], ['12389'], ['unknown']]. Coincidencia del orden observado de IP: False; de secuencia AS: False. No permite afirmar simetría completa por observaciones incompletas.

## 4. Public Path

Por destino se selecciona un par RIPE del mismo protocolo, ronda e IPv4 pública. Se maximiza la unión de IP, luego se minimizan saltos sin respuesta y separación temporal. El grafo es dirigido; las adyacencias son inferidas por traceroute, los huecos son explícitos y no se crean enlaces cartesianos entre respuestas múltiples.

Destino 138.204.230.242: mediciones seleccionadas [227942829, 227942832]. Publicación y UUID público pendientes.

Destino 200.14.48.134: mediciones seleccionadas [227953132, 227953345]. Publicación y UUID público pendientes.

Destino 90.150.251.81: mediciones seleccionadas [227925939, 227927183]. Publicación y UUID público pendientes.

## Reproducción, integridad y limitaciones

Análisis utilizado: resultados/analisis_20261027T001138_a8f6b3d9. Regenerar con ./main analyze después de conservar las consultas ASN; ./main verify comprueba los manifiestos. Exportar PCAP con ./main packet-export y contrastar patrones con ./main patterns. El código, configuración activa y original, capturas, tablas, grafos y originales se reúnen con ./main bundle, excluyendo credenciales y claves privadas.

Reproducción local acreditada en reproduccion_ronda_1.json: 51 ejecuciones regeneradas sin nuevas mediciones ni consultas ASN, con tablas, métricas y tres CX2 idénticos. Se verificaron 2405 archivos del paquete. El alcance corresponde a las ejecuciones incluidas en esa constancia; la publicación de grafos se verifica por separado.

Las mediciones describen las rutas observadas en estos horarios y bajo estos protocolos. No cuantifican por sí solas velocidad de acceso, congestión sostenida, censura o reglas de filtrado. Los timeouts y las rutas incompletas se conservan como resultados con sus límites de interpretación.

## Referencias

https://www.caida.org/catalog/software/scamper/

https://www.wireshark.org/docs/man-pages/tshark.html

https://atlas.ripe.net/docs/

https://stat.ripe.net/docs/data-api/api-endpoints/network-info

https://www.ndexbio.org/docs/using-the-ndex-api/

https://cytoscape.org/cx/cx2/cx2-visual-styles/

## Anexo de capturas

![Preparación inicial, 26-10-2026: api configurada sin secreto](../../capturas/api_configurada_sin_secreto.png)

![Vista local de cierre: primera ronda completa, 51 ejecuciones y 17 por destino; sesión WOM 186.189.89.115](../../capturas/campana_ronda1_casa204144_completa.jpg)

![Preparación inicial, 26-10-2026: creditos 50000](../../capturas/creditos_50000.png)

![ndex cuenta reconectada sesion2](../../capturas/ndex_cuenta_reconectada_sesion2.jpg)

![Preparación inicial, 26-10-2026: registro exitoso](../../capturas/registro_exitoso.png)

![RIPE Atlas, medición 227905859: TCP desde la sonda 1018487 hasta Valparaíso; nueve saltos observados](../../capturas/ripe_actual_TCP_227905859.jpg)

![RIPE 227916578: vuelta ICMP desde Cuba; IP pública observada, identidad del equipo respondiente sin establecer](../../capturas/ripe_cuba_vuelta_ICMP_227916578.jpg)

![RIPE 227925416: Rusia UDP; respuestas múltiples y 18 registros de TTL, incluido 255 no consecutivo; ruta incompleta](../../capturas/ripe_rusia_UDP_TTL255_227925416.jpg)

![Preparación inicial, 26-10-2026: sonda 1018487 connected](../../capturas/sonda_1018487_connected.png)

![Preparación inicial, 26-10-2026: sonda 31416 abandoned](../../capturas/sonda_31416_abandoned.png)

![Preparación inicial, 26-10-2026: sonda 6652 connected](../../capturas/sonda_6652_connected.png)

![Preparación inicial, 26-10-2026: sonda 870 ipv4 actual](../../capturas/sonda_870_ipv4_actual.png)

![sonda ipv4 WOM nueva sesion](../../capturas/sonda_ipv4_WOM_nueva_sesion.jpg)

![sonda reconectada WOM](../../capturas/sonda_reconectada_WOM.jpg)

![wireshark cita tcp ripe sesion2](../../capturas/wireshark_cita_tcp_ripe_sesion2.jpg)

![wireshark cita tcp scamper sesion2](../../capturas/wireshark_cita_tcp_scamper_sesion2.jpg)

![Wireshark: ripe / traceroute / ICMP | sesión 186.189.89.115](../../capturas/wireshark_ripe_traceroute_ICMP_casa204144.jpg)

![Wireshark: ripe / traceroute / TCP | sesión 186.189.89.115](../../capturas/wireshark_ripe_traceroute_TCP_casa204144.jpg)

![Wireshark: ripe / traceroute / UDP | sesión 186.189.89.115](../../capturas/wireshark_ripe_traceroute_UDP_casa204144.jpg)

![Wireshark: scamper / trace / icmp-paris | sesión 186.189.89.115](../../capturas/wireshark_scamper_trace_icmp-paris_casa204144.jpg)

![Wireshark: scamper / trace / icmp | sesión 186.189.89.115](../../capturas/wireshark_scamper_trace_icmp_casa204144.jpg)

![Wireshark: scamper / trace / tcp-ack | sesión 186.189.89.115](../../capturas/wireshark_scamper_trace_tcp-ack_casa204144.jpg)

![Wireshark: scamper / trace / tcp | sesión 186.189.89.115](../../capturas/wireshark_scamper_trace_tcp_casa204144.jpg)

![Wireshark: scamper / trace / udp-paris | sesión 186.189.89.115](../../capturas/wireshark_scamper_trace_udp-paris_casa204144.jpg)

![Wireshark: scamper / trace / udp | sesión 186.189.89.115](../../capturas/wireshark_scamper_trace_udp_casa204144.jpg)

![Wireshark: scamper / tracelb / icmp-echo | sesión 186.189.89.115](../../capturas/wireshark_scamper_tracelb_icmp-echo_casa204144.jpg)

![Wireshark: scamper / tracelb / tcp-ack-sport | sesión 186.189.89.115](../../capturas/wireshark_scamper_tracelb_tcp-ack-sport_casa204144.jpg)

![Wireshark: scamper / tracelb / tcp-sport | sesión 186.189.89.115](../../capturas/wireshark_scamper_tracelb_tcp-sport_casa204144.jpg)

![Wireshark: scamper / tracelb / udp-dport | sesión 186.189.89.115](../../capturas/wireshark_scamper_tracelb_udp-dport_casa204144.jpg)

![Wireshark: scamper / tracelb / udp-sport | sesión 186.189.89.115](../../capturas/wireshark_scamper_tracelb_udp-sport_casa204144.jpg)
