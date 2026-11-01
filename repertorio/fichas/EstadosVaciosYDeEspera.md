# EstadosVaciosYDeEspera

Qué muestra una pantalla cuando no hay nada (todavía, o ya) y cuando está cargando: una frase que dice qué pasa y qué hacer, y un esqueleto con la forma del contenido que viene.

```html
<div class="r-vacio"><svg>…</svg><b>Por hoy no queda nada por mandar</b><p>Buen trabajo. Mañana a las 9 vas a tener negocios nuevos.</p></div>
<div class="r-esqueleto"><i class="alta"></i><i style="width:60%"></i><i style="width:40%"></i></div>
```

**Reglas.**
- Tres vacíos distintos, con texto distinto: **todavía nada** (recién empieza: decir qué va a aparecer y cuándo), **ya nada** (terminó: felicitar y decir cuándo vuelve a haber) y **nada con este filtro** (ofrecer sacar el filtro).
- El vacío de "ya nada" es un momento bueno: se dice. Sin emojis; con un ícono de línea del set.
- Mientras carga, un esqueleto con la forma de lo que viene (una tarjeta, tres líneas), nunca una rueda sola ni la pantalla en blanco. Se respeta `prefers-reduced-motion`.
- Si tarda más de 8 segundos, el esqueleto se reemplaza por un texto ("Tarda más de lo normal. Revisá la conexión.") con un botón para reintentar.

**De dónde viene.** Los estados vacíos del modo prospector ("Por hoy no queda nada por mandar. Buen trabajo.") y la carga con memoria del panel (1.16.4).
