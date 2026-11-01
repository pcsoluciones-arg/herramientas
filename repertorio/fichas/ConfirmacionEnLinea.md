# ConfirmacionEnLinea

Las acciones que se pueden deshacer se hacen de una y muestran "Deshacer" por unos segundos; las que no (borrar, cerrar un prospecto) piden confirmación en el lugar, con el verbo de la acción, nunca con el cartel del navegador.

```html
<!-- se puede deshacer -->
<div class="r-deshacer">Marcado como contestó<button>Deshacer</button></div>
<!-- no se puede deshacer: en el lugar, no en una ventana -->
<div class="r-confirma"><span>¿Descartar Dental Núñez? No vuelve a entrar en otra tanda.</span><button class="r-control r-control--secundario">No</button><button class="r-control r-control--principal">Descartar</button></div>
```

**Reglas.**
- Marcar, mover, reordenar, archivar: sin pregunta y con Deshacer durante 6 segundos.
- Borrar, descartar, cerrar, publicar a un sitio: una confirmación en el lugar del botón, con el nombre de la cosa y la consecuencia en una frase.
- El botón de confirmar dice el verbo (Descartar, Publicar), el otro dice No o Cancelar. Nunca "Aceptar / Cancelar".
- `window.confirm` y `alert` no se usan: en una app instalada rompen la sensación de app y bloquean la pantalla.
- Una sola confirmación abierta a la vez; Escape o tocar fuera la cancela.

**De dónde viene.** `preguntar()` del panel de PC Soluciones (1.20.2), que ya reemplazó los carteles del navegador.
