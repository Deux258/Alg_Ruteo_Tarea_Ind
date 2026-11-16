# Modelo probabilístico de falla por terremoto

Se adopta un modelo de región circular de daño centrada en el epicentro del evento Maule 2010. El radio es aleatorio y compartido por toda la red. Una intersección entre el área de daño y un trazado causa la falla de ese enlace.

## Fundamento bibliográfico

Vass et al. (2021) describen fallas regionales mediante áreas de daño anidadas. Su definición 3 establece la falla de los enlaces que intersectan el área. Las ecuaciones (4) y (7) obtienen probabilidades individuales y conjuntas integrando los escenarios, y (8) expresa la probabilidad conjunta mediante el mínimo de las marginales cuando las áreas son anidadas. La sección IV-A considera discos centrados en el epicentro. [Artículo, DOI 10.1109/JSAC.2021.3064652](https://doi.org/10.1109/JSAC.2021.3064652)

La adaptación de esta tarea fija el epicentro observado, usa tres radios posibles y sustituye las integrales sobre escenarios por sumas ponderadas. Además, usa distancias geodésicas para representar la extensión geográfica de Chile. Los radios y sus pesos son decisiones de modelación de esta tarea. [Parámetros para los pasos siguientes](../config/modelo_falla.json)

## Evento y parámetros

El centro se lee de las primeras dos coordenadas del GeoJSON USGS, en orden longitud y latitud, con valores −72,898° y −36,122°. El registro identifica el terremoto del 27 de febrero de 2010 de magnitud 8,8. La tercera coordenada representa profundidad en kilómetros y se conserva como metadato del evento. La distancia utilizada por este modelo es superficial. [Evento USGS](https://earthquake.usgs.gov/earthquakes/eventpage/official20100227063411530_30)

| Escenario | Radio de daño | Probabilidad del escenario |
| --- | ---: | ---: |
| radio_100 | 100 km | 0,25 |
| radio_200 | 200 km | 0,50 |
| radio_300 | 300 km | 0,25 |

Los pesos suman uno. Estos valores retoman el plan inicial como escenario académico ilustrativo. Su escala permite estudiar tres extensiones distintas alrededor del epicentro, con mayor peso en la intermedia. La magnitud identifica el evento de referencia. El modelo no proporciona una relación calibrada entre magnitud y radio. El resultado expresa incertidumbre supuesta sobre la extensión del daño, condicionada a ese terremoto.

Los datos de fibra disponibles contienen geometrías e identificadores. Una calibración empírica necesitaría inventarios de cortes y características constructivas o curvas de fragilidad compatibles con esta infraestructura. El GeoJSON USGS incluye referencias a ShakeMap, que describe movimiento del suelo y necesitaría una relación adicional de fragilidad para traducirse a falla de cable. Por ello, los parámetros adoptados se reportan con el estado `ilustrativa_sin_calibracion_empirica`.

## Probabilidad de falla de un enlace

Sea \(d_e\) la distancia mínima desde el epicentro a cualquier punto del trazado del enlace \(e\). Para cada escenario \(s\), el indicador de falla es

\[
F_e(s)=\mathbf{1}[d_e\leq r_s].
\]

La probabilidad marginal se calcula como

\[
p_e=\sum_{s=1}^{3}w_s F_e(s).
\]

| Distancia mínima al trazado | Probabilidad de falla |
| --- | ---: |
| \(0\leq d_e\leq100\) km | 1,00 |
| \(100<d_e\leq200\) km | 0,75 |
| \(200<d_e\leq300\) km | 0,25 |
| \(d_e>300\) km | 0,00 |

Se incluye el borde del disco. Para evaluar el indicador se conserva la precisión de la distancia calculada, redondeándola únicamente para presentación. Se usa la geometría completa del trazado, incluidos sus segmentos intermedios. Un corte en cualquier punto inhabilita el enlace completo para el cálculo de conectividad.

Los valores extremos, uno dentro de 100 km y cero fuera de 300 km, son consecuencias deliberadas de este conjunto de escenarios. Condicionan la estimación y requieren explicitarse al presentar resultados.

## Fallas correlacionadas y ATTR posterior

Cada escenario aplica un único radio a todos los enlaces. Si dos enlaces tienen distancias mínimas de 150 y 250 km, sus probabilidades son 0,75 y 0,25. Ambos fallan juntos en el escenario de 300 km, con probabilidad 0,25. Para cualquier conjunto no vacío de enlaces, la probabilidad de falla simultánea equivale a la suma de los pesos de los escenarios que los afectan a todos. Con estos discos anidados coincide con el mínimo de sus probabilidades individuales.

En el paso 9 se evalúa cada grafo superviviente \(G_s=(V,\{e:d_e>r_s\})\). Se conservan todos los vértices y las mismas nueve asignaciones de terminales, incluidos los que quedan aislados. Si un componente contiene \(k_i\) terminales, el ATTR de ese escenario es

\[
\operatorname{ATTR}_s=\frac{\sum_i\binom{k_i}{2}}{\binom{9}{2}},
\qquad
\mathbb E[\operatorname{ATTR}_{después}]
=\sum_{s=1}^{3}w_s\operatorname{ATTR}_s.
\]

La enumeración de tres escenarios obtiene el valor esperado exacto bajo este modelo. La base calculada con todos los enlaces disponibles es 4/36. El ATTR esperado posterior debe quedar entre cero y ese valor. La operación de los equipos se asume disponible, aunque sus conexiones pueden perderse por los cortes.

## Aplicación en el repositorio

[`scripts/probabilidades.py`](../scripts/probabilidades.py) carga el evento en PostGIS como punto 2D EPSG:4326, conserva la profundidad como atributo y calcula `ST_Distance(enlaces.geom::geography, epicentro.geom::geography) / 1000.0` para cada enlace. [`scripts/resultados.py`](../scripts/resultados.py) evalúa los escenarios con `pgr_connectedComponents`, incluye los terminales en vértices sin enlaces supervivientes y obtiene la media ponderada. [`main.py`](../main.py) genera la exportación SQL, el resumen de ATTR y el mapa Leaflet.

Las asignaciones de terminales son aproximadas. El análisis aplica un evento de 2010 al levantamiento de infraestructura posterior entregado en el curso, por lo que las cifras representan un escenario hipotético sobre la red de Yafün.
