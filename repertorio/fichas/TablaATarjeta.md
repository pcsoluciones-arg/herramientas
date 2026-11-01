# TablaATarjeta

Una tabla que en la computadora es tabla y en el teléfono se vuelve una lista de tarjetas, sin duplicar el HTML: cada celda muestra su encabezado desde `data-col`.

```html
<table class="r-tabla">
  <thead><tr><th>Cliente</th><th>Trabajo</th><th class="n">Monto</th><th>Estado</th></tr></thead>
  <tbody><tr class="clic">
    <td data-col="Cliente">Emiliano</td><td data-col="Trabajo">Página</td><td class="n" data-col="Monto">$ 178.200</td><td data-col="Estado"><span class="r-estado r-estado--listo">Entregado</span></td>
  </tr></tbody>
</table>
```

**Reglas.**
- Hasta `corte-telefono` (640px) la tabla se apila: cada fila es una tarjeta con `sombra-1`, cada celda una línea rótulo / valor.
- Las columnas numéricas llevan `.n`: alineadas a la derecha y con `tabular-nums`, también en la tarjeta.
- Una fila que se puede abrir lleva `.clic`: hover en la computadora, toda la tarjeta tocable en el teléfono.
- Hasta seis columnas. Con más, lo que sobra va a la ficha del registro, no a la tabla.
- El encabezado de la tabla va en `superficie-2`, sin bordes verticales.

**De dónde viene.** El panel de PC Soluciones (`td::before{content:attr(data-col)}`).
