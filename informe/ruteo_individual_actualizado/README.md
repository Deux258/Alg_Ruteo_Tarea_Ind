# Tarea Individual: Path Discovery — edición con explicación de plataformas

Esta edición parte de Ruteo_Individual.zip aportado por el estudiante el 29 de octubre de 2026. Conserva su introducción, conclusión y portada. Añade la sección 2.1 al comienzo de Metodología; actualiza las referencias y compacta el índice. La sección nueva está en secciones/plataformas.tex y puede editarse directamente.

El PDF revisado es Informe_Ruteo_Individual.pdf. Los detalles de cambios y verificaciones están en revision/cambios.json. Las fuentes y metadatos de la edición anterior se conservan en revision/origen/. El ZIP original del estudiante permanece intacto.

## Compilar

Con TeX Live y latexmk, desde esta carpeta:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

El PDF compilado aparece en build/main.pdf. El ZIP de esta edición contiene main.tex, secciones/, datos/, figuras/ y el logo, por lo que puede cargarse en un editor LaTeX seleccionando main.tex como archivo principal.

En el proyecto local también puede compilarse con Docker Compose, desde su raíz:

```bash
docker compose -f compose.latex.yaml run --rm --workdir /work/informe/ruteo_individual_actualizado latex
```

Esta edición contiene cambios editoriales manuales del estudiante. Para conservarlos, editar estas fuentes y compilar: el generador del informe original vuelve a crear el texto anterior a esa edición.

SHA256.json contiene los hashes de los archivos de esta entrega. Esta revisión no añade mediciones ni modifica los datos originales.
