#!/usr/bin/env python3
"""Revisor de reglas de PC Soluciones.

Revisa con código las reglas de escritura y de método que no hace falta juzgar a ojo.
La lista completa de reglas, de dónde sale cada una y cuáles quedan para un revisor
humano o agente está en el documento del proyecto claude/reglas-verificables.md.

Uso:
    python3 revisar.py [--perfil P] [--idioma I] [--json] RUTA [RUTA ...]

    --perfil  texto (por defecto), sitio, panel, entrega o carpeta. Cada perfil suma
              reglas propias (ver PERFILES más abajo).
    --idioma  neutro, voseo o libre. Si no se indica, se toma de .reglas.json o queda libre.
    --json    salida en JSON en vez de texto.

Si en la raíz del proyecto hay un archivo .reglas.json, se toma de ahí la configuración:
    {"perfil": "sitio", "idioma": "voseo",
     "idioma_por_archivo": [["*.md", "neutro"], ["src/*", "voseo"]],
     "ignorar": ["dist/*", "relevamiento/*"],
     "preview": false}

Resultado: una línea por hallazgo, "FALLA" o "AVISO". Sale con código 1 si hay alguna FALLA.
Solo lee. No cambia ningún archivo.
"""
import argparse
import fnmatch
import html
import json
import os
import re
import struct
import sys
import unicodedata
import zipfile

# ---------------------------------------------------------------- vocabulario

# Formas de voseo que no se confunden con otra cosa. Se buscan como palabra entera, sin mayúsculas.
VOSEO = """tenés podés querés sabés hacés decís sos venís mirás escribís contás llamás pedís elegís tocás
andás seguís entendés necesitás preferís buscás encontrás vendés trabajás cobrás pagás usás tenelo
mirá tocá hacé elegí pedí contá escribí llamá avisá fijate decime contame avisame escribime mandame
contanos escribinos llamanos avisanos consultanos pasate sumate animate acordate olvidate quedate
mandá dejá probá descargá completá compartí agendá reservá""".split()

# Formas de tuteo que no se confunden con tercera persona ni con el imperativo de vos.
TUTEO = """tienes puedes quieres sabes haces dices eres vienes necesitas prefieres buscas encuentras
escríbenos cuéntanos llámanos avísanos consúltanos contáctanos dime cuéntame avísame escríbeme
mándame fíjate entérate súmate anímate acuérdate quédate""".split()

EXT_TEXTO = {".md", ".txt", ".html", ".htm", ".json", ".csv"}
EXT_CODIGO = {".js", ".mjs", ".py", ".css", ".toml"}
EXT_IMAGEN = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}

RADIOS_OK = {0, 4, 8, 14, 22, 28, 999}
LETRAS_OK = {12, 13, 14, 15, 16, 20, 26}

# Archivos y carpetas que pueden estar en la raíz de PC Soluciones (regla del 15/10/2026).
RAIZ_OK = re.compile(r"^(0\d - .+|Autoemoción.*|_Archivo|_BORRAR|youtube|\..+)$")

hallazgos = []


def anotar(nivel, archivo, linea, regla, detalle):
    hallazgos.append({"nivel": nivel, "archivo": archivo, "linea": linea, "regla": regla, "detalle": detalle})


def nfc(s):
    return unicodedata.normalize("NFC", s)


# ---------------------------------------------------------------- reglas de texto

def lineas_con(patron, texto):
    for n, linea in enumerate(texto.splitlines(), 1):
        for m in patron.finditer(linea):
            yield n, m, linea


def texto_visible(h):
    """Texto que ve una persona en un HTML: sin script, style ni etiquetas."""
    h = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", h)
    h = re.sub(r"(?s)<!--.*?-->", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    return html.unescape(h)


def regla_guiones(ruta, texto):
    for n, m, _ in lineas_con(re.compile("[—–]"), texto):
        anotar("FALLA", ruta, n, "guiones", "guion largo o semilargo (%s)" % ("—" if m.group() == "—" else "–"))


def regla_idioma(ruta, texto, idioma):
    if idioma not in ("neutro", "voseo"):
        return
    lista = VOSEO if idioma == "neutro" else TUTEO
    nombre = "voseo en texto neutro" if idioma == "neutro" else "tuteo en texto con voseo"
    patron = re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, lista)) + r")(?![\w-])", re.I)
    for n, m, _ in lineas_con(patron, nfc(texto)):
        anotar("FALLA", ruta, n, "idioma", "%s: «%s»" % (nombre, m.group()))


