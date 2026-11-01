# VisorConFondoDesenfocado

Al abrir una foto, obra o video, la página queda detrás desenfocada y oscurecida en lugar de taparse con un velo negro: se sigue sabiendo dónde se estaba.

```css
html.visor-abierto main, html.visor-abierto header, html.visor-abierto footer {
  filter: blur(14px) brightness(.85) saturate(.85);
}
```

```html
<div class="r-visor abierto" role="dialog" aria-modal="true">
  <img class="r-visor__pieza" src="obra.webp" alt="…">
</div>
```

**Reglas.** Se desenfoca la página (main, cabecera y pie), no el velo: el velo solo agrega un tono (`rgba(10,12,14,.45)`). La pieza usa `sombra-3`. Escape y tocar afuera cierran; el foco vuelve al elemento que abrió el visor. En celular, deslizar hacia los costados avanza y hacia abajo cierra. Las obras conservan sus márgenes de papel.

**Cuándo usarlo.** Galerías de vehículos, obras, trabajos realizados, capturas de un caso, videos.

**De dónde viene.** Sitio de Marta Pérez Temperley (visor de obra y de video). En Autoemoción el visor de la ficha usa hoy un velo plano casi negro: es un buen candidato para pasarlo a esta técnica.
