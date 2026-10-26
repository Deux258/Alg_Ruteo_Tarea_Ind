# Adaptación de los destinos de la campaña

Decisión del estudiante del 25 de octubre de 2026. No se atribuye esta autorización al docente.

| Contexto | IP del enunciado | Sonda original | IP utilizada | Sonda utilizada |
|---|---|---:|---|---:|
| Valparaíso | 138.204.228.2 | 31416 | 138.204.230.242 | 6652 |
| Habana | 200.14.48.134 | 12734 | 200.14.48.134 | 12734 |
| Rusia | 37.79.153.66 | 870 | 90.150.251.81 | 870 |

La API pública de RIPE Atlas registra la sonda 31416 como Abandoned desde el 14 de diciembre de 2025. Esto acredita su indisponibilidad para participar en las mediciones actuales; no demuestra una falla del proveedor ni permite atribuir la desconexión a una decisión concreta de RIPE. Se conserva el estado y su fecha como justificación de la sustitución.

El estudiante autorizó elegir un reemplazo. Se seleccionó la sonda pública 6652, un ancla conectada de INSACOM SpA, por pertenecer al mismo AS61506 y estar declarada en Valparaíso, aproximadamente a 0,29 km de la ubicación declarada de la sonda original. Las posiciones son aproximadas; no se afirma que ambas sondas compartan edificio, router o enlace. Su prefijo actual es 138.204.230.0/24, diferente del prefijo original 138.204.228.0/24. La sustitución conserva ciudad y AS, pero cambia el extremo medido.

La sonda rusa 870 está conectada y publica 90.150.251.81. El estudiante autorizó actualizar únicamente la IP y conservar el ID. Se verificará la correspondencia antes de cada medición RIPE. Si cambia durante la campaña, se detendrá la ejecución para conservar la coherencia de los pares.

La configuración original se conserva en `config/campana_enunciado.json`; `config/campana.json` contiene los destinos activos. El DOCX y los originales históricos no se modificaron. Las respuestas API, criterios y autorizaciones están en `datos/originales/seleccion_sondas_*/` y `datos/originales/actualizacion_rusia_*/`, con manifiestos SHA-256.

No se utiliza la indisponibilidad de una sonda para concluir nada sobre velocidad, censura o calidad de su ISP. Las referencias del enunciado motivan los casos de estudio y no constituyen resultados de esta campaña.
