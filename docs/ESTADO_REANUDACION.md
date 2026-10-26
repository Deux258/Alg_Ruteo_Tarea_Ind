# Estado de ejecución

Actualizado el 26 de octubre de 2026. Los horarios y nombres de ejecuciones usan UTC.

La campaña se reanudó desde la conexión fija domiciliaria WOM, en Quilicura. IPv4 pública de la sesión: 186.189.107.115; prefijo 186.189.107.0/24; AS52341 según RIPEstat. La sonda local es 1018487. La presencia de 100.88.0.1 es compatible con NAT del operador, sin confirmar CGNAT ni explicar por sí sola las rutas inversas incompletas.

## Destinos autorizados

| Destino | IPv4 activa | ID RIPE |
|---|---|---:|
| Valparaíso | 138.204.230.242 | 6652 |
| Habana | 200.14.48.134 | 12734 |
| Rusia | 90.150.251.81 | 870 |

El usuario autorizó reemplazar 31416 indisponible y actualizar la IP de 870. No se atribuye esta autorización al docente. `docs/CAMBIOS_DESTINOS.md`, las consultas originales y `config/campana_enunciado.json` conservan las diferencias y su justificación.

## Campaña en curso

El contador vigente se obtiene con `./main status`; el plan tiene 153 celdas únicas. `.state/campaign.json` conserva cada celda y su run. El supervisor persistente de la reanudación registra su PID en `.state/continuacion_recuperada.pid` y su salida en `resultados/continuacion_recuperada.log`; las rondas posteriores usan `resultados/campana_ronda_2.log` y `campana_ronda_3.log`.

No iniciar otra campaña mientras este supervisor siga activo. El proceso ejecuta una medición local por vez, con 20 pps máximos de Scamper, y separa las rondas al menos treinta minutos desde el cierre anterior. Después de cada ronda exporta paquetes, consulta los ASN faltantes, genera tablas y contrasta patrones. Un error o resultado incierto detiene la continuación para revisión; no se reenvía automáticamente un POST.

La ronda 1 sufrió una discontinuidad nocturna. Se conservaron todos los originales y se excluyó un tracelb de más de ocho horas; se repite esa celda y otra sin WARTS final. La adjudicación está sellada y enlazada desde `config/exclusiones_calidad.json`. `docs/INCIDENTES_CAMPANA.md` explica el alcance y la limitación temporal. No cambiar parámetros ni editar originales para ocultar la discontinuidad.

## Wireshark y evidencia visual

Se revisaron catorce PCAP de campaña en Wireshark gráfico real 4.6.6 mediante el navegador local, con un contenedor Compose e imagen fijada por digest. Los PCAP están montados en solo lectura. No se controló la aplicación nativa instalada del host.

Las catorce capturas por método y una cita ICMP adicional están en `capturas/wireshark_*.png`. La procedencia está en `resultados/revision_wireshark_gui.json` y en la revisión sellada `datos/originales/revision_gui_wireshark_20261026T115707_2aa4f046`. El índice general conserva hashes en `capturas/indice.json`. Las fichas HTML históricas se identifican como datos procesados con TShark y no como GUI.

El piloto fue aceptado con revisión reproducible TShark sellada, sin afirmar revisión manual de sus tres PCAP. Esa declaración se conserva. Las imágenes gráficas nuevas corresponden a los catorce métodos de la campaña.

Algunas respuestas ICMP a TCP están en PCAP y no en WARTS. `scripts/correlacion_tcp.py` las relaciona por direcciones, IPID, puertos y tiempo. No interpretar automáticamente los ceros de Scamper como routers que bloquean TCP. Se preparó `scripts/diagnostico_tcp.py`, control adicional con la opción oficial rawtcp y puertos de origen; se ejecuta de forma secuencial en la separación entre rondas, con `kind=targeted_validation`, fuera de las 153 celdas y del entrenamiento de patrones.

## Cuentas y próximos cierres

RIPE Atlas está habilitado. La API key tiene exclusivamente permiso para programar mediciones hasta el 24-11-2026; permanece en `.env`, modo 600 y fuera de Git y entrega. Las claves privadas de la sonda permanecen en volúmenes Docker. No mostrar ni copiar esos secretos.

La sesión de NDEx fue restablecida por el usuario el 26-10-2026. Aún faltan los tres UUID públicos. Esperar el análisis de las tres rondas para elegir el par de cada destino; subir CX2 por la sesión del navegador, hacerlo público y ejecutar `./main publish-receipt RUTA_CX2 UUID` para verificarlo de forma anónima. Conservar captura de cada grafo y sus dos IDs RIPE.

El informe en `informe/path_discovery` es un avance hasta completar campaña, contraste entre rondas, respuesta selectiva, grafos públicos y verificación. Regenerar con `scripts/informe_academico.py ANALISIS_FINAL` usando Python con ReportLab; inspeccionar visualmente el PDF y generar la entrega con `./main bundle ANALISIS_FINAL`.

## Reproducción sin nuevas mediciones

`config/reproduccion.json` contiene los parámetros efectivos sin credenciales. En una copia extraída de la entrega, copiar ese archivo a `config/local.json` y ejecutar `./main analyze` sin `--online-asn`: usa las consultas RIPEstat conservadas. `./main patterns` utiliza solo las exportaciones actuales de ejecuciones principales admitidas; excluye pilotos, diagnósticos y resultados descartados. `./main verify` valida los manifiestos. No ejecutar `campaign` para regenerar tablas o grafos.

Los pilotos universitarios y los intentos inválidos permanecen separados y no cuentan como campaña. Si cambia la IPv4 pública, preservar la sesión y revisar los pares afectados antes de continuar.
