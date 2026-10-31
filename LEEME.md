# Herramientas de PC Soluciones

Herramientas compartidas que usan el panel, los sitios de clientes, el sitio propio y los informes. Un solo código para todos, así no hay copias que se desactualizan.

## revisar.py: revisor de reglas

Revisa con código las reglas de escritura y de método que no necesitan juicio: guiones largos, voseo o tuteo según el proyecto, títulos del tipo "no es X: es Y", marcadores sin reemplazar, Open Graph, schema igual al texto visible, botones de WhatsApp medibles, área segura del iPhone, zips con archivos vacíos, imágenes con C2PA, .docx con alto de línea fijo, PDF fuera de A4, claves en el código y el orden de la carpeta raíz. La lista completa, con el origen de cada regla, está en el documento del proyecto `claude/reglas-verificables.md`.

Solo lee: no cambia ningún archivo. Usa Python 3 sin bibliotecas externas.

```
python3 revisar.py --perfil sitio --idioma voseo dist/        # un sitio armado
python3 revisar.py --perfil sitio --preview --idioma neutro preview/
python3 revisar.py --idioma neutro informe.md propuesta.docx  # un entregable
python3 revisar.py --perfil carpeta "~/mnt/PC Soluciones"      # orden de la raíz
python3 revisar.py .                                           # toma la configuración de .reglas.json
```

Perfiles:

| Perfil | Para qué | Reglas que suma |
|---|---|---|
| `texto` (por defecto) | Documentos, propuestas, informes | Guiones, idioma, títulos, marcadores, claves; zip, docx, pdf e imágenes si los hay |
| `sitio` | La carpeta armada de un sitio (lo que se publica) | Lo anterior, más Open Graph, indexación, área segura, WhatsApp, copy público, firma del pie y schema |
| `panel` | El repositorio del panel | Lo de `texto`, más la escala de radios y de letra del CSS |
| `carpeta` | La raíz de PC Soluciones en OneDrive | Solo nombres: qué hay en la raíz, `_BORRAR` de más, builds dentro de OneDrive |

En los `.md`, lo que va entre comillas invertidas (código o un ejemplo citado) no se revisa.

Resultado: una línea por hallazgo, `FALLA` o `AVISO`. Sale con código 1 si hay alguna `FALLA`, así se puede usar antes de un push o de una entrega.

### Configuración por proyecto

Un archivo `.reglas.json` en la raíz del proyecto evita repetir opciones:

```json
{"perfil": "sitio",
 "idioma": "voseo",
 "idioma_por_archivo": [["*.md", "neutro"]],
 "ignorar": ["fuente/*"],
 "preview": false}
```

## Cómo se usa desde otra conversación

Agregar el repositorio a la sesión (`pcsoluciones-arg/herramientas`) y correr `revisar.py` sobre lo que se va a publicar o entregar. En la Mac, si hace falta, copiar `revisar.py` a `~/Trabajo-local/` y correrlo desde ahí: no va dentro de OneDrive.

## Reglas de este repositorio

- Documentación y comentarios en español neutro con tuteo, sin guiones largos.
- Sin claves ni datos de clientes.
- Una regla nueva entra con su caso de prueba en `pruebas/`, y antes de subirla se corre `python3 pruebas/correr.py`.
- Commits firmados como Manuel Tonnelier (pcsolucionesbelgrano@gmail.com).
