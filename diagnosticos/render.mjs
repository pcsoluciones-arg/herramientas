// Arma la página del diagnóstico con el mismo molde del panel (htmlPropuesta de src/diagnostico.js).
// Uso: node render.mjs <diagnostico.json> <salida.html> [--panel ../panel-prospector] [--ahora 2026-11-06]
//   --panel  carpeta del repositorio pcsoluciones-arg/panel-prospector (por defecto, al lado de herramientas
//            o la variable PANEL). Tiene que estar en la sesión: es privado.
//   --ahora  fecha con la que se decide si la oferta está vigente (por defecto, hoy).
import { readFileSync, writeFileSync, existsSync, mkdtempSync, copyFileSync } from "fs";
import { tmpdir } from "os";
import { dirname, resolve } from "path";
import { fileURLToPath, pathToFileURL } from "url";

const args = process.argv.slice(2);
const opcion = (n, def) => { const i = args.indexOf(n); return i >= 0 ? args.splice(i, 2)[1] : def; };
const aqui = dirname(fileURLToPath(import.meta.url));
const panel = resolve(opcion("--panel", process.env.PANEL || resolve(aqui, "..", "..", "panel-prospector")));
const ahora = opcion("--ahora", null);
const [entrada, salida] = args;
if (!entrada || !salida) { console.error("Uso: node render.mjs <diagnostico.json> <salida.html> [--panel carpeta] [--ahora AAAA-MM-DD]"); process.exit(2); }
if (!existsSync(resolve(panel, "src", "diagnostico.js"))) { console.error("No encuentro " + resolve(panel, "src", "diagnostico.js") + ": clonar pcsoluciones-arg/panel-prospector o pasar --panel"); process.exit(2); }

const { htmlPropuesta } = await import(pathToFileURL(resolve(panel, "src", "diagnostico.js")).href);
const d = JSON.parse(readFileSync(entrada, "utf8"));
// El panel sirve las tipografías como sg.woff2 y mr.woff2 (servidor.js); en el repositorio tienen el nombre largo.
// Se copian con el nombre corto, y además el marco del iPhone, a una carpeta temporal.
const fuentes = mkdtempSync(resolve(tmpdir(), "fuentes-diag-"));
copyFileSync(resolve(panel, "fuentes", "space-grotesk-latin-wght-normal.woff2"), resolve(fuentes, "sg.woff2"));
copyFileSync(resolve(panel, "fuentes", "manrope-latin-wght-normal.woff2"), resolve(fuentes, "mr.woff2"));
if (existsSync(resolve(panel, "src", "iphone.webp"))) copyFileSync(resolve(panel, "src", "iphone.webp"), resolve(fuentes, "iphone.webp"));
const html = htmlPropuesta({ datos: d.datos, fotos: d.fotos, captura: d.captura }, {
  foto: (x) => x, fuentes: pathToFileURL(fuentes).href, modo: "publico",
  ahora: ahora ? new Date(ahora + "T12:00:00-03:00") : new Date()
});
writeFileSync(salida, html);
console.log("ok", Math.round(html.length / 1024), "KB");
