# Registrar la sonda de esta tarea

**Registro completado el 25 de octubre de 2026.** ID [1018487](https://atlas.ripe.net/probes/1018487/), estado Connected, ubicación aproximada Quilicura. Saldo inicial observado: 50.000 créditos. API key configurada en `.env` con permisos 600, únicamente Schedule a new measurement y vencimiento 24 de noviembre de 2026. No crear otra sonda ni otra clave para reanudar. Las capturas están en `resultados/registro_ripe_1018487/`.

Los pasos siguientes quedan como referencia para reproducir la configuración.

La sonda ya tiene una identidad persistente. Registrar la clave existente evita generar una sonda diferente.

1. Entrar a https://atlas.ripe.net/ y crear una cuenta RIPE NCC Access o iniciar sesión.
2. Abrir `resultados/sonda_clave_publica.txt` y copiar la línea completa desde `ssh-rsa` hasta su comentario final. Es la clave pública de la sonda Docker; no es la API key.
3. Abrir https://atlas.ripe.net/apply/swprobe/, pegar esa clave pública y completar los datos solicitados. Si pide ubicación, indicar la ubicación real de la conexión de casa. Enviar el registro y conservar el ID asignado. El procesamiento puede no ser inmediato.
4. Revisar en My Probes que la sonda corresponda al equipo y alcance el estado Connected. El contenedor se gestiona con `docker compose up -d atlas`, `docker compose ps` y `docker compose logs --tail 30 atlas`. Los volúmenes externos conservan la identidad; no eliminarlos.
5. Revisar My Credits. Si la cuenta es elegible y aparece Claim 50K free credits, reclamar ese saldo inicial. Si no aparece, comprobar las opciones disponibles en el dashboard; no depender del cupón de una presentación antigua. Confirmar saldo suficiente antes de realizar mediciones.
6. En la tarjeta My API Keys del dashboard, pulsar el símbolo `+`. Elegir una etiqueta, por ejemplo Tarea Path Discovery, mantener Enabled y añadir el permiso para crear mediciones (Schedule a new measurement o la denominación equivalente que muestre la interfaz). Guardar la clave en el momento de creación: se muestra completa una sola vez. No copiarla al chat.
7. En una terminal del equipo, ejecutar:

```bash
cd /home/diego/Documentos/GitHub/Alg_Ruteo_Tarea_Ind
python3 scripts/configurar_ripe.py
```

El asistente pide el ID de la sonda, ISP comercial y la API key. La entrada de la clave es oculta. Guarda `.env` con permisos 600 y `config/local.json`, ambos ignorados por Git. No hace solicitudes de medición ni gasta créditos.

8. Avisar al agente cuando termine el registro, indicando solamente el ID de la sonda. El agente verificará el estado, que su IP pública corresponda a la conexión de casa y los permisos antes del piloto RIPE.

La clave de la sonda identifica el contenedor. La API key autoriza a la cuenta a crear mediciones: son elementos distintos. Registrar la sonda no crea automáticamente una API key.

Fuentes: https://atlas.ripe.net/docs/howtos/software-probes/ ; https://atlas.ripe.net/docs/apis/rest-api-manual/authentication/api-keys/ ; https://atlas.ripe.net/docs/getting-started/credits/ .
