# Guía operativa

Ejecutar los comandos desde la raíz del proyecto. Python 3.11 o posterior y Docker son las dependencias del host. El código Python de medición/análisis usa la biblioteca estándar. El PDF añade ReportLab opcional.

## Preparación

```bash
./scripts/build-tools.sh
./scripts/test.sh
./main plan
./main sources
./main preflight
```

La tasa es como máximo 20 pps, con una sola tarea Scamper simultánea. Las capturas incluyen ICMP y el destino; el host escribe el flujo PCAPNG para conservar permisos correctos. Las mediciones reales requieren salida a Internet y acceso a Docker.

## Registrar la sonda y configurar el acceso

La sonda `path-discovery-atlas` se gestiona con Docker Compose. `./main probe-init` crea los volúmenes externos si es una instalación nueva, reutiliza la identidad existente y levanta el servicio `atlas`. Si encuentra el contenedor anterior detenido sin etiquetas Compose, lo conserva con un nombre `-legacy-...` y reutiliza sus volúmenes. La imagen queda fijada por digest en `compose.yaml` y `.state/probe_image.json`. Las claves privadas están en volúmenes Docker.

```bash
docker compose --env-file /dev/null up -d atlas
docker compose --env-file /dev/null ps
docker compose --env-file /dev/null logs --tail 30 atlas
docker compose --env-file /dev/null stop atlas
```

Los procesos de Scamper y captura son ejecuciones temporales del servicio `tools` mediante Compose, con red del host y sin iniciar la sonda como dependencia. `./main` carga únicamente las credenciales conocidas de `.env` como datos; no ejecuta el contenido del archivo. Las credenciales no se inyectan en los contenedores.

1. Crear una cuenta personal en https://access.ripe.net/.
2. Registrar la clave de `resultados/sonda_clave_publica.txt` en https://atlas.ripe.net/apply/swprobe/. Es una clave **pública**; no copiar claves privadas.
3. Esperar la asignación del ID y el estado Connected. El registro puede requerir procesamiento manual por RIPE.
4. Comprobar créditos en el dashboard. Reclamar los créditos iniciales si la cuenta es elegible o acumularlos con la sonda. Confirmar saldo suficiente antes de medir; el CLI no da por hecho el saldo de la cuenta.
5. Crear una API key con permiso para crear mediciones. Guardarla únicamente en `.env`, que queda ignorado por Git.
6. Crear `config/local.json` con el ID, ISP comercial, UDP observado y, si se conoce, la condición CGNAT. Ejemplo **de configuración, no de evidencia real**:

```json
{"local_probe_id": 1234567, "isp_comercial": "Completar", "udp_base_port": null, "cg_nat_confirmado": "pendiente", "baf_confirmed": true}
```

```bash
cp .env.example .env
chmod 600 .env
# Editar .env localmente. No enviar la API key por chat.
set -a
source .env
set +a
./main preflight
```

Para guardar el ID y la API key sin mostrar la clave ni escribirla en el historial, usar `python3 scripts/configurar_ripe.py` desde una terminal. Ver el paso a paso en `docs/REGISTRO_RIPE.md`. El archivo `.env` existente se conserva; no reemplazarlo con `.env.example` después de completar las credenciales.

La sonda usa puertos internos 12023 y 18080, para evitar el servicio de drones en 8080. No se cambian reglas globales del firewall. No borrar los volúmenes `pd-atlas-*`: contienen la identidad persistente de la sonda.

## Destinos y adaptaciones autorizadas

El usuario autorizó reemplazar 31416 por 6652 y actualizar la IP de 870. Ver `docs/CAMBIOS_DESTINOS.md`. El archivo `config/campana_enunciado.json` conserva la configuración original y `config/campana.json` contiene los destinos activos. Las respuestas API originales y la justificación están selladas con SHA-256. No atribuir la decisión del estudiante al docente.

## Piloto

Usar inicialmente la sonda cubana, que coincide con la IP publicada:

```bash
./main pilot --target 200.14.48.134 --tool scamper --method udp
./main pilot --target 200.14.48.134 --tool ripe --method UDP --direction ida
./main pilot --target 200.14.48.134 --tool ripe --method UDP --direction vuelta
./main packet-export NOMBRE_DEL_RUN
```

