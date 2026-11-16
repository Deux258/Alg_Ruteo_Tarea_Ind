import json

from .probabilidades import TABLAS_RIESGO
from .topologia import copy_rows, psql


def leer_resultados(modelo_id):
    salida = psql("""
BEGIN ISOLATION LEVEL REPEATABLE READ;
CREATE TEMP TABLE modelo_solicitado (id text) ON COMMIT DROP;
COPY modelo_solicitado FROM STDIN WITH (FORMAT csv);
""" + copy_rows([(modelo_id,)]) + """
WITH modelo AS (
    SELECT m.id, m.evento_id, m.configuracion
    FROM tarea_ruteo.modelo_falla m JOIN modelo_solicitado s USING (id)
), escenarios AS (
    SELECT s.id, s.radio_km, s.probabilidad
    FROM modelo m CROSS JOIN LATERAL jsonb_to_recordset(m.configuracion->'escenarios')
        AS s(id text, radio_km double precision, probabilidad numeric)
), componentes AS (
    SELECT s.id AS escenario, c.node, c.component
    FROM escenarios s CROSS JOIN modelo m
    CROSS JOIN LATERAL pgr_connectedComponents(format(
        'SELECT e.id, e.source, e.target, 1::float8 AS cost, 1::float8 AS reverse_cost
         FROM tarea_ruteo.enlaces e JOIN tarea_ruteo.probabilidades_falla p ON p.enlace_id = e.id
         WHERE p.modelo_id = %L AND p.distancia_km > %L::double precision',
        m.id, s.radio_km
    )) c
    UNION ALL
    SELECT NULL, node, component FROM tarea_ruteo.componentes
), terminales_por_componente AS (
    SELECT s.id, count(*) AS n
    FROM (SELECT id FROM escenarios UNION ALL SELECT NULL) s
    CROSS JOIN tarea_ruteo.terminales t
    LEFT JOIN componentes c ON c.escenario IS NOT DISTINCT FROM s.id AND c.node = t.vertice_id
    -- pgRouting omite vértices sin enlaces supervivientes. Cada uno conserva su propio componente.
    GROUP BY s.id, coalesce(c.component, t.vertice_id)
), pares AS (
    SELECT id, sum(n * (n - 1) / 2)::bigint AS conectados
    FROM terminales_por_componente GROUP BY id
), denominador AS (
    SELECT count(*) * (count(*) - 1) / 2 AS total FROM tarea_ruteo.terminales
), posteriores AS (
    SELECT s.*, p.conectados AS pares_conectados,
           p.conectados::numeric / d.total AS attr,
           (SELECT count(*) FROM tarea_ruteo.probabilidades_falla f CROSS JOIN modelo m
            WHERE f.modelo_id = m.id AND f.distancia_km <= s.radio_km) AS enlaces_caidos
    FROM escenarios s JOIN pares p USING (id) CROSS JOIN denominador d
), enlaces AS (
    SELECT e.id, f.distancia_km, f.probabilidad
    FROM tarea_ruteo.enlaces e JOIN tarea_ruteo.probabilidades_falla f ON f.enlace_id = e.id
    JOIN modelo m ON m.id = f.modelo_id
)
SELECT json_build_object(
    'huella_topologia', (SELECT md5(string_agg(id::text || ':' || encode(ST_AsEWKB(geom, 'NDR'), 'hex'), ',' ORDER BY id))
                        FROM tarea_ruteo.enlaces),
    'total_enlaces', (SELECT count(*) FROM tarea_ruteo.enlaces),
    'modelo', m.configuracion,
    'evento', json_build_object('id', q.id, 'magnitud', q.magnitud, 'tiempo_ms', q.tiempo_ms,
        'longitud', ST_X(q.geom), 'latitud', ST_Y(q.geom), 'profundidad_km', q.profundidad_km),
    'enlaces', (SELECT json_agg(e ORDER BY e.id) FROM enlaces e),
    'terminales', (SELECT json_agg(t ORDER BY t.id) FROM (
        SELECT id, nombre, roles, longitud, latitud, vertice_id, distancia_vertice_m
        FROM tarea_ruteo.terminales
    ) t),
    'attr', json_build_object(
        'modelo_id', m.id, 'evento_id', q.id, 'pares_totales', d.total,
        'pares_conectados_antes', b.conectados, 'antes', b.conectados::numeric / d.total,
        'despues_esperado', (SELECT sum(probabilidad * pares_conectados) / d.total FROM posteriores),
        'escenarios', (SELECT json_agg(p ORDER BY p.radio_km, p.id) FROM posteriores p)
    )
)
FROM modelo m JOIN tarea_ruteo.evento_sismico q ON q.id = m.evento_id
CROSS JOIN denominador d JOIN pares b ON b.id IS NULL;
COMMIT;
""")
    if not salida:
        raise ValueError(f'No hay resultados para el modelo {modelo_id}')
    return json.loads(salida)


