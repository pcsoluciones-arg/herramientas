# Repertorio de estilo: copia para los agentes

Copia del Repertorio de estilo de Manu, el design system que vive como artifact en claude.ai ("Repertorio de estilo", https://claude.ai/artifact/2yWSdKe7fPz4QRBHhKDzCi). **La fuente es el artifact.** Esta carpeta existe porque los agentes de las fábricas no leen artifacts: la leen el especificador al crear una marca, el revisor de interfaz del panel y el revisor visual de los sitios y las piezas.

No se edita a mano. Para cambiar algo, se cambia el artifact y se vuelve a exportar.

## Qué hay

| Archivo | Qué es |
|---|---|
| `README-repertorio.md` | Principios, las dos capas (autor y proyecto), luz, sombra, tipografía, imagen, movimiento, iconografía y escritura |
| `capas.md` | Las seis capas por medio (Sitios, Paneles, Apps, Piezas, Documentos, Impresos) y cómo se aplica una capa a un proyecto |
| `senales-de-plantilla.md` | Lista de control de lo que hace que algo se lea como plantilla o como diseño generado |
| `como-sumar.md` | Cómo entra una técnica nueva y la bitácora de versiones |
| `relevamiento.md` | El relevamiento de los proyectos propios del que salió el repertorio |
| `tokens.json`, `design-system.json` | Los tokens (colores por rol, escalas, sombras, radios) y la descripción del sistema |
| `fichas/<Nombre>.md` | La ficha de cada técnica: qué resuelve, cuándo usarla, cómo se construye |
| `huellas.json` | El sha256 de cada archivo según el artifact, para comprobar que la copia es exacta |

Las vistas previas de cada ficha (`preview.html`) y su CSS no se copian: se ven en el artifact.

## Exportada

1/11/2026, versión del artifact `1793509328-8a03` (repertorio 1.1 del 29/10/2026).

## Cómo se actualiza

Desde una conversación de Claude con acceso a los artifacts de Manu: leer cada archivo de `project/` del artifact con `read_file`, escribirlo acá tal cual (las fichas como `fichas/<Nombre>.md`), poner en `huellas.json` los sha256 que da `list_files` y correr `python3 pruebas/correr.py`, que compara cada archivo con su huella.
