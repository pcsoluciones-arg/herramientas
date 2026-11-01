# UnaTareaPorPantalla

Una app para quien ejecuta: cada pantalla plantea una sola tarea, dice en qué paso está y tiene un único botón principal, fijo abajo, que es lo que sigue.

```html
<main class="r-tarea">
  <span class="r-tarea__paso">Paso 2 de 3</span>
  <h1>Mandale la imagen</h1>
  <p class="r-tarea__lead">Dental Núñez contestó. Copiá el mensaje y pegalo en el chat.</p>
  <div class="r-tarea__cuerpo">…la tarjeta del negocio, el mensaje…</div>
  <div class="r-tarea__accion"><button class="r-control r-control--principal">Copiar mensaje</button><button class="r-control r-control--secundario">Ya lo mandé</button></div>
</main>
```

**Reglas.**
- Un título que dice qué hacer, en imperativo, y una línea que dice por qué. Nada más arriba.
- Un botón principal con el verbo de la acción y, como máximo, uno secundario. Tres acciones en una pantalla es una pantalla de panel, no de app.
- El botón principal queda fijo abajo, encima de la barra flotante, con un degradé del papel para que el contenido pase por debajo.
- Lo que se necesita para la tarea está en la pantalla (el mensaje a copiar, el número a buscar). Nunca hay que ir a otra pestaña a buscar un dato.
- Al terminar, la pantalla dice qué pasó y qué sigue ("Listo. Mañana te avisamos si contestó.") y vuelve sola a la lista.
- El texto de la app va en el registro del proyecto (en Prospéctor, voseo).

**Cuándo no.** En administración: ahí se compara y se decide mirando muchas cosas, y manda la capa Paneles.

**De dónde viene.** El modo prospector del panel de PC Soluciones, que ya trabaja por pasos (Paso 2 · El mensaje, Paso 3 · Cuando elijan uno) pero dentro de tarjetas plegadas de una lista.
