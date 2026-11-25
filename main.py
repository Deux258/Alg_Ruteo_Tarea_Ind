import argparse
import base64
import json
import re
import subprocess
import webbrowser

from scripts import probabilidades, topologia
from scripts.resultados import generar_sql, leer_resultados


def generar_mapa(raiz, datos):
    leaflet = raiz / "scripts/leaflet"
    css = (leaflet / "leaflet.css").read_text(encoding="utf-8")

    def imagen_embebida(coincidencia):
        imagen = (leaflet / coincidencia[1]).read_bytes()
        return (
            "url(data:image/png;base64,"
            + base64.b64encode(imagen).decode("ascii")
            + ")"
        )

    css = re.sub(r"url\((images/[-\w]+\.png)\)", imagen_embebida, css)
    js = (
        (leaflet / "leaflet.js")
        .read_text(encoding="utf-8")
        .split("//# sourceMappingURL=", 1)[0]
    )
    licencia = (leaflet / "LICENSE").read_text(encoding="utf-8")
    datos_json = json.dumps(datos, ensure_ascii=False, allow_nan=False).replace(
        "<", r"\u003c"
    )
    plantilla = (raiz / "scripts/mapa.html").read_text(encoding="utf-8")
    return (
        plantilla.replace("/* LEAFLET_CSS */", css)
        .replace("/* LEAFLET_JS */", f"/*\n{licencia}\n*/\n{js}")
        .replace("/* DATOS_MAPA */", datos_json)
    )


def main():
    parser = argparse.ArgumentParser(description='Reproduce el análisis de la fibra de Yafün ante el 27F')
    parser.add_argument('--sin-navegador', action='store_true', help='Genera el mapa para una sesión sin interfaz gráfica')
    parser.add_argument('--regenerar-sql', action='store_true', help='Reconstruye main.sql desde los archivos de entrada')
    opciones = parser.parse_args()
    raiz = topologia.ROOT
    subprocess.run(['docker', 'compose', 'up', '-d', '--wait', 'db'], cwd=raiz, check=True)
    archivo_sql = raiz / 'main.sql'
    if opciones.regenerar_sql:
        if topologia.psql("SELECT to_regclass('tarea_ruteo.terminales') IS NOT NULL;") == 'f':
            topologia.psql('BEGIN;\n' + topologia.sql_topologia() + 'COMMIT;\n')
    else:
        topologia.psql(archivo_sql.read_text(encoding='utf-8'))

    probabilidades.main()
    modelo = json.loads((raiz / 'config/modelo_falla.json').read_text(encoding='utf-8'))
    resultados = leer_resultados(modelo['id'])
    campos = ('id', 'nombre', 'roles', 'tipo')
    catalogo = {tuple(n[c] for c in campos) + (float(n['longitud']), float(n['latitud']))
                for n in topologia.leer_terminales()}
    terminales_cargados = {tuple(n[c] for c in campos) + (n['longitud'], n['latitud'])
                          for n in resultados['terminales']}
    if catalogo != terminales_cargados:
        raise ValueError('El catálogo cambió. Regenera main.sql con --regenerar-sql en un proyecto Compose nuevo.')
    if len(resultados['enlaces'] or []) != resultados['total_enlaces']:
        raise ValueError('Faltan probabilidades para algunos enlaces')
    if any(abs(e['probabilidad'] - e['probabilidad_escenarios']) > 1e-12 for e in resultados['enlaces']):
        raise ValueError('Las probabilidades de la BD no coinciden con los escenarios de ATTR')

    red = json.loads((raiz / "datos/fibra_yafun.geojson").read_text(encoding="utf-8"))
    riesgo_por_id = {enlace["id"]: enlace for enlace in resultados["enlaces"]}
    for trazado in red["features"]:
        trazado["properties"].update(riesgo_por_id[trazado["id"]])

    attr = resultados['attr']
    attr['terminales'] = resultados['terminales']
    attr['diferencia_pp'] = (attr['despues_esperado'] - attr['antes']) * 100
    attr['reduccion_relativa'] = (1 - attr['despues_esperado'] / attr['antes']) if attr['antes'] else None
    mapa_datos = {
        "evento": resultados["evento"],
        "terminales": resultados["terminales"],
        "red": red,
        "attr": attr,
        "fondo": json.loads(
            (raiz / "datos/mapa_base.geojson").read_text(encoding="utf-8")
        ),
    }
    contenido_mapa = generar_mapa(raiz, mapa_datos)
    if opciones.regenerar_sql:
        archivo_sql.write_text(generar_sql(resultados), encoding='utf-8')
    (raiz / 'datos/attr_base.json').write_text(
        json.dumps(topologia.resumir_topologia(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8',
    )
    (raiz / 'datos/attr_posterior.json').write_text(
        json.dumps(attr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8',
    )
    mapa = raiz / 'mapa.html'
    mapa.write_text(contenido_mapa, encoding='utf-8')
    print(f"ATTR inicial: {attr['antes']:.6f} | ATTR posterior esperado: {attr['despues_esperado']:.6f}")
    print(f'Mapa Leaflet: {mapa}')
    if not opciones.sin_navegador and not webbrowser.open(mapa.as_uri()):
        print('Abre la ruta del mapa en un navegador con interfaz gráfica.')


if __name__ == "__main__":
    main()
