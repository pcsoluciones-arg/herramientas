# Fábrica de presencia en este sitio

Esta carpeta es una copia de `pcsoluciones-arg/herramientas/sitios/`, hecha por `instalar.py`. No se edita acá: se cambia el original en `herramientas` y se vuelve a instalar. La revisión de cada pedido de cambio (PR) corta si la copia no es igual a la original. El único archivo propio del sitio es `config.json`.

## Recorrido

| Cómo entra el cambio | Qué pasa |
|---|---|
| El panel PCS publica fotos o textos (push a `main`) | `publicar.yml` corre los controles de código. Si el riesgo es bajo, sella y publica. Si es alto, abre el pedido "Cambios en main esperan tu aprobación" y no publica. |
| Un PR de la fábrica, con la etiqueta `listo` | `revision.yml` corre los controles. Riesgo bajo: `publicar.yml` lo junta en `main` y publica. Riesgo alto: etiqueta `espera-manu`. |
| Manu aprueba | GitHub → Actions → Publicar → Run workflow, con el número del PR (o vacío para publicar `main` tal como está). |

## Ramas y sello

- **`produccion` es la rama que publica Cloudflare.** Solo la escribe `publicar.yml`.
- **`main` es donde se juntan los cambios.** El panel escribe ahí.
- **Cada commit de `produccion` lleva un sello** (`sello.py`): un certificado de GitHub atado al contenido exacto del commit, y la línea `Publica-main` con el commit de `main` que publica. `build.py` lo verifica en Cloudflare y escribe ese commit en `version.json`, que es lo que mira el panel.

## Riesgo

Lo decide `riesgo_sitio.py`. Sale solo: fotos nuevas en `fotos/` y `ficha-google/`, lo que carga el panel en las secciones de `secciones.json`, textos en campos que ya existen de `contenido.json` y documentación. Todo sin datos de contacto ni precios, sin retirar más fotos de las que entran y en menos de 300 líneas. Lo demás espera a Manu.

## Controles

`controles.sh` corre, en orden: la copia igual a la original, `build.py`, `wrangler deploy --dry-run`, `revisar.py --perfil sitio` sobre `dist/` y `navegador.py` a 390 y 1360 px. Para correrlos a mano, con `herramientas` al lado del sitio:

```
bash fabrica/controles.sh ../herramientas
```

Después de publicar, `publicar_sitio.py` controla en vivo `version.json`, que todas las imágenes respondan 200 y que `www` redirija con 301.

## Archivos

| Archivo | Qué hace |
|---|---|
| `config.json` | Repositorio, flujo del sello, URL y Worker del sitio |
| `sello.py` | Verificación del sello (la usa `build.py` en Cloudflare) |
| `riesgo_sitio.py` | Filtro de riesgo |
| `publicar_sitio.py` | Publicación (lo corre `publicar.yml`) |
| `controles.sh` | Controles de código |
