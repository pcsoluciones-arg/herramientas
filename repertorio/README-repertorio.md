Repertorio personal de técnicas, criterios y formas que se aplican a cualquier proyecto (PC Soluciones, Autoemoción, CRW, sitios de clientes) sin borrar la identidad de cada uno. Se enriquece con cada referencia nueva: cada técnica tiene su ficha con vista previa en la pestaña de componentes.

## Cómo se usa: dos capas

Cada pieza que se diseña tiene dos capas, y este repertorio solo define la primera.

- **Capa de autor (constante).** Cómo se construye: luz, transparencia, sombra, proporción, ritmo, movimiento, el catálogo de técnicas y los controles de calidad. Es lo que hace que un trabajo se reconozca como propio aunque cambie la marca.
- **Capa del proyecto (variable).** Paleta, tipografías, fotografía, voz y logo. Los pone cada marca. Los colores de este repertorio son lugares reservados: `acento` se reemplaza por el color de acción del proyecto, `papel`, `superficie` y `tinta` por sus neutros.

Para aplicarlo a un proyecto: mapear sus colores a los roles (`papel`, `superficie`, `superficie-2`, `tinta`, `tinta-suave`, `tinta-tenue`, `acento`, `on-acento`), mapear su familia tipográfica a `texto`, y recién después elegir técnicas del catálogo. La regla que ya funcionó en la familia APK vale acá: se repite la regla, no el resultado. Una técnica se adopta cuando la razón viene del producto (la bolsa está en el centro de la foto, el auto necesita ver la trompa), nunca "para que no sea igual".

## Las seis capas por medio

La capa de autor es una sola; lo que cambia es el medio donde se aplica. Cada medio tiene sus reglas, sus fichas y su escala, y una pieza pertenece a una sola capa. El detalle de cada una está en la sección **Capas**.

| Capa | Medio | Para quién |
| --- | --- | --- |
| Sitios | Pantalla con scroll que se lee una vez | El visitante |
| Paneles | Pantalla de trabajo, densa, computadora primero | Quien administra |
| Apps | Celular primero, una tarea por pantalla, instalable | Quien ejecuta (prospector, cliente) |
| Piezas | Lienzo fijo para redes | Quien mira el feed |
| Documentos | Hoja A4 y correo: presupuestos, informes, membrete | El cliente que decide |
| Impresos | Papel con tinta: QR, cartel, folleto | Quien lo tiene en la mano |

Al 29/10/2026 están escritas Sitios (desde la 0.1), Paneles y Apps (1.1). Piezas, Documentos e Impresos tienen sus reglas repartidas en los proyectos y entran como capas en las próximas versiones.

## Principios

- **Simple.** Una idea por bloque y un solo gesto protagonista por pantalla. Si una pantalla tiene vidrio, sujeto fuera del marco y carrusel a la vez, sobran dos.
- **Elegante.** Pocas decisiones, bien medidas: tres tamaños de sombra, cinco radios, una familia tipográfica. Las proporciones se miden; no se empujan bloques a ojo (ver `aire-seccion`).
- **Claro.** Los títulos dicen de qué trata lo que sigue. Los botones dicen qué pasa al tocarlos. El contraste mínimo es 4,5:1 para texto y 3:1 para íconos, bordes de controles y foco, en los dos temas.
- **Eficiente.** Sin scroll lateral, sin pasos que nadie usa, carruseles en lugar de scroll interminable, controles visibles sin buscarlos.
- **Práctico.** Funciona en el celular primero: áreas táctiles de 44px, campos de 16px, safe areas, modo oscuro pensado a mano y no invertido. Dos cortes de ancho en todo el repertorio: `corte-telefono` (640) y `corte-tablet` (1024).
- **Útil.** Todo elemento cumple una función que se puede nombrar. Lo decorativo se gana el lugar mostrando el producto, nunca rellenando.

## Luz, transparencia y sombra

El estilo es luminoso: fondos claros cálidos (`papel`), superficies blancas que flotan encima (`superficie`) y una sola fuente de luz cenital.

