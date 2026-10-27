## Path Discovery: comparación de Scamper y RIPE Atlas

Tarea individual - Algoritmos de Ruteo. Fuente del enunciado: Tarea Individual.docx, conservada con hash. Fecha de elaboración en UTC: 2026-10-26T21:17:07.146065+00:00.

Estado de campaña al generar: 24/153; esta edición analiza 22 ejecuciones principales válidas; 3 pilotos conservados y separados; 0/3 grafos públicos registrados. El documento es de avance mientras queden evidencias pendientes.

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

Ronda 1: 22/51 ejecuciones válidas. Inicio observado: 2026-10-26T20:46:19.639257+00:00; cierre observado: 2026-10-26T21:07:33.444089+00:00.

Ronda 2: 0/51 ejecuciones válidas. Inicio observado: pendiente; cierre observado: pendiente.

Ronda 3: 0/51 ejecuciones válidas. Inicio observado: pendiente; cierre observado: pendiente.

La unidad normalizada es una respuesta por intento y TTL. Se preservan respuestas múltiples, errores y timeouts. Un TTL 255 separado de los anteriores se conserva como registro, sin inventar los TTL intermedios ni enlaces entre capas no consecutivas. Los ASN son asociaciones IP-prefijo obtenidas con RIPEstat y no una ruta BGP observada.

## 1. Path Discovery Scamper

## Valparaiso - 138.204.230.242

| Método | Rondas | Mediana IP únicas | Cobertura | Jaccard entre rondas | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| icmp | 1 | 9 | 100.0% | No contrastado | 9 | 4.5 | 1 |
| icmp-paris | 1 | 9 | 100.0% | No contrastado | 9 | 4.8 | 1 |
| udp | 1 | 9 | 100.0% | No contrastado | 9 | 3.8 | 1 |
| udp-paris | 1 | 9 | 100.0% | No contrastado | 10 | 5.5 | 1 |
| tcp | 1 | 0 | 0.0% | No contrastado | 10 | 53.8 | 0 |
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
| udp-dport | 1 | Ninguna | 93 | 57 |
| icmp-echo | 1 | Ninguna | 44 | 57 |
| udp-sport | 1 | Ninguna | 48 | 57 |
| tcp-sport | 1 | Ninguna | 38 | 57 |
| tcp-ack-sport | 1 | Ninguna | 27 | 57 |

Las IP adicionales se comparan contra la unión de los seis trace de la misma ronda. Más IP con más paquetes se interpreta como una relación entre cobertura y costo, sin atribuir superioridad independiente del presupuesto de sondas.

## Habana - 200.14.48.134

| Método | Rondas | Mediana IP únicas | Cobertura | Jaccard entre rondas | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| icmp | 1 | 13 | 76.5% | No contrastado | 22 | 51.4 | 1 |
| icmp-paris | 1 | 13 | 76.5% | No contrastado | 23 | 55.6 | 1 |
| udp-paris | 1 | 13 | 66.7% | No contrastado | 28 | 76.0 | 1 |
| udp | 1 | 11 | 85.7% | No contrastado | 17 | 29.8 | 0 |
| tcp | 1 | 0 | 0.0% | No contrastado | 10 | 54.1 | 0 |

Métodos con mayor información según mediana de IP únicas, cobertura y estabilidad: icmp, icmp-paris. Empate en estos criterios. Selección provisional: faltan rondas. La ausencia de llegada se conserva y no invalida automáticamente una medición.

Tabla tipo 1, ronda 1. Las rondas 2 y 3 y todos los intentos están en los anexos CSV de este análisis. Se conserva más de una IP por TTL cuando corresponde.

| HOP | udp | icmp | udp-paris | icmp-paris | tcp | tcp-ack |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | 192.168.100.1 [non_global] | ? not_recorded | NO_MEDIDO |
| 2 | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | 100.88.0.1 [non_global] | ? not_recorded | NO_MEDIDO |
| 3 | 10.87.0.3 [non_global] | 10.87.0.2 [non_global] | 10.87.0.3 [non_global] | 10.87.0.2 [non_global] | ? not_recorded | NO_MEDIDO |
| 4 | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | 10.87.0.46 [non_global] | ? not_recorded | NO_MEDIDO |
| 5 | ? not_recorded | ? not_recorded | 10.87.0.46 [non_global] | ? not_recorded | ? not_recorded | NO_MEDIDO |
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

Las IP adicionales se comparan contra la unión de los seis trace de la misma ronda. Más IP con más paquetes se interpreta como una relación entre cobertura y costo, sin atribuir superioridad independiente del presupuesto de sondas.

## Rusia - 90.150.251.81

| Método | Rondas | Mediana IP únicas | Cobertura | Jaccard entre rondas | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |

Tabla tipo 1, ronda 1. Las rondas 2 y 3 y todos los intentos están en los anexos CSV de este análisis. Se conserva más de una IP por TTL cuando corresponde.

Sin resultados disponibles para esta tabla.

