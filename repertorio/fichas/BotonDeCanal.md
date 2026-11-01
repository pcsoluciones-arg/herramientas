# BotonDeCanal

Tres botones con roles fijos: principal (la acción de la marca, en `acento`), de canal (WhatsApp, en `canal-whatsapp`) y secundario (superficie con borde).

```html
<a class="r-boton r-boton--canal"
   href="https://wa.me/549…?text=…"
   data-lead="whatsapp" data-lead-origin="cabecera">Escribir por WhatsApp</a>
```

**Reglas.**
- Un solo color por botón, sin degradé.
- El verde de WhatsApp es `canal-whatsapp` (#188741), que pasa AA con texto blanco; el #25D366 de manual no.
- Cada botón de WhatsApp lleva un mensaje precargado propio según dónde está y un `data-lead-origin` que se mide (GA4 `generate_lead` y beacon propio, como en Autoemoción).
- El logo de WhatsApp se usa oficial, descargado, nunca redibujado.
- El botón principal sigue siendo el color de la marca: si todos los botones pasan a verde, la página empieza a leerse como plantilla de WhatsApp (lección de las landings de APK).
- Alto de 44px como mínimo; hover con `sombra-2` y 1px hacia arriba.

**De dónde viene.** Landings de APK, sitio de Autoemoción y preferencias de medición de PC Soluciones.