def generar_sql(resultados):
    huella_topologia = resultados['huella_topologia']
    evento = resultados['evento']
    modelo = resultados['modelo']
    filas_evento = [(evento['id'], evento['magnitud'], evento['tiempo_ms'],
                    evento['profundidad_km'], evento['longitud'], evento['latitud'])]
    filas_modelo = [(modelo['id'], evento['id'], json.dumps(modelo, ensure_ascii=False))]
    filas_enlaces = [(modelo['id'], e['id'], e['distancia_km'], e['probabilidad'])
                     for e in resultados['enlaces']]
    return """-- Probabilidades de falla de los enlaces de fibra del Maule.
-- Ejecutar con psql sobre la topología creada por scripts/topologia.py.
BEGIN;
SELECT pg_advisory_xact_lock(7171717);
DO $$
BEGIN
    IF (SELECT md5(string_agg(id::text || ':' || encode(ST_AsEWKB(geom, 'NDR'), 'hex'), ',' ORDER BY id))
        FROM tarea_ruteo.enlaces) IS DISTINCT FROM '""" + huella_topologia + """' THEN
        RAISE EXCEPTION 'La topología no coincide con la usada para calcular el riesgo';
    END IF;
END $$;

""" + TABLAS_RIESGO + """
CREATE TEMP TABLE evento_exportado (
    id text, magnitud double precision, tiempo_ms bigint, profundidad_km double precision,
    longitud double precision, latitud double precision
) ON COMMIT DROP;
COPY evento_exportado FROM STDIN WITH (FORMAT csv);
""" + copy_rows(filas_evento) + """
INSERT INTO tarea_ruteo.evento_sismico (id, magnitud, tiempo_ms, profundidad_km, geom)
SELECT id, magnitud, tiempo_ms, profundidad_km, ST_SetSRID(ST_MakePoint(longitud, latitud), 4326)
FROM evento_exportado
ON CONFLICT (id) DO UPDATE SET magnitud = excluded.magnitud, tiempo_ms = excluded.tiempo_ms,
    profundidad_km = excluded.profundidad_km, geom = excluded.geom;

CREATE TEMP TABLE modelo_exportado (LIKE tarea_ruteo.modelo_falla) ON COMMIT DROP;
COPY modelo_exportado (id, evento_id, configuracion) FROM STDIN WITH (FORMAT csv);
""" + copy_rows(filas_modelo) + """
INSERT INTO tarea_ruteo.modelo_falla (id, evento_id, configuracion)
SELECT id, evento_id, configuracion FROM modelo_exportado
ON CONFLICT (id) DO UPDATE SET evento_id = excluded.evento_id, configuracion = excluded.configuracion;

CREATE TEMP TABLE riesgo_exportado (LIKE tarea_ruteo.probabilidades_falla) ON COMMIT DROP;
COPY riesgo_exportado (modelo_id, enlace_id, distancia_km, probabilidad) FROM STDIN WITH (FORMAT csv);
""" + copy_rows(filas_enlaces) + """
INSERT INTO tarea_ruteo.probabilidades_falla (modelo_id, enlace_id, distancia_km, probabilidad)
SELECT modelo_id, enlace_id, distancia_km, probabilidad FROM riesgo_exportado
ON CONFLICT (modelo_id, enlace_id) DO UPDATE
SET distancia_km = excluded.distancia_km, probabilidad = excluded.probabilidad;
COMMIT;
"""