- **Sombra definida.** Usar `sombra-contacto`, `sombra-1`, `sombra-2` y `sombra-3`: desenfoque corto, desplazamiento hacia abajo y spread negativo, más una línea de contacto de 1px. Dan un borde de sombra nítido que se lee como objeto apoyado. Evitar las sombras de 24px o más de desenfoque sin spread negativo (el halo difuso de plantilla).
- **Sombra teñida.** Es regla, no excepción: una sombra toma el color de lo que la proyecta o del fondo donde cae, nunca negro sobre color. El botón principal lleva `sombra-acento`. Sobre un fondo de color, la sombra toma el tono de ese fondo: en Impianti `rgba(12,66,32,…)` sobre verde, en Autoemoción cada botón proyecta su propio color (`--btn-shadow`). Es la diferencia más barata entre una sombra pegada y una sombra con luz.
- **Vidrio con motivo.** `vidrio` + `vidrio-borde` + `sombra-vidrio` con `desenfoque-vidrio` y saturate(1.6). Solo encima de algo que valga la pena dejar ver (foto, mapa, contenido que pasa por detrás al hacer scroll). Sobre papel liso es un gris con pretensiones. El filo de luz de arriba (`inset 0 1px 0`) es lo que lo hace leer como cristal.
- **Vidrio polarizado.** El mismo cristal con el tratamiento opuesto: satinado, oscurece y tiñe lo que pasa por detrás (`brightness(.72)` con la saturación conservada), con texto claro encima. El tinte es una terna RGB en `--tinte`: humo por defecto o el color del proyecto. Para fotos muy luminosas, piezas premium y el tema oscuro. Un solo tinte por proyecto.
- **Color con tacto.** Los bloques de color y los fondos llevan grano, tono (luz sobre el mismo color) o fibra de papel, para dar calidez y sensación de material (`.r-grano`, `.r-tono`, `.r-fibra`). El color plano queda para botones, íconos, datos y para los proyectos cuya identidad lo pide.
- **Negro con profundidad.** En los modos oscuros, el fondo tiene espacios luminosos: una luz motivada que cae desde arriba, un halo detrás del protagonista y viñeta en los bordes, sobre `negro-profundo` y con grano (`.r-profundo`). Una sola fuente de luz y de un solo tono, siempre cayendo sobre algo. En pantallas de trabajo va a intensidad `profundidad-app` (.06) con `.r-profundo--app`: el fondo respira sin competir con los datos.
- **Profundidad por capas, no por cantidad.** Tres planos alcanzan: papel, superficie, flotante (vidrio, hoja, visor). Un cuarto plano solo para el sujeto fuera del marco.

## Tipografía

`texto` (Schibsted Grotesk) es la familia de las vistas previas del repertorio; en un proyecto se reemplaza por la suya. Lo que se mantiene es la escala y el criterio:

- Titulares con tracking negativo (`display` -0,025em, `titulo-1` -0,02em) y peso 650 a 700. Texto corrido a 16px con 25px de interlineado.
- Una familia por proyecto, dos como máximo (títulos y texto). Tres familias con roles separados (títulos, texto y una monoespaciada para datos) es la combinación que más se repite en dashboards generados.
- Cifras en `cifra` con `tabular-nums`, para que los precios y conteos no bailen.
- En Paneles y Apps rige la escala `app-*` (20, 16, 15, 14, 13, 12 y la cifra de 26): cerrada, sin tamaños intermedios. Ver EscalaDeAplicacion.
- Evitar Inter y Roboto como familia principal: son el valor por defecto de todo lo generado.

## Imagen

- Cada recorte destaca al sujeto con aire arriba; caras y trompas nunca cortadas ni pegadas al borde.
- Las obras y documentos conservan sus márgenes reales (pasepartout, como los recortes de prensa en el sitio de Marta).
- Las capturas de un sistema se muestran en la pantalla real del producto cuando es el resultado final; el "antes" va en una ventana simple.
- El sujeto fuera del marco necesita una foto con el sujeto recortado (PNG sin fondo). Ver su ficha.

## Movimiento

Corto y con sentido: 150 a 250ms para estados, 300ms con `cubic-bezier(.2,.8,.2,1)` para hojas y visores (entra rápido, frena suave). Hover de tarjeta: subir 1 a 2px y pasar de `sombra-1` a `sombra-2`. Respetar siempre `prefers-reduced-motion`. Nada se mueve solo en loop salvo una cinta de logos con máscara en los bordes.

## Iconografía

Íconos de línea propios en viewBox 24, trazo 1,8 a 2, puntas redondeadas y color por `currentColor` (como el diccionario de Prospector y el sprite de CRW Base). Un solo set por proyecto. Sin emojis en la interfaz: quedan para los mensajes de WhatsApp, donde ayudan a leer.

## Escritura

- Español neutro, sin voseo salvo que el proyecto lo pida.
- Sin guiones largos y sin títulos con la forma "no es X: es Y".
- Los títulos y las bajadas dicen directamente de qué trata lo que viene; nada de acertijos.
- Explicar la función de algo antes que la consecuencia de su ausencia.
- Evitar frases de fórmula (las de confianza genérica, las de "todo lo esencial, nada más"): decir algo que solo ese negocio puede decir.

## Foco y accesibilidad

Foco de teclado con `foco`: 2px sólido y 2px de separación. Estados de aviso y error siempre con palabra o ícono, nunca solo con color. Contraste verificado en los dos temas.
