import argparse
import json
from pathlib import Path
from zipfile import ZipFile

import shapefile


CAPA = "Respuesta_T5610/fibra_optica_detectada"


def extraer_fibra(archivo):
    with ZipFile(archivo) as zip_file:
        proyeccion = zip_file.read(f"{CAPA}.prj").decode("ascii")
    if not proyeccion.startswith('GEOGCS["GCS_WGS_1984",'):
        raise ValueError("La capa debe venir en WGS84 geográfico")

    features = []
    with shapefile.Reader(f"{archivo}/{CAPA}.shp", encoding="latin-1") as capa:
        if capa.shapeType != shapefile.POLYLINE:
            raise ValueError("Se esperaba una capa de líneas de fibra")
        for fila in capa.iterShapeRecords():
            identificador = fila.record.oid + 1
            features.append({
                "type": "Feature",
                "id": identificador,
                "properties": {"id_fuente": fila.record["id"]},
                "geometry": fila.shape.__geo_interface__,
            })
    if not features:
        raise ValueError("La capa de fibra está vacía")
    return features


def main():
    parser = argparse.ArgumentParser(description="Extrae la fibra detectada de Respuesta_T5610.zip")
    parser.add_argument("archivo", type=Path)
    parser.add_argument("salida", type=Path)
    args = parser.parse_args()
    features = extraer_fibra(args.archivo)
    lineas = [json.dumps(feature, ensure_ascii=False, allow_nan=False) for feature in features]
    contenido = '{"type":"FeatureCollection","features":[\n' + ',\n'.join(lineas) + '\n]}\n'
    args.salida.write_text(contenido, encoding="utf-8")
    print(f"{len(features)} trazados exportados a {args.salida}")


if __name__ == "__main__":
    main()
