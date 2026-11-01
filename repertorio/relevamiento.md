# Relevamiento de proyectos

Estado de cada proyecto al 27 de octubre de 2026, leído del código de los repositorios y de los sitios publicados. Sirve para saber qué capa de proyecto tiene cada uno y qué técnicas ya existen y se pueden llevar a otro.

## PC Soluciones · pcsoluciones.com.ar

- **Paleta.** Petróleo `#013E4D` / `#014E5F` / `#006C82`, teal `#0EA5A4`, naranja `#E4570F` con `#FF9A5C`, ámbar `#EDC02E`; neutros slate de Tailwind. Un color por página (Inicio turquesa, Cómo trabajamos azul, Casos dorado, GEO violeta, Precios verde, Técnica naranja).
- **Tipografía.** Space Grotesk 700 en títulos (48px, -1.2px), Manrope en texto.
- **Forma.** Radios 14 y 22px; sombra `0 8px 24px -8px rgba(15,23,42,.18), 0 2px 6px rgba(15,23,42,.06)`; botones teal con sombra teñida `0 6px 18px -6px rgba(14,165,164,.6)`; nav de vidrio blanco al 92% con blur 14px.
- **Para llevarse.** La sombra teñida del botón y la barra de progreso con degradé por página.

## Prospector · panel de prospección

- **Paleta.** Misma familia que el sitio: fondo `#F4F8F9`, tinta `#013E4D`, acento `#0EA5A4`; semánticos con trío suave/tinta/borde (ámbar, coral, verde, violeta). Oscuro propio: `#0B191E`, papel `#11252C`, acento `#1FBAB6`.
- **Tipografía.** Space Grotesk (títulos, botones, cifras con tabular-nums) y Manrope, servidas desde el dominio.
- **Forma.** Radios 10 (controles), 14 (tarjetas), 18 (modal), 30 (barra inferior). Una sola sombra suave.
- **Para llevarse.** Barra inferior flotante de vidrio con `color-mix` al 82% y `blur(22px) saturate(1.6)`; tabla que en el celular se vuelve tarjeta con `td::before{content:attr(data-col)}`; buscador como paleta de comandos; velo de modal que desenfoca y desatura; filtros que se despliegan; pull-to-refresh propio.

## CRW Base · panel interno de CRW

- **Paleta.** Oscura por defecto en tonos cuero: shell `#2B2823`, superficie `#1A1814`, oro `#C8A96E`, texto `#F4F2EA`. Claro en crema `#FAF9F5` con texto azul marino `#1B2A4A` y oro oscurecido `#8A7242`.
- **Tipografía.** Bebas Neue, Manrope y JetBrains Mono (heredadas del Brand System v1.2).
- **Forma.** Radios de 6 a 30px sin escala cerrada; sombra casi plana (`0 1px 0`).
- **Para llevarse.** Barra superior satinada `blur(18px) saturate(1.5)`; barra de pestañas flotante; barra lateral que se pliega de 232 a 76px con tooltips; hoja inferior que se arrastra para cerrar; interruptores y grupos de ajustes tipo iOS; Gantt hecho a mano.

## Autoemoción · sitio público

- **Paleta.** Negro cálido `#0A0A0A`, superficie `#141210`, marfil `#F4EADE`, oro `#C69B3C` y champán `#CBB073`. Modo claro marfil completo; el pie queda oscuro en los dos.
- **Tipografía.** Sora (títulos y precios), Inter (texto), Space Grotesk (datos y rótulos).
- **Forma.** Radios 14, 20 y pill; ancho 1180px; secciones de 96px.
- **Para llevarse.** Sombra de cada botón en su propio color vía `--btn-shadow`; header que pasa a vidrio al bajar; héroe con foto de día y de noche; grano SVG sutil; mapa de Google oscurecido con filtros CSS; tarjeta de vehículo con encuadre por orientación de foto; botón compartir de vidrio; WhatsApp con `data-lead` medido en GA4 y botón flotante que se oculta cuando el CTA está a la vista; pie en columnas con la firma de PC Soluciones.

