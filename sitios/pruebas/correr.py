#!/usr/bin/env python3
"""Pruebas de la Fábrica de presencia: sello, filtro de riesgo, instalar.py, controles en vivo y navegador.py.

Uso: python3 sitios/pruebas/correr.py   (también lo corre pruebas/correr.py del repositorio)

Las pruebas del sello necesitan la biblioteca cryptography y las del navegador, Playwright con Chromium. Si faltan,
se saltean con un aviso: el resto corre solo con la biblioteca estándar.
"""
import base64
import functools
import http.server
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import threading

AQUI = pathlib.Path(__file__).resolve().parent
SITIOS = AQUI.parent
sys.path.insert(0, str(SITIOS))
import sello  # noqa: E402
import riesgo_sitio  # noqa: E402

fallas = 0


def caso(nombre, ok, detalle=""):
    global fallas
    print(("ok    " if ok else "FALLA ") + nombre + ("" if ok or not detalle else f"  ({detalle})"))
    fallas += 0 if ok else 1


# ---------------------------------------------------------------- sello

CONFIG = {"repo": "pcsoluciones-arg/sitio-prueba", "flujo": "publicar.yml", "url": "https://prueba.com.ar/", "worker": "prueba"}
try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
except ImportError:
    rsa = None
    print("aviso: falta la biblioteca cryptography, se saltean las pruebas del sello")
if rsa:
    b64 = lambda b: base64.urlsafe_b64encode(b).decode().rstrip("=")
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    nums = priv.public_key().public_numbers()
    claves = [{"kid": "k1", "kty": "RSA", "n": b64(nums.n.to_bytes(256, "big")), "e": b64(nums.e.to_bytes(3, "big"))}]

    def token(**cambios):
        datos = {"iss": sello.EMISOR, "aud": sello.audiencia(CONFIG["repo"], "abc"), "repository": CONFIG["repo"],
                 "repository_owner": "pcsoluciones-arg", "job_workflow_ref": sello.flujo_de(CONFIG), "run_id": "1", "actor": "manu"}
        datos.update(cambios)
        cab = b64(json.dumps({"alg": "RS256", "kid": "k1"}).encode())
        cuerpo = b64(json.dumps(datos).encode())
        firma = priv.sign(f"{cab}.{cuerpo}".encode(), padding.PKCS1v15(), hashes.SHA256())
        return f"{cab}.{cuerpo}.{b64(firma)}"

    v = lambda t, arbol="abc", c=CONFIG: sello.verificar_token(t, arbol, claves, c)[0]
    caso("sello válido", v(token()))
    caso("sello de otro contenido", not v(token(), "otro"))
    caso("sello de otro flujo", not v(token(job_workflow_ref=CONFIG["repo"] + "/.github/workflows/x.yml@refs/heads/main")))
    caso("sello de publicar.yml en otra rama", not v(token(job_workflow_ref=CONFIG["repo"] + "/.github/workflows/publicar.yml@refs/heads/otra")))
    caso("sello de otro sitio de la cuenta", not v(token(repository="pcsoluciones-arg/sitio-otro")))
    caso("sello de otra cuenta", not v(token(repository="otra/sitio-prueba", repository_owner="otra")))
    caso("sello de otro emisor", not v(token(iss="https://otro")))
    caso("sello del panel no sirve para un sitio", not v(token(aud="panel-prospector:sello:abc")))
    t = token()
    caso("firma alterada", not v(t[:-4] + ("AAAA" if not t.endswith("AAAA") else "BBBB")))
    caso("clave desconocida", not sello.verificar_token(t, "abc", [dict(claves[0], kid="otra")], CONFIG)[0])
    caso("lee el sello y el origen del mensaje",
         sello.sello_de(f"Publica\n\n{sello.ORIGEN} 123abc\n{sello.TRAILER} {t}\n") == t
         and sello.origen_de(f"Publica\n\n{sello.ORIGEN} 123abc\n") == "123abc")
    caso("commit sin sello", sello.sello_de("Arreglo rápido\n") is None)

