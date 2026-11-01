#!/usr/bin/env python3
"""Sello de publicación de la Fábrica de presencia (repositorios sitio-*).

Es el mismo sello que usa el panel (panel-prospector/fabrica/sello.py), con el repositorio y el flujo tomados de
fabrica/config.json en vez de fijos en el código. El original vive en pcsoluciones-arg/herramientas, en sitios/, e
instalar.py lo copia a fabrica/ de cada sitio: build.py lo usa en Cloudflare sin depender de otro repositorio.

Cómo funciona:
- Cloudflare publica la rama `produccion`. Cada commit de esa rama lo crea el flujo publicar.yml de GitHub Actions
  (rama main) y lleva en el mensaje la línea `Sello-fabrica: <token>` y la línea `Publica-main: <commit de main>`.
- El token es un certificado OIDC que emite GitHub: dice qué repositorio y qué flujo lo pidió, y su audiencia es el
  árbol del commit (su contenido exacto). GitHub lo firma con sus claves.
- Antes de publicar, build.py llama a verificar_head(): baja las claves públicas de GitHub y revisa la firma, el
  emisor, el repositorio, el flujo y que la audiencia corresponda a este árbol. Si algo no coincide, el build corta
  y queda andando la versión anterior.

El sello frena errores (un commit que llega a produccion sin pasar por la fábrica). No frena a alguien con permiso
de escritura que quiera saltearlo, porque build.py está dentro del mismo árbol.

Uso:
    python3 fabrica/sello.py audiencia ARBOL     # la audiencia que pide publicar.yml
    python3 fabrica/sello.py verificar           # verifica el commit HEAD
    python3 fabrica/sello.py origen              # el commit de main que publicó HEAD (Publica-main)

Solo biblioteca estándar de Python: corre igual en GitHub Actions, en Cloudflare y en cualquier computadora.
"""
import base64
import hashlib
import json
import pathlib
import subprocess
import sys
import urllib.request

EMISOR = "https://token.actions.githubusercontent.com"
CLAVES_URL = EMISOR + "/.well-known/jwks"
# Solo se aceptan sellos de repositorios de esta cuenta. config.json está dentro del árbol sellado y cambiarlo es de
# riesgo alto, pero este límite queda fijo en el código.
DUENO = "pcsoluciones-arg"
TRAILER = "Sello-fabrica:"
ORIGEN = "Publica-main:"
CONFIG = pathlib.Path(__file__).resolve().parent / "config.json"
# DigestInfo de SHA-256 para RSASSA-PKCS1-v1_5 (RFC 8017, sección 9.2)
_SHA256_INFO = bytes.fromhex("3031300d060960864801650304020105000420")


def leer_config(ruta=CONFIG):
    """Devuelve el config.json del sitio. Tiene que traer "repo" (cuenta/nombre) de esta cuenta."""
    with open(ruta, encoding="utf-8") as f:
        c = json.load(f)
    repo = c.get("repo", "")
    if not repo.startswith(DUENO + "/") or repo.count("/") != 1:
        raise ValueError(f"config.json: \"repo\" tiene que ser {DUENO}/<nombre> (dice {repo!r}).")
    return c


def flujo_de(config):
    """job_workflow_ref que tiene que traer el sello: publicar.yml de la rama main del repositorio del sitio."""
    archivo = config.get("flujo", "publicar.yml")
    return f"{config['repo']}/.github/workflows/{archivo}@refs/heads/main"


def audiencia(repo, arbol):
    return f"{repo.split('/', 1)[1]}:sello:{arbol}"


def _b64(t):
    return base64.urlsafe_b64decode(t + "=" * (-len(t) % 4))


