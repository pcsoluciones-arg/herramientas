# HojaComoFormulario

En una app, cargar o corregir un dato se hace en una hoja que sube desde abajo, no en una ventana centrada: deja ver de qué registro se trata, se cierra arrastrando y el botón de guardar queda fijo al pie de la hoja.

```html
<div class="r-hoja r-hoja--form">
  <div class="r-hoja__asa"></div>
  <h3 class="r-hoja__tit">Reprogramar la llamada</h3>
  <label>Día <input class="r-control r-control--campo" type="date"></label>
  <label>Hora <input class="r-control r-control--campo" type="time"></label>
  <div class="r-hoja__pie"><button class="r-control r-control--secundario">Cancelar</button><button class="r-control r-control--principal">Guardar</button></div>
</div>
```

**Reglas.**
- Hasta cinco campos. Con más, es un flujo de pasos (UnaTareaPorPantalla), no una hoja.
- Campos de 44px y 16px de texto. El primer campo recibe el foco al abrir; el teclado no tapa el botón porque el pie es `sticky`.
- El botón principal dice qué hace (Guardar, Reprogramar, Mandar), nunca "Aceptar".
- Se cierra con el asa, con Cancelar o tocando fuera. Nunca con el botón del navegador, que en una app instalada no está.
- Una sola hoja abierta a la vez.

**De dónde viene.** La hoja inferior de CRW Base y las ventanas con botones fijos del panel de PC Soluciones (1.23.2), que en el celular ya se comportan casi como hoja.
