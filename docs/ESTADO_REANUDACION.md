# Estado y continuidad al 26-10-2026

Sesión activa: `casa_20261026T204144_f8fa5b43`, IPv4 `186.189.89.115`, WOM AS52341, prefijo `186.189.89.0/24`. El usuario confirmó conexión domiciliaria sin VPN. La sonda RIPE 1018487 está conectada y coincidió con los dos servicios de IP en el preflight `datos/originales/preflight_20261026T204152_e49dd179`, sin bloqueos.

## Ejecución actual

El servicio finito `path-discovery-casa-20261026-204144.service` ejecuta el piloto, su inspección reproducible TShark y, si queda validado, las tres rondas. No iniciar otro coordinador ni repetir POST mientras esté activo. Se mantiene un inhibidor temporal de reposo/suspensión; se libera al finalizar. El proceso no se reinicia automáticamente después de un error o reinicio del equipo.

```bash
systemctl --user status path-discovery-casa-20261026-204144.service
./main status
tail -n 30 resultados/casa_20261026T204144_f8fa5b43_supervisor.log
systemd-inhibit --list
```

Los logs por ronda tienen el prefijo `casa_20261026T204144_f8fa5b43_`. Los contadores de la sesión están en `.state/campaign.json`; el piloto aceptado en `.state/pilot.json`; las rondas procesadas en `.state/postprocessing.json`. Ante `running` sin proceso o `needs_review`, inspeccionar originales antes de decidir una repetición. No alterar horas de ejecución ni declarar aceptado un POST sin resultado.

## Sesión histórica

Los 60 resultados completos de `186.189.107.115` no cuentan en las nuevas 153 celdas. Su estado, configuraciones públicas, capturas y decisiones permanecen conservados. Archivo sellado: `datos/originales/cambio_sesion_20261026T204144_9c115e26`. Informe histórico: `informe/sesiones/186.189.107.115_casa_20261026T204144_f8fa5b43/informe.pdf`.

```bash
./main analyze --session-ip 186.189.107.115
```

Las capturas antiguas conservan su asociación original a PCAP y se marcan como históricas; no se reasignan a nuevas ejecuciones. Los 14 métodos de la primera ronda nueva ya se revisaron en Wireshark 4.6.6 y se conservaron capturas nuevas; la revisión sellada está en `datos/originales/revision_wireshark_casa_20261026T204144_f8fa5b43`. El contraste entre rondas sigue pendiente.

## Segunda ronda y continuación

La segunda ronda terminó el 27-10-2026 a las 00:08:47 UTC (26-10, 21:08:47 en Santiago), con 51/51 celdas completas. El análisis sellado `resultados/analisis_20261027T001138_a8f6b3d9` reúne 102 mediciones válidas de las dos rondas, sin invalidaciones registradas. La tercera inició a las 00:38:59 UTC y terminó a las 02:04:58 UTC (26-10, 23:04:58 Santiago). El análisis `resultados/analisis_20261027T020719_b8304fe1` registra 153 ejecuciones válidas y ninguna invalidada. El servicio terminó correctamente. Las pruebas dirigidas corroboraron un caso RIPE y un segundo caso Scamper; el primer candidato Scamper no se corroboró y permanece conservado. La captura `capturas/campana_ronda2_casa204144_completa.jpg` muestra el cierre de la segunda ronda, no su estado posterior.

## Primera ronda cerrada y reproducida

La ronda 1 terminó el 26-10-2026 a las 22:11:37 UTC (19:11:37 Santiago): **51/51 celdas válidas**, distribuidas en 18 trace, 15 tracelb, 9 RIPE de ida y 9 de vuelta. Análisis sellado: `resultados/analisis_20261026T221234_87acb72d`. No contiene resultados de la sesión anterior. La ronda 2 comienza como mínimo a las 22:41:37 UTC; la ronda 3 mantiene la misma separación tras el cierre de la segunda.

