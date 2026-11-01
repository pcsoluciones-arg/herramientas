# Revisores de la Fábrica de presencia

Las cuatro skills de los revisores de la etapa 2 de PCS Central (doc del proyecto `claude/fabrica-presencia-plan.md`). Revisan los sitios de clientes (`sitio-*`) y, los de idioma y visual, también las piezas para redes.

| Skill | Revisor | Modelo | Revisa |
|---|---|---|---|
| `revisor-idioma/` | Idioma y estilo | Sonnet 5.5 | Sitio y piezas |
| `revisor-tecnica/` | Técnica | Haiku 5.5 | Sitio |
| `revisor-seo-geo/` | SEO y GEO | Sonnet 5.5 | Sitio |
| `revisor-visual/` | Visual | Sonnet 5.5 con visión | Sitio y piezas |

El original de cada skill vive acá. En la cuenta de Manu hay una versión corta que lee esta (decisión 4 del plan).

## Cómo se usan

Cada revisor corre con contexto limpio: no vio cómo se hizo el cambio. Antes de llamarlos, quien orquesta (la tarea programada "Fábrica de sitios" o una conversación) corre los controles de código y deja:

| Entrada | Dónde |
|---|---|
| El repositorio del sitio, en la rama del cambio | la carpeta del sitio |
| El sitio armado | `dist/` (lo arma `build.py`) |
| El informe de los controles (`revisar.py` y `navegador.py`) | `bash fabrica/controles.sh ../herramientas /tmp/capturas > /tmp/controles.txt` |
| Las capturas a 390 y 1360 px, con el scroll en 0 | `/tmp/capturas/` |
| El cambio, si es un PR | `git diff origin/main...HEAD` |
| El pedido, si lo hay | el texto del issue |
| Las piezas, si se revisan piezas | la imagen y su texto |

En un sitio que todavía no tiene la fábrica instalada, los controles se corren a mano: `python3 ../herramientas/revisar.py --perfil sitio --idioma <idioma> --url <url> dist/` y `python3 ../herramientas/sitios/navegador.py dist/ --capturas /tmp/capturas`.

Cada revisor lee primero el informe de los controles y **no repite lo que el código ya revisó**: lo que es FALLA ya frena la publicación por sí solo.

## Qué devuelven

Un bloque JSON y nada más, igual que los revisores del panel:

```json
{"revisor": "idioma" | "tecnica" | "seo-geo" | "visual", "veredicto": "aprobado" | "cambios",
 "observaciones": [{"gravedad": "bloquea" | "sugerencia", "donde": "archivo:línea, sección o captura", "que": "qué pasa", "como": "cómo se corrige"}]}
```

`veredicto` es "cambios" si hay al menos una observación que bloquea. En un cambio, cada revisor bloquea solo lo que el cambio trae o empeora; lo que ya estaba va como sugerencia que empieza con «Ya estaba:». Cuando Manu llama a un revisor en una conversación, devuelve lo mismo como una lista corta en vez de JSON.

## Reglas para cambiarlas

- Una regla que el código puede decidir sin equivocarse seguido va a `revisar.py` o a `sitios/navegador.py`, no a una skill.
- Las skills dicen qué mirar y cómo decidir la gravedad. El criterio de diseño vive en `repertorio/` (copia del Repertorio de estilo de claude.ai), no se copia en las skills.
- Documentación en español neutro con tuteo, sin guiones largos.
