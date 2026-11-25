import json
import math
from statistics import NormalDist

if __package__:
    from .topologia import ROOT, copy_rows, psql
else:
    from topologia import ROOT, copy_rows, psql


TABLAS_RIESGO = """CREATE TABLE IF NOT EXISTS tarea_ruteo.evento_sismico (
 id text PRIMARY KEY, magnitud double precision NOT NULL, tiempo_ms bigint NOT NULL,
 profundidad_km double precision NOT NULL, geom geometry(Point,4326) NOT NULL);
CREATE TABLE IF NOT EXISTS tarea_ruteo.modelo_falla (
 id text PRIMARY KEY, evento_id text NOT NULL REFERENCES tarea_ruteo.evento_sismico(id), configuracion jsonb NOT NULL);
CREATE TABLE IF NOT EXISTS tarea_ruteo.probabilidades_falla (
 modelo_id text NOT NULL REFERENCES tarea_ruteo.modelo_falla(id), enlace_id bigint NOT NULL REFERENCES tarea_ruteo.enlaces(id),
 distancia_km double precision NOT NULL CHECK (distancia_km >= 0),
 probabilidad double precision NOT NULL CHECK (probabilidad BETWEEN 0 AND 1),
 PRIMARY KEY (modelo_id, enlace_id));
"""


def escenarios_shakemap(modelo, atenuacion):
    if atenuacion['eventid'] != modelo['evento_id']:
        raise ValueError('La curva de atenuación pertenece a otro sismo')
    distancias = atenuacion['distances']['repi']
    curva = atenuacion['gmpe'][modelo['condicion_sitio']]['MMI']
    umbral = modelo['umbral_mmi']
    cantidad = modelo['cuantiles']
    if not isinstance(cantidad, int) or cantidad < 1:
        raise ValueError('El número de cuantiles debe ser un entero positivo')

    normal = NormalDist()
    escenarios = []
    for indice in range(cantidad):
        z = normal.inv_cdf((indice + 0.5) / cantidad)
        excesos = [media + z * sigma - umbral
                   for media, sigma in zip(curva['mean'], curva['stddev'], strict=True)]
        if len(excesos) != len(distancias):
            raise ValueError('La curva MMI y las distancias no coinciden')
        if excesos[0] < 0:
            radio = 0.0
        else:
            primer_cruce = next((i for i, valor in enumerate(excesos) if valor < 0), None)
            if primer_cruce is None:
                raise ValueError('El alcance de la curva USGS no basta para estimar el radio')
            anterior = primer_cruce - 1
            fraccion = excesos[anterior] / (excesos[anterior] - excesos[primer_cruce])
            radio = distancias[anterior] + fraccion * (distancias[primer_cruce] - distancias[anterior])
        escenarios.append({'id': f'cuantil_{indice + 1:02}', 'radio_km': radio,
                          'probabilidad': 1 / cantidad})
    return escenarios