| tracelb | Ronda | IP adicionales frente a unión de 6 trace | Sondas tracelb | Sondas de referencia |
| --- | --- | --- | --- | --- |

Las IP adicionales se comparan contra la unión de los seis trace de la misma ronda. Más IP con más paquetes se interpreta como una relación entre cobertura y costo, sin atribuir superioridad independiente del presupuesto de sondas.

## 2. Path Discovery RIPE

La definición efectiva, la solicitud, el ID, la sonda participante y los tiempos reales se conservan para cada medición. La aceptación de una solicitud no se contó como ejecución: se esperó un resultado con el ID y sonda correctos. Las capturas locales de ida permiten contar solicitudes; las de vuelta son parciales y no permiten reconstruir todo el tráfico remoto.

## Valparaiso - protocolos RIPE de ida

| Protocolo | Rondas | Mediana IP únicas | Cobertura | Jaccard | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ICMP | 1 | 9 | 100.0% | No contrastado | 27 | 23.8 | 1 |
| TCP | 1 | 9 | 100.0% | No contrastado | 27 | 12.1 | 1 |
| UDP | 1 | 9 | 100.0% | No contrastado | 27 | 10.0 | 1 |

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

Sin resultados disponibles para esta tabla.

## Rusia - protocolos RIPE de ida

| Protocolo | Rondas | Mediana IP únicas | Cobertura | Jaccard | Mediana sondas | Mediana duración (s) | IP destino observada |
| --- | --- | --- | --- | --- | --- | --- | --- |

Sin resultados disponibles para esta tabla.

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
| ip.id | Variable; rango observado 4983 a 5479; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 76; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 1; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 1500 a 4044; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
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
| ip.id | Variable; rango observado 39744 a 39994; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 88; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 6; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 32503 a 34801; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
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
| ip.id | Variable; rango observado 11144 a 11370; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 76; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 17; n=27 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 61128 a 63402; n=27. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
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
| frame.len | Constante: 58; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 44; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 17; n=9 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Incremento -257 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| udp.srcport | Constante: 32769; n=9 | Pendiente: aún no hay otra ronda contrastada |
| udp.dstport | Constante: 33435; n=9 | Pendiente: aún no hay otra ronda contrastada |
| udp.length | Constante: 24; n=9 | Pendiente: aún no hay otra ronda contrastada |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=9 | Pendiente: aún no hay otra ronda contrastada |
| udp.payload | Variable; longitudes observadas [16] bytes; n=9. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| data.data | Variable; longitudes observadas [16] bytes; n=9. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

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
| frame.len | Constante: 58; n=93 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=93 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=93 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Variable; rango observado 1 a 9; n=93. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=93 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 44; n=93 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 17; n=93 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 56053 a 58193; n=93. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| udp.srcport | Constante: 32769; n=93 | Pendiente: aún no hay otra ronda contrastada |
| udp.dstport | Variable; rango observado 33435 a 33461; n=93. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| udp.length | Constante: 24; n=93 | Pendiente: aún no hay otra ronda contrastada |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=93 | Pendiente: aún no hay otra ronda contrastada |
| udp.payload | Variable; longitudes observadas [16] bytes; n=93. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| data.data | Variable; longitudes observadas [16] bytes; n=93. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [16] bytes. Bytes iniciales: 66b10000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

## scamper / tracelb / udp-sport

Ficha ilustrada para 138.204.230.242. Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones.

| Campo | Regla observada en ronda 1 | Contraste rondas 2 y 3 |
| --- | --- | --- |
| frame.len | Constante: 58; n=48 | Pendiente: aún no hay otra ronda contrastada |
| ip.src | Constante: 192.168.100.7; n=48 | Pendiente: aún no hay otra ronda contrastada |
| ip.dst | Constante: 138.204.230.242; n=48 | Pendiente: aún no hay otra ronda contrastada |
| ip.ttl | Variable; rango observado 1 a 5; n=48. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| ip.id | Incremento 1 por sonda; base propia de cada ejecución; n=48 | Pendiente: aún no hay otra ronda contrastada |
| ip.len | Constante: 44; n=48 | Pendiente: aún no hay otra ronda contrastada |
| ip.proto | Constante: 17; n=48 | Pendiente: aún no hay otra ronda contrastada |
| ip.checksum | Variable; rango observado 57122 a 58193; n=48. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| udp.srcport | Variable; rango observado 32769 a 32774; n=48. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| udp.dstport | Constante: 33435; n=48 | Pendiente: aún no hay otra ronda contrastada |
| udp.length | Constante: 24; n=48 | Pendiente: aún no hay otra ronda contrastada |
| udp.checksum | Incremento 1 por sonda; base propia de cada ejecución; n=48 | Pendiente: aún no hay otra ronda contrastada |
| udp.payload | Variable; longitudes observadas [16] bytes; n=48. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |
| data.data | Variable; longitudes observadas [16] bytes; n=48. No se predice valor exacto. | Pendiente: aún no hay otra ronda contrastada |

