#!/usr/bin/env python3
"""Filtro de riesgo de la Fábrica de presencia (repositorios sitio-*).

Decide si un cambio en el sitio de un cliente se publica solo (riesgo bajo) o espera la aprobación de Manu (riesgo
alto), mirando qué archivos toca y, en contenido.json, qué campos cambia. Es código y no un modelo: siempre da lo
mismo para el mismo diff. Un agente puede subir el riesgo, nunca bajarlo.

Riesgo bajo (todo el cambio tiene que estar acá):
- fotos/ (WebP, JPG, PNG o AVIF) y ficha-google/ (JPG o PNG), agregando o reemplazando, sin borrar.
- contenido.json, dentro de las secciones que declara secciones.json (lo que carga el panel): fotos nuevas, títulos
  y bajadas, orden. Sin retirar más ítems de los que entran.
- contenido.json, fuera de esas secciones: solo textos en campos que ya existen, sin agregar ni quitar campos.
- Documentación (.md), salvo CLAUDE.md.
- En ningún caso datos de contacto (teléfono, correo, enlaces, dominio) ni precios. Si un texto los nombra, el cambio
  es de riesgo alto aunque el resto sea bajo.
- Menos de 300 líneas en total.

Todo lo demás es de riesgo alto: build.py, wrangler.toml, secciones.json, .reglas.json, CLAUDE.md, marca.json,
publico/, fuente/, estilos y código, .github/, fabrica/ (la fábrica no puede aflojar sus propias reglas).

El original vive en pcsoluciones-arg/herramientas (sitios/); instalar.py lo copia a fabrica/ de cada sitio.

Uso:
    python3 fabrica/riesgo_sitio.py BASE HEAD            # resumen legible
    python3 fabrica/riesgo_sitio.py BASE HEAD --json     # {"riesgo": "bajo"|"alto", "motivos": [...], ...}

Sale siempre con código 0; el resultado va en la salida. Solo biblioteca estándar de Python.
"""
import fnmatch
import json
import re
import subprocess
import sys

# Archivos que siempre esperan a Manu. Se miran antes que la lista de bajo.
ALTO = [
    "build.py", "wrangler.toml", "secciones.json", ".reglas.json", "CLAUDE.md", "marca.json",
    "publico/*", "fuente/*", ".github/*", "fabrica/*",
    "*.css", "*.js", "*.mjs", "*.html", "*.htm", "*.toml", "*.py", "package.json", "package-lock.json",
]
FOTOS = {"fotos": (".webp", ".jpg", ".jpeg", ".png", ".avif"), "ficha-google": (".jpg", ".jpeg", ".png")}
MAX_LINEAS = 300
CAMPOS_ITEM = {"id", "titulo", "bajada", "fotos"}
NOMBRE_FOTO = re.compile(r"^[a-z0-9][a-z0-9-]{0,80}$")
# Campos de contacto, precios o dominio: cambiarlos es siempre de riesgo alto, diga lo que diga el texto.
CAMPO_SENSIBLE = re.compile(
    r"(^|_)(tel|telefono|tel[eé]fonos?|celular|whatsapp|wa|email|correo|mail|precios?|tarifas?|costos?|valor|"
    r"dominio|url|web|enlace|link|direcci[oó]n|domicilio|instagram|facebook|redes)($|_)", re.I)
