# VidrioPolarizado

Cristal satinado de alta calidad con polarizado: oscurece y tiñe lo que pasa por detrás, deja ver solo color y luz, y lleva texto claro encima. El tinte puede ser neutro (humo) o del color del proyecto.

```html
<div class="r-polarizado">…</div>                                         <!-- humo -->
<div class="r-polarizado r-polarizado--color" style="--tinte:92 68 22">…</div> <!-- oro -->
```

**Cómo está hecho.**
- **Polarizado.** `backdrop-filter: blur(var(--desenfoque-satinado)) saturate(1.35) brightness(.72)`. Baja la luz de la foto pero conserva su color, como un vidrio de auto.
- **Tinte.** `rgb(var(--tinte) / var(--densidad))`. `--tinte` es una terna RGB y `--densidad` va de .45 a .6. Cada proyecto pone su color: un verde profundo, el oro de Autoemoción oscurecido o el petróleo de PC Soluciones.
- **Satinado.** Grano fino de ruido SVG en modo overlay al 22% y un brillo diagonal blanco al 10% que se apaga antes de la mitad. Es la diferencia entre un vidrio de plástico y uno trabajado.
- **Espesor.** `sombra-polarizado`: canto de luz arriba, canto oscuro abajo y sombra corta definida.

**Cuándo usarlo.**
- Navegación y paneles sobre fotos muy luminosas, donde el vidrio luminoso no alcanza para que se lea el texto.
- Piezas premium: Autoemoción, Crowd FC, ofertas destacadas.
- Fichas sobre video o sobre una foto de ambiente.
- Modo oscuro de un proyecto que en claro usa el vidrio luminoso.

**Cuándo no.**
- Sobre fondo liso.
- En bloques largos de lectura.
- Varios tintes distintos en la misma pantalla. El tinte es un solo color por proyecto; la vista previa muestra tres solo para compararlos.

**Legibilidad.** Texto en `#F4F3EF`; el secundario al 74% de opacidad (`.r-suave`). Hay que verificarlo sobre la zona más brillante de la foto real. Si no pasa 4,5:1, subir `--densidad` antes que bajar el brillo de la foto.

**Relación con el vidrio luminoso.** Son el mismo cristal con dos tratamientos:

| | Luminoso | Polarizado |
| --- | --- | --- |
| Efecto sobre lo de atrás | Lo aclara | Lo oscurece y lo tiñe |
| Texto | Oscuro | Claro |
| Tema | Claro | Oscuro, o fotos de mucha luz |