with tempfile.TemporaryDirectory() as d:
    c = pathlib.Path(d, "config.json")
    c.write_text(json.dumps(dict(CONFIG, repo="otra/sitio-prueba")))
    try:
        sello.leer_config(c)
        caso("config.json de otra cuenta se rechaza", False)
    except ValueError:
        caso("config.json de otra cuenta se rechaza", True)

# ---------------------------------------------------------------- filtro de riesgo

SECCIONES = {"formato": "secciones/v1", "sitio": {"url": "https://prueba.com.ar/"},
             "secciones": [{"clave": "trabajos", "foto": {"ancho": 640, "alto": 800}, "maximo_visibles": 12}]}
CONTENIDO = {
    "formato": "contenido/v1",
    "trabajos": [
        {"id": "calefon", "titulo": "Cambio de calefón", "bajada": "De uno viejo a uno nuevo.", "fotos": [{"archivo": "calefon", "rol": "unica"}]},
        {"id": "bacha", "titulo": "Cañería de bacha", "bajada": "Caños nuevos.", "fotos": [{"archivo": "bacha", "rol": "unica"}]},
    ],
    "servicios": [{"icono": "gota", "titulo": "Pérdidas de agua", "bajada": "Encuentro la pérdida y la reparo."}],
    "preguntas": [{"pregunta": "¿Cobrás la visita?", "respuesta": "La visita es sin cargo."}],
    "zonas": {"caba": ["Núñez", "Belgrano"]},
    "contacto": {"telefono": "11 6249-2740"},
}
BASE = {"build.py": "print(1)\n", "wrangler.toml": 'name = "prueba"\n', "secciones.json": json.dumps(SECCIONES),
        "contenido.json": json.dumps(CONTENIDO, ensure_ascii=False, indent=2) + "\n", "fotos/calefon.webp": "W",
        "fotos/bacha.webp": "W", "ficha-google/calefon.jpg": "J", "LEEME.md": "hola\n", "CLAUDE.md": "reglas\n",
        "publico/favicon.png": "P"}


def repo_juguete(cambios):
    """Arma un repositorio con BASE y aplica cambios {ruta: contenido | None}. Devuelve (dir, base, head)."""
    tmp = tempfile.mkdtemp()
    g = lambda *a: subprocess.run(["git", "-C", tmp, *a], capture_output=True, text=True, check=True).stdout.strip()
    g("init", "-q")
    g("config", "user.email", "t@t")
    g("config", "user.name", "t")
    for ruta, txt in BASE.items():
        f = pathlib.Path(tmp, ruta)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(txt)
    g("add", "-A")
    g("commit", "-qm", "base")
    base = g("rev-parse", "HEAD")
    for ruta, txt in cambios.items():
        f = pathlib.Path(tmp, ruta)
        if txt is None:
            f.unlink()
        else:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(txt)
    g("add", "-A")
    g("commit", "-qm", "cambio", "--allow-empty")
    return tmp, base, g("rev-parse", "HEAD")


def riesgo_de(cambios):
    tmp, base, head = repo_juguete(cambios)
    cwd = os.getcwd()
    os.chdir(tmp)
    try:
        return riesgo_sitio.evaluar(base, head)
    finally:
        os.chdir(cwd)
        shutil.rmtree(tmp, ignore_errors=True)


def contenido(**cambios):
    c = json.loads(json.dumps(CONTENIDO))
    for k, f in cambios.items():
        f(c)
    return json.dumps(c, ensure_ascii=False, indent=2) + "\n"


NUEVO = {"id": "termo", "titulo": "Termotanque nuevo", "bajada": "Instalación completa.", "fotos": [{"archivo": "termo", "rol": "unica"}]}


def esperar(nombre, cambios, nivel):
    r = riesgo_de(cambios)
    caso(f"{nombre}: {nivel}", r["riesgo"] == nivel, "; ".join(r["motivos"]) or "sin motivos")


