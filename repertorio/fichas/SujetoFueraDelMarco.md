# SujetoFueraDelMarco

El sujeto de una foto (persona, auto, planta, producto) sobresale por arriba del marco redondeado que lo contiene y gana profundidad sin agregar elementos.

**Referencia.** Mail de bienvenida de Zoom (oct 2026): la mujer frente a la notebook pasa con la cabeza por encima del borde superior de la foto.

**Cómo funciona.** La misma imagen en dos capas, en la misma posición exacta. Abajo, la foto completa recortada por el marco (`clip-path: inset(var(--asomo) 0 0 0 round var(--radio-l))`). Arriba, el sujeto recortado en PNG sin fondo. Dentro del marco las dos capas coinciden pixel a pixel; lo que el sujeto tiene por encima del borde queda a la vista sobre el papel.

```html
<div class="r-fuera" style="aspect-ratio:4/3;--asomo:20%">
  <span class="r-fuera__marco"></span>   <!-- lleva la sombra, que el clip-path cortaría -->
  <img class="r-fuera__fondo"  src="foto.webp"         alt="">
  <img class="r-fuera__sujeto" src="foto-sujeto.webp"  alt="Descripción de la foto">
</div>
```

**Qué aporta el proyecto.** Una foto con aire arriba del sujeto (que se pueda encuadrar con el marco más abajo) y el mismo archivo con el fondo quitado, exportado al mismo tamaño. El recorte se hace con la herramienta de quitar fondo de Adobe o de Photoshop; los bordes de pelo y hojas son lo que más se nota, revisarlos.

**Cuándo usarla.**
- Cabecera o bloque protagonista de una página: una por página.
- Equipo en "Quiénes somos" (cada retrato sale de su tarjeta).
- Autoemoción: el auto con la trompa o el techo pasando el borde.
- PC Soluciones y CRW: el celular con el sistema en uso saliendo de la tarjeta.
- Impianti: una planta sobre el corte entre secciones.

**Cuándo no.** Obras de arte y documentos (se respetan sus márgenes), grillas de muchas tarjetas (el efecto se vuelve ruido), fotos donde el recorte del sujeto queda desprolijo.

**Detalles.** El marco usa `sombra-2` y el sujeto un `drop-shadow` corto para anclarse. `--asomo` entre 12% y 25% de la altura: más que eso y el marco parece un zócalo. En celular, reducir `--asomo` para que la cabeza no choque con la barra superior.
