# Orquestador de la Fábrica de sitios

Instrucciones de cada corrida de la tarea programada "Fábrica de sitios". Corres sin nadie mirando: no preguntes, decide según esto y deja todo escrito en GitHub. Antes, lee `sitios/LEEME.md` y `skills/LEEME.md` de este repositorio.

La Fábrica de sitios toma los pedidos de cambio de los sitios de clientes (`pcsoluciones-arg/sitio-*`), los especifica, los construye, los hace revisar por los cuatro revisores de presencia, los aprueba y se los pasa a `publicar.yml` del sitio, que publica lo de riesgo bajo y deja lo de riesgo alto esperando a Manu. Es la misma forma que la Fábrica de software del panel (`panel-prospector/fabrica/orquestador.md`), con los revisores de presencia en lugar de los del panel.

## 0. Preparar

1. Agrega a la sesión `pcsoluciones-arg/herramientas` (lectura) y clónalo en `/home/claude/herramientas`.
2. Lee `sitios/sitios.json`: es la lista de sitios con la fábrica instalada. Para cada uno, agrégalo a la sesión con acceso push (`add_repo`) y clónalo al lado de `herramientas` (`/home/claude/<nombre>`). Si uno no se puede agregar, sigue con los demás y anótalo para el aviso final.
3. Configura git en cada clon: `user.name "Manuel Tonnelier"`, `user.email "pcsolucionesbelgrano@gmail.com"`.
4. Para GitHub usa `gh api repos/pcsoluciones-arg/<sitio>/...` (REST; GraphQL no está disponible). El estado de la revisión de un PR se lee en `commits/<sha>/check-runs` (check `controles`).
5. En cada sitio, crea las etiquetas que falten: `fabrica`, `en-curso`, `listo`, `espera-manu`, `necesita-manu`, `publicado`, `desactualizado` (`gh api repos/pcsoluciones-arg/<sitio>/labels -f name=<etiqueta>`; si ya existe, sigue).

## 1. Elegir qué hacer (una sola cosa por corrida, entre todos los sitios)

Antes de elegir, **pon al día los PR que esperan a Manu** (no cuenta como "la cosa" de la corrida). Para cada PR abierto de la fábrica (rama `fabrica/`) con `espera-manu` o `desactualizado` que esté atrás de `main` con conflictos (`mergeable_state` igual a `dirty`, o la etiqueta `desactualizado`): en su rama, `git merge origin/main`. Si hay conflictos, lanza el constructor (`model: "opus"`) con la lista para que los resuelva sin cambiar lo aprobado; si no puede, pon `necesita-manu` y notifica. Después `bash fabrica/controles.sh ../herramientas`, commit y push a la misma rama, quita `desactualizado` y comenta "Puesto al día con main. Espera la aprobación de Manu."

Después, elige en este orden, mirando todos los sitios:

1. **Un PR de la fábrica con la revisión en rojo** (check `controles` en `failure`) y sin `necesita-manu`: vuelve al paso 4 con el registro del error como corrección.
2. **Un pedido abierto con `en-curso`**, sin PR y sin comentarios en las últimas 3 horas: una corrida anterior se cortó. Retómalo desde el último paso que dejó comentado.
3. **Fotos publicadas sin revisión visual:** un commit de `main` de los últimos 14 días que agrega o cambia archivos en `fotos/` y no tiene un comentario de commit que empiece con `**Revisión visual**` (`gh api repos/pcsoluciones-arg/<sitio>/commits/<sha>/comments`). Ve al paso 9.
4. **El pedido abierto más viejo con `fabrica`**, sin `en-curso`, `espera-manu` ni `necesita-manu`. Si hay en varios sitios, el más viejo de todos.
5. Si no hay nada: termina sin comentar nada, con la última línea "Sin novedades".

Nunca tomes el pedido "Cambios en main esperan tu aprobación" ni otro con `espera-manu`: esos los resuelve Manu.

Al tomar un pedido, ponle `en-curso` y comenta "Tomado por la fábrica de sitios" con la fecha.

## 2. Registro

Cada paso deja un comentario en el pedido (o en el PR, una vez abierto) que empieza con el nombre del paso y el modelo, por ejemplo `**Especificación** (Opus 5.5)`. Sin comentarios largos: lo esencial y, si hace falta, un bloque plegado (`<details>`).

## 3. Especificación

Lanza un agente con `model: "opus"` y estas instrucciones: `sitios/agentes/especificacion.md`, más el nombre del sitio, la ruta de su clon, el texto del pedido y sus comentarios. Publica su resultado como comentario. Si dice que el pedido ya está resuelto o que no se entiende, comenta, quita `en-curso`, pon `necesita-manu` y notifica.

## 4. Construcción

Lanza un agente con `model: "opus"`: `sitios/agentes/constructor.md`, la especificación, la ruta del clon y, si es una corrección, la lista de lo que hay que corregir. Trabaja en la rama `fabrica/<n>-<tema>`, deja en `/tmp/fabrica/<sitio>-<n>/` las capturas y el informe de los controles, y abre o actualiza el PR. Tú no escribes en el sitio.

## 5. Revisión de código

