# Matriz de cumplimiento de la rúbrica actualizada

Fuente: `datos/originales/enunciado_actualizado_20261026/rubrica.txt` y enunciado del mismo directorio, conservados con manifiesto SHA-256. Puntaje máximo: 120. Esta matriz es de seguimiento: ninguna fila se considera cumplida hasta verificar la evidencia final seleccionada.

| Criterio | Puntos | Evidencia y acción para el máximo puntaje | Estado |
|---|---:|---|---|
| 1.1 Rutas Scamper, seis métodos y tres IP | 6 | WARTS, PCAP y tablas por destino de la selección vigente. | Verificado: 54 trace aceptados, tres destinos y tres rondas. |
| 1.2 Comparación de seis métodos | 6 | Tabla por destino: IP únicas, cobertura, estabilidad y costo; justificar el método elegido. | Verificado: tablas por destino y estadísticas de las tres rondas; informe §3.1. |
| 1.3 Tráfico trace, seis métodos | 18 | Fichas de transporte y payload con capturas de Wireshark, reglas observadas y predicciones verificadas en otra ronda. | Verificado: seis fichas, capturas reales y predicciones contrastadas; §3.2. |
| 1.4 Respuesta selectiva Scamper | 6 | Mismo IP, métodos contrastados, repeticiones y evidencia; especificar si la regla es hipótesis o está demostrada. | Observación corroborada: 37.79.226.46 responde ICMP y no se observa con UDP; no se demostró una ACL concreta. |
| 1.5 Ejecución tracelb, cinco modos | 5 | Originales y tablas de los cinco modos para las tres IP. | Verificado: 45 tracelb aceptados en los cinco modos. |
| 1.6 Mejora por tracelb | 5 | IP adicionales frente a la unión de trace y comparación de número de paquetes. | Verificado: IP adicionales y costo por destino/ronda; §3.3. |
| 1.7 Tráfico tracelb, cinco modos | 15 | Cinco fichas de Wireshark con transporte, payload y predicciones contrastadas. | Verificado: cinco fichas y predicciones contrastadas; §3.3. |
| 2.1 RIPE: IP y AS por salto | 3 | Tres tablas con UDP, ICMP y TCP, ASN y saltos vacíos explícitos. | Verificado: tres tablas principales y rondas adicionales en anexos. |
| 2.2 Comparación de tres protocolos RIPE | 3 | Comparación por destino, IP únicas y cobertura, con criterio de elección. | Verificado: comparación de tres protocolos y elección por destino; §3.4. |
| 2.3 Tráfico RIPE, tres protocolos | 18 | Tres fichas de Wireshark con bytes, transporte y patrón contrastado. | Verificado: tres fichas y predicciones contrastadas; §3.4. |
| 2.4 Respuesta selectiva RIPE | 3 | Misma IP observada y ausente por protocolo, con repeticiones e incertidumbre. | Observación corroborada: 200.0.16.25 responde TCP y no se observa con ICMP; no se demostró una ACL concreta. |
| 3.1 Obtención de ruta e interfaces | 6 | Tablas ida/vuelta y análisis de coincidencias; presentar interfaces del mismo router solo si existe evidencia de alias. | Tablas y coincidencias documentadas; no se demostró alias entre interfaces de un mismo router. Limitación explícita en §3.5. |
| 3.1 Comparación ida/vuelta | 6 | Nueve tablas destino/protocolo; cuantificar coincidencias y diferencias sin atribuir router por IP. | Verificado: nueve tablas principales, conteos, Jaccard y orden de capas; §3.5. |
| 4.1 Selección de ruta más completa | 6 | Registrar criterio reproducible, ronda, protocolo y dos IDs de medición para cada destino. | Verificado: selección reproducible con las tres rondas; §3.7. |
| 4.2 Grafo en NDEx | 4 | Tres grafos dirigidos con huecos y adyacencias inferidas; capturas y acceso público. | Verificado: tres grafos definitivos PUBLIC, recibos y capturas. |
| 4.3 UUID e IDs RIPE | 6 | Tres UUID, enlaces y descripción de cada grafo con los dos IDs originales. | Verificado: tres UUID y seis IDs RIPE vinculados al CX2 final. |
| 5 Presentación general | 4 | Informe con WOM, IP pública, prefijo, ASN y tres IP del enunciado actualizado. | Informe LaTeX con datos de portada suministrados, WOM, IP/prefijo/ASN, BGP HE y destinos actualizados; sujeto a revisión académica. |

La selección de originales aceptados está en `config/seleccion_revision.json`. El destino ruso anterior pertenece al conjunto histórico, no al dataset de la rúbrica. Las rondas rusas se obtienen en una campaña posterior; comparar tendencias dentro de cada destino, sin presentarlas como mediciones simultáneas de todos los destinos. Los resultados vacíos o discordantes se informan con sus limitaciones, sin inventar respuestas ni reglas de firewall.