Revisar el PCAPNG de RIPE UDP y el `emitted.tsv`: anotar el menor puerto destino observado en `udp_base_port`. Mantener el puerto TCP 80. Comprobar la definición RIPE, cuyos demás parámetros se omiten en la solicitud para conservar defaults.

Repetir el piloto Scamper UDP después de fijar el puerto; agregar el run piloto anterior a `excluded_runs` en `config/local.json` para que no entre en análisis repetidos. Conservar todos los originales. La aceptación comprueba los tres resultados, sus hashes, la IP pública común y el puerto UDP observado. Puede acreditarse revisión manual de Wireshark o revisión reproducible con TShark, conservando el modo real utilizado:

```bash
./main pilot-review --target 200.14.48.134
# Usar la carpeta devuelta por pilot-review:
./main pilot-accept --target 200.14.48.134 --packet-review resultados/revision_piloto_FECHA_ID
# Alternativa únicamente si se revisó realmente la GUI:
# ./main pilot-accept --wireshark-reviewed
```

El usuario confirmó que Wireshark está instalado en el host. La sesión de automatización solo expone el navegador, por lo que se preparó `compose.wireshark.yaml` para abrir Wireshark gráfico local en http://127.0.0.1:8767/. Su imagen se fija por digest y sus PCAP se montan en `/captures` como solo lectura. No se habilitan capacidades de captura sobre la red del host. `scripts/preparar_wireshark.py` reutiliza la imagen fijada por digest en `config/wireshark-image.env.example`. Si falta, espera el cierre de la primera ronda antes de descargar ese mismo digest para evitar contaminar sus RTT. TShark y Dumpcap del servicio tools siguen disponibles. En la GUI, abrir el PCAP, filtrar por destino y examinar cabeceras y bytes; guardar las capturas en `capturas/`.

## Campaña

```bash
./main campaign --round 1
# Esperar al menos treinta minutos desde el cierre de la ronda anterior.
./main campaign --round 2
./main campaign --round 3
./main status
```

Cada ronda contiene 51 trabajos. Un fallo deja el trabajo en `needs_review`; el programa no repite un POST incierto. Revisar el run original y el dashboard antes de adoptar una decisión de recuperación. `ripe-fetch NOMBRE_DEL_RUN` crea otro directorio de recuperación con el mismo ID RIPE y conserva el original sellado. No crea una medición adicional. Si el POST no devolvió ID, recuperarlo desde el dashboard antes de continuar y conservar esa decisión en el registro de operación.

Para continuar una campaña tras recuperar un resultado, actualizar únicamente el registro del trabajo correspondiente en `.state/campaign.json` con `status: completed` y su nuevo `run_id`, luego repetir el comando de esa ronda. Esta recuperación es deliberadamente explícita. No editar resultados ni manifiestos.

Si cambia la IP pública, el proceso se detiene. Conservar la sesión anterior; comenzar otra requiere separar la evidencia, volver a verificar la conexión y repetir los pares afectados. No reutilizar resultados de sesiones diferentes como si formaran un par.

## Análisis reproducible

```bash
./main verify
./main analyze --online-asn
# Posteriormente, sin consultas de red:
./main analyze
./main packet-export NOMBRE_DEL_RUN
./main patterns
./main report
```

`analyze --include-pilots` produce una revisión exploratoria que se marca expresamente como piloto. No acredita las 153 ejecuciones. Los análisis se guardan en directorios nuevos; elegir el análisis pertinente para publicar y entregar.

`analyze --diagnostic-pilots` permite verificar el procesamiento de un piloto excluido por cambio de IP pública, como el capturado en la universidad. Las filas conservan `run_status` y `pilot`; el contador de mediciones principales válidas permanece en cero. El formato WARTS/JSON puede omitir detalles de intentos sin respuesta: se marca `not_recorded` en lugar de inventar timeouts y se conserva el PCAP para examinar los paquetes enviados.

Las tablas distinguen `*` (timeout), errores, huecos sin registro y `NO_MEDIDO`. Las IP no globales conservan `non_global` en lugar de ASN inventados. Los campos aleatorios o sin muestras suficientes no se presentan como predicciones. Revisar manualmente payload y encabezados citados en `packets_full.json` y PCAP: el clasificador automático de patrones no sustituye esa explicación.

