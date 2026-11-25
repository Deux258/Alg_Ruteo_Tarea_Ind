# Tarea individual 2 de Algoritmos de Ruteo

Diego Muñoz Barra

El informe resume la evidencia de la rúbrica, los resultados y la captura del mapa. El ATTR de la red modelada pasa de **0,072727** a **0,050909**, una caída de **2,18 puntos porcentuales** o **30 % relativo**.

## Ejecución

Se necesita Python 3.10 o superior, Docker con el daemon iniciado y Docker Compose v2 con soporte para `up --wait`. La imagen fijada en `compose.yaml` incluye PostgreSQL 16, PostGIS 3.5 y pgRouting 3.7.3. La primera ejecución puede descargar la imagen. [Imagen de pgRouting](https://hub.docker.com/r/pgrouting/pgrouting/tags)

Desde la raíz del repositorio:

```bash
python3 main.py
```

El comando inicia la BD, carga `main.sql`, recalcula las probabilidades y ambos ATTR, guarda los resultados y abre `mapa.html` en el navegador predeterminado. En una terminal sin sesión gráfica, usar `python3 main.py --sin-navegador` y abrir el HTML por su ruta cuando esté disponible. El mapa lleva Leaflet 1.9.4 y la cartografía de Natural Earth en el propio HTML. La ejecución usa la biblioteca estándar de Python. [Leaflet](https://leafletjs.com/reference-1.9.4.html) · [Natural Earth 1:50m, versión 5.1.2](https://github.com/nvkelso/natural-earth-vector/blob/v5.1.2/geojson/ne_50m_admin_0_countries.geojson)

## Importar main.sql por separado

`main.sql` incluye extensiones, geometrías, terminales, creación de topología con `pgr_createTopology`, evento, modelo y filas de probabilidad. Usar `psql` con una base vacía y las extensiones disponibles en el servidor:

```bash
docker compose up -d --wait db
docker compose exec -T db psql -X -v ON_ERROR_STOP=1 -U ruteo -d ruteo < main.sql
```

La carga es transaccional. Puede repetirse en la misma base cuando las geometrías y el catálogo coinciden. Para regenerar el SQL después de cambiar los insumos de infraestructura o terminales, usar un nombre de proyecto Compose nuevo y ejecutar `COMPOSE_PROJECT_NAME=ti2-regeneracion python3 main.py --regenerar-sql --sin-navegador`.

## Datos y resultados

- **Infraestructura y topología.** `datos/fibra_yafun.geojson` corresponde a `fibra_optica_detectada` del archivo SAIP `Respuesta_T5610.zip`, facilitado en Canvas. Conserva 1.915 trazados con **10.312,76 km**, medidos con `ST_Length(geom::geography)`. Yafün reporta cerca de **28.000 km de recorrido documentado**. El alcance de ese recorrido y el de la capa de fibra entregada son distintos. La topología tiene 2.080 vértices y 175 componentes. Se usan los extremos coincidentes a `10⁻⁹` grados, una tolerancia submilimétrica para absorber precisión numérica. Los cruces interiores quedan sin empalme y se usan exclusivamente los enlaces observados en el archivo. [Informe Yafün](https://yafun.nic.cl/estudio-resiliencia-internet-nacional/) · [Recorrido Yafün](https://yafun.nic.cl/mapas/recorrido-yafun/) · [Archivo SAIP en Canvas](https://udp.instructure.com/courses/44775/modules/items/2251961)
- **Nodos clave.** [Catálogo](datos/nodos_clave.csv) con 12 ubicaciones y fuentes, incluidas la estación de amarre SAm-1 de Arica, el centro de datos Google PARAM Quilicura y la referencia troncal REUNA La Serena. Se asociaron a 11 vértices distintos por proximidad, con una sola unidad de análisis por vértice. Santiago y Quilicura comparten el vértice 374. Las distancias y los componentes figuran en [el resultado de operación](datos/attr_base.json). El empalme físico de cada instalación requiere datos adicionales, especialmente en Santiago.
- **Terremoto y modelo.** El GeoJSON USGS del evento `official20100227063411530_30` y la curva nominal de atenuación están en el repositorio. Se adapta el modelo de regiones de daño de Vass et al. a la intensidad MMI de ShakeMap. La [documentación del modelo](docs/modelo_falla.md) describe cada parámetro, el cálculo exacto para los escenarios discretizados y sus limitaciones.
- **Resultados.** Antes hay 4 de 55 pares conectados. El sismo reduce a 2,8 el número esperado de pares comunicados. En los cuatro escenarios de mayor radio, las tres localidades del grupo Las Cabras–Peumo–Pichidegua pierden conectividad entre sí. Huasco y Freirina conservan su conexión en los diez escenarios. [Escenarios y afectación por nodo](datos/attr_posterior.json)

`scripts/extraer_fibra.py` es una herramienta opcional para reproducir la conversión del ZIP original. Requiere PyShp 3.1.6 y el archivo de Canvas. La ejecución principal ya incluye el GeoJSON convertido.
