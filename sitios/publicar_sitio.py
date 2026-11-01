#!/usr/bin/env python3
"""Publicación de la Fábrica de presencia. Lo corre .github/workflows/publicar.yml del sitio, desde la rama main.

Se dispara de tres formas:
- Push a main (los commits del panel PCS): publica main si el cambio desde la última publicación es de riesgo bajo.
  Si es alto, abre o actualiza un pedido "Cambios en main esperan tu aprobación" y no publica.
- Pedido de cambio (PR) con la etiqueta `listo`, o revisión en verde de un PR que ya la tiene: igual que el panel.
  Riesgo bajo: lo junta en main y publica. Riesgo alto: etiqueta `espera-manu` y termina.
- Aprobación de Manu (Actions → Publicar → Run workflow): publica el PR indicado aunque sea de riesgo alto, o main
  tal como está si no indica número. Las sesiones de Claude no pueden lanzar flujos de Actions, así que ese
  lanzamiento es su aprobación. La primera publicación sellada de un sitio (todavía sin rama produccion) solo sale así.

Después de crear el commit sellado en `produccion` espera el build de Cloudflare y controla en vivo:
version.json con el commit publicado, todas las imágenes de la página respondiendo 200 y www con 301 al dominio.

El original vive en pcsoluciones-arg/herramientas (sitios/); instalar.py lo copia a fabrica/ de cada sitio.
"""
import html.parser
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import riesgo_sitio as riesgo  # noqa: E402
import sello  # noqa: E402

CHECK_REVISION = "controles"
TITULO_PEDIDO = "Cambios en main esperan tu aprobación"
AUTOR = {"GIT_AUTHOR_NAME": "Manuel Tonnelier", "GIT_AUTHOR_EMAIL": "pcsolucionesbelgrano@gmail.com",
         "GIT_COMMITTER_NAME": "Fábrica de presencia", "GIT_COMMITTER_EMAIL": "pcsolucionesbelgrano@gmail.com"}


# ---------------------------------------------------------------- GitHub y git

def sh(*a, ok=True):
    r = subprocess.run(a, capture_output=True, text=True)
    if ok and r.returncode:
        sys.exit(f"Falló {' '.join(a)}:\n{r.stderr}")
    return r.stdout.strip()


