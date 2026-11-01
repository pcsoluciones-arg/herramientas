# VidrioLuminoso

Panel translúcido con desenfoque detrás, filo de luz arriba y sombra corta abajo, para poner texto o navegación encima de una imagen sin taparla.

```html
<div class="r-vidrio">…</div>
```

Toma `vidrio`, `vidrio-borde`, `sombra-vidrio`, `radio-l` y `desenfoque-vidrio` (con `saturate(1.6)`, que devuelve el color que el desenfoque apaga).

**Cuándo usarlo.** Barras de navegación fijas que dejan ver el contenido que pasa por detrás, paneles de texto sobre foto, la barra de pestañas flotante, botones sobre una foto (compartir, galería).

**Cuándo no.** Sobre `papel` liso o sobre `superficie`: ahí no hay nada que dejar ver y se lee como un gris apagado. Tampoco apilado (vidrio sobre vidrio).

**Legibilidad.** El texto sobre vidrio se verifica sobre la zona más clara y la más oscura de la imagen. Si no pasa 4,5:1 en las dos, subir la opacidad de `vidrio` en ese proyecto (Prospector usa 0,94 en su barra superior) antes que agregar sombras al texto.

**De dónde viene.** Barra superior de CRW Base (`blur(18px) saturate(1.5)`), barra inferior de Prospector (`blur(22px) saturate(1.6)`), header de Autoemoción que pasa a vidrio al bajar.
