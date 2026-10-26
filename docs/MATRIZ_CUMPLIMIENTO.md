# Matriz de cumplimiento

Los estados distinguen implementación disponible de evidencia académica pendiente. No constituyen una autoevaluación docente.

| Requisito del enunciado | Procedimiento | Evidencia | Estado al 26-10-2026 |
|---|---|---|---|
| ISP y prefijo público | preflight y confirmación ISP comercial | preflight.json, network-info.json de RIPEstat; URL BGP HE de referencia | IPv4/prefijo/AS verificados; WOM confirmado por el usuario |
| Scamper 20260902 | build-tools, fuente con SHA256 | versión e imagen | Implementado |
| Tres rutas con seis métodos | campaña, 54 ejecuciones trace | WARTS, JSONL, tabla1 por ronda | Campaña en curso; contador en ./main status |
| Comparar métodos | analyze | rankings.json, IP, cobertura y Jaccard | Implementado; primera ronda en curso y contraste entre rondas pendiente |
| Transporte y payload trace | packet-export, patterns, Wireshark | PCAPNG, JSON completo, TSV, predicciones | Catorce métodos revisados en GUI; contraste entre rondas pendiente |
| Respuesta selectiva Scamper | candidatos y pruebas dirigidas | selective_candidates.json y validación manual | Candidatos implementados; corroboración pendiente |
| Cinco modos tracelb por destino | campaña, 45 ejecuciones | WARTS y JSONL | Campaña en curso; contador en ./main status |
| IP adicionales tracelb | unión de seis métodos en misma ronda | tracelb_additional.json con referencia completa | Implementado; primera ronda en curso y contraste entre rondas pendiente |
| Transporte y payload tracelb | packet-export y Wireshark | fichas de cinco métodos | Cinco capturas GUI y originales conservados; contraste entre rondas pendiente |
| Sonda Docker e ID | probe-init, registro personal | clave pública, digest, ID | Compose operativo; sonda 1018487 Connected con captura |
| Créditos y API por consola | dashboard y clave en entorno | comprobación de saldo y solicitudes sin claves | 50.000 créditos iniciales observados; API funcional con permiso acotado |
| RIPE UDP, ICMP y TCP | 27 ejecuciones de ida | request, definition, ID y results | Campaña en curso; contador en ./main status |
| IP y AS por salto | normalize y RIPEstat | responses.csv y tablas ripe_ida | Pilotos y resultados de campaña disponibles; completar tres rondas |
| Transporte y payload RIPE | captura local de ida | PCAPNG, JSON, TSV y predicciones | Pilotos y resultados de campaña disponibles; completar tres rondas |
| Respuesta selectiva RIPE | candidatos y validación dirigida | misma IP, métodos y PCAP | Corroboración pendiente |
| Rutas inversas tres protocolos | 27 mediciones desde IDs remotos | request, results y captures parciales | Campaña en curso con adaptaciones autorizadas por el usuario y documentadas |
| Simetría y cantidad de IP | comparación IP/AS y orden inverso | symmetry.json y tabla2 por ronda | Implementación y revisión según resultados |
| Grafo por destino | par compatible con mayor información | tres CX2 y selection.json | Pares provisionales disponibles; selección final tras tres rondas |
| Tres UUID públicos con dos IDs cada uno | publish y lectura anónima | publication.json, summary, export | Cuenta iniciada en NDEx; tres publicaciones pendientes |
| Informe y reproducción | report, verify y bundle | MD/PDF, manifiesto y entrega.tar.gz | Informe de avance disponible; cierre pendiente |
