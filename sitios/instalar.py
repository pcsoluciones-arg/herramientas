#!/usr/bin/env python3
"""Instala (o verifica) la Fábrica de presencia en un repositorio sitio-*.

El código de la fábrica vive una sola vez, acá en herramientas/sitios/. Este script lo copia al sitio:

    sitios/sello.py, riesgo_sitio.py, publicar_sitio.py,
    controles.sh y LEEME-fabrica.md               ->  fabrica/  (el LEEME queda como fabrica/LEEME.md)
    sitios/flujos/publicar.yml y revision.yml     ->  .github/workflows/

Va copiado y no referenciado porque build.py verifica el sello en Cloudflare sin acceso a otro repositorio, y porque
publicar.yml ejecuta la versión que ya pasó por la aprobación del sitio. La revisión de cada PR corre
`instalar.py --verificar` y corta si la copia no es igual a la original: para cambiar la fábrica se cambia acá y se
vuelve a instalar en cada sitio (riesgo alto: lo aprueba Manu).

También crea fabrica/config.json si no existe (no lo pisa): el repositorio y el flujo del sello, la URL del sitio y
el Worker. Lo que no se pasa por opción se toma de git, secciones.json y wrangler.toml.

Uso:
    python3 sitios/instalar.py RUTA_DEL_SITIO [--repo cuenta/nombre] [--url https://...] [--worker nombre]
    python3 sitios/instalar.py --verificar RUTA_DEL_SITIO

No toca build.py: el cambio para que verifique el sello y escriba el commit de origen en version.json se hace en el
PR del sitio (ver sitios/LEEME.md, "Instalar en un sitio nuevo").
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import sello  # noqa: E402

COPIAS = [
    ("sello.py", "fabrica/sello.py"),
    ("riesgo_sitio.py", "fabrica/riesgo_sitio.py"),
    ("publicar_sitio.py", "fabrica/publicar_sitio.py"),
    ("controles.sh", "fabrica/controles.sh"),
    ("LEEME-fabrica.md", "fabrica/LEEME.md"),
    ("flujos/publicar.yml", ".github/workflows/publicar.yml"),
    ("flujos/revision.yml", ".github/workflows/revision.yml"),
]


def diferencias(sitio):
    """Lista de (copia, motivo) para cada archivo que no es igual al original."""
    malas = []
    for origen, destino in COPIAS:
        d = sitio / destino
        if not d.exists():
            malas.append((destino, "falta"))
        elif d.read_bytes() != (AQUI / origen).read_bytes():
            malas.append((destino, f"distinta de herramientas/sitios/{origen}"))
    return malas


def repo_de_git(sitio):
    r = subprocess.run(["git", "-C", str(sitio), "remote", "get-url", "origin"], capture_output=True, text=True)
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+?)(?:\.git)?/?$", r.stdout.strip())
    return m.group(1) if m else None


def config_por_defecto(sitio, repo=None, url=None, worker=None):
    if not url:
        try:
            url = json.loads((sitio / "secciones.json").read_text(encoding="utf-8"))["sitio"]["url"]
        except Exception:
            url = None
    if not worker:
        m = re.search(r'(?m)^name\s*=\s*"([^"]+)"', (sitio / "wrangler.toml").read_text(encoding="utf-8")) \
            if (sitio / "wrangler.toml").exists() else None
        worker = m.group(1) if m else None
    c = {"formato": "fabrica-sitio/v1",
         "_nota": "Lo lee la fábrica (sello, publicación). Cambiarlo es de riesgo alto: lo aprueba Manu.",
         "repo": repo or repo_de_git(sitio), "flujo": "publicar.yml", "url": url, "worker": worker}
    faltan = [k for k in ("repo", "url", "worker") if not c[k]]
    if faltan:
        sys.exit("No se pudo averiguar " + ", ".join(faltan) + ": pasarlo con --" + " --".join(faltan) + ".")
    if not c["url"].endswith("/"):
        c["url"] += "/"
    return c


def verificar(sitio):
    malas = diferencias(sitio)
    for destino, motivo in malas:
        print(f"FALLA {destino}: {motivo}. Volver a instalar desde herramientas (python3 sitios/instalar.py .).")
    try:
        c = sello.leer_config(sitio / "fabrica/config.json")
        git = repo_de_git(sitio)
        if git and git != c["repo"]:
            print(f"FALLA fabrica/config.json: dice {c['repo']} y el repositorio es {git}.")
            malas.append(("fabrica/config.json", "repo"))
        for k in ("url", "worker"):
            if not c.get(k):
                print(f"FALLA fabrica/config.json: falta \"{k}\".")
                malas.append(("fabrica/config.json", k))
    except Exception as e:
        print(f"FALLA fabrica/config.json: {e}")
        malas.append(("fabrica/config.json", str(e)))
    if not malas:
        print(f"La fábrica de {sitio.name} es igual a la de herramientas ({len(COPIAS)} archivos) y config.json está bien.")
    return not malas


def instalar(sitio, repo, url, worker):
    for origen, destino in COPIAS:
        d = sitio / destino
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(AQUI / origen, d)
        if destino.endswith(".sh"):
            d.chmod(0o755)
        print("copiado", destino)
    cfg = sitio / "fabrica/config.json"
    if cfg.exists():
        print("fabrica/config.json ya existe: no se toca.")
    else:
        cfg.write_text(json.dumps(config_por_defecto(sitio, repo, url, worker), ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print("creado fabrica/config.json")
    return verificar(sitio)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Instala o verifica la Fábrica de presencia en un repositorio sitio-*.")
    ap.add_argument("sitio")
    ap.add_argument("--verificar", action="store_true", help="solo compara la copia con la original")
    ap.add_argument("--repo")
    ap.add_argument("--url")
    ap.add_argument("--worker")
    a = ap.parse_args()
    sitio = pathlib.Path(a.sitio).resolve()
    if not (sitio / "build.py").exists():
        sys.exit(f"{sitio} no parece un repositorio de sitio (falta build.py).")
    ok = verificar(sitio) if a.verificar else instalar(sitio, a.repo, a.url, a.worker)
    sys.exit(0 if ok else 1)
