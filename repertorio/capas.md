# Capas

Qué define cada capa, qué fichas la componen y cómo se aplica a un proyecto. Las seis comparten tokens, luz, sombra, tacto y escritura; cada una tiene su escala y sus formas.

## Sitios

Pantalla con scroll que el visitante lee una vez. Escala `display` a `detalle`, `aire-seccion` entre bloques, héroe con el producto como protagonista.
Fichas: SujetoFueraDelMarco, VidrioLuminoso, VidrioPolarizado, SuperficieConTacto, NegroConProfundidad, Sombras, ProgresoDeLectura, CarruselConAsomo, VisorConFondoDesenfocado, BotonDeCanal.
Proyectos: pcsoluciones.com.ar, Autoemoción, Impianti, Plomero de Barrio, APK, Marta, Crowd FC.

## Paneles

Pantalla de trabajo para quien administra: densa, con listas, tablas, filtros, fichas y formularios. Computadora primero; en la tablet la barra lateral arranca plegada; en el teléfono la reemplaza la barra flotante y las tablas se vuelven tarjetas.
- Escala `app-*` y controles de `alto-control` (44 en táctil). Nada por debajo de 12px.
- Cuatro estados semánticos con su palabra. El acento queda para la acción y lo activo.
- Cada nivel es una sola cosa: barra lateral = áreas; pestañas = vistas de un área; ficha = todo lo de un registro. Un nombre por pantalla, igual arriba y abajo.
- Lo urgente a mano; lo que se configura una vez, al pie.
- Modo oscuro con `r-profundo--app`.
Fichas: EscalaDeAplicacion, EstadosSemanticos, PestanasYFiltros, BarraLateral, TablaATarjeta, FichaConPestanas, más BarraFlotante y VidrioLuminoso para el celular.
Proyectos: panel de PC Soluciones (administración), CRW Base, panel de Autoemoción.

## Apps

Celular primero, para quien ejecuta una tarea: el prospector, el cliente que aprueba una pieza. Comparte controles y estados con Paneles.
- Una tarea por pantalla, con su paso y un botón principal fijo abajo.
- Cargar y corregir se hace en hojas que suben; lo reversible se deshace, lo irreversible se confirma en el lugar.
- Estados vacíos que dicen qué pasa y qué sigue; esqueleto mientras carga.
- Instalable: manifest, ícono, pantalla completa, zonas seguras, historial propio, bienvenida de una vez cuando cambia la versión.
- Texto en el registro del proyecto (en Prospéctor, voseo).
Fichas: UnaTareaPorPantalla, HojaComoFormulario, EstadosVaciosYDeEspera, ConfirmacionEnLinea, AppInstalada, más BarraFlotante, HojaInferior y EstadosSemanticos.
Proyectos: Prospéctor (modo prospector), la app de CRW cuando llegue.

## Piezas

Lienzo fijo para redes (4:5, cuadrado, historia, reel). Molde de marca por cliente, texto con acento, placa final de contacto, formato por red. Reglas hoy en el generador de piezas del panel de PC Soluciones; entran como fichas en la próxima versión.

## Documentos

Hoja A4 y correo: presupuestos, informes, diagnósticos y el membrete institucional de todos los correos. Portada, tabla de precios, antes y después, firma, PDF sin sombras negras (ver pdf-portadas en PC Soluciones). Reglas hoy en los generadores de presupuesto e informe de PC Soluciones; entran como fichas en la próxima versión.

## Impresos

Papel con tinta: QR, cartel, folleto, tarjeta. QR con emblema al centro y corrección alta, versión vectorial a un color para imprenta, sangrado, tamaño mínimo del QR. Reglas hoy en los generadores de QR de Plomero de Barrio e Impianti; entran como fichas en la próxima versión.

## Cómo se aplica una capa a un proyecto

1. Mapear la paleta del proyecto a los roles (`papel`, `superficie`, `tinta`, `acento`…) y su familia a `texto`. En PC Soluciones: papel y superficie del blanco cálido con un punto de petróleo, tinta `#013E4D`, acento teal `#0EA5A4`, Space Grotesk en títulos y controles, Manrope en el cuerpo.
2. Rehacer `sombra-acento` con el color de acción del proyecto.
3. Elegir la capa por el medio y tomar sus fichas. No mezclar escalas: una pantalla de panel no usa `display`.
4. Pasar la lista de Señales de plantilla antes de mostrar.