TITULO_MD = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")
TITULO_HTML = re.compile(r"(?is)<h[1-6][^>]*>(.*?)</h[1-6]>")
INVERSION = re.compile(r"(?i)\bno (es|son|se trata de|era|fue)\b[^.?!]{1,80}?[:;,.]\s*(es|son|se trata de|sino|era|fue)\b")


def regla_titulos(ruta, texto, es_html):
    titulos = []
    if es_html:
        for m in TITULO_HTML.finditer(texto):
            n = texto.count("\n", 0, m.start()) + 1
            titulos.append((n, texto_visible(m.group(1)).strip()))
    else:
        for n, linea in enumerate(texto.splitlines(), 1):
            m = TITULO_MD.match(linea)
            if m:
                titulos.append((n, m.group(1)))
    for n, t in titulos:
        if INVERSION.search(t):
            anotar("FALLA", ruta, n, "titulos", "título con inversión del tipo «no es X: es Y»: %s" % t[:80])


# TODO y XXX solo en mayúsculas: en minúscula "todo" es una palabra común.
MARCADORES = re.compile(r"(\{\{[^}]*\}\}|\[completar[^\]]*\]|(?-i:\bTODO\b|\bXXX\b)|lorem ipsum|(?-i:__[A-Z]{3,}__))", re.I)


def regla_marcadores(ruta, texto):
    for n, m, _ in lineas_con(MARCADORES, texto):
        anotar("FALLA", ruta, n, "marcadores", "marcador sin reemplazar: %s" % m.group())


# ---------------------------------------------------------------- reglas de sitio

def meta(h, prop):
    m = re.search(r'(?is)<meta[^>]+(?:property|name)=["\']%s["\'][^>]*>' % re.escape(prop), h)
    if not m:
        return None
    c = re.search(r'(?is)content=["\']([^"\']*)["\']', m.group())
    return c.group(1) if c else ""


