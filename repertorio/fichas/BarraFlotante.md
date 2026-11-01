# BarraFlotante

Barra de pestañas en forma de cápsula de vidrio, separada de los bordes de la pantalla, por la que se ve pasar el contenido. Es la navegación principal de los paneles en el celular.

```html
<nav class="r-barra r-vidrio" style="position:fixed;left:12px;right:12px;bottom:max(12px, env(safe-area-inset-bottom))">
  <button aria-current="page"><svg>…</svg>Hoy</button>
  …
</nav>
```

**Qué aporta el proyecto.** De tres a cinco destinos con ícono de línea y una palabra cada uno. La pestaña activa toma `acento` sobre `acento-suave`.

**Reglas.** El contenido deja 100px libres abajo para que el último elemento no quede tapado. Respetar `safe-area-inset-bottom`. Los globos de notificación van en `error` con un borde del color de la barra, que los recorta. En escritorio la misma navegación pasa a barra lateral plegable (de 232 a 76px, con tooltips al plegarse), como en CRW Base y Prospector.

**De dónde viene.** CRW Base y Prospector, que ya la comparten. Se puede llevar al panel de Autoemoción y al futuro panel de PC Soluciones.
