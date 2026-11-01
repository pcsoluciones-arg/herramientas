# PestanasYFiltros

Pestañas en píldora para las vistas de una sección y chips con conteo para filtrar una lista. Son dos cosas distintas y se ven distintas: la pestaña cambia de pantalla, el filtro cambia lo que se muestra en la misma.

```html
<nav class="r-pestanas" role="tablist">
  <button role="tab" aria-selected="true">Resumen</button><button role="tab">Prospectos</button>…
</nav>
<div class="r-filtros">
  <button aria-pressed="true">En el sitio <span class="n">8</span></button><button>Retirados <span class="n">1</span></button>
</div>
```

**Reglas.**
- La pestaña activa se rellena con `tinta` y texto en `papel`; el filtro activo, con `acento-suave` y texto en `acento`. Así no se confunden.
- El mismo nombre arriba (pestañas) y abajo (barra flotante del celular). Un nombre por pantalla.
- Hasta cinco pestañas por sección. Con más, sobra una sección o falta una ficha.
- Los filtros muestran el conteo; un filtro sin nada que mostrar se queda con 0, no desaparece.
- En el celular las pestañas se deslizan de costado con la siguiente asomando (ver FichaConPestanas), y los controles suben a 40 y 36px.

**De dónde viene.** Del panel de PC Soluciones (filtro de rubros con conteo, pestañas de módulo) y de la barra de pestañas de CRW Base.