Payload observado: [16] bytes. Bytes iniciales: 66b10000000000000000000000000000. Offsets que cambiaron dentro de la ejecución: [1].

Restricción observada: la suma de payload_word0_BE, udp.checksum, udp.srcport, udp.dstport módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada.

El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia.

Control de recepción TCP: {"reviewed_scamper_tcp_runs": 4, "runs_with_matching_icmp_quotes": 4, "runs_with_pcap_warts_discrepancy": 4, "interpretation": "Correlación estricta por direcciones, IPID, puertos y orden temporal. Presencia en PCAP no implica aceptación por Scamper. Causa de la diferencia no establecida; no demuestra bloqueo TCP de los routers."}. Las respuestas presentes en PCAP y ausentes en WARTS se informan por separado; no prueban filtrado de red. Detalle reproducible en resultados/correlacion_tcp_captura.json.

Candidatos de respuesta selectiva detectados: 172. La ausencia de una IP en un método no demuestra una regla de firewall: puede deberse a carga, balanceo, pérdida o rutas diferentes. Se requiere corroboración entre rondas y pruebas dirigidas acotadas para cada herramienta.

Pruebas dirigidas de respuesta selectiva pendientes. Este requisito no se da por cerrado por la mera lista de candidatos.

## 3. Path way RIPE: ida y vuelta

Cada comparación conserva la numeración desde cada origen y también compara el orden inverso de la vuelta. Las IP corresponden a interfaces observadas; direcciones distintas no demuestran routers distintos ni se asume alias entre interfaces. Las secuencias AS tampoco prueban una ruta BGP.

## Valparaiso - comparación de sentidos

| Protocolo | Ronda | IDs ida / vuelta | IP únicas ida / vuelta | Jaccard IP intermedias | Observación incompleta |
| --- | --- | --- | --- | --- | --- |
| UDP | 1 | 227903487 / 227903721 | 9 / 7 | 0.071 | True |
| ICMP | 1 | 227905446 / 227905809 | 9 / 7 | 0.077 | False |
| TCP | 1 | 227905859 / 227905911 | 9 / 6 | 0.077 | True |

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

## Habana - comparación de sentidos

| Protocolo | Ronda | IDs ida / vuelta | IP únicas ida / vuelta | Jaccard IP intermedias | Observación incompleta |
| --- | --- | --- | --- | --- | --- |

Tabla tipo 2: UDP, ronda 1. Las otras rondas permanecen en CSV.

Sin resultados disponibles para esta tabla.

Tabla tipo 2: ICMP, ronda 1. Las otras rondas permanecen en CSV.

Sin resultados disponibles para esta tabla.

Tabla tipo 2: TCP, ronda 1. Las otras rondas permanecen en CSV.

Sin resultados disponibles para esta tabla.

## Rusia - comparación de sentidos

| Protocolo | Ronda | IDs ida / vuelta | IP únicas ida / vuelta | Jaccard IP intermedias | Observación incompleta |
| --- | --- | --- | --- | --- | --- |

Tabla tipo 2: UDP, ronda 1. Las otras rondas permanecen en CSV.

Sin resultados disponibles para esta tabla.

Tabla tipo 2: ICMP, ronda 1. Las otras rondas permanecen en CSV.

Sin resultados disponibles para esta tabla.

Tabla tipo 2: TCP, ronda 1. Las otras rondas permanecen en CSV.

Sin resultados disponibles para esta tabla.

## 4. Public Path

Por destino se selecciona un par RIPE del mismo protocolo, ronda e IPv4 pública. Se maximiza la unión de IP, luego se minimizan saltos sin respuesta y separación temporal. El grafo es dirigido; las adyacencias son inferidas por traceroute, los huecos son explícitos y no se crean enlaces cartesianos entre respuestas múltiples.

Destino 138.204.230.242: mediciones seleccionadas [227905446, 227905809]. Publicación y UUID público pendientes.

## Reproducción, integridad y limitaciones

Análisis utilizado: resultados/analisis_20261026T210739_9c7bbca5. Regenerar con ./main analyze después de conservar las consultas ASN; ./main verify comprueba los manifiestos. Exportar PCAP con ./main packet-export y contrastar patrones con ./main patterns. El código, configuración activa y original, capturas, tablas, grafos y originales se reúnen con ./main bundle, excluyendo credenciales y claves privadas.

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

![campana sesion WOM 20 mediciones](../../capturas/campana_sesion_WOM_20_mediciones.jpg)

![Preparación inicial, 26-10-2026: creditos 50000](../../capturas/creditos_50000.png)

![ndex cuenta reconectada sesion2](../../capturas/ndex_cuenta_reconectada_sesion2.jpg)

![Preparación inicial, 26-10-2026: registro exitoso](../../capturas/registro_exitoso.png)

![RIPE Atlas, medición 227905859: TCP desde la sonda 1018487 hasta Valparaíso; nueve saltos observados](../../capturas/ripe_actual_TCP_227905859.jpg)

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