Espera hasta 20 minutos a que el check `controles` del último commit del PR termine (consulta cada minuto). En rojo: lee el error (el resumen del check o `/tmp/fabrica/<sitio>-<n>/controles.txt`), vuelve al paso 4 con eso (cuenta como una vuelta). En verde: sigue.

## 6. Cuatro revisores, en paralelo

En un solo mensaje, lanza cuatro agentes. A cada uno pásale solo la ruta de su skill (que la lea completa) y sus entradas, nada de lo que hablaste con los demás:

| Revisor | Skill | Modelo |
|---|---|---|
| Idioma y estilo | `skills/revisor-idioma/SKILL.md` | `sonnet` |
| Técnica | `skills/revisor-tecnica/SKILL.md` | `haiku` |
| SEO y GEO | `skills/revisor-seo-geo/SKILL.md` | `sonnet` |
| Visual | `skills/revisor-visual/SKILL.md` | `sonnet` |

Entradas de cada uno (las de la tabla de `skills/LEEME.md`): la ruta del clon del sitio en la rama del PR con `dist/` armado, `/tmp/fabrica/<sitio>-<n>/controles.txt`, la carpeta de capturas `/tmp/fabrica/<sitio>-<n>/capturas/`, el diff (`git diff origin/main...HEAD`), el texto del pedido y la ruta de `herramientas`. Diles que es un cambio: bloquean solo lo que el cambio trae o empeora.

Publica cada veredicto como comentario en el PR.

## 7. Aprobador

Lanza un agente con `model: "opus"`: `sitios/agentes/aprobador.md`, la especificación, el diff y los cuatro veredictos.

- **"corregir":** vuelve al paso 4 con su lista. Máximo 3 vueltas en total; en la cuarta, pon `necesita-manu`, notifica y termina.
- **"aprobar":** comenta su resumen en el PR y ponle la etiqueta `listo`. Desde ahí sigue `publicar.yml` del sitio.
- **"necesita-manu":** etiqueta, notifica y termina.

## 8. Después de `listo`

Espera hasta 20 minutos mirando el PR (la publicación espera el build de Cloudflare y los controles en vivo):

- **Etiqueta `publicado`:** quita `en-curso` del pedido, comenta "Publicado" con el commit y termina. Sin notificación: lo de riesgo bajo no molesta a Manu. Si el cambio tocó `trabajos` de `contenido.json`, sí notifica: Manu tiene que tocar **Leer del sitio** en el panel.
- **Etiqueta `espera-manu`:** notifica a Manu y termina. La próxima corrida no lo vuelve a tomar.
- **`necesita-manu` o nada en 20 minutos:** notifica con lo que se sabe y termina.

## 9. Revisión visual de fotos publicadas

Las fotos que carga el panel se publican después de los controles de código, sin esperar a los agentes (decisión 3 del plan). Acá las mira el revisor visual:

1. En el clon del sitio, `git checkout <sha>` del commit elegido, `python3 build.py` y `python3 ../herramientas/sitios/navegador.py dist/ --capturas /tmp/fabrica/<sitio>-fotos/capturas > /tmp/fabrica/<sitio>-fotos/controles.txt`.
2. Lanza el revisor visual (`model: "sonnet"`, `skills/revisor-visual/SKILL.md`) con las capturas, el informe, la lista de fotos del commit (`git show --name-only <sha> -- fotos/`) y la ruta de cada foto para que la mire.
3. Comenta en el commit (`gh api repos/pcsoluciones-arg/<sitio>/commits/<sha>/comments -f body=...`) empezando con `**Revisión visual** (Sonnet 5.5)` y el veredicto.
4. Si hay algo que bloquea (por ejemplo, una cara de un tercero o una patente legible), abre un pedido con `fabrica` y `necesita-manu` titulado "Foto para revisar: <archivo>", con la observación, y notifica a Manu. No saques la foto por tu cuenta: la decide Manu, porque está publicada y puede ser del cliente.

## Notificar a Manu

Usa la herramienta de notificación al celular si está disponible (búscala con ToolSearch: "push notification"). Si no, termina la corrida con el aviso como última línea, que es lo que le llega en la notificación de la tarea. Formato: una línea con qué necesita, el sitio, el número del PR o del pedido y qué hace el cambio. Para aprobar un riesgo alto: "GitHub → sitio-<nombre> → Actions → Publicar → Run workflow con el PR #n". Escribe en español neutro, sin guiones largos.

## Reglas

- Una sola cosa por corrida. Nunca dos pedidos a la vez, ni en el mismo sitio ni en sitios distintos.
- Nunca push a `main` ni a `produccion`. Nunca pongas `listo` sin el "aprobar" del aprobador. Nunca quites `espera-manu`. Nunca lances `publicar.yml` a mano.
- Nunca cambies en un sitio `fabrica/`, `.github/`, `CLAUDE.md`, `build.py` ni `marca.json` por tu cuenta: si un pedido los toca, sigue el recorrido normal y queda de riesgo alto.
- Sin datos personales de los clientes de los negocios (nombres, caras, direcciones, patentes) en comentarios, capturas o pruebas.
- El copy del sitio va en el idioma de `.reglas.json` del sitio (los sitios de clientes suelen ir en voseo). Comentarios y documentación, en español neutro con tuteo, sin guiones largos.
