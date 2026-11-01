# NegroConProfundidad

En los modos y secciones oscuras, el fondo deja de ser un negro plano. Gana espacios luminosos: una luz motivada que cae desde arriba, un halo suave detrás del protagonista y los bordes que se apagan, con grano encima.

```html
<section class="r-profundo">…</section>
<section class="r-profundo" style="--luz:226 190 120; --intensidad:.13">…</section>
<section class="r-profundo" style="--luz-x:72%; --luz-y:10%; --halo-y:40%">…</section>
```

**Cómo está hecho.** Tres capas sobre `negro-profundo`, más el grano oscuro (`grano-sobre-oscuro`), que además evita el escalonado del degradé:
- **Luz cenital.** `--luz-x` y `--luz-y` la mueven hacia donde está el sujeto.
- **Halo.** Va detrás de la pieza protagonista, al 60% de la intensidad. `--halo-x` y `--halo-y` lo ubican.
- **Viñeta.** Oscurece los bordes.

**Qué aporta el proyecto.** El color de la luz en `--luz` (terna RGB):
- neutra cálida por defecto;
- el oro muy bajo en Autoemoción y Crowd FC;
- el teal muy bajo en el oscuro de Prospector.

`--intensidad` va de .08 a .16.

**Reglas que la separan de los orbes de plantilla.**
- Una sola fuente de luz, con dirección; nunca manchas sueltas en las esquinas.
- La luz cae sobre algo (el sujeto, el titular, la pieza), no flota sola.
- Un solo tono y desaturado. Nada de violeta, azul eléctrico o fucsia saturados.
- Se percibe como profundidad. Si se ve como mancha de color, bajar `--intensidad`.

**Cuándo usarla.**
- Héroes y secciones oscuras de Autoemoción y Crowd FC.
- Fondo del visor de piezas.
- Modo oscuro de cualquier panel o app, con `.r-profundo--app`: intensidad `profundidad-app` (.06), luz más arriba y halo en el tercio superior, donde está el encabezado. El fondo respira sin competir con los datos.

**De dónde viene.** Gusto propio declarado en octubre de 2026. Antecedente: las luces radiales tenues del sitio de Autoemoción, que ya van en esta dirección.