esperar("foto nueva desde el panel", {"fotos/termo.webp": "W", "ficha-google/termo.jpg": "J",
                                      "contenido.json": contenido(a=lambda c: c["trabajos"].insert(0, NUEVO))}, "bajo")
esperar("entra una y se retira una", {"fotos/termo.webp": "W", "contenido.json": contenido(a=lambda c: (c["trabajos"].insert(0, NUEVO), c["trabajos"].pop()))}, "bajo")
esperar("se retira sin que entre otra", {"contenido.json": contenido(a=lambda c: c["trabajos"].pop())}, "alto")
esperar("cambia el título de un trabajo", {"contenido.json": contenido(a=lambda c: c["trabajos"][0].update(titulo="Calefón nuevo"))}, "bajo")
esperar("cambia el orden de los trabajos", {"contenido.json": contenido(a=lambda c: c["trabajos"].reverse())}, "bajo")
esperar("título de trabajo con precio", {"contenido.json": contenido(a=lambda c: c["trabajos"][0].update(titulo="Calefón desde $45.000"))}, "alto")
esperar("trabajo con un campo nuevo", {"contenido.json": contenido(a=lambda c: c["trabajos"][0].update(precio="1"))}, "alto")
esperar("texto de un servicio", {"contenido.json": contenido(a=lambda c: c["servicios"][0].update(bajada="Encuentro dónde está la pérdida."))}, "bajo")
esperar("servicio con teléfono", {"contenido.json": contenido(a=lambda c: c["servicios"][0].update(bajada="Llamame al 11 6249-2740."))}, "alto")
esperar("servicio con enlace", {"contenido.json": contenido(a=lambda c: c["servicios"][0].update(bajada="Mirá www.otro.com.ar"))}, "alto")
esperar("respuesta que mantiene el «sin cargo»", {"contenido.json": contenido(a=lambda c: c["preguntas"][0].update(respuesta="Sí: la visita es sin cargo en Núñez."))}, "bajo")
esperar("respuesta que cambia el precio", {"contenido.json": contenido(a=lambda c: c["preguntas"][0].update(respuesta="La visita cuesta $10.000."))}, "alto")
esperar("servicio nuevo", {"contenido.json": contenido(a=lambda c: c["servicios"].append({"icono": "x", "titulo": "Gas", "bajada": "Gas."}))}, "alto")
esperar("renombrar una zona", {"contenido.json": contenido(a=lambda c: c["zonas"]["caba"].__setitem__(1, "Colegiales"))}, "bajo")
esperar("zona nueva", {"contenido.json": contenido(a=lambda c: c["zonas"]["caba"].append("Saavedra"))}, "alto")
esperar("campo de contacto", {"contenido.json": contenido(a=lambda c: c["contacto"].update(telefono="11 5555-0000"))}, "alto")
esperar("campo nuevo de primer nivel", {"contenido.json": contenido(a=lambda c: c.update(promo="Hola"))}, "alto")
esperar("contenido.json roto", {"contenido.json": "{"}, "alto")
esperar("documentación", {"LEEME.md": "hola de nuevo\n"}, "bajo")
for ruta in ("build.py", "wrangler.toml", "secciones.json", "CLAUDE.md", "marca.json", "publico/favicon.png",
             ".github/workflows/publicar.yml", "fabrica/sello.py", "estilos.css", ".reglas.json", "herramientas/og.py"):
    esperar(f"tocar {ruta}", {ruta: "x\n"}, "alto")
esperar("borrar una foto", {"fotos/bacha.webp": None}, "alto")
esperar("un HTML dentro de fotos/", {"fotos/pagina.html": "<h1>x</h1>"}, "alto")
esperar("una subcarpeta en fotos/", {"fotos/a/b.webp": "W"}, "alto")
esperar("más de 300 líneas", {"LEEME.md": "hola\n" * 400}, "alto")

# ---------------------------------------------------------------- instalar.py

