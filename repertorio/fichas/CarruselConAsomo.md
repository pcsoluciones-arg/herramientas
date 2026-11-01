# CarruselConAsomo

Fila deslizable con scroll-snap donde se ve un pedazo de la tarjeta anterior y la siguiente, para que se entienda que hay más sin depender de puntos ni contadores.

```html
<div class="r-carrusel">
  <div class="r-carrusel__pista"><article>…</article>…</div>
  <button class="r-carrusel__flecha prev" aria-label="Anterior">…</button>
  <button class="r-carrusel__flecha next" aria-label="Siguiente">…</button>
</div>
```

**Reglas.** El asomo es `asomo-carrusel` (28px) a cada lado. Las flechas van a los costados de la sección, visibles sin hacer scroll, y se apagan en los extremos. Cuando la tarjeta tiene imagen arriba, centrar las flechas sobre la imagen y no sobre la tarjeta entera (el sitio de Marta lo resuelve midiendo la imagen y escribiendo `--mitad`). En escritorio, dos tarjetas por vista; en celular, una.

**Cuándo usarlo.** Para reemplazar listas largas que obligan a scrollear: vehículos, casos, obras, testimonios.

**De dónde viene.** Preferencia de diseño de octubre de 2026 y el carrusel del sitio de Marta.