def medida_imagen(ruta):
    """Ancho y alto de un PNG, JPG o WebP leyendo solo la cabecera (sin bibliotecas)."""
    try:
        with open(ruta, "rb") as f:
            d = f.read(65536)
    except OSError:
        return None
    if d[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", d[16:24])
    if d[:4] == b"RIFF" and d[8:12] == b"WEBP":
        if d[12:16] == b"VP8X":
            return (int.from_bytes(d[24:27], "little") + 1, int.from_bytes(d[27:30], "little") + 1)
        if d[12:16] == b"VP8 ":
            return struct.unpack("<HH", d[26:30])
        if d[12:16] == b"VP8L":
            b = int.from_bytes(d[21:25], "little")
            return ((b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1)
    if d[:2] == b"\xff\xd8":
        i = 2
        while i < len(d) - 9:
            if d[i] != 0xFF:
                i += 1
                continue
            marca = d[i + 1]
            if marca in (0xC0, 0xC1, 0xC2):
                alto, ancho = struct.unpack(">HH", d[i + 5:i + 9])
                return (ancho, alto)
            i += 2 + struct.unpack(">H", d[i + 2:i + 4])[0]
    return None


def regla_sitio(ruta, h, preview):
    visible = texto_visible(h)
    base = os.path.dirname(ruta)

    # Open Graph completo y su imagen en 1200 × 630
    faltan = [p for p in ("og:title", "og:description", "og:image", "og:url") if not meta(h, p)]
    if faltan:
        anotar("FALLA", ruta, 0, "open-graph", "faltan etiquetas: " + ", ".join(faltan))
    img = meta(h, "og:image")
    if img:
        local = os.path.join(base, re.sub(r"^https?://[^/]+/", "", img).lstrip("/"))
        medida = medida_imagen(local) if os.path.exists(local) else None
        if medida and tuple(medida) != (1200, 630):
            anotar("FALLA", ruta, 0, "open-graph", "la imagen %s mide %d × %d (tiene que ser 1200 × 630)" % (img, medida[0], medida[1]))
        elif not medida:
            anotar("AVISO", ruta, 0, "open-graph", "no se pudo medir la imagen %s; comprobar 1200 × 630" % img)

    # Publicado: sin noindex y con canonical. En una preview, al revés: con noindex.
    robots = (meta(h, "robots") or "").lower()
    if preview and "noindex" not in robots:
        anotar("FALLA", ruta, 0, "indexacion", "es una preview y no tiene noindex")
    if not preview and "noindex" in robots:
        anotar("FALLA", ruta, 0, "indexacion", "tiene noindex y es el sitio publicado")
    if not preview and not re.search(r'(?i)<link[^>]+rel=["\']canonical["\']', h):
        anotar("FALLA", ruta, 0, "indexacion", "falta <link rel=\"canonical\">")

    # Área segura del iPhone
    vp = meta(h, "viewport") or ""
    if "viewport-fit=cover" not in vp.replace(" ", ""):
        anotar("FALLA", ruta, 0, "area-segura", "el viewport no tiene viewport-fit=cover")
    if "env(safe-area-inset" not in h:
        anotar("AVISO", ruta, 0, "area-segura", "no hay env(safe-area-inset-*) en el CSS de la página (puede estar en un .css aparte)")

    # Botones de WhatsApp medibles: cada uno con su mensaje propio
    textos = {}
    for m in re.finditer(r'(?i)href=["\'](https?://(?:wa\.me|api\.whatsapp\.com|web\.whatsapp\.com)[^"\']*)["\']', h):
        n = h.count("\n", 0, m.start()) + 1
        enlace = html.unescape(m.group(1))
        t = re.search(r"[?&]text=([^&]*)", enlace)
        if not t or not t.group(1):
            anotar("FALLA", ruta, n, "whatsapp", "botón de WhatsApp sin mensaje precargado: %s" % enlace[:60])
        else:
            textos.setdefault(t.group(1), []).append(n)
    for t, ns in textos.items():
        if len(ns) > 1:
            anotar("AVISO", ruta, ns[0], "whatsapp", "%d botones con el mismo mensaje (líneas %s): no se sabe desde cuál escribieron" % (len(ns), ", ".join(map(str, ns))))

    # Copy público: sin "landing" y con la promesa vigente
    for n, m, _ in lineas_con(re.compile(r"(?i)\blanding(s)?\b"), visible):
        anotar("FALLA", ruta, 0, "copy-publico", "aparece la palabra «%s» en el texto visible" % m.group())
    for n, m, _ in lineas_con(re.compile(r"(?i)\b3 semanas\b|\btres semanas\b"), visible):
        anotar("AVISO", ruta, 0, "copy-publico", "promesa vieja «%s»: la vigente es «Tu página lista en 3 días»" % m.group())

    # Firma del pie
    if "pcsoluciones.com.ar" in ruta.replace(os.sep, "/").lower() or "fuente-del-sitio" in ruta:
        pass  # el sitio propio no se firma a sí mismo
    elif not re.search(r'(?is)<footer.*?pcsoluciones\.com\.ar.*?</footer>', h):
        anotar("AVISO", ruta, 0, "firma", "el pie no enlaza a pcsoluciones.com.ar (firma «Sitio desarrollado por PC Soluciones»)")

    # Schema igual al texto visible: cada pregunta de un FAQPage tiene que estar en la página
    plano = re.sub(r"\s+", " ", visible).lower()
    for m in re.finditer(r'(?is)<script[^>]+application/ld\+json[^>]*>(.*?)</script>', h):
        try:
            datos = json.loads(m.group(1))
        except ValueError:
            anotar("FALLA", ruta, h.count("\n", 0, m.start()) + 1, "schema", "JSON-LD que no se puede leer")
            continue
        pila = [datos]
        while pila:
            x = pila.pop()
            if isinstance(x, list):
                pila.extend(x)
            elif isinstance(x, dict):
                if x.get("@type") == "Question" and isinstance(x.get("name"), str):
                    q = re.sub(r"\s+", " ", html.unescape(x["name"])).strip().lower()
                    if q and q not in plano:
                        anotar("FALLA", ruta, 0, "schema", "pregunta del schema que no está en el texto visible: %s" % x["name"][:70])
                pila.extend(x.values())


# ---------------------------------------------------------------- reglas del panel

SECRETOS = re.compile(r"(sk-(?:proj-)?[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")


def regla_secretos(ruta, texto):
    for n, m, _ in lineas_con(SECRETOS, texto):
        anotar("FALLA", ruta, n, "secretos", "parece una clave o token (%s…)" % m.group()[:8])


def regla_css(ruta, texto):
    for n, m, _ in lineas_con(re.compile(r"border-radius\s*:\s*([^;\"'}]+)"), texto):
        for v in re.findall(r"(\d+(?:\.\d+)?)px", m.group(1)):
            if float(v) not in RADIOS_OK:
                anotar("AVISO", ruta, n, "css-radios", "radio de %spx (los de la escala son 4, 8, 14, 22, 28 o 999)" % v)
    for n, m, _ in lineas_con(re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px"), texto):
        if float(m.group(1)) not in LETRAS_OK:
            anotar("AVISO", ruta, n, "css-letra", "letra de %spx (la escala es 12, 13, 14, 15, 16, 20 y 26)" % m.group(1))


# ---------------------------------------------------------------- reglas de archivos

def regla_zip(ruta):
    try:
        with zipfile.ZipFile(ruta) as z:
            vacios = [i.filename for i in z.infolist() if not i.is_dir() and i.file_size == 0]
            malos = z.testzip()
    except zipfile.BadZipFile:
        anotar("FALLA", ruta, 0, "zip", "el zip está roto")
        return
    for v in vacios:
        anotar("FALLA", ruta, 0, "zip", "archivo en 0 bytes dentro del zip: %s (¿estaba solo en la nube de OneDrive?)" % v)
    if malos:
        anotar("FALLA", ruta, 0, "zip", "archivo dañado dentro del zip: %s" % malos)


def regla_c2pa(ruta):
    try:
        with open(ruta, "rb") as f:
            d = f.read()
    except OSError:
        return
    if b"c2pa" in d or b"jumb" in d[:200000] and b"jumd" in d[:200000]:
        anotar("FALLA", ruta, 0, "c2pa", "la imagen tiene metadatos C2PA: pasarla por limpiar_credenciales.py")


def regla_nombre_ascii(ruta):
    nombre = os.path.basename(ruta)
    if nombre.lower().endswith(".csv") and any(ord(c) > 127 for c in nombre):
        anotar("FALLA", ruta, 0, "nombres", "CSV con tildes en el nombre: renombrarlo a ASCII antes de moverlo (OneDrive se traba)")


def regla_docx(ruta):
    try:
        with zipfile.ZipFile(ruta) as z:
            x = z.read("word/document.xml").decode("utf8", "replace")
    except (zipfile.BadZipFile, KeyError):
        anotar("FALLA", ruta, 0, "docx", "el .docx no se puede abrir")
        return
    fijas = [s for s in re.findall(r"<w:spacing\b[^>]*>", x) if "w:line=" in s and 'w:lineRule="auto"' not in s]
    if fijas:
        anotar("AVISO", ruta, 0, "docx", "%d párrafos con alto de línea fijo: recorta imágenes (usar lineRule auto)" % len(fijas))


def regla_pdf(ruta):
    try:
        with open(ruta, "rb") as f:
            d = f.read()
    except OSError:
        return
    cajas = re.findall(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]", d)
    for c in cajas:
        ancho, alto = float(c[2]) - float(c[0]), float(c[3]) - float(c[1])
        if abs(ancho - 595.28) > 2 or abs(alto - 841.89) > 2:
            anotar("AVISO", ruta, 0, "pdf", "página de %.0f × %.0f pt (A4 es 595 × 842)" % (ancho, alto))
            break
    if b"/FontFile" not in d and b"/Font" in d:
        anotar("AVISO", ruta, 0, "pdf", "las tipografías no parecen embebidas")


def regla_carpeta_raiz(raiz):
    for nombre in sorted(os.listdir(raiz)):
        if not RAIZ_OK.match(nfc(nombre)):
            anotar("FALLA", os.path.join(raiz, nombre), 0, "carpeta", "en la raíz de PC Soluciones solo van las carpetas 00 a 07, Autoemoción, _Archivo, _BORRAR y youtube")
    for actual, carpetas, _ in os.walk(raiz):
        if os.path.basename(actual) == "_BORRAR":
            carpetas[:] = []
            continue
        for c in carpetas:
            if c == "_BORRAR" and actual != raiz:
                anotar("FALLA", os.path.join(actual, c), 0, "carpeta", "hay una _BORRAR fuera de la raíz: va una sola, en la raíz")
            if c in ("node_modules", "dist", ".wrangler") or c.startswith("_tmp"):
                anotar("AVISO", os.path.join(actual, c), 0, "carpeta", "build o temporal dentro de OneDrive: va en ~/Trabajo-local")


# ---------------------------------------------------------------- recorrido

def cargar_config(rutas):
    for r in rutas:
        d = os.path.abspath(r if os.path.isdir(r) else os.path.dirname(r))
        while True:
            c = os.path.join(d, ".reglas.json")
            if os.path.exists(c):
                with open(c, encoding="utf8") as f:
                    return json.load(f), d
            padre = os.path.dirname(d)
            if padre == d:
                break
            d = padre
    return {}, None


def idioma_de(rel, config, idioma_cli):
    if idioma_cli:
        return idioma_cli
    for patron, idioma in config.get("idioma_por_archivo", []):
        if fnmatch.fnmatch(rel, patron):
            return idioma
    return config.get("idioma", "libre")


def archivos(rutas, ignorar, base):
    for r in rutas:
        if os.path.isfile(r):
            yield r
            continue
        for actual, carpetas, nombres in os.walk(r):
            carpetas[:] = [c for c in carpetas if not c.startswith(".") and c not in ("node_modules", "_BORRAR", "__pycache__")]
            for n in nombres:
                ruta = os.path.join(actual, n)
                rel = os.path.relpath(ruta, base or r)
                if not any(fnmatch.fnmatch(rel, p) for p in ignorar):
                    yield ruta


def revisar(ruta, perfil, idioma, preview):
    ext = os.path.splitext(ruta)[1].lower()
    regla_nombre_ascii(ruta)
    if ext == ".zip":
        return regla_zip(ruta)
    if ext == ".docx":
        return regla_docx(ruta)
    if ext == ".pdf":
        return regla_pdf(ruta)
    if ext in EXT_IMAGEN and ext != ".svg":
        return regla_c2pa(ruta)
    if ext not in EXT_TEXTO | EXT_CODIGO | {".svg"}:
        return
    try:
        with open(ruta, encoding="utf8") as f:
            texto = f.read()
    except (UnicodeDecodeError, OSError) as e:
        if isinstance(e, OSError) and e.errno == 35:
            anotar("AVISO", ruta, 0, "lectura", "no se pudo leer: el archivo está solo en la nube de OneDrive")
        return
    regla_secretos(ruta, texto)
    if ext in EXT_CODIGO:
        if perfil == "panel" and ext in (".css",):
            regla_css(ruta, texto)
        return
    es_html = ext in (".html", ".htm")
    visible = texto_visible(texto) if es_html else texto
    regla_guiones(ruta, texto if not es_html else visible)
    regla_idioma(ruta, visible, idioma)
    regla_titulos(ruta, texto, es_html)
    if ext != ".json":
        regla_marcadores(ruta, visible if es_html else texto)
    if es_html and perfil == "sitio":
        regla_sitio(ruta, texto, preview)
    if es_html and perfil == "panel":
        regla_css(ruta, texto)


def main():
    ap = argparse.ArgumentParser(description="Revisor de reglas de PC Soluciones (solo lee).")
    ap.add_argument("rutas", nargs="+")
    ap.add_argument("--perfil", choices=["texto", "sitio", "panel", "entrega", "carpeta"])
    ap.add_argument("--idioma", choices=["neutro", "voseo", "libre"])
    ap.add_argument("--preview", action="store_true", help="la página es una preview (tiene que llevar noindex)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    config, base = cargar_config(a.rutas)
    perfil = a.perfil or config.get("perfil", "texto")
    preview = a.preview or bool(config.get("preview"))
    ignorar = config.get("ignorar", [])

    if perfil == "carpeta":
        for r in a.rutas:
            regla_carpeta_raiz(r)
    else:
        for ruta in archivos(a.rutas, ignorar, base):
            rel = os.path.relpath(ruta, base) if base else ruta
            revisar(ruta, perfil, idioma_de(rel, config, a.idioma), preview)

    if a.json:
        print(json.dumps(hallazgos, ensure_ascii=False, indent=1))
    else:
        for h in hallazgos:
            donde = h["archivo"] + (":%d" % h["linea"] if h["linea"] else "")
            print("%-5s %s  [%s] %s" % (h["nivel"], donde, h["regla"], h["detalle"]))
        fallas = sum(1 for h in hallazgos if h["nivel"] == "FALLA")
        avisos = len(hallazgos) - fallas
        print("\n%d fallas, %d avisos." % (fallas, avisos) if hallazgos else "Sin hallazgos.")
    sys.exit(1 if any(h["nivel"] == "FALLA" for h in hallazgos) else 0)


if __name__ == "__main__":
    main()