def api(ruta, metodo="GET", datos=None):
    args = ["gh", "api", "-X", metodo, f"repos/{REPO}/{ruta}"]
    if datos is not None:
        args += ["--input", "-"]
    r = subprocess.run(args, input=json.dumps(datos) if datos is not None else None, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{metodo} {ruta}: {r.stderr or r.stdout}")
    return json.loads(r.stdout) if r.stdout.strip() else {}


def comentar(n, texto):
    api(f"issues/{n}/comments", "POST", {"body": texto})


def etiquetar(n, *et):
    api(f"issues/{n}/labels", "POST", {"labels": list(et)})


def resumen(texto):
    print(texto)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(texto + "\n")


def numero_pr():
    if os.environ.get("PR"):
        return int(os.environ["PR"])
    sha = os.environ.get("HEAD_SHA")
    if sha and EVENTO == "workflow_run":
        prs = [p for p in api(f"commits/{sha}/pulls") if p["state"] == "open"]
        return prs[0]["number"] if prs else None
    return None


def revision_ok(sha):
    runs = api(f"commits/{sha}/check-runs?per_page=100")["check_runs"]
    r = [c for c in runs if c["name"] == CHECK_REVISION]
    if not r:
        return None
    return max(r, key=lambda c: c["id"])["conclusion"]


def hay_produccion():
    return subprocess.run(["git", "ls-remote", "--exit-code", "--heads", "origin", "produccion"],
                          capture_output=True).returncode == 0


def ultimo_main_publicado():
    """El commit de main que está publicado (línea Publica-main del último commit de produccion)."""
    sh("git", "fetch", "-q", "origin", "produccion")
    origen = sello.origen_de(sh("git", "log", "-1", "--format=%B", "origin/produccion"))
    return origen or sh("git", "rev-parse", "origin/produccion")


def pedido_de_espera(motivos, desde, hasta):
    """Abre (o actualiza) el pedido que avisa a Manu que main tiene cambios de riesgo alto sin publicar."""
    texto = (f"**Espera tu aprobación.** `main` tiene cambios de riesgo alto que no se publicaron "
             f"(desde `{desde[:7]}` hasta `{hasta[:7]}`):\n" + "\n".join(f"- {m}" for m in motivos)
             + "\n\nPara aprobar: GitHub → Actions → Publicar → Run workflow, con el número vacío (publica main tal como "
             "está). Para rechazar, revertir esos commits en main o decírselo a Claude en una conversación.")
    abiertos = [i for i in api("issues?state=open&labels=espera-manu&per_page=50")
                if i.get("title") == TITULO_PEDIDO and "pull_request" not in i]
    if abiertos:
        comentar(abiertos[0]["number"], texto)
        return abiertos[0]["number"]
    nuevo = api("issues", "POST", {"title": TITULO_PEDIDO, "body": texto, "labels": ["espera-manu", "riesgo:alto"]})
    return nuevo.get("number")


def pedir_sello(arbol):
    url, tok = os.environ["ACTIONS_ID_TOKEN_REQUEST_URL"], os.environ["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]
    aud = urllib.parse.quote(sello.audiencia(REPO, arbol), safe="")
    req = urllib.request.Request(f"{url}&audience={aud}", headers={"Authorization": f"bearer {tok}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["value"]


def esperar_cloudflare(sha, minutos=8):
    fin = time.time() + minutos * 60
    while time.time() < fin:
        runs = [c for c in api(f"commits/{sha}/check-runs?per_page=100")["check_runs"] if "Workers Builds" in c["name"]]
        if runs and runs[0]["status"] == "completed":
            return runs[0]["conclusion"], runs[0].get("details_url", "")
        time.sleep(20)
    return "sin_respuesta", ""


# ---------------------------------------------------------------- controles en vivo

class _Imagenes(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img" and a.get("src") and not a["src"].startswith("data:"):
            self.urls.append(a["src"])
        if tag in ("img", "source") and a.get("srcset"):
            self.urls += [p.strip().split(" ")[0] for p in a["srcset"].split(",") if p.strip()]
        if tag == "meta" and a.get("property") == "og:image" and a.get("content"):
            self.urls.append(a["content"])
        if tag == "link" and "icon" in (a.get("rel") or "") and a.get("href") and not a["href"].startswith("data:"):
            self.urls.append(a["href"])


class _SinRedireccion(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def _pedir(url, seguir=True, metodo="GET"):
    """Devuelve (estado, encabezados, cuerpo). No levanta excepción por estados HTTP."""
    abridor = urllib.request.build_opener() if seguir else urllib.request.build_opener(_SinRedireccion)
    req = urllib.request.Request(url, method=metodo, headers={"User-Agent": "fabrica-pcs/1", "Cache-Control": "no-cache"})
    try:
        with abridor.open(req, timeout=20) as r:
            return r.status, dict(r.headers), r.read() if metodo == "GET" else b""
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), b""


def verificar_en_vivo(url, commits, minutos=3, www=True):
    """Controles después de publicar. Devuelve una lista de problemas (vacía si está todo bien).

    commits: los valores que puede traer version.json["commit"] (o ["origen"]) para esta publicación.
    """
    problemas = []
    base = url if url.endswith("/") else url + "/"
    fin, v = time.time() + minutos * 60, None
    while True:
        estado, _, cuerpo = _pedir(base + f"version.json?t={int(time.time())}")
        try:
            v = json.loads(cuerpo) if estado == 200 else None
        except ValueError:
            v = None
        if v and (v.get("commit") in commits or v.get("origen") in commits):
            break
        if time.time() > fin:
            problemas.append(f"version.json no muestra el commit publicado (muestra {v and (v.get('origen') or v.get('commit'))}).")
            break
        time.sleep(15)

    estado, _, cuerpo = _pedir(base)
    if estado != 200:
        problemas.append(f"La página responde {estado}.")
    else:
        p = _Imagenes()
        p.feed(cuerpo.decode("utf-8", "replace"))
        for img in dict.fromkeys(p.urls):
            completa = urllib.parse.urljoin(base, img)
            e, _, _ = _pedir(completa, metodo="HEAD")
            if e == 405:
                e, _, _ = _pedir(completa)
            if e != 200:
                problemas.append(f"La imagen {completa} responde {e}.")

    if www:
        dominio = urllib.parse.urlparse(base).hostname or ""
        if dominio and not dominio.startswith("www.") and "." in dominio and not dominio.endswith(".workers.dev"):
            e, cab, _ = _pedir(f"https://www.{dominio}/", seguir=False)
            destino = urllib.parse.urlparse(cab.get("Location", "") or cab.get("location", "")).hostname
            if e != 301 or destino != dominio:
                problemas.append(f"www.{dominio} responde {e} hacia {destino or 'ningún lado'} (tiene que ser 301 a {dominio}).")
    return problemas


# ---------------------------------------------------------------- recorrido

def main():
    n = numero_pr()
    if EVENTO in ("workflow_run", "pull_request_target") and n is None:
        return resumen("Sin pedido de cambio abierto para este evento. Nada que publicar.")

    sh("git", "fetch", "-q", "origin", "main")
    primera = not hay_produccion()
    if primera and not A_MANO:
        return resumen("Este sitio todavía no tiene la rama produccion. La primera publicación sellada la lanza Manu "
                       "desde Actions → Publicar → Run workflow.")
    desde = None if primera else ultimo_main_publicado()

    if n is not None:
        pr = api(f"pulls/{n}")
        etiquetas = {e["name"] for e in pr["labels"]}
        if pr["state"] != "open" or pr["base"]["ref"] != "main" or pr["head"]["repo"]["full_name"] != REPO:
            return resumen(f"El PR #{n} no está abierto contra main de este repositorio.")
        if "listo" not in etiquetas and not A_MANO:
            return resumen(f"El PR #{n} todavía no tiene la etiqueta listo del aprobador.")
        head = pr["head"]["sha"]
        estado = revision_ok(head)
        if estado != "success":
            return resumen(f"La revisión de código del PR #{n} está en {estado or 'espera'}. Se publica cuando termine en verde.")

        sh("git", "fetch", "-q", "origin", f"pull/{n}/head")
        base = sh("git", "merge-base", "origin/main", head)
        r = riesgo.evaluar(base, head)
        if r["riesgo"] == "alto" and not A_MANO:
            if "espera-manu" not in etiquetas:
                etiquetar(n, "riesgo:alto", "espera-manu")
                comentar(n, "**Espera tu aprobación.** Riesgo alto:\n" + "\n".join(f"- {m}" for m in r["motivos"])
                         + "\n\nPara aprobar: GitHub → Actions → Publicar → Run workflow, con el número de este PR.")
            return resumen(f"PR #{n}: riesgo alto, espera la aprobación de Manu.")

        # Lo que está en main y todavía no se publicó tiene que poder salir solo (o lo aprueba Manu).
        if desde and not A_MANO:
            pendiente = riesgo.evaluar(desde, "origin/main")
            if pendiente["riesgo"] == "alto":
                comentar(n, "**No se publicó:** main tiene cambios de riesgo alto sin publicar:\n"
                         + "\n".join(f"- {m}" for m in pendiente["motivos"])
                         + "\n\nManu puede publicarlos junto con este PR desde Actions → Publicar → Run workflow.")
                etiquetar(n, "necesita-manu")
                return resumen("main tiene cambios de riesgo alto sin publicar. Publicación detenida.")

        if pr.get("mergeable_state") == "dirty" or pr.get("mergeable") is False:
            if "desactualizado" not in etiquetas:
                etiquetar(n, "desactualizado")
            comentar(n, "**No se publicó:** el PR quedó desactualizado frente a `main` y tiene conflictos. "
                     "La próxima corrida de la fábrica lo pone al día y vuelve a pedir la aprobación.")
            return resumen(f"PR #{n} desactualizado frente a main. No se publicó.")

        titulo = f"{pr['title']} (#{n})"
        api(f"pulls/{n}/merge", "PUT", {"merge_method": "squash", "sha": head, "commit_title": titulo})
        sh("git", "fetch", "-q", "origin", "main")
    else:
        # Push a main (los commits del panel) o aprobación de Manu sin número.
        if desde and not A_MANO:
            r = riesgo.evaluar(desde, "origin/main")
            if r["riesgo"] == "alto":
                p = pedido_de_espera(r["motivos"], desde, sh("git", "rev-parse", "origin/main"))
                return resumen(f"main tiene cambios de riesgo alto. No se publicó; espera a Manu (pedido #{p}).")
            resumen("Riesgo bajo:\n" + "\n".join(f"- {c}" for c in r["cambios"]))
        titulo = (sh("git", "log", "-1", "--format=%s", "origin/main") if not A_MANO
                  else "Publicación de main aprobada por Manu")

    m = sh("git", "rev-parse", "origin/main")
    arbol = sh("git", "rev-parse", "origin/main^{tree}")
    padres = ["-p", m]
    if not primera:
        prod = sh("git", "rev-parse", "origin/produccion")
        if sh("git", "rev-parse", "origin/produccion^{tree}") == arbol:
            return resumen("produccion ya tiene este contenido. Nada que publicar.")
        padres = ["-p", prod, "-p", m]

    quien = "Manu (a mano)" if A_MANO else "la fábrica (riesgo bajo)"
    mensaje = (f"Publica: {titulo}\n\nAprobado por {quien}.\n\n"
               f"{sello.ORIGEN} {m}\n{sello.TRAILER} {pedir_sello(arbol)}\n")
    nuevo = subprocess.run(["git", "commit-tree", arbol, *padres, "-F", "-"], input=mensaje,
                           capture_output=True, text=True, env=dict(os.environ, **AUTOR), check=True).stdout.strip()
    sh("git", "push", "origin", f"{nuevo}:refs/heads/produccion")
    resumen(f"Sellado y enviado a produccion: {nuevo[:7]} (main {m[:7]}). Esperando a Cloudflare…")

    resultado, enlace = esperar_cloudflare(nuevo)
    problemas = []
    if resultado == "success":
        problemas = verificar_en_vivo(CONFIG["url"], {nuevo, m})
        texto = "**Publicado.** Cloudflare terminó el build sin errores." + (
            "" if not problemas else "\n\nPero los controles en vivo encontraron problemas:\n" + "\n".join(f"- {p}" for p in problemas))
    elif resultado == "sin_respuesta":
        texto = "**Enviado a Cloudflare**, pero el build no respondió en 8 minutos. Revisar Workers & Pages → Deployments."
    else:
        texto = f"**Cloudflare no publicó** (resultado: {resultado}). Queda andando la versión anterior."
    if enlace:
        texto += f" [Ver el build]({enlace})"
    resumen(texto)
    bien = resultado == "success" and not problemas
    if n is not None:
        comentar(n, texto + f"\n\nCommit en produccion: `{nuevo[:7]}`.")
        etiquetar(n, "publicado" if bien else "necesita-manu")
    elif not bien:
        api("issues", "POST", {"title": f"La publicación de {m[:7]} necesita revisión", "body": texto, "labels": ["necesita-manu"]})
    if not bien:
        sys.exit(1)


def avisar_falla(e):
    """Cualquier error inesperado queda escrito en el PR (o en un pedido), para que no falle en silencio."""
    try:
        cuerpo = (f"**No se publicó:** la publicación falló con un error inesperado:\n\n```\n{str(e)[:800]}\n```\n\n"
                  "Queda andando la versión anterior. La fábrica lo revisa en la próxima corrida.")
        n = numero_pr()
        if n is not None:
            comentar(n, cuerpo)
            etiquetar(n, "necesita-manu")
        else:
            api("issues", "POST", {"title": "La publicación del sitio falló", "body": cuerpo, "labels": ["necesita-manu"]})
    except Exception:
        pass


CONFIG = sello.leer_config() if (AQUI / "config.json").exists() else {"repo": os.environ.get("GITHUB_REPOSITORY", ""), "url": ""}
REPO = os.environ.get("GITHUB_REPOSITORY") or CONFIG["repo"]
EVENTO = os.environ.get("EVENTO", "")
A_MANO = EVENTO == "workflow_dispatch"

if __name__ == "__main__":
    if REPO != CONFIG.get("repo"):
        sys.exit(f"fabrica/config.json dice {CONFIG.get('repo')!r} y este repositorio es {REPO!r}.")
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        avisar_falla(e)
        raise
