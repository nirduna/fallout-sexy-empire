#!/usr/bin/env bash
# Kompiliert die Rotlicht-Skripte mit sslc (sfall edition).
#
# Benoetigt:
#   SSLC             Pfad zum sslc-Compiler (sfall edition 4.5 oder neuer)
#   FO2_SCRIPTS_SRC  Pfad zu scripts_src des Restoration Project (RPU) oder des
#                    Unofficial Patch (mit headers/ und den sfall-Headern in sfall/)
# Optional:
#   RL_SCRIPT_BASE   Index des ersten Rotlicht-Skripts in scripts.lst
#                    (Zeilenzahl der scripts.lst + 1; Standard 1559 = RPU, Unofficial Patch: 1309)
#   RL_GVAR_BASE     erste neue GVAR (Anzahl der GVARs in vault13.gam; Standard 791 = RPU,
#                    Unofficial Patch: 696)
#   RL_SELBSTTEST=1  baut gl_rotlicht mit Selbsttest
#   RL_DEBUG=1       baut Debug-Optionen ein (z. B. Haus sofort uebernehmen)
#   OUT              Zielordner fuer die .int-Dateien (Standard build/scripts)
#   TEXT_OUT         Zielordner fuer die .msg-Dateien (Standard build/text)
#   TEXT_ENCODING    Kodierung der Texte im Spiel (Standard WINDOWS-1252, siehe Phase 5)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
: "${SSLC:?SSLC muss auf den sslc-Compiler zeigen}"
: "${FO2_SCRIPTS_SRC:?FO2_SCRIPTS_SRC muss auf scripts_src des RPU (oder Unofficial Patch) zeigen}"
BASE="${RL_SCRIPT_BASE:-1559}"
GVAR_BASE="${RL_GVAR_BASE:-791}"
TEXT_ENCODING="${TEXT_ENCODING:-WINDOWS-1252}"
OUT="${OUT:-$ROOT/build/scripts}"
mkdir -p "$OUT"

# Vorab: stimmen Katalog und Texte mit den Skripten ueberein?
if command -v python3 > /dev/null; then
  python3 "$ROOT/tools/gen_katalog.py" > /dev/null
  if ! git -C "$ROOT" diff --quiet -- scripts_src/headers/rl_katalog.h text_src/german/dialog/_rl_module.inc 2>/dev/null; then
    echo "HINWEIS: rl_katalog.h/_rl_module.inc wurden aus tools/ausbau_sim.py neu erzeugt."
  fi
  python3 "$ROOT/tools/check_msg.py" || { echo "FEHLER: Texte passen nicht zu den Skripten"; exit 1; }
fi

# sslc wertet nur EINEN -m-Schalter und nur EINEN -I-Pfad aus. Deshalb
# kompilieren wir eine Kopie von scripts_src und schreiben die Einstellungen
# in deren config/rl_build.h. Der einzige -I-Pfad sind die Header der Basis.
GEN="$(mktemp -d)"
trap 'rm -rf "$GEN"' EXIT
cp -r "$ROOT/scripts_src" "$GEN/"
{
  echo "#define RL_SCRIPT_BASE ($BASE)"
  echo "#define RL_GVAR_BASE ($GVAR_BASE)"
  if [ "${RL_SELBSTTEST:-0}" = "1" ]; then echo "#define RL_SELBSTTEST"; fi
  if [ "${RL_DEBUG:-0}" = "1" ]; then echo "#define RL_DEBUG"; fi
} > "$GEN/scripts_src/config/rl_build.h"
echo "Build: RL_SCRIPT_BASE=$BASE RL_GVAR_BASE=$GVAR_BASE SELBSTTEST=${RL_SELBSTTEST:-0} DEBUG=${RL_DEBUG:-0}"

FLAGS=(-q -l -p -O2 -I"$FO2_SCRIPTS_SRC/headers")

status=0
while IFS= read -r src; do
  name="$(basename "$src" .ssl)"
  # sslc loest #include relativ zum Arbeitsverzeichnis der Quelle auf
  if (cd "$(dirname "$src")" && "$SSLC" "${FLAGS[@]}" "$(basename "$src")" -o "$OUT/$name.int"); then
    echo "OK    $name.int"
  else
    echo "FEHLER $src"
    status=1
  fi
done < <(find "$GEN/scripts_src" -name '*.ssl' | sort)

# Texte: UTF-8-Quellen in die Kodierung der Installation (Standard Windows-1252)
TEXT_OUT="${TEXT_OUT:-$ROOT/build/text}"
while IFS= read -r msg; do
  rel="${msg#$ROOT/text_src/}"
  mkdir -p "$TEXT_OUT/$(dirname "$rel")"
  # Zeilen "# @include datei" durch den Inhalt der Datei ersetzen (gemeinsame Texte)
  if awk -v dir="$(dirname "$msg")" '
        /^# @include / { f = dir "/" $3; while ((getline l < f) > 0) print l; close(f); next }
        { print }' "$msg" | iconv -f UTF-8 -t "$TEXT_ENCODING" > "$TEXT_OUT/$rel"; then
    echo "OK    $rel"
  else
    echo "FEHLER $rel (Zeichen ausserhalb von $TEXT_ENCODING?)"
    status=1
  fi
done < <(find "$ROOT/text_src" -type f ! -name '*.inc' | sort)   # .msg, cuts/*.txt, *.add
exit $status
