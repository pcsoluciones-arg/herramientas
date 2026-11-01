# HojaInferior

Panel que sube desde el borde inferior para cargar o editar algo sin salir de la pantalla, con un asa para arrastrarlo hacia abajo y cerrarlo.

```html
<div class="r-hoja" role="dialog" aria-label="Nueva tarea">
  <div class="r-hoja__asa"></div>
  …
</div>
```

**Reglas.** Radio `radio-xl` solo arriba, `sombra-hoja`, entrada de 300ms con `cubic-bezier(.2,.8,.2,1)`. Detrás, un velo suave con desenfoque de 4 a 6px. Se cierra tocando el velo, con Cancelar o arrastrando más de 110px. Campos de 44px de alto y 16px de letra. En escritorio pasa a ventana centrada con `radio-l`.

**Cuándo usarla.** Formularios cortos en paneles (nueva tarea, cargar un gasto, cambiar el estado de un vehículo), en lugar de los `prompt()` del navegador o de páginas nuevas.

**De dónde viene.** CRW Base (formularios propios que reemplazaron los `prompt()`).
