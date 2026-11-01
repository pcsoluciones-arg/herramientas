# ProgresoDeLectura

Línea fina pegada a la barra superior que muestra cuánto falta para el final de la página, y que toma el tono de la sección que se está leyendo.

```html
<div class="r-progreso"><i></i></div>
<script>
  addEventListener('scroll', () => {
    const r = scrollY / (document.documentElement.scrollHeight - innerHeight);
    document.querySelector('.r-progreso i').style.width = (r * 100) + '%';
  }, {passive: true});
</script>
```

**Qué aporta el proyecto.** El color de cada sección o de cada página (en PC Soluciones, uno por página).

**Reglas.** De 2 a 3px de alto, sin brillo. Va pegada al borde inferior de la barra superior, nunca suelta en medio de la pantalla. Solo en páginas largas de lectura (Cómo trabajamos, casos, artículos); en una landing corta sobra.

**De dónde viene.** climbup.com.ar (referente guardado en septiembre de 2026), aplicada en el sitio de PC Soluciones; Autoemoción y el sitio de Marta tienen una versión de 1px con brillo.
