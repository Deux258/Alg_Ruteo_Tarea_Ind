# Tarea individual 2 de Algoritmos de Ruteo

## 1. Infraestructura de fibra óptica reportada por Yafün

La fuente es el *Estudio y recomendaciones sobre la resiliencia de la infraestructura del Internet chileno*, NIC Chile, versión 2.0, diciembre de 2018, proyecto CORFO 15BPE-47225. El informe descargado queda en `datos/originales/`, que se excluye de Git. [Publicación de NIC Chile](https://yafun.nic.cl/estudio-resiliencia-internet-nacional/)

```bash
mkdir -p datos/originales
curl -fL 'https://www.nic.cl/estudios/resiliencia_uchile_corfo_subtel.pdf' \
  -o datos/originales/resiliencia_uchile_corfo_subtel.pdf
sha256sum datos/originales/resiliencia_uchile_corfo_subtel.pdf
```

SHA-256 verificado el 16 de noviembre de 2026: `e2046aa536fe9d96a89cf5e03b58e16d7ec147fe659482494393482597cd655f`.

### Capa entregada en Canvas

La capa de trabajo es [`datos/fibra_yafun.geojson`](datos/fibra_yafun.geojson). Conserva los **1.915 trazados** del shapefile `fibra_optica_detectada` incluido en `Respuesta_T5610.zip`, con las coordenadas WGS84 originales en orden longitud, latitud. El campo `properties.id_fuente` conserva el identificador del DBF, que se repite en algunos registros. El `id` de cada entidad GeoJSON es el número de fila del shapefile, comenzando en 1.

El ZIP está en el módulo Papers de Canvas. Se guardó el original en `datos/originales/Respuesta_T5610.zip`, fuera de Git. SHA-256 verificado `39d96b25dac8c654d9977b7a3e0acfcbce034b8e1c94df9b49ca4293f52ceda0`. Las capas de postación eléctrica, caminos sin postación y trayectos en ferry quedan fuera del análisis de fibra existente. [Respuesta T5610 en Canvas](https://udp.instructure.com/courses/44775/modules/items/2251961)


Para regenerar el GeoJSON desde el ZIP, ejecutar desde la raíz del repositorio:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pyshp==3.1.6
.venv/bin/python scripts/extraer_fibra.py datos/originales/Respuesta_T5610.zip datos/fibra_yafun.geojson
```

La capa describe trazados detectados en el levantamiento. La entrega del shapefile solo contiene el campo `id` y no aporta operadores, empalmes ni continuidad lógica entre segmentos.

## 2. Catálogo de nodos clave

[`datos/nodos_clave.csv`](datos/nodos_clave.csv) contiene nueve ubicaciones de referencia. Cada fila registra el rol, evidencia, URL de la fuente, referencia dentro de la fuente, procedencia de las coordenadas y estado de asociación a la red. Una localidad con dos roles sigue siendo una sola ubicación. Los roles múltiples y sus fuentes se registran con `|` como separador.

| Rol | Ubicaciones | Criterio |
| --- | --- | --- |
| Generación | Santiago, Valparaíso, Concepción | Servicios DNS autoritativos de .CL que generan respuestas. |
| Intercambio | Santiago, Curicó, Concepción | PIT documentados por SUBTEL. |
| Recepción | Peumo, Pichidegua, Las Cabras, Huasco, Freirina | Localidades asociadas a conexiones o corredores de fibra descritos por Yafün. |

Fuentes: [NIC Chile, red DNS .CL](https://www.nic.cl/estadisticas/mapaDNS.html) · [SUBTEL, redes regionales, pp. 37–39](https://www.subtel.gob.cl/wp-content/uploads/2022/08/Informe-Redes-Regionales-publico.pdf) · [GeoNames, archivo de Chile](https://download.geonames.org/export/dump/CL.zip).

El catálogo combina el levantamiento Yafün de 2018 con fuentes funcionales de 2019 y 2022. Las coordenadas representan localidades. `trazado_cercano_id` apunta a la entidad más próxima del GeoJSON. `distancia_fibra_m` aproxima la distancia mínima a la línea en metros, calculada en un plano local centrado en cada localidad. Las nueve asociaciones están pendientes de verificar como empalmes físicos. Santiago, en particular, queda a unos 11,2 km del trazado más próximo al punto representativo de la ciudad. La proximidad sirve para revisar la correspondencia en el paso de topología.

## 3 y 4. Topología y ATTR inicial

Iniciar la base local y cargar los datos con Python y Docker Compose:

```bash
docker compose up -d --wait
python3 scripts/topologia.py
```

El script crea el esquema `tarea_ruteo`, importa los trazados, ejecuta `pgr_createTopology` de pgRouting 3.7 y calcula componentes conexas. El volumen de PostgreSQL es persistente. Para evitar sobrescribir datos, el script detiene la ejecución si el esquema ya existe. Los resultados se pueden consultar de nuevo sin recrearlo:

```bash
docker compose exec db psql -U ruteo -d ruteo -c 'TABLE tarea_ruteo.terminales'
cat datos/attr_base.json
```

Los extremos dentro de la tolerancia de 0,000000001 grados se consideran el mismo vértice. Los cruces geométricos intermedios se mantienen sin conectar, dado que los datos no identifican empalmes. Cada localidad se asigna al extremo más cercano del trazado que está más próximo a su punto representativo. El archivo de resultados guarda ambas distancias. Estas asignaciones son aproximaciones, sujetas a verificación física. Una fibra que pasa por una localidad no acredita que el servicio se conecte allí.

Con estas hipótesis, la red cargada tiene 1.915 enlaces, 2.080 vértices y 175 componentes. Cuatro de los 36 pares de terminales se ubican en el mismo componente, por lo que el **ATTR inicial es 4/36 = 0,1111**. El resultado es una estimación condicionada a las asignaciones de terminales y a la información del levantamiento.

## 5. Sismo 8.8 del Maule

El GeoJSON oficial del evento USGS `official20100227063411530_30` está guardado en `datos/sismo_maule_2010.geojson`. El original descargado se conserva en `datos/originales/sismo_maule_2010_usgs.geojson`. Corresponde al terremoto de Maule del 27 de febrero de 2010, magnitud 8,8, profundidad 22,9 km, con epicentro en 36,122° S, 72,898° O. La geometría GeoJSON guarda coordenadas como longitud, latitud, profundidad.

Fuente: [evento oficial USGS](https://earthquake.usgs.gov/earthquakes/eventpage/official20100227063411530_30) · [API FDSN GeoJSON](https://earthquake.usgs.gov/fdsnws/event/1/). SHA-256 del archivo: `fee979e84540bbacf34443e7d332049002798d5c81ba81e335f8f387bb8f8b74`.

## 6. Modelo probabilístico de falla

Se adopta una adaptación discreta del modelo de fallas regionales correlacionadas de Vass et al. (2021), con un radio de daño compartido por toda la red y el epicentro oficial del Maule fijo. La probabilidad de falla de cada enlace es la suma de los pesos de los escenarios cuyo disco alcanza cualquier punto del trazado. [Artículo de referencia](https://doi.org/10.1109/JSAC.2021.3064652)

| Radio | Peso del escenario |
| --- | ---: |
| 100 km | 0,25 |
| 200 km | 0,50 |
| 300 km | 0,25 |

**Los radios y pesos son parámetros ilustrativos elegidos para esta tarea**, sin calibración empírica con cortes del 27F. Las probabilidades marginales resultantes son 1,00 hasta 100 km, 0,75 hasta 200 km, 0,25 hasta 300 km y 0,00 más allá de 300 km. El límite superior de cada intervalo está incluido.

La definición, las ecuaciones y los supuestos están en [docs/modelo_falla.md](docs/modelo_falla.md). El cálculo lee los parámetros de [config/modelo_falla.json](config/modelo_falla.json) y conserva los nueve terminales al medir la conectividad de cada escenario.

## 7. Probabilidad de falla por enlace

Con la base iniciada y la topología cargada, ejecutar:

```bash
python3 scripts/probabilidades.py
docker compose exec db psql -U ruteo -d ruteo -c 'SELECT probabilidad, count(*) FROM tarea_ruteo.probabilidades_falla GROUP BY probabilidad ORDER BY probabilidad'
```

El script carga el evento en `tarea_ruteo.evento_sismico`, guarda una copia de la configuración del modelo en `tarea_ruteo.modelo_falla` y actualiza la distancia geodésica y la probabilidad en `tarea_ruteo.probabilidades_falla`. Comprueba que la geometría de la base coincide con el GeoJSON antes de calcular. Cada ejecución es transaccional y vuelve a calcular el modelo indicado en la configuración.

Con los parámetros ilustrativos actuales, los 1.915 enlaces se distribuyen en 1.242 con probabilidad 0, 225 con 0,25, 277 con 0,75 y 171 con 1. Estas son probabilidades del modelo condicionado al evento, con el mismo radio compartido por toda la red. Los escenarios completos se conservan en la configuración para calcular el ATTR posterior.

## 8. Exportación de probabilidades

[`main.sql`](main.sql) contiene las distancias y probabilidades de los 1.915 enlaces, el evento y la configuración del modelo. Para aplicar el archivo sobre una base que ya tiene cargada la topología del paso 3, ejecutar:

```bash
docker compose exec -T db psql -X -v ON_ERROR_STOP=1 -U ruteo -d ruteo < main.sql
```

El archivo comprueba que coincidan los identificadores y geometrías de los trazados. La importación se realiza en una transacción y puede repetirse para actualizar los resultados del mismo modelo.

## 9. ATTR posterior al sismo

| Radio | Peso | Enlaces caídos | Pares conectados | ATTR |
| ---: | ---: | ---: | ---: | ---: |
| 100 km | 25 % | 171 | 4 de 36 | 0,1111 |
| 200 km | 50 % | 448 | 4 de 36 | 0,1111 |
| 300 km | 25 % | 673 | 1 de 36 | 0,0278 |

El **ATTR esperado baja de 0,1111 a 0,0903**, una diferencia de **2,08 puntos porcentuales**. A 300 km, Huasco y Freirina forman el único par que conserva conectividad. Los resultados dependen de los radios y pesos ilustrativos y de la asignación aproximada de las localidades a vértices del grafo. El cálculo guarda los valores completos en [`datos/attr_posterior.json`](datos/attr_posterior.json).

## 10. Reproducción y mapa Leaflet

Desde la raíz del repositorio, con Docker Compose y Python 3 disponibles:

```bash
python3 main.py
```

`main.py` inicia la base, carga la topología si falta, calcula las probabilidades y genera `main.sql`, `datos/attr_posterior.json` y `mapa.html`. Abrir `mapa.html` en el navegador. El mapa muestra ambos ATTR, los terminales, el epicentro y la red, con un selector para ver la probabilidad marginal o los enlaces caídos para cada radio. El HTML incluye los datos, la biblioteca Leaflet y un fondo vectorial de Sudamérica que funciona sin conexión. [Leaflet 1.9.4](https://leafletjs.com/reference-1.9.4.html) · [Natural Earth 1:50m, versión 5.1.2](https://github.com/nvkelso/natural-earth-vector/blob/v5.1.2/geojson/ne_50m_admin_0_countries.geojson)
