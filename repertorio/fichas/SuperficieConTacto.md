# SuperficieConTacto

Los bloques de color y los fondos llevan grano, variación de tono o fibra, para que se sientan como un material con tacto y calidez y no como un relleno digital plano.

```html
<section class="r-tono r-grano" style="background-color:#1F5A3F">…</section>
<main class="r-fibra" style="background-color:#EFE9DD">…</main>
```

**Las tres texturas.** Las tres se pueden combinar.

| Clase | Qué hace | Intensidad |
| --- | --- | --- |
| `.r-grano` | Puntos de ruido oscuros encima del color, sin cambiarlo. En fondos oscuros, `.r-grano--oscuro` (puntos claros). | `grano-sobre-claro`, `grano-sobre-oscuro` |
| `.r-tono` | Luz que entra desde arriba a la izquierda y baja un punto la temperatura hacia abajo, siempre dentro del mismo color. | Fija; se nota más en colores medios. |
| `.r-fibra` | Grano más abierto y cálido, estirado en horizontal como fibra de papel. | `fibra` |

**Reglas.**
- Lo habitual es tono más grano en bloques de color y fibra en fondos de lectura.
- El grano se percibe pero no se ve: si a un metro de la pantalla se distinguen los puntos, sobra.
- El tono nunca cambia de color: no es un degradé de un color a otro, es luz sobre un mismo material.

**Plano, cuando el proyecto lo pide.** Botones (un solo color, sin degradé), íconos, gráficos y datos, y marcas cuya identidad es el color plano.

**Por qué funciona.** Una superficie real nunca tiene un solo valor de color: la luz la recorre y el material tiene poro. Además, el grano evita el escalonado de los degradés en pantallas comunes.

**De dónde viene.** Gusto propio declarado en octubre de 2026. El grano SVG del sitio de Autoemoción es el antecedente: `feTurbulence` en `body::before` a .055 en oscuro y .22 en multiply en claro.