Para respuesta selectiva, revisar `selective_candidates.json`, elegir la misma IP observada repetidamente con un método y ausente con otro, y usar pruebas dirigidas acotadas con Scamper en una terminal, conservando comandos, PCAP y WARTS. La no aparición en un traceroute puede deberse a otra ruta; no atribuir una ACL sin evidencia adicional.

## NDEx y entrega

Crear una cuenta en https://www.ndexbio.org/ y configurar las credenciales en el entorno local. Los tres grafos se publican explícitamente desde el análisis elegido:

```bash
./main publish resultados/analisis_FECHA/grafos/IP.cx2.json
./main report
./main bundle resultados/analisis_FECHA
```

Se conserva intento, respuesta, UUID, lectura anónima y exportación. Si ocurre un timeout durante la publicación, revisar la cuenta antes de repetirla. Completar la evidencia con una captura del visor NDEx por grafo. `bundle` empaqueta por lista permitida, excluye `.state`, `.tools`, `.env`, claves privadas y `config/local.json`, y comprueba que las credenciales activas no aparezcan en archivos de texto.

La captura y publicación de rutas revela la IP pública de la conexión, como pide el trabajo. Revisar el contenido concreto del paquete antes de entregarlo al docente.

## Wireshark gráfico y reproducción de la entrega

El servicio gráfico tiene una imagen pública fijada por digest y acceso limitado a localhost. Monta los PCAP en solo lectura; no necesita permisos de captura del host.

```bash
docker compose --env-file config/wireshark-image.env.example -f compose.wireshark.yaml --profile gui up -d wireshark
# Abrir http://127.0.0.1:8767/ y File > Open > /captures/...
```

La revisión de catorce métodos está documentada en `resultados/revision_wireshark_gui.json`. Las leyendas de Echo Request sobre ausencia de Echo Reply no niegan respuestas ICMP Time Exceeded. `scripts/correlacion_tcp.py` distingue respuestas presentes en PCAP de las aceptadas por Scamper. Los controles rawtcp son adicionales y no cambian la campaña principal.

En una copia extraída de la entrega, `cp config/reproduccion.json config/local.json` permite regenerar con `./main analyze` sin `--online-asn`. No se necesita la API key para este análisis. No ejecutar `campaign` para reproducir tablas. `./main patterns` usa exclusivamente las exportaciones actuales de ejecuciones principales admitidas, sin pilotos ni diagnósticos. `scripts/estructura_payload.py` conserva segmentos ASCII, offsets y restricciones entre palabras del payload y cabeceras, aprendiendo la base de cada ejecución de su primer paquete y contrastando los posteriores.

Con la sesión NDEx iniciada, usar New > Upload Networks, seleccionar el CX2 del análisis final, marcar Make network public y confirmar Import Network. Después registrar el UUID con `./main publish-receipt RUTA_CX2 UUID`; esta comprobación usa lectura anónima y no extrae credenciales del navegador. Capturar cada grafo y sus dos IDs RIPE.

El paquete se marca como entrega final únicamente si, además de las 153 celdas, acredita tres grafos públicos del análisis seleccionado, catorce métodos revisados, corroboraciones selectivas y un informe actualizado. Si falta algo, se genera como paquete de avance y se detallan sus comprobaciones en `package_status.json`.


## Verificación de una entrega cerrada sin red

Generar el paquete desde un análisis de ronda cerrada o desde la campaña completa, mientras no se estén agregando nuevas mediciones principales a esa sesión. Ejecutar `python3 scripts/reproducir_entrega.py entrega/IDENTIFICADOR/paquete_preparacion.tar.gz` (o `entrega.tar.gz` para el cierre completo). El verificador extrae en un directorio temporal, comprueba cada SHA-256, bloquea las llamadas HTTP antes de importar el CLI, valida los originales y ejecuta `analyze` sin consultas nuevas. Exige igualdad de bytes en respuestas, métricas, tablas y CX2; el resumen solo puede cambiar su fecha de generación. Conserva la constancia en `resultados/reproduccion_ronda_N.json`. Un paquete hecho mientras avanzaba una ronda puede contener más originales que el análisis incluido; en ese caso el verificador informa la diferencia y no declara reproducción acreditada.
