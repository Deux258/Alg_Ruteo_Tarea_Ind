# Informe LaTeX — Path Discovery

Autor: Diego Muñoz. Profesor: Nicolas Boettcher. Asignatura: Algoritmos de Ruteo.

`main.tex` compila el informe. `secciones/` contiene puntos de edición manual que el generador conserva. `datos/` contiene texto y tablas derivados de evidencia, y `figuras/` las capturas reales y los tres grafos vectoriales. Modificar el generador para cambiar contenido derivado: la regeneración sobrescribe `datos/` y `main.tex`.

## Fuentes de datos

Selección cerrada: `resultados/analisis_20261027T151549_92fa68e2`, 153 ejecuciones. `config/evidencia_informe.json` fija los archivos de patrones, payload y respuesta selectiva por ruta y SHA-256. `fuentes.json` registra los manifiestos de originales, publicaciones, capturas y archivos generados. No se toma automáticamente el análisis más reciente.

La ronda 2 se muestra en el cuerpo; las estadísticas usan las tres rondas. Las rondas 1 y 3 y las respuestas múltiples están en anexos. No se mezcla el destino ruso de la selección histórica con la alternativa del enunciado actualizado.

## Regeneración y compilación con Docker Compose

Desde la raíz del proyecto:

```bash
docker compose -f compose.latex.yaml build
docker compose -f compose.latex.yaml run --rm latex python3 /work/scripts/generar_informe_latex.py \
  --analysis /work/resultados/analisis_20261027T151549_92fa68e2 \
  --evidence /work/config/evidencia_informe.json --output /work/informe/latex
docker compose -f compose.latex.yaml run --rm latex
```

El PDF aparece en `informe/latex/build/main.pdf`. El PDF revisado para entrega es `informe/latex/informe.pdf`. La compilación y la generación se ejecutan sin red; la construcción inicial de la imagen descarga paquetes oficiales de Debian. `SOURCE_DATE_EPOCH` fija la fecha del análisis en los metadatos del PDF. La imagen concreta queda registrada en `compilacion.json`.

Alternativa local: Python 3.11 o posterior con `pip install -e '.[report]'`; ejecutar `python scripts/generar_informe_latex.py` con los mismos argumentos relativos a la raíz, y `latexmk -pdf -outdir=build main.tex` desde esta carpeta. Se necesitan TeX Live, español, Latin Modern y los paquetes del preámbulo.

`--draft` permite preparar una edición parcial identificada en `fuentes.json`. Sin esa opción el generador exige campaña completa, tres publicaciones públicas coincidentes, 14 revisiones GUI y dos casos de respuesta selectiva corroborados. Una fuente alterada o seleccionada sin hash detiene el proceso.

## Límites y lectura académica

Las IP representan interfaces; no se demostró que dos interfaces pertenezcan al mismo router mediante alias resolution. La respuesta selectiva se repitió, pero no demuestra una ACL específica. Se separan las respuestas TCP observadas en PCAP de los saltos aceptados en WARTS. Los traceroutes no prueban velocidad de acceso ni censura. La matriz de rúbrica localiza evidencia; no garantiza una calificación.

La copia de compatibilidad `informe/path_discovery/informe.pdf` corresponde al mismo PDF final. Las versiones anteriores se guardan en `informe/historico/`. El paquete de fuentes LaTeX puede compilarse por sí solo con sus figuras; regenerar las tablas requiere el paquete completo de evidencia.

## Comprobar la reproducción exacta

```bash
python scripts/verificar_informe_latex.py --analysis resultados/analisis_20261027T151549_92fa68e2
```

La comprobación compara los archivos de fuentes y figuras y el PDF completo por SHA-256. Su constancia está en `resultados/reproduccion_informe_latex.json`.