with tempfile.TemporaryDirectory() as d:
    sitio = pathlib.Path(d, "sitio-prueba")
    sitio.mkdir()
    (sitio / "build.py").write_text("print(1)\n")
    (sitio / "wrangler.toml").write_text('name = "prueba"\n')
    (sitio / "secciones.json").write_text(json.dumps(SECCIONES))
    subprocess.run(["git", "-C", str(sitio), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(sitio), "remote", "add", "origin", "https://github.com/pcsoluciones-arg/sitio-prueba"], check=True)
    inst = lambda *a: subprocess.run([sys.executable, str(SITIOS / "instalar.py"), *a, str(sitio)], capture_output=True, text=True)
    r = inst()
    cfg = json.loads((sitio / "fabrica/config.json").read_text())
    caso("instalar crea la copia y config.json", r.returncode == 0 and cfg["repo"] == "pcsoluciones-arg/sitio-prueba"
         and cfg["url"] == "https://prueba.com.ar/" and cfg["worker"] == "prueba", r.stdout + r.stderr)
    caso("verificar una copia igual", inst("--verificar").returncode == 0)
    with open(sitio / "fabrica/riesgo_sitio.py", "a") as f:
        f.write("# cambio a mano\n")
    caso("verificar una copia cambiada a mano: falla", inst("--verificar").returncode == 1)
    inst()
    (sitio / ".github/workflows/publicar.yml").unlink()
    caso("verificar sin un flujo: falla", inst("--verificar").returncode == 1)
    inst()
    caso("reinstalar no pisa config.json", json.loads((sitio / "fabrica/config.json").read_text()) == cfg)
    (sitio / "fabrica/config.json").write_text(json.dumps(dict(cfg, repo="pcsoluciones-arg/sitio-otro")))
    caso("verificar con config.json de otro repositorio: falla", inst("--verificar").returncode == 1)

# ---------------------------------------------------------------- controles en vivo (publicar_sitio.verificar_en_vivo)

import publicar_sitio  # noqa: E402


class _Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


with tempfile.TemporaryDirectory() as d:
    pathlib.Path(d, "index.html").write_text('<img src="bien.png"><img src="fotos/falta.webp">'
                                             '<meta property="og:image" content="bien.png">')
    pathlib.Path(d, "bien.png").write_bytes(b"\x89PNG")
    pathlib.Path(d, "version.json").write_text(json.dumps({"commit": "prod123", "origen": "main456"}))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(_Silencioso, directory=d))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    p = publicar_sitio.verificar_en_vivo(url, {"main456"}, minutos=0, www=False)
    caso("en vivo: version.json con el commit de origen", not any("version.json" in x for x in p), "; ".join(p))
    caso("en vivo: encuentra la imagen que responde 404", any("falta.webp" in x and "404" in x for x in p), "; ".join(p))
    caso("en vivo: la imagen que está no se marca", not any("bien.png" in x for x in p), "; ".join(p))
    p = publicar_sitio.verificar_en_vivo(url, {"otro"}, minutos=0, www=False)
    caso("en vivo: version.json con otro commit", any("version.json" in x for x in p), "; ".join(p))
    srv.shutdown()

# ---------------------------------------------------------------- recorrido de publicar_sitio.py (GitHub simulado)

