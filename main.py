import base64
import json
import re
import subprocess

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
    raiz = topologia.ROOT
    subprocess.run(
        ["docker", "compose", "up", "-d", "--wait", "db"], cwd=raiz, check=True
    )
    if (
        topologia.psql("SELECT to_regclass('tarea_ruteo.terminales') IS NOT NULL;")
        == "f"
    ):
        topologia.main()

    probabilidades.main()
    modelo = json.loads((raiz / "config/modelo_falla.json").read_text(encoding="utf-8"))
    resultados = leer_resultados(modelo["id"])
    if len(resultados["enlaces"] or []) != resultados["total_enlaces"]:
        raise ValueError("Faltan probabilidades para algunos enlaces")

    red = json.loads((raiz / "datos/fibra_yafun.geojson").read_text(encoding="utf-8"))
    riesgo_por_id = {enlace["id"]: enlace for enlace in resultados["enlaces"]}
    for trazado in red["features"]:
        trazado["properties"].update(riesgo_por_id[trazado["id"]])

    attr = resultados["attr"]
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
    (raiz / "main.sql").write_text(generar_sql(resultados), encoding="utf-8")
    (raiz / "datos/attr_posterior.json").write_text(
        json.dumps(attr, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    mapa = raiz / "mapa.html"
    mapa.write_text(contenido_mapa, encoding="utf-8")
    print(
        f"ATTR inicial: {attr['antes']:.6f} | ATTR posterior esperado: {attr['despues_esperado']:.6f}"
    )
    print(f"Mapa Leaflet: {mapa}")


if __name__ == "__main__":
    main()
