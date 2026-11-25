# Modelo de falla y fiabilidad de la red

## Parámetros y procedencia

El epicentro del 27F se lee del GeoJSON oficial del Maule, con longitud −72,898°, latitud −36,122°, magnitud Mw 8,8 y profundidad 22,9 km. El modelo usa distancia epicentral superficial. La profundidad se conserva en la BD como atributo del evento. [Evento USGS](https://earthquake.usgs.gov/earthquakes/eventpage/official20100227063411530_30)

| Insumo o parámetro | Valor y justificación |
| --- | --- |
| Intensidad nominal media μ(d) y dispersión σ(d) | Series `gmpe.soil.MMI.mean` y `stddev` del ShakeMap Atlas del evento, en unidades MMI. USGS usa Vs30 = 180 m/s para la curva nominal de suelo. Se aplica como supuesto homogéneo al corredor de fibra. |
| Distancia d | `distances.repi` de la curva, expresada en km. Para cada enlace, `ST_Distance(geom::geography, epicentro::geography)/1000` mide la distancia mínima al trazado completo. |
| Umbral | VI en la escala MMI. Vass et al. usan el nivel VI de su escala MCS como umbral principal en la sección VIII-B. Se traslada el grado ordinal VI a MMI como aproximación metodológica. |
| Incertidumbre | Desviación normal estándar compartida Z. Usar el mismo Z para toda la red representa la incertidumbre sobre el alcance de un solo evento y conserva áreas de daño anidadas. |
| Cuadratura | Diez intervalos equiprobables de Z. Cada intervalo pesa 0,10 y se representa por su cuantil central. Se eligen diez para poder inspeccionar todos los casos en la tabla y el mapa. |

Fuentes de los parámetros y del método. [Vass et al., §§ III, IV-A y VIII](https://doi.org/10.1109/JSAC.2021.3064652) · [Manual de formatos ShakeMap](https://ghsc.code-pages.usgs.gov/esi/shakemap/docs2020/manual4_0/ug_products.html) · [Curva nominal del Maule](https://earthquake.usgs.gov/product/shakemap/official20100227063411530_30/atlas/1594161725779/download/attenuation_curves.json)

## Función y aplicación a fibra

Para el escenario j, zⱼ = Φ⁻¹((j − 0,5)/10) y la intensidad nominal ajustada a distancia d es μ(d) + σ(d)zⱼ. Rⱼ es la distancia del primer cruce descendente bajo MMI VI, interpolada linealmente entre dos muestras consecutivas. El primer cruce mantiene una región circular continua alrededor del epicentro. Cuando la curva empieza bajo VI, el escenario no causa cortes. Se usan las curvas nominales sin sumar el campo `mean_bias`.

Un enlace con distancia mínima dₑ falla si Rⱼ > 0 y dₑ ≤ Rⱼ. Su probabilidad marginal pₑ es la suma de los pesos de esos escenarios. La disponibilidad de un enlace de fibra exige continuidad a lo largo de todo su trazado, por lo que un corte en cualquier punto elimina ese enlace del grafo. Compartir el radio mantiene la correlación de las fallas, incluida la de trazados coincidentes.

La curva describe agitación sísmica. El umbral de falla es un supuesto adoptado para la red y la capa SAIP aporta geometrías e identificadores. Harían falta registros de cortes y características de los cables, ductos y cruces para calibrar una fragilidad propia. El modelo circular y de suelo homogéneo simplifica diferencias de terreno, ruptura finita, tsunami, energía y recuperación. Evalúa el sismo de 2010 sobre una infraestructura levantada con posterioridad.

## ATTR

Para K vértices terminales distintos, el ATTR es la media de la probabilidad de que exista un camino entre cada par no ordenado de terminales:

`ATTR = [Σ(i<j) P(i ↔ j)] / C(K,2)`.

Por escenario, con kᵢ terminales en el componente i, el numerador se obtiene como `Σ C(kᵢ,2)`. Los vértices aislados siguen contando en K. El ATTR anterior usa la probabilidad de falla de base de 0 y el grafo completo. El posterior suma el ATTR de los diez escenarios ponderados por 0,10. La enumeración es exacta para esa distribución discreta y aproxima la incertidumbre normal continua. El programa coteja las probabilidades marginales almacenadas con los mismos radios y pesos que usa para el ATTR, y aplica cada escenario conjuntamente a todos los enlaces. La adaptación de la métrica se basa en la sección VI y las ecuaciones (8) y (9) del artículo base del curso. [Boettcher et al. (2018)](https://doi.org/10.1109/TLA.2018.8789553)
