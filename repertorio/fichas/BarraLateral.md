# BarraLateral

Barra de navegación de la computadora que se pliega de 232 a 76px: abierta muestra ícono y nombre por grupos; plegada deja solo los íconos con tooltip, y los grupos se vuelven una línea.

```html
<nav class="r-lateral">
  <div class="grupo">Clientes</div>
  <a aria-current="page"><svg>…</svg><span class="txt">Clientes</span></a>
  <a><svg>…</svg><span class="txt">Trabajos</span><span class="cuenta">3</span></a>
  <div class="pie">…Configuración, usuario…</div>
</nav>
```

**Reglas.**
- Los ítems van en grupos de dos a cinco, con un rótulo corto. Un grupo solo tiene sentido si hay dos.
- Lo que se usa todos los días arriba; configuración, manual y usuario en el pie.
- El ítem activo se marca con `acento-suave` y `acento`. El contador (`.cuenta`) solo para lo que pide acción (atrasado, sin cobrar), nunca como adorno.
- Plegada se recuerda por navegador. En la tablet arranca plegada; en el teléfono no existe: la reemplaza la barra flotante de abajo.
- El rótulo de grupo es el único lugar del panel donde se usa mayúscula espaciada.

**De dónde viene.** CRW Base (232 a 76 px con tooltips) y el panel de PC Soluciones (plegado recordado, grupos Gestión y Módulos).