def recorrido(evento, cambios, con_produccion=True, pr=None):
    """Arma un origin local con main (y produccion), aplica cambios en main y corre publicar_sitio.main().
    Devuelve (llamadas a la API, mensaje del último commit de produccion o None, árbol de main, árbol de produccion)."""
    raiz = pathlib.Path(tempfile.mkdtemp())
    g = lambda d, *a: subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=True).stdout.strip()
    origen, trabajo = raiz / "origen.git", raiz / "trabajo"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origen)], check=True)
    subprocess.run(["git", "clone", "-q", str(origen), str(trabajo)], check=True, capture_output=True)
    g(trabajo, "config", "user.email", "t@t")
    g(trabajo, "config", "user.name", "t")
    for ruta, txt in BASE.items():
        f = trabajo / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(txt)
    g(trabajo, "add", "-A")
    g(trabajo, "commit", "-qm", "base")
    g(trabajo, "push", "-q", "origin", "HEAD:main")
    if con_produccion:
        m = g(trabajo, "rev-parse", "HEAD")
        p = subprocess.run(["git", "-C", str(trabajo), "commit-tree", "HEAD^{tree}", "-p", m, "-m", f"Publica\n\n{sello.ORIGEN} {m}\n"],
                           capture_output=True, text=True, check=True).stdout.strip()
        g(trabajo, "push", "-q", "origin", f"{p}:refs/heads/produccion")
    for ruta, txt in cambios.items():
        f = trabajo / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(txt)
    g(trabajo, "add", "-A")
    g(trabajo, "commit", "-qm", "Panel PCS: foto nueva", "--allow-empty")
    g(trabajo, "push", "-q", "origin", "HEAD:main")

    llamadas = []
    ps = publicar_sitio
    viejos = (ps.api, ps.pedir_sello, ps.esperar_cloudflare, ps.verificar_en_vivo, ps.EVENTO, ps.A_MANO, ps.REPO, ps.CONFIG)

    def api(ruta, metodo="GET", datos=None):
        llamadas.append((metodo, ruta, datos))
        return [] if metodo == "GET" else {"number": 99}

    ps.api, ps.pedir_sello = api, lambda arbol: "token-de-prueba"
    ps.esperar_cloudflare = lambda sha, minutos=8: ("success", "")
    ps.verificar_en_vivo = lambda url, commits, **k: []
    ps.EVENTO, ps.A_MANO, ps.REPO = evento, evento == "workflow_dispatch", CONFIG["repo"]
    ps.CONFIG = CONFIG
    os.environ.pop("PR", None)
    if pr:
        os.environ["PR"] = str(pr)
    cwd = os.getcwd()
    os.chdir(trabajo)
    salida = None
    try:
        ps.main()
    except SystemExit as e:
        salida = e.code
    finally:
        os.chdir(cwd)
        ps.api, ps.pedir_sello, ps.esperar_cloudflare, ps.verificar_en_vivo, ps.EVENTO, ps.A_MANO, ps.REPO, ps.CONFIG = viejos
    prod = subprocess.run(["git", "-C", str(origen), "log", "-1", "--format=%B", "produccion"], capture_output=True, text=True)
    arbol_main = g(origen, "rev-parse", "main^{tree}")
    arbol_prod = subprocess.run(["git", "-C", str(origen), "rev-parse", "produccion^{tree}"], capture_output=True, text=True).stdout.strip()
    shutil.rmtree(raiz, ignore_errors=True)
    return llamadas, (prod.stdout if prod.returncode == 0 else None), arbol_main, arbol_prod, salida


def revision_con(checks):
    viejo = publicar_sitio.api
    publicar_sitio.api = lambda ruta, metodo="GET", datos=None: {"check_runs": checks}
    try:
        return publicar_sitio.revision_ok("abc")
    finally:
        publicar_sitio.api = viejo


caso("revisión: el controles en skipped de Publicar no tapa el success de Revisión",
     revision_con([{"id": 1, "name": "controles", "conclusion": "success"},
                   {"id": 2, "name": "controles", "conclusion": "skipped"}]) == "success")
caso("revisión: un controles nuevo en failure manda",
     revision_con([{"id": 1, "name": "controles", "conclusion": "success"},
                   {"id": 3, "name": "controles", "conclusion": "failure"}]) == "failure")
caso("revisión: sin controles válido devuelve None",
     revision_con([{"id": 2, "name": "controles", "conclusion": "skipped"}]) is None)

