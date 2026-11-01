# AppInstalada

Una app web que se instala en el celular desde el navegador y se comporta como app: ícono propio, pantalla completa sin barra de direcciones, arranca en la última pantalla, respeta las zonas seguras y avisa con notificaciones.

**Qué hace falta.**
- `manifest.webmanifest` con nombre, nombre corto, ícono de 192 y 512 px (con fondo, sin transparencia), `display: standalone`, color del tema y `start_url` con `?instalada=1` para medir cuántos entran por el ícono.
- `<meta name="theme-color">` por tema y `viewport-fit=cover`, con `env(safe-area-inset-*)` en la cabecera y en la barra flotante.
- Un service worker mínimo: cachea la pantalla y los íconos para que abra al instante, y deja pasar la API en vivo. Si no hay señal, la pantalla lo dice (EstadosVaciosYDeEspera) y no se queda en blanco.
- Instrucción de instalación dentro de la app la primera vez ("Agregá Prospéctor a tu pantalla de inicio"), con los pasos de iPhone (Compartir, Agregar a inicio) y Android (Instalar), porque el aviso del navegador no siempre aparece.
- La barra flotante lleva hasta cinco ítems; el del medio es la acción principal (redondo, solo ícono, con `aria-label`), como ¿Te contestó? en Prospéctor.
- Notificaciones solo para lo que pide acción (contestó, llamada confirmada), con permiso pedido después de la primera tarea hecha, nunca al abrir.
- Al abrir después de una versión nueva, una pantalla de bienvenida de una sola vez que muestra qué cambió, con un botón "Entendido". Se guarda por persona en el servidor, no en el navegador.

**Reglas.**
- Sin `alert`, `confirm` ni enlaces que abran el navegador fuera de la app, salvo WhatsApp e Instagram, que son el trabajo.
- El botón "atrás" del sistema vuelve a la pantalla anterior de la app (historial propio), nunca la cierra.
- Lo que se escribe se guarda a medida que se escribe: en una app no hay "perdí lo que tenía".

**De dónde viene.** Decisión del 29/10/2026 para Prospéctor: que los prospectores lo vivan como una app, no como un sitio.
