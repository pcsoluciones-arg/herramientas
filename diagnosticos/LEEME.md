# Fábrica de diagnósticos

Herramientas para armar el diagnóstico con presupuesto de un negocio prospectado (formato `diagnostico/v2`: un solo link en `pcsoluciones.com.ar/d/<slug>`, con el presupuesto oculto hasta que Manu lo activa). El recorrido completo lo sigue la skill `fabrica-diagnosticos` de la cuenta de Manu. Salen de la primera corrida, la de la Guardería Altos del Canal (6/11/2026, registro en el documento del proyecto `claude/fabrica-diagnosticos-corrida-1.md`).

Este repositorio es público: acá van solo las herramientas y un negocio inventado de ejemplo. Los datos de cada negocio real (chat, fotos, `marca.json`, `caso.json`, INTERNO, registro) viven en OneDrive, en `07 - Prospector/Diagnósticos/<slug>/`.

## Qué hay

| Archivo | Para qué | Uso |
|---|---|---|
| `tr.py` | Transcribe los audios del chat de WhatsApp exportado | `python3 -I tr.py audio1.opus audio2.opus > transcripcion.txt` |
| `fotos.py` | Pasa una foto a data URL JPEG de 1000 px y calidad 76, debajo de 1 MB | `from fotos import dataurl` |
| `portadas.py` | Grilla de portadas candidatas con el molde real, una letra por opción | `python3 -I portadas.py base.json grilla.jpg f1.jpg@center\ 30% f2.jpg` |
| `molde_landing.py` | Página de ejemplo para el mockup, con la estructura final de Altos del Canal | `python3 -I molde_landing.py marca.json pagina-ejemplo.html` |
| `capturar_landing.py` | Capturas de la página de ejemplo: computadora, celular con el área segura del iPhone y páginas completas | `python3 -I capturar_landing.py pagina-ejemplo.html capturas/` |
| `mockup.py` | Mockup de computadora e iPhone en 1400 × 870 | `python3 -I mockup.py capturas/desk.png capturas/movil-iphone.png mockup.jpg` |
| `armar.py` | Arma el `diagnostico-<slug>.json` desde `caso.json` (textos y rutas de fotos) | `python3 -I armar.py caso.json diagnostico-<slug>.json` |
| `render.mjs` | Arma la página con `htmlPropuesta` del repositorio del panel (privado: tiene que estar en la sesión) | `node render.mjs diagnostico.json pagina.html [--panel ../panel-prospector] [--ahora AAAA-MM-DD]` |
| `verificar.py` | 5 tamaños de pantalla, scroll lateral, contenido que no entra, PDF en hojas A4 y la tira de pantallas | `python3 -I verificar.py pagina.html diagnostico-<slug>` |
| `registro.py` | Registro de la corrida: pasos, tiempos, decisiones de Manu, problemas, revisor | ver `python3 registro.py -h` |
| `tarifario.json` | Lista de precios vigente que usa `revisar.py --perfil diagnostico` | se actualiza cuando cambia el tarifario |
| `ejemplo/` | Negocio inventado (Bicicletería Rueda Libre) para probar todo: `marca-ejemplo.json`, `caso-ejemplo.json` y `hacer_imagenes.py` | |

El revisor de datos (agente) está en `skills/revisor-diagnostico/SKILL.md`, y sus controles de código en `revisar.py --perfil diagnostico`.

## Recorrido con las herramientas

```
python3 -I tr.py chat/*.opus > transcripcion.txt
python3 -I portadas.py base.json grilla-portadas.jpg fotos/f21.jpg@center\ 30% fotos/f51.jpg
python3 -I molde_landing.py marca.json pagina-ejemplo.html
python3 -I capturar_landing.py pagina-ejemplo.html capturas/
python3 -I mockup.py capturas/desk.png capturas/movil-iphone.png mockup.jpg
python3 -I armar.py caso.json diagnostico-<slug>.json
node render.mjs diagnostico-<slug>.json pagina.html
python3 -I verificar.py pagina.html diagnostico-<slug>
python3 revisar.py --perfil diagnostico diagnostico-<slug>.json diagnostico-<slug>.pdf
```

Para el PDF con el presupuesto activo, armar una copia del JSON con `presupuesto.activo: true` y repetir `render.mjs` y `verificar.py`.

## Probar con el ejemplo

```
cd diagnosticos
python3 -I ejemplo/hacer_imagenes.py
python3 -I molde_landing.py ejemplo/marca-ejemplo.json /tmp/landing.html
python3 -I capturar_landing.py /tmp/landing.html /tmp/capturas
python3 -I mockup.py /tmp/capturas/desk.png /tmp/capturas/movil-iphone.png /tmp/mockup.jpg
python3 -I armar.py ejemplo/caso-ejemplo.json /tmp/diag.json
node render.mjs /tmp/diag.json /tmp/diag.html --ahora 2026-11-06
python3 -I verificar.py /tmp/diag.html /tmp/diag
python3 ../revisar.py --perfil diagnostico /tmp/diag.json /tmp/diag.pdf
```

## Qué necesita

- Python 3 con Pillow y Playwright (`pip install pillow playwright` y `playwright install chromium`). `tr.py` además ffmpeg, numpy y faster-whisper.
- Node 18 o más, y el repositorio `pcsoluciones-arg/panel-prospector` al lado de `herramientas` (o `--panel`). `render.mjs` copia sus tipografías con el nombre que usa el panel (`sg.woff2` y `mr.woff2`): sin eso el PDF sale con la letra del sistema.
- Las tipografías de cada negocio se bajan con npm (`npm install @fontsource/<fuente>`) y se indican en `marca.json` como archivos woff2.
- El logo de WhatsApp es el oficial de Meta (`whatsapp-blanco.svg`, en la carpeta de Impianti en OneDrive). No se redibuja.

## marca.json

Lo que cambia de un negocio a otro en la página de ejemplo. Rutas relativas al propio archivo.

| Campo | Qué es |
|---|---|
| `nombre` | Nombre del negocio (título de la página y texto alternativo del logo) |
| `logo` | PNG del logo en negativo (letras claras), para que se lea sobre el vidrio de la barra |
| `whatsapp_svg` | El SVG oficial de WhatsApp |
| `fotos.negocio` | La foto que muestra el negocio entero de un vistazo (cabecera, a la derecha) |
| `fotos.textura` | La textura del lugar (chapa, madera, pared), sin textos; puede generarse con IA a partir de un prompt |
| `fotos.instalaciones` | Foto real del lugar o de un cartel |
| `fotos.banda` | Foto del lugar para la franja final |
| `colores` | `principal`, `oscuro`, `boton`, `detalle` (íconos y estrellas), `ola1` y `ola2` (las dos líneas de la ondulación), `blanco` (el blanco de la marca, medido en sus fotos, nunca blanco puro), `tilde` y, si hace falta, `texto_boton` |
| `tipografias` | `titulo` (familia, archivo woff2, estilo, peso y ancho) y `texto` (familia y un woff2 por peso) |
| `textos` | `menu`, `boton`, `titulo`, `bajada`, `secundario`, `estrellas`, tres `recuadros` (ícono, título, texto), `instalaciones` (título, bajada y lista) y `banda` (título y texto) |

Cada foto admite `pos` (foco en CSS), `recorte` ([izquierda, arriba, derecha, abajo]) y `calidad`. Íconos disponibles en `ICONOS` de `molde_landing.py`.
