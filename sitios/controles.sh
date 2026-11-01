#!/usr/bin/env bash
# Controles de código de la Fábrica de presencia, sobre la carpeta de un repositorio sitio-*.
# Los corren revision.yml (cada PR) y publicar.yml (cada push a main, antes de sellar), y se pueden correr a mano.
#
# Uso, desde la raíz del sitio: bash fabrica/controles.sh RUTA_A_HERRAMIENTAS [CARPETA_DE_CAPTURAS]
#
# 1. La copia de fabrica/ y de los flujos es igual a la original de herramientas (instalar.py --verificar).
# 2. build.py arma dist/ sin errores.
# 3. wrangler deploy --dry-run sin errores.
# 4. revisar.py --perfil sitio sobre dist/ (idioma y URL de .reglas.json): sin FALLA.
# 5. navegador.py sobre dist/ a 390 y 1360 px: sin FALLA. Deja las capturas para el revisor visual.
#
# El original vive en pcsoluciones-arg/herramientas (sitios/); instalar.py lo copia a fabrica/ de cada sitio.
set -uo pipefail
HERR="${1:?Falta la ruta a herramientas}"
CAPTURAS="${2:-/tmp/capturas}"
fallas=0
paso() { echo; echo "== $1"; }

paso "Copia de la fábrica igual a la original"
python3 "$HERR/sitios/instalar.py" --verificar . || fallas=1

paso "Armar el sitio (build.py)"
python3 build.py || { echo "FALLA: build.py"; exit 1; }

paso "Simular la publicación (wrangler --dry-run)"
npx -y wrangler@4 deploy --dry-run --outdir /tmp/dry > /tmp/wrangler-dry.log 2>&1 || { tail -30 /tmp/wrangler-dry.log; echo "FALLA: wrangler"; fallas=1; }

paso "Reglas de escritura y de método (revisar.py)"
python3 "$HERR/revisar.py" --perfil sitio dist/ || fallas=1

paso "Navegador a 390 y 1360 px (navegador.py)"
python3 "$HERR/sitios/navegador.py" dist/ --capturas "$CAPTURAS" || fallas=1

echo
[ $fallas -eq 0 ] && echo "Controles del sitio: todo en verde." || echo "Controles del sitio: hay fallas."
exit $fallas
