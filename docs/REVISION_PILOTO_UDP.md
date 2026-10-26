# Observaciones del piloto UDP

Revisión realizada sobre exportaciones de TShark 4.0.17, perteneciente a Wireshark, sin revisión de la interfaz gráfica. La evidencia sellada y las referencias a PCAP y bytes se localizan con `resultados/revision_piloto_udp_2026-10-25.json`.

| Campo | Scamper trace UDP | RIPE UDP de ida |
|---|---|---|
| Solicitudes emitidas observadas | 15 | 63 |
| TTL emitidos | 1–13, con reintentos | 1–21, tres solicitudes por TTL |
| Tamaño IPv4 | 44 bytes | 76 bytes |
| Longitud UDP | 24 bytes | 56 bytes |
| Puerto origen observado | 32769 | 20480 |
| Puerto destino | 33435 a 33449 | 33435 constante |
| IPID | 1 a 15 | Variable; sin incremento constante observado |
| Checksum UDP | 0xdfdc a 0xdfce, resta uno | 0x0001 a 0x003f, suma uno |
| Payload | 16 bytes cero | 48 bytes; varían sus dos primeros bytes |
| Citas ICMP correlacionadas | 11 | 40 |

Para el paquete n, contando desde uno dentro de esta ejecución de Scamper, se comprobó en los 15 paquetes `IPID=n`, `dport=33434+n` y `UDP checksum=0xdfdd-n`. La secuencia TTL depende de las respuestas y reintentos; no se confundió el número de emisión con el salto.

En los 63 paquetes RIPE se comprobó `UDP checksum=n` y que la palabra de los dos primeros bytes de payload vale `0x7c7d-n`. Los 46 bytes restantes conservan el texto y relleno de Atlas de esta captura. Estas compensaciones son compatibles con conservar la suma de comprobación mientras varía el identificador utilizado para correlación; no se extrapola su base numérica a otra ejecución sin contrastarla.

Las respuestas ICMP citan la cabecera IPv4 y UDP original. Se verificó la asociación por destino, IPID y puertos. NAT puede modificar esos campos, por lo que una cita no correlacionada no se descartará automáticamente de los resultados de la medición.

Las reglas anteriores describen este piloto. La campaña contrastará su constancia o variación entre ejecuciones y rondas antes de presentar predicciones generales. Los puertos origen y las bases de contadores pueden depender de la ejecución.

La vuelta RIPE 227477165 presenta respuestas intermedias en su resultado remoto y no llegó al destino. El PCAP local no contiene solicitudes remotas observables. Esto limita la inspección local de su transporte y no prueba una regla de firewall ni confirma CGNAT.
