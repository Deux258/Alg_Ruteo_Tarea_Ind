import csv
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def psql(sql):
    result = subprocess.run(
        ['docker', 'compose', 'exec', '-T', 'db', 'psql', '-X', '-qAt',
         '-v', 'ON_ERROR_STOP=1', '-U', 'ruteo', '-d', 'ruteo'],
        cwd=ROOT, input=sql, encoding='utf-8', capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def copy_rows(rows):
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer, lineterminator='\n')
    writer.writerows(rows)
    return buffer.getvalue() + '\\.\n'


def main():
    features = json.loads((ROOT / 'datos/fibra_yafun.geojson').read_text(encoding='utf-8'))['features']
    with (ROOT / 'datos/nodos_clave.csv').open(encoding='utf-8', newline='') as stream:
        nodes = list(csv.DictReader(stream))
    if not features or len(nodes) < 2 or len({n['id'] for n in nodes}) != len(nodes):
        raise ValueError('Se requieren enlaces y al menos dos nodos con identificadores únicos')
    edges = [(f['id'], f['properties']['id_fuente'], json.dumps(f['geometry'])) for f in features]
    terminals = [(n['id'], n['nombre'], n['roles'], n['longitud'], n['latitud']) for n in nodes]
    sql = '''
BEGIN;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgrouting;
CREATE SCHEMA tarea_ruteo;
CREATE TABLE tarea_ruteo.entrada (id bigint PRIMARY KEY, id_fuente text, geometria text);
COPY tarea_ruteo.entrada FROM STDIN WITH (FORMAT csv);
''' + copy_rows(edges) + '''
CREATE TABLE tarea_ruteo.enlaces AS
SELECT id, id_fuente, ST_SetSRID(ST_GeomFromGeoJSON(geometria), 4326)::geometry(LineString,4326) AS geom,
       NULL::bigint AS source, NULL::bigint AS target
FROM tarea_ruteo.entrada;
ALTER TABLE tarea_ruteo.enlaces ADD PRIMARY KEY (id);
CREATE INDEX ON tarea_ruteo.enlaces USING gist (geom);
DROP TABLE tarea_ruteo.entrada;
SELECT pgr_createTopology('tarea_ruteo.enlaces', 0.000000001, 'geom', 'id');
DO $$ BEGIN
  IF EXISTS (SELECT FROM tarea_ruteo.enlaces WHERE source IS NULL OR target IS NULL OR ST_IsEmpty(geom) OR NOT ST_IsValid(geom)) THEN
    RAISE EXCEPTION 'Topología incompleta o geometría inválida';
  END IF;
END $$;
CREATE TABLE tarea_ruteo.terminales (id text PRIMARY KEY, nombre text, roles text, longitud double precision, latitud double precision);
COPY tarea_ruteo.terminales FROM STDIN WITH (FORMAT csv);
''' + copy_rows(terminals) + '''
ALTER TABLE tarea_ruteo.terminales ADD COLUMN enlace_id bigint;
ALTER TABLE tarea_ruteo.terminales ADD COLUMN vertice_id bigint;
ALTER TABLE tarea_ruteo.terminales ADD COLUMN distancia_linea_m double precision;
ALTER TABLE tarea_ruteo.terminales ADD COLUMN distancia_vertice_m double precision;
WITH ubicaciones AS (
  SELECT *, ST_SetSRID(ST_MakePoint(longitud, latitud), 4326) AS punto FROM tarea_ruteo.terminales
), candidatos AS (
  SELECT t.id, t.punto, e.id AS enlace_id, e.source, e.target, e.geom
  FROM ubicaciones t CROSS JOIN LATERAL (
    SELECT * FROM tarea_ruteo.enlaces ORDER BY ST_Distance(geom::geography, t.punto::geography), id LIMIT 1
  ) e
), seleccion AS (
  SELECT *, CASE WHEN ST_Distance(punto::geography, ST_StartPoint(geom)::geography) <=
                           ST_Distance(punto::geography, ST_EndPoint(geom)::geography)
                 THEN source ELSE target END AS vertice_id
  FROM candidatos
)
UPDATE tarea_ruteo.terminales t SET enlace_id = s.enlace_id, vertice_id = s.vertice_id,
  distancia_linea_m = ST_Distance(s.punto::geography, s.geom::geography),
  distancia_vertice_m = ST_Distance(s.punto::geography, v.the_geom::geography)
FROM seleccion s JOIN tarea_ruteo.enlaces_vertices_pgr v ON v.id = s.vertice_id WHERE t.id = s.id;
CREATE TABLE tarea_ruteo.componentes AS
SELECT * FROM pgr_connectedComponents('SELECT id, source, target, 1::float8 AS cost, 1::float8 AS reverse_cost FROM tarea_ruteo.enlaces');
COMMIT;
'''
    psql(sql)
    result = psql('''
WITH grupos AS (
  SELECT c.component, count(*) AS cantidad FROM tarea_ruteo.terminales t
  JOIN tarea_ruteo.componentes c ON c.node = t.vertice_id GROUP BY c.component
), metricas AS (
  SELECT (SELECT count(*) FROM tarea_ruteo.terminales) AS terminales,
         coalesce(sum(cantidad * (cantidad - 1) / 2), 0) AS pares_conectados FROM grupos
)
SELECT json_build_object('enlaces', (SELECT count(*) FROM tarea_ruteo.enlaces),
 'vertices', (SELECT count(*) FROM tarea_ruteo.enlaces_vertices_pgr),
 'componentes', (SELECT count(DISTINCT component) FROM tarea_ruteo.componentes),
 'terminales', terminales, 'pares_conectados', pares_conectados,
 'pares_totales', terminales * (terminales - 1) / 2,
 'attr', pares_conectados::numeric / (terminales * (terminales - 1) / 2),
 'nodos', (SELECT json_agg(json_build_object('id', t.id, 'nombre', t.nombre, 'enlace_id', t.enlace_id,
   'vertice_id', t.vertice_id, 'componente', c.component,
   'distancia_linea_m', round(t.distancia_linea_m::numeric, 1),
   'distancia_vertice_m', round(t.distancia_vertice_m::numeric, 1)) ORDER BY t.id)
   FROM tarea_ruteo.terminales t LEFT JOIN tarea_ruteo.componentes c ON c.node = t.vertice_id))
FROM metricas;
''')
    data = json.loads(result)
    (ROOT / 'datos/attr_base.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
