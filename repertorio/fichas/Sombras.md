# Sombras

Escala de cuatro sombras definidas (poco desenfoque, desplazamiento visible, spread negativo y línea de contacto) más la regla de teñirlas con el color del fondo.

| Token | Clase | Para |
| --- | --- | --- |
| `sombra-contacto` | `.r-elev-0` | Filas, chips, campos: apoyados en la superficie. |
| `sombra-1` | `.r-elev-1` | Tarjetas y botones en reposo. |
| `sombra-2` | `.r-elev-2` | Hover de tarjeta, menús, marcos de imagen. |
| `sombra-3` | `.r-elev-3` | Modales y piezas abiertas en el visor. |

**Sombra teñida (regla, desde la 1.1).** Una sombra toma el color de lo que la proyecta o del fondo donde cae; el negro queda solo para superficies neutras sobre papel. El botón principal lleva `sombra-acento`, que cada proyecto rehace con su color de acción. Sobre un fondo de color, reemplazar el negro por el tono más oscuro de ese fondo con más opacidad. Ejemplo sobre el verde de Impianti: `0 1px 1px rgba(5,30,14,.25), 0 10px 16px -8px rgba(5,30,14,.65)`. En un botón de color, la sombra puede tomar el color del propio botón, como en Autoemoción:

```css
.boton{box-shadow:var(--sombra-boton, var(--sombra-1))}
.boton--oro{--sombra-boton:0 8px 16px -8px rgba(198,155,60,.6), 0 2px 4px -2px rgba(0,0,0,.35)}
```

**Evitar.** Sombras de 24px o más de desenfoque sin spread negativo, sombras en todos los elementos a la vez (si todo flota, nada flota) y sombras de color sobre fondo blanco que parecen brillo.

**En el tema oscuro.** La sombra casi no se ve sobre negro: la elevación se marca además con una superficie un punto más clara (`superficie` sobre `papel`) y el filo de luz del vidrio.