FOTO = {"fotos/termo.webp": "W", "contenido.json": contenido(a=lambda c: c["trabajos"].insert(0, NUEVO))}
ll, msj, am, ap, sal = recorrido("push", FOTO)
caso("push del panel con riesgo bajo: sella y publica main",
     am == ap and msj and f"{sello.TRAILER} token-de-prueba" in msj and sello.ORIGEN in msj and sal is None, f"{msj!r} {sal}")
ll, msj, am, ap, sal = recorrido("push", {"build.py": "print(2)\n"})
caso("push con riesgo alto: no publica y abre el pedido para Manu",
     am != ap and any(m == "POST" and r == "issues" and d and "espera-manu" in d.get("labels", []) for m, r, d in ll), str(ll))
ll, msj, am, ap, sal = recorrido("workflow_dispatch", {"build.py": "print(2)\n"})
caso("Manu aprueba main con riesgo alto: publica", am == ap and "Aprobado por Manu" in (msj or ""), f"{msj!r}")
ll, msj, am, ap, sal = recorrido("push", FOTO, con_produccion=False)
caso("primera publicación por push: no publica (la lanza Manu)", msj is None)
ll, msj, am, ap, sal = recorrido("workflow_dispatch", FOTO, con_produccion=False)
caso("primera publicación lanzada por Manu: crea produccion", am == ap and msj and sello.TRAILER in msj, f"{msj!r}")
os.environ.pop("PR", None)

# ---------------------------------------------------------------- navegador.py

try:
    import playwright  # noqa: F401
    hay_navegador = True
except ImportError:
    hay_navegador = False
    print("aviso: falta Playwright, se saltean las pruebas de navegador.py")
if hay_navegador:
    def navegar(carpeta):
        r = subprocess.run([sys.executable, str(SITIOS / "navegador.py"), str(AQUI / "casos" / carpeta), "--json", "--sin-limitar"],
                           capture_output=True, text=True, timeout=240)
        try:
            h = json.loads(r.stdout)
        except ValueError:
            return None, None, r.stderr[-300:]
        return {x["regla"] for x in h if x["nivel"] == "FALLA"}, {x["regla"] for x in h if x["nivel"] == "AVISO"}, r.stderr[-300:]

    f, a, err = navegar("navegador-malo")
    esperado = {"scroll-lateral", "pie", "fijo-mezcla", "imagenes", "archivos", "consola", "contraste"}
    caso("navegador: página con fallas", f == esperado and "toque" in (a or set()), f"esperado {sorted(esperado)}, hallado {sorted(f or [])} / {sorted(a or [])} {err}")
    f, a, err = navegar("navegador-bueno")
    caso("navegador: página sin fallas ni avisos", f == set() and a == set(), f"hallado {sorted(f or [])} / {sorted(a or [])} {err}")

# ---------------------------------------------------------------- orquestador de la Fábrica de sitios

RAIZ = SITIOS.parent
try:
    lista = json.loads((SITIOS / "sitios.json").read_text())["sitios"]
    bien = bool(lista) and all(re.fullmatch(r"pcsoluciones-arg/sitio-[a-z0-9-]+", s.get("repo", "")) and s.get("url", "").startswith("https://") for s in lista)
    caso("orquestador: sitios.json con repositorios sitio-* y su URL", bien, json.dumps(lista)[:200])
except (OSError, ValueError, KeyError) as e:
    caso("orquestador: sitios.json con repositorios sitio-* y su URL", False, str(e))

textos = {p: p.read_text() for p in [SITIOS / "orquestador.md", *sorted((SITIOS / "agentes").glob("*.md"))]}
faltan = sorted({ref for t in textos.values() for ref in re.findall(r"`((?:sitios|skills)/[\w/.-]+\.(?:md|json|py|sh))`", t)
                 if not (RAIZ / ref).exists()})
caso("orquestador: los archivos que nombran existen", not faltan, ", ".join(faltan))
guiones = [p.name for p, t in textos.items() if "—" in t or "–" in t]
caso("orquestador: sin guiones largos", not guiones, ", ".join(guiones))

print(f"\n{fallas} fallas")
sys.exit(1 if fallas else 0)