El paquete de avance `entrega/20261026T221959_2c887a28/paquete_preparacion.tar.gz` se extrajo y verificó sin red: **51 ejecuciones, 59 archivos de resultados idénticos, 2405 archivos del paquete y 163 manifiestos originales verificados**. Constancia: `resultados/reproduccion_ronda_1.json`. No es la entrega final. La revisión detectó y corrigió la exclusión por nombre de una respuesta pública RIPE llamada `local.json`; la configuración privada activa y las credenciales siguen excluidas.

El informe de avance de la primera ronda analizó 51 ejecuciones e incorporó las 14 revisiones GUI y los controles TCP; su revisión visual quedó registrada en `resultados/revision_pdf_sesion_activa.json`. El informe activo fue regenerado automáticamente tras la segunda ronda con 102 ejecuciones; se revisará nuevamente después de la tercera. El avance anterior de 22 mediciones se conserva en `informe/avances/casa_20261026T204144_f8fa5b43/22_mediciones/`. Pasaron 63 pruebas.

## Interpretación de estabilidad corregida

El informe conservado de las dos primeras rondas es histórico y usó Jaccard 1 cuando ambas ejecuciones no observaron IP. Esa convención puede confundirse con estabilidad real de ruta. El cálculo se corrigió para excluir pares de conjuntos vacíos; si todos los pares están vacíos, la estabilidad queda sin valor y se muestra «Sin IP observadas». El análisis automático de la tercera ronda utilizará el código corregido. Pasaron 64 pruebas, incluida la comparación entre rutas vacías y rutas con respuesta.

## Reproducción y revisión de 153 mediciones

`resultados/reproduccion_ronda_3.json` acredita la regeneración offline de 153 ejecuciones con 59 archivos de resultados idénticos, 4004 archivos del paquete y 281 manifiestos originales verificados. El informe de avance actual contiene 75 páginas y fue revisado visualmente; `resultados/revision_pdf_sesion_activa.json` registra su SHA-256. El primer caso Scamper dirigido no se corroboró; una segunda prueba acotada sí corroboró el contraste para 195.22.211.61 con ICMP frente a UDP, y la prueba RIPE corroboró 200.0.16.25 con TCP frente a ICMP. Ninguna de estas observaciones identifica una regla de firewall por sí sola. Pasaron 64 pruebas.

## Cierres pendientes

Publicar los tres grafos definitivos en NDEx con dos IDs RIPE cada uno, revisar el informe final y reproducir su entrega. Los grafos definitivos están en `resultados/analisis_20261027T020719_b8304fe1/grafos/` y todavía no tienen UUID públicos. La revisión automática rechazó activar la casilla de visibilidad pública sin confirmación explícita en el momento de esa acción; no se publicó ni se evitó esa revisión. La sesión de NDEx puede requerir autenticación del usuario al momento de publicar.

La API key RIPE permanece en `.env`, fuera de Git y de la entrega. No mostrar ni copiar secretos. La sonda utiliza Docker Compose, red del host e identidad persistente. NDEx requiere sesión del usuario en el navegador para publicar; no extraer credenciales ni tokens.

## Reproducción

En una copia de la entrega, copiar `config/reproduccion.json` a `config/local.json` y ejecutar `./main analyze` sin `--online-asn`; usa consultas ASN conservadas. `./main verify` comprueba originales. `./main analyze --session-ip IP` selecciona explícitamente una sesión histórica. Nunca ejecutar `campaign` para regenerar tablas o grafos.

Las ejecuciones nuevas cargadas con la versión actual del adquiridor registran relojes monotonic/boottime e identificador de arranque; una suspensión o cambio de arranque impide aceptar el resultado como continuo. La primera ronda ya estaba en curso al incorporar este control y se mantiene protegida por el inhibidor de suspensión y sus registros de sistema.

El análisis distingue el contador WARTS de Scamper y las solicitudes observadas en PCAP. El clasificador de solicitudes, revisión 2, filtra el protocolo del método; sus derivados se regeneran sin repetir mediciones. Hay contraste representativo de las tres familias en `resultados/revision_familias.json` y verificador reproducible sin red en `scripts/reproducir_entrega.py`. El avance de 22 mediciones se conserva en `informe/avances/casa_20261026T204144_f8fa5b43/22_mediciones`.
