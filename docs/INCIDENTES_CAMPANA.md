# Incidentes y límites temporales de la campaña

## Sesión histórica 186.189.107.115 (fuera de la campaña activa)

Los siguientes párrafos describen únicamente las mediciones de la sesión anterior, conservadas como anexo histórico. No corresponden a las nuevas rondas de 186.189.89.115.

La ronda 1 comenzó el 26-10-2026 a las 01:30:20 UTC y sufrió dos interrupciones. La primera fue un error de acceso a un servicio externo antes de enviar una solicitud RIPE; se comprobó que no existía POST y se reanudó esa celda sin duplicarla. La segunda produjo un intervalo extendido durante la noche; no se establece su causa a partir de los registros disponibles.

El tracelb UDP-dport ruso `scamper_20261026T024854_fb1d5630` abarcó desde las 02:48:54 hasta las 11:36:02 UTC. Se conserva íntegro y se excluye de la comparación por calidad temporal. El intento TCP-sport `scamper_20261026T114443_ad95de92` perdió su controlador y solo dejó 70 bytes WARTS sin registro final; se conserva como intento interrumpido, no como medición válida. Se detuvo su captura residual antes de reanudar. Las decisiones, estados anterior y posterior y hashes están sellados en `datos/originales/incidente_interrupcion_20261026T114921_f34fd3cb`. Las dos celdas se repiten explícitamente; los otros resultados se conservan.

La ronda 1 no constituye una ventana continua. Las comparaciones que la incorporan deben mostrar sus horas reales y advertir que cambios entre métodos pueden reflejar cambios temporales. Las rondas siguientes se separan al menos treinta minutos desde el cierre efectivo anterior. No se reconstruyen tiempos ni se cambia la fecha de los originales para ocultar esta limitación.

En TCP se observaron respuestas ICMP en PCAP que no fueron incorporadas por Scamper a WARTS. Se contrastan por destino, direcciones, IPID, puertos y tiempo en `resultados/correlacion_tcp_captura.json`. Esta discrepancia de captura y detección impide atribuir automáticamente los ceros de Scamper a un firewall o a ausencia de respuesta en la red. Los resultados de la herramienta y las observaciones de paquetes se presentan por separado.


## Cambio de sesión del 26-10-2026 y campaña activa

El equipo reinició y volvió a suspenderse. El coordinador anterior ya no estaba activo; se conservaron 51 celdas completas de la primera ronda y nueve de la segunda. El intento TCP-sport `scamper_20261026T124823_a8e33742` dejó 70 bytes WARTS sin resultado final. Se selló como intento interrumpido con fecha de revisión; su hora real de finalización es desconocida. No se cuenta como medición válida.

La IPv4 pública cambió de 186.189.107.115 a 186.189.89.115, prefijo 186.189.89.0/24, AS52341. El usuario confirmó nuevamente WOM domiciliaria y ausencia de VPN. La API de la sonda 1018487 mostró inicialmente direcciones de AS3549; tras reconectar el contenedor y consultar nuevamente, informó la misma IPv4 WOM que dos servicios externos. La causa de la discrepancia inicial no quedó establecida. No se afirma que el usuario estuviera en otra red ni que hubiera una VPN.

Los estados previos, parámetros públicos, informe y registros del sistema se conservaron en `datos/originales/cambio_sesion_20261026T204144_9c115e26` (consultar la ruta exacta en `config/reproduccion.json`, campo `session_archive`). Los 60 resultados históricos permanecen disponibles y pueden analizarse mediante `./main analyze --session-ip 186.189.107.115`. El contador activo y las comparaciones nuevas filtran la IPv4 de sesión y no mezclan ambos orígenes.

Se preparó un nuevo piloto completo y tres rondas desde la IPv4 vigente. Un servicio transitorio de systemd ejecuta una sola campaña, sin reinicio automático, y mantiene un bloqueo temporal de reposo y suspensión. Antes de cada ejecución se verifica la IPv4 esperada; cualquier cambio detiene las mediciones. El bloqueo se libera al terminar el proceso. Reiniciar o apagar el equipo todavía interrumpe la campaña y exige revisar el intento antes de reanudar.
