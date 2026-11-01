# FichaConPestanas

La ficha de un registro (un cliente, un prospecto) con todo lo suyo en pestañas: en la computadora caben todas; en el teléfono se deslizan de costado con la siguiente asomando, como un carrusel.

```html
<section class="r-ficha">
  <header class="r-ficha__cab"><span class="ini">EM</span><div><h2>Emiliano · Plomero de Barrio</h2><span class="r-detalle">Núñez · abono Mantenimiento</span></div></header>
  <nav class="r-ficha__pestanas" role="tablist"><button role="tab" aria-selected="true">Resumen</button><button role="tab">Trabajos</button>…</nav>
  <div class="r-ficha__cuerpo">…</div>
</section>
```

**Reglas.**
- La ficha es el único lugar donde todo lo de un registro está junto. Las listas transversales (Trabajos, Publicaciones) muestran las mismas cosas filtradas por otro criterio; la ficha las filtra por el registro.
- Las pestañas usan subrayado en `acento`, no píldora: así se distinguen de las pestañas de sección (ver PestanasYFiltros).
- En el teléfono, la fila de pestañas se desvanece en el borde derecho (`mask-image`) para que se note que sigue, y la pestaña activa se lleva a la vista al abrir (`scrollIntoView`).
- Hasta ocho pestañas. Resumen va primero y es lo que se ve al abrir.
- Las acciones principales del registro (editar, cobrar, publicar) van en la cabecera, no dentro de una pestaña.

**De dónde viene.** Decisión del panel de PC Soluciones 2.0 (ficha del cliente) y el gesto del carrusel con asomo.
