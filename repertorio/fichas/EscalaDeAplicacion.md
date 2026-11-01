# EscalaDeAplicacion

Seis tamaños de texto y dos alturas de control para pantallas de trabajo: cierran la escala para que un panel no acumule quince tamaños distintos.

| Estilo | Tamaño | Para |
| --- | --- | --- |
| `app-pantalla` | 20/26, 700 | El título de la pantalla, uno solo. |
| `app-bloque` | 16/22, 650 | Títulos de tarjeta, bloque y ventana. |
| `app-cuerpo` | 15/22, 400 | Texto de lectura, ayuda, avisos. |
| `app-control` | 14/20, 600 | Botones, celdas, campos, pestañas. |
| `app-detalle` | 13/18, 500 | Fechas, metadatos, rótulos. |
| `app-chip` | 12/16, 700 | Chips y contadores. Es el mínimo: nada por debajo. |
| `app-cifra` | 26/30, 700 | Totales del escritorio, con `tabular-nums`. |

**Controles.** `alto-control` (40px) en la computadora y `alto-control-tactil` (44px) en teléfono y tablet. Los campos del celular van a 16px para que el iPhone no haga zoom al tocarlos. Radio `radio-s` en todos.

```html
<div class="r-app">
  <h1>Contenido y redes</h1>
  <button class="r-control r-control--principal">Agregar trabajo</button>
  <input class="r-control r-control--campo" placeholder="Buscar">
</div>
```

**Cuándo usarla.** En cualquier panel de gestión (PC Soluciones, CRW Base, Autoemoción). Se combina con la escala de Sitios solo en una pantalla de bienvenida o en el escritorio, nunca dentro de listas y formularios.

**Qué aporta el proyecto.** Su tipografía (en PC Soluciones, Space Grotesk para títulos y controles y Manrope para el cuerpo) y el color de acento. El botón principal proyecta sombra de su propio color por `--sombra-acento` (ver Sombras).
