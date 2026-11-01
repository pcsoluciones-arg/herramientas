# EstadosSemanticos

Cuatro estados (listo, atención, problema, neutro), cada uno con su trío de tokens suave / tinta / borde, en claro y oscuro, para chips, avisos y contadores. El color acompaña a la palabra, nunca la reemplaza.

```html
<span class="r-estado r-estado--listo">En el sitio</span>
<span class="r-estado r-estado--atencion">Borrador</span>
<span class="r-estado r-estado--problema">No se publicó</span>
<span class="r-estado">Retirado</span>
<div class="r-aviso r-aviso--atencion"><svg>…</svg>El token de GitHub vence en 12 días.</div>
```

**Por qué cuatro y no más.** Cada estado nuevo es una decisión más para quien mira. Listo, atención y problema cubren todo lo que un panel necesita decir sobre una cosa; neutro es lo que no está en juego. Si un flujo pide un quinto (por ejemplo, "en curso" distinto de "atención"), se usa `acento-suave` con `acento`, que ya existe.

**Cómo está hecho.** El chip lleva un punto de 6px del mismo color del texto al 70%: así se distingue también en escala de grises. Los tríos vienen del panel de PC Soluciones, donde ya pasaron la prueba de contraste en los dos temas (texto sobre suave 4,5:1 o más).

**Cuándo no.** Para marcar un filtro activo o una pestaña (eso es `acento`), ni para decorar: un estado dice algo sobre el objeto que acompaña.