def _rsa_ok(clave, datos, firma):
    n = int.from_bytes(_b64(clave["n"]), "big")
    e = int.from_bytes(_b64(clave["e"]), "big")
    k = (n.bit_length() + 7) // 8
    if len(firma) != k:
        return False
    em = pow(int.from_bytes(firma, "big"), e, n).to_bytes(k, "big")
    t = _SHA256_INFO + hashlib.sha256(datos).digest()
    return em == b"\x00\x01" + b"\xff" * (k - len(t) - 3) + b"\x00" + t


def bajar_claves():
    with urllib.request.urlopen(CLAVES_URL, timeout=20) as r:
        return json.load(r)["keys"]


def verificar_token(token, arbol, claves, config):
    """Devuelve (ok, motivo). No mira el vencimiento: el sello vale para siempre para ese contenido."""
    repo, flujo = config["repo"], flujo_de(config)
    try:
        cab_b, cuerpo_b, firma_b = token.strip().split(".")
        cab, datos = json.loads(_b64(cab_b)), json.loads(_b64(cuerpo_b))
    except Exception:
        return False, "El sello no tiene el formato de un certificado de GitHub."
    if cab.get("alg") != "RS256":
        return False, "El sello no usa la firma esperada (RS256)."
    clave = next((c for c in claves if c.get("kid") == cab.get("kid")), None)
    if not clave:
        return False, "La clave del sello no está entre las de GitHub."
    if not _rsa_ok(clave, f"{cab_b}.{cuerpo_b}".encode(), _b64(firma_b)):
        return False, "La firma del sello no es válida."
    aud = datos.get("aud")
    if datos.get("iss") != EMISOR:
        return False, "El sello no lo emitió GitHub Actions."
    if datos.get("repository_owner") not in (None, DUENO) or not str(datos.get("repository", "")).startswith(DUENO + "/"):
        return False, f"El sello es de un repositorio de otra cuenta ({datos.get('repository')})."
    if datos.get("repository") != repo:
        return False, f"El sello es de otro repositorio ({datos.get('repository')})."
    if datos.get("job_workflow_ref") != flujo:
        return False, f"El sello no salió de publicar.yml en main ({datos.get('job_workflow_ref')})."
    if (aud if isinstance(aud, list) else [aud]) != [audiencia(repo, arbol)]:
        return False, "El sello corresponde a otro contenido."
    return True, f"Sello válido (publicar.yml, corrida {datos.get('run_id')}, pedida por {datos.get('actor')})."


def linea(texto_commit, prefijo):
    lineas = [l for l in texto_commit.splitlines() if l.startswith(prefijo)]
    return lineas[-1][len(prefijo):].strip() if lineas else None


def sello_de(texto_commit):
    return linea(texto_commit, TRAILER)


def origen_de(texto_commit):
    """El commit de main que publicó un commit de produccion. build.py lo escribe en version.json."""
    return linea(texto_commit, ORIGEN)


def _git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout.strip()


def origen_head():
    try:
        return origen_de(_git("log", "-1", "--format=%B"))
    except Exception:
        return None


def verificar_head(config_ruta=CONFIG):
    try:
        config = leer_config(config_ruta)
    except Exception as e:
        return False, f"No se pudo leer fabrica/config.json ({e})."
    try:
        arbol, texto = _git("rev-parse", "HEAD^{tree}"), _git("log", "-1", "--format=%B")
    except Exception as e:
        return False, f"No se pudo leer el commit con git ({e})."
    token = sello_de(texto)
    if not token:
        return False, "El commit no tiene sello de la fábrica."
    try:
        claves = bajar_claves()
    except Exception as e:
        return False, f"No se pudieron bajar las claves de GitHub ({e}). Reintentar el build."
    return verificar_token(token, arbol, claves, config)


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else ""
    if accion == "audiencia" and len(sys.argv) == 3:
        print(audiencia(leer_config()["repo"], sys.argv[2]))
    elif accion == "verificar":
        ok, motivo = verificar_head()
        print(motivo)
        sys.exit(0 if ok else 1)
    elif accion == "origen":
        print(origen_head() or "")
    else:
        sys.exit(__doc__)