def main():
    model_path = ROOT / 'config/modelo_falla.json'
    model = json.loads(model_path.read_text(encoding='utf-8'))
    event = json.loads((ROOT / model['evento_archivo']).read_text(encoding='utf-8'))
    if event['id'] != model['evento_id'] or event['properties']['mag'] != model['magnitud_evento']:
        raise ValueError('El evento no coincide con la configuración')
    if event['geometry']['type'] != 'Point':
        raise ValueError('El epicentro debe ser un punto')
    lon, lat, depth = event['geometry']['coordinates']
    if not all(math.isfinite(v) for v in (lon, lat, depth)) or not (-180 <= lon <= 180 and -90 <= lat <= 90):
        raise ValueError('Coordenadas inválidas')
    atenuacion = json.loads((ROOT / model['atenuacion_archivo']).read_text(encoding='utf-8'))
    scenarios = escenarios_shakemap(model, atenuacion)
    model['escenarios'] = scenarios
    features = json.loads((ROOT / 'datos/fibra_yafun.geojson').read_text(encoding='utf-8'))['features']
    event_rows = [(event['id'], event['properties']['mag'], event['properties']['time'], lon, lat, depth, model['id'], json.dumps(model, ensure_ascii=False))]
    scenario_rows = [(s['id'], s['radio_km'], s['probabilidad']) for s in scenarios]
    edge_rows = [(f['id'], json.dumps(f['geometry'])) for f in features]
    sql = '''BEGIN;
SELECT pg_advisory_xact_lock(7171717);
CREATE TEMP TABLE entrada_evento (id text, magnitud double precision, tiempo_ms bigint, lon double precision, lat double precision, profundidad double precision, modelo_id text, modelo_json jsonb) ON COMMIT DROP;
COPY entrada_evento FROM STDIN WITH (FORMAT csv);
''' + copy_rows(event_rows) + '''
CREATE TEMP TABLE entrada_escenarios (id text PRIMARY KEY, radio_km double precision, peso numeric) ON COMMIT DROP;
COPY entrada_escenarios FROM STDIN WITH (FORMAT csv);
''' + copy_rows(scenario_rows) + '''
CREATE TEMP TABLE entrada_enlaces (id bigint PRIMARY KEY, geom_json text) ON COMMIT DROP;
COPY entrada_enlaces FROM STDIN WITH (FORMAT csv);
''' + copy_rows(edge_rows) + '''
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM tarea_ruteo.enlaces) OR
    (SELECT count(*) FROM tarea_ruteo.enlaces) <> (SELECT count(*) FROM entrada_enlaces) OR
    EXISTS (SELECT 1 FROM entrada_enlaces i LEFT JOIN tarea_ruteo.enlaces e USING (id)
       WHERE e.id IS NULL OR NOT ST_OrderingEquals(e.geom, ST_SetSRID(ST_GeomFromGeoJSON(i.geom_json),4326))) THEN
   RAISE EXCEPTION 'Los enlaces de la base no coinciden con el GeoJSON';
 END IF;
END $$;
''' + TABLAS_RIESGO + '''
INSERT INTO tarea_ruteo.evento_sismico SELECT id, magnitud, tiempo_ms, profundidad, ST_SetSRID(ST_MakePoint(lon,lat),4326) FROM entrada_evento
ON CONFLICT (id) DO UPDATE SET magnitud=excluded.magnitud, tiempo_ms=excluded.tiempo_ms, profundidad_km=excluded.profundidad_km, geom=excluded.geom;
INSERT INTO tarea_ruteo.modelo_falla SELECT modelo_id, id, modelo_json FROM entrada_evento
ON CONFLICT (id) DO UPDATE SET evento_id=excluded.evento_id, configuracion=excluded.configuracion;
WITH distancias AS (
 SELECT e.id, ST_Distance(e.geom::geography, ST_SetSRID(ST_MakePoint(i.lon,i.lat),4326)::geography)/1000.0 AS distancia_km, i.modelo_id
 FROM tarea_ruteo.enlaces e CROSS JOIN entrada_evento i
), resultados AS (
 SELECT d.id, d.modelo_id, d.distancia_km,
        COALESCE(sum(s.peso) FILTER (WHERE s.radio_km > 0 AND d.distancia_km <= s.radio_km),0) AS probabilidad
 FROM distancias d CROSS JOIN entrada_escenarios s GROUP BY d.id, d.modelo_id, d.distancia_km
)
INSERT INTO tarea_ruteo.probabilidades_falla SELECT modelo_id, id, distancia_km, probabilidad FROM resultados
ON CONFLICT (modelo_id,enlace_id) DO UPDATE SET distancia_km=excluded.distancia_km, probabilidad=excluded.probabilidad;
COMMIT;
'''
    psql(sql)
    print(f"Probabilidades calculadas para {len(features)} enlaces del modelo {model['id']}")


if __name__ == '__main__':
    main()
