# Fábrica de presencia: código compartido de los sitios

Código de la Fábrica de presencia (etapa 2 de PCS Central) para los repositorios `pcsoluciones-arg/sitio-*`. Vive una sola vez acá; `instalar.py` lo copia a cada sitio. Plan y decisiones: documento del proyecto `claude/fabrica-presencia-plan.md`.

## Qué hay

| Archivo | Qué hace | Se copia al sitio |
|---|---|---|
| `sello.py` | Verifica el sello de cada commit de `produccion`. Repositorio y flujo salen de `fabrica/config.json` | `fabrica/sello.py` |
| `riesgo_sitio.py` | Filtro de riesgo: decide si un cambio sale solo o espera a Manu | `fabrica/riesgo_sitio.py` |
| `publicar_sitio.py` | Publicación: sella, envía a `produccion` y controla en vivo | `fabrica/publicar_sitio.py` |
| `controles.sh` | Controles de código: copia igual, `build.py`, `wrangler --dry-run`, `revisar.py`, `navegador.py` | `fabrica/controles.sh` |
| `LEEME-fabrica.md` | Explicación para quien abre el repositorio del sitio | `fabrica/LEEME.md` |
| `flujos/publicar.yml`, `flujos/revision.yml` | Flujos de GitHub Actions | `.github/workflows/` |
| `instalar.py` | Copia todo lo anterior y crea `fabrica/config.json`; con `--verificar`, compara | no |
| `navegador.py` | Controles en Chromium a 390 y 1360 px y capturas para el revisor visual | no (corre desde acá) |
| `pruebas/` | Pruebas de todo lo anterior | no |

`revisar.py` y `navegador.py` corren desde este repositorio, que es público: la revisión de cada sitio lo baja en cada corrida.

## Recorrido de un cambio

| Cómo entra | Qué pasa |
|---|---|
| El panel PCS publica fotos o textos (push a `main`) | `publicar.yml` corre `controles.sh`. Riesgo bajo: sella y publica. Riesgo alto: abre el pedido "Cambios en main esperan tu aprobación" (`espera-manu`) y no publica. |
| Un PR con la etiqueta `listo` | `revision.yml` corre `controles.sh` y pone `riesgo:bajo` o `riesgo:alto`. Riesgo bajo: `publicar.yml` lo junta en `main` y publica. Alto: `espera-manu`. |
| Manu aprueba | GitHub → Actions → Publicar → Run workflow, con el número del PR, o vacío para publicar `main` tal como está. |

Después de publicar, `publicar_sitio.py` espera el build de Cloudflare y controla en vivo: `version.json` con el commit publicado, todas las imágenes de la página respondiendo 200 y `www` con 301 al dominio. Si algo falla, lo deja en el PR (o en un pedido) con `necesita-manu`.

La primera publicación sellada de un sitio (cuando todavía no existe la rama `produccion`) solo la lanza Manu.

## Riesgo

Sale solo, si todo el cambio está en:

- `fotos/` (WebP, JPG, PNG o AVIF) y `ficha-google/` (JPG o PNG), agregando o reemplazando, sin borrar ni crear subcarpetas.
- `contenido.json`, dentro de las secciones de `secciones.json` (lo que carga el panel): ítems nuevos, títulos, bajadas y orden, sin campos nuevos y sin retirar más ítems de los que entran.
- `contenido.json`, fuera de esas secciones: textos en campos que ya existen, sin agregar ni quitar campos ni elementos de una lista.
- Documentación `.md`, salvo `CLAUDE.md`.
- Sin datos de contacto (teléfono, correo, enlaces, dominio) ni precios en lo que cambia, y sin tocar campos con esos nombres.
- Menos de 300 líneas.

Todo lo demás espera a Manu: `build.py`, `wrangler.toml`, `secciones.json`, `.reglas.json`, `CLAUDE.md`, `marca.json`, `publico/`, `fuente/`, estilos y código, `.github/` y `fabrica/`.

## Instalar en un sitio nuevo

Es el paso 3 del plan para cada sitio, en un PR del sitio (riesgo alto: lo aprueba Manu).

1. Con `herramientas` al lado del sitio: `python3 ../herramientas/sitios/instalar.py .` Copia la fábrica y crea `fabrica/config.json` tomando el repositorio de git, la URL de `secciones.json` y el Worker de `wrangler.toml`.
2. En `build.py`, al principio, verificar el sello cuando corre en Cloudflare:

   ```python
   if os.environ.get("WORKERS_CI") == "1":
       sys.path.insert(0, os.path.join(AQUI, "fabrica"))
       import sello
       ok, motivo = sello.verificar_head()
       if not ok:
           sys.exit(f"ERROR: esta publicación no pasó por la fábrica. {motivo} Queda andando la versión anterior.")
   ```

3. En `build.py`, en `version.json`, sumar el commit de `main` que se publica, que es el que compara el panel: `"origen": sello.origen_head()`.
4. Sumar `.reglas.json` con el perfil, el idioma del cliente y la URL: `{"perfil": "sitio", "idioma": "voseo", "url": "https://…/", "idioma_por_archivo": [["*.md", "neutro"]]}`.
5. Correr `bash fabrica/controles.sh ../herramientas` y abrir el PR.
6. **Paso de Manu:** aprobar el PR desde Actions (crea `produccion` con la primera publicación sellada) y cambiar la rama de Cloudflare Workers Builds de `main` a `produccion`.

## Cambiar la fábrica

Se cambia acá, con su prueba en `pruebas/`, y se corre `python3 pruebas/correr.py` desde la raíz del repositorio (corre también las de esta carpeta). Después se vuelve a instalar en cada sitio con un PR por sitio: hasta que no se instale, la revisión de ese sitio corta porque la copia no es igual a la original.

## Lo que el sello no cubre

El sello frena errores: un commit que llega a `produccion` sin pasar por la fábrica no sale en vivo. No frena a alguien con permiso de escritura que quiera saltearlo, porque `build.py` está dentro del mismo árbol. Es la misma regla que en el panel.