# Menciones de contacto o de precio dentro de un texto.
MENCION = re.compile(
    r"(\+?\d[\d \-().]{6,}\d"                       # teléfonos (8 cifras o más, con o sin separadores)
    r"|[\w.+-]+@[\w-]+\.[\w.]+"                       # correos
    r"|https?://\S+|www\.\S+|wa\.me\S*"               # enlaces
    r"|\b[\w-]+\.(?:com|net|org|ar)(?:\.ar)?\b"       # dominios
    r"|\$\s?\d[\d.,]*|\b(?:usd|ars|u\$s)\b|\bpesos\b"  # montos
    r"|\bprecios?\b|\bcuestan?\b|\bgratis\b|\bsin (?:cargo|costo)\b|\bdescuentos?\b|\bcuotas\b|\d+\s?%)",
    re.I)


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def mostrar(rev, ruta):
    r = subprocess.run(["git", "show", f"{rev}:{ruta}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def menciones(texto):
    """Lista ordenada de menciones de contacto o precio en un texto, normalizadas."""
    if not isinstance(texto, str):
        return []
    return sorted(re.sub(r"\s+", " ", m.group()).strip().lower() for m in MENCION.finditer(texto))


def coincide(ruta, patrones):
    return any(fnmatch.fnmatch(ruta, p) for p in patrones)


def evaluar(base, head):
    motivos, cambios = [], []
    total = 0
    for c in git("diff", "--numstat", f"{base}...{head}").splitlines():
        a, q, _ = c.split("\t", 2)
        total += (int(a) if a.isdigit() else 0) + (int(q) if q.isdigit() else 0)
    if total > MAX_LINEAS:
        motivos.append(f"El cambio tiene {total} líneas (más de {MAX_LINEAS}).")

    for l in git("diff", "--name-status", "--no-renames", f"{base}...{head}").splitlines():
        if not l:
            continue
        partes = l.split("\t")
        estado, ruta = partes[0], partes[-1]
        carpeta = ruta.split("/", 1)[0] if "/" in ruta else ""
        if coincide(ruta, ALTO):
            motivos.append(f"Toca {ruta}, que siempre necesita aprobación.")
        elif carpeta in FOTOS:
            if ruta.count("/") != 1 or not ruta.lower().endswith(FOTOS[carpeta]):
                motivos.append(f"{ruta}: en {carpeta}/ solo van imágenes ({', '.join(FOTOS[carpeta])}), sin subcarpetas.")
            elif estado.startswith("D"):
                motivos.append(f"Borra {ruta} del repositorio.")
            else:
                cambios.append(("foto nueva" if estado.startswith("A") else "foto cambiada") + f": {ruta}")
        elif ruta == "contenido.json":
            if estado.startswith("D"):
                motivos.append("Borra contenido.json.")
            else:
                m, c = revisar_contenido(base, head)
                motivos += m
                cambios += c
        elif ruta.endswith(".md"):
            cambios.append(f"documentación: {ruta}")
        else:
            motivos.append(f"Toca {ruta}, que no está en la lista de lo que se publica solo.")
    return {"riesgo": "alto" if motivos else "bajo", "motivos": list(dict.fromkeys(motivos)),
            "cambios": cambios, "lineas": total}


def claves_de_secciones(rev):
    txt = mostrar(rev, "secciones.json")
    try:
        sec = json.loads(txt) if txt else {}
    except ValueError:
        return set()
    return {x.get("clave") for x in sec.get("secciones", []) if isinstance(x, dict) and x.get("clave")}


def revisar_contenido(base, head):
    motivos, cambios = [], []
    try:
        viejo = json.loads(mostrar(base, "contenido.json") or "{}")
        nuevo = json.loads(mostrar(head, "contenido.json") or "")
    except ValueError:
        return ["contenido.json no se puede leer como JSON."], []
    if not isinstance(viejo, dict) or not isinstance(nuevo, dict):
        return ["contenido.json tiene que ser un objeto."], []
    if set(viejo) != set(nuevo):
        agregados, quitados = sorted(set(nuevo) - set(viejo)), sorted(set(viejo) - set(nuevo))
        motivos.append("contenido.json agrega o quita campos de primer nivel: "
                       + ", ".join([f"+{k}" for k in agregados] + [f"-{k}" for k in quitados]) + ".")
    # Las secciones se toman de la base: si el cambio toca secciones.json ya es de riesgo alto por sí solo.
    secciones = claves_de_secciones(base)
    for k in sorted(set(viejo) & set(nuevo)):
        if k in secciones:
            m, c = revisar_seccion(k, viejo[k], nuevo[k])
        else:
            m, c = revisar_textos(k, viejo[k], nuevo[k])
        motivos += m
        cambios += c
    return motivos, cambios


def revisar_seccion(clave, viejo, nuevo):
    """Una sección que carga el panel: lista de ítems {id, titulo, bajada, fotos: [{archivo, rol}]}."""
    if not isinstance(viejo, list) or not isinstance(nuevo, list):
        return [f"contenido.json: la sección {clave} dejó de ser una lista."], []
    motivos, cambios = [], []
    por_id = {str(x.get("id")): x for x in viejo if isinstance(x, dict)}
    ids_nuevos = []
    for x in nuevo:
        if not isinstance(x, dict) or "id" not in x:
            motivos.append(f"contenido.json: la sección {clave} tiene un ítem sin id.")
            continue
        i = str(x["id"])
        ids_nuevos.append(i)
        extra = set(x) - CAMPOS_ITEM
        if extra:
            motivos.append(f"contenido.json: el ítem {i} de {clave} agrega campos ({', '.join(sorted(extra))}).")
        for f in x.get("fotos", []) if isinstance(x.get("fotos"), list) else [None]:
            if not isinstance(f, dict) or not NOMBRE_FOTO.match(str(f.get("archivo", ""))) or set(f) - {"archivo", "rol"}:
                motivos.append(f"contenido.json: el ítem {i} de {clave} tiene una foto con un formato inesperado.")
                break
        antes = por_id.get(i, {})
        for campo in ("titulo", "bajada"):
            if x.get(campo) != antes.get(campo) and menciones(x.get(campo)) != menciones(antes.get(campo)):
                motivos.append(f"contenido.json: el {campo} de {i} ({clave}) nombra contacto o precio: «{str(x.get(campo))[:60]}».")
        if i not in por_id:
            cambios.append(f"{clave}: entra «{x.get('titulo', i)}»")
        elif x != antes:
            cambios.append(f"{clave}: cambia «{x.get('titulo', i)}»")
    if len(set(ids_nuevos)) != len(ids_nuevos):
        motivos.append(f"contenido.json: la sección {clave} tiene ids repetidos.")
    entran = len(set(ids_nuevos) - set(por_id))
    salen = len(set(por_id) - set(ids_nuevos))
    if salen > entran:
        motivos.append(f"contenido.json: en {clave} salen {salen} y entran {entran} (se retiran más de los que entran).")
    elif salen:
        cambios.append(f"{clave}: se retiran {salen} (entran {entran})")
    if [i for i in ids_nuevos if i in por_id] != [str(x.get('id')) for x in viejo if isinstance(x, dict) and str(x.get('id')) in ids_nuevos]:
        cambios.append(f"{clave}: cambia el orden")
    return motivos, cambios


def revisar_textos(ruta, viejo, nuevo):
    """Fuera de las secciones del panel: misma forma, solo cambian textos, sin contacto ni precios."""
    motivos, cambios = [], []
    if CAMPO_SENSIBLE.search(ruta.split(".")[-1].split("[")[0]) and viejo != nuevo:
        return [f"contenido.json: cambia {ruta}, que es un campo de contacto, precio o dominio."], []
    if type(viejo) is not type(nuevo):
        return [f"contenido.json: {ruta} cambia de tipo."], []
    if isinstance(viejo, dict):
        if set(viejo) != set(nuevo):
            return [f"contenido.json: {ruta} agrega o quita campos."], []
        for k in viejo:
            m, c = revisar_textos(f"{ruta}.{k}", viejo[k], nuevo[k])
            motivos += m
            cambios += c
    elif isinstance(viejo, list):
        if len(viejo) != len(nuevo):
            return [f"contenido.json: {ruta} pasa de {len(viejo)} a {len(nuevo)} elementos (agrega o quita)."], []
        for n, (a, b) in enumerate(zip(viejo, nuevo)):
            m, c = revisar_textos(f"{ruta}[{n}]", a, b)
            motivos += m
            cambios += c
    elif isinstance(viejo, str):
        if viejo != nuevo:
            if menciones(viejo) != menciones(nuevo):
                motivos.append(f"contenido.json: {ruta} cambia un dato de contacto o de precio: «{nuevo[:60]}».")
            else:
                cambios.append(f"texto: {ruta}")
    elif viejo != nuevo:
        motivos.append(f"contenido.json: {ruta} cambia un valor que no es texto ({viejo!r} → {nuevo!r}).")
    return motivos, cambios


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    r = evaluar(sys.argv[1], sys.argv[2])
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False))
    else:
        print(f"Riesgo {r['riesgo']} ({r['lineas']} líneas).")
        for m in r["motivos"]:
            print(" -", m)
        if r["cambios"]:
            print("Cambios:")
            for c in r["cambios"]:
                print(" ·", c)