## Autoemoción · panel (Filament)

- **Paleta.** Zinc de Filament con el oro `#A37E2C` / `#D4B06A` puesto a mano en los tableros propios.
- **Para llevarse.** Franjas de estado fijas bajo la barra superior ("modo eliminar", "ver como"); control segmentado; mini gráfico de barras en CSS; tiles de conteo con filas y chevron.
- **Pendiente.** Fuera de los tableros propios se ve como Filament de fábrica: es el lugar donde la capa de autor más rinde.

## Marta Pérez Temperley · sitio de artista

- **Paleta.** Solo oscura: tinta `#14110F`, hueso `#F2EDE6`, un único acento bermellón `#D8341C`.
- **Tipografía.** Cormorant Garamond e Inter.
- **Forma.** Radio cero en todo; sombra de obra colgada `0 34px 70px rgba(0,0,0,.6), 0 6px 16px rgba(0,0,0,.4)`.
- **Para llevarse.** Visor que desenfoca la página (main, cabecera y pie) en lugar de tapar con negro, con swipe y foco devuelto; libros que se hojean con respaldo 3D propio; pasepartout para recortes; carrusel con la tarjeta siguiente asomando y flechas centradas sobre la imagen; compartir nativo o copiar al portapapeles; retrato tipo polaroid inclinado.

## APK · Bolsas Inflables y Slip Sheets

- **Paleta.** Naranja `#EB5F33`, verde oliva `#5C623D`, negro `#030F08`, blanco `#F4F8F1`, WhatsApp `#188741`.
- **Tipografía.** Barlow (H1 52px/600, H2 32px/600).
- **Forma.** Radios de 4 a 7px; sombras profundas `0 18px 50px rgba(0,0,0,.3)`; navbar de 80px en un renglón con vidrio.
- **Para llevarse.** El sistema de familia: invariantes y variables por landing, y la regla para divergir.

## Impianti · impiantiarg.com.ar

- **Paleta.** Verdes `#164827` / `#093B1A`, oliva claro `#BDC779`, cremas `#F2EEEB` / `#F6F7F2`.
- **Tipografía.** Young Serif en títulos (56px/400), Archivo y Lato.
- **Forma.** Radios 12, 14 y pill; sombra teñida de verde `0 1px 2px rgba(12,66,32,.07), 0 10px 20px -8px rgba(12,66,32,.2)`.
- **Para llevarse.** La sombra teñida y la serif cálida como alternativa a la grotesca.

## Crowd FC · crowdfc.pages.dev

- **Paleta.** Casi negro `#0D0B09`, oro `#C8A96E`, paneles translúcidos muy tenues (`rgba(250,249,245,.02)` a `.04`), velo `rgba(0,0,0,.45)`. Es el Brand System v1.2.
- **Tipografía.** Bebas Neue en mayúscula para todos los titulares (88px en el héroe), Manrope en texto, JetBrains Mono en rótulos, botones e idioma, DM Serif Display en frases.
- **Forma.** Radios pill, 14 y 10px; sombra `0 10px 40px rgba(0,0,0,.35)` y un brillo dorado `0 0 12px #C8A96E`; seis desenfoques distintos (de 2 a 12px).
- **Para llevarse.** La foto aérea del estadio y la de la tribuna llena, que cuentan el producto sin explicarlo; el video con subtítulos y pantalla completa.
- **Oportunidad.** Es el proyecto donde el sujeto fuera del marco tiene más sentido: hinchas y jugadores saliendo del marco de la foto. Cuando llegue la identidad nueva, la capa de autor ya queda lista para aplicarla.

## Sin relevar todavía

- Panel de gestión de PC Soluciones: no existe aún (se arma sobre Prospector).
