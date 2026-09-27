#!/usr/bin/env bash
# Kompiliert die Rotlicht-Skripte mit sslc (sfall edition).
#
# Benoetigt:
#   SSLC             Pfad zum sslc-Compiler (sfall edition 4.5 oder neuer)
#   FO2_SCRIPTS_SRC  Pfad zu scripts_src des Fallout 2 Unofficial Patch
#                    (mit headers/ und den sfall-Headern in sfall/)
# Optional:
#   RL_SCRIPT_BASE   Index des ersten Rotlicht-Skripts in scripts.lst
#                    (Zeilenzahl der scripts.lst + 1; Standard 1309 = Unofficial Patch)
#   RL_SELBSTTEST=1  baut gl_rotlicht mit Selbsttest
#   RL_DEBUG=1       baut Debug-Optionen ein (z. B. Haus sofort uebernehmen)
#   OUT              Zielordner fuer die .int-Dateien (Standard build/scripts)
#   TEXT_OUT         Zielordner fuer die .msg-Dateien (Standard build/text)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
: "${SSLC:?SSLC muss auf den sslc-Compiler zeigen}"
: "${FO2_SCRIPTS_SRC:?FO2_SCRIPTS_SRC muss auf scripts_src des Unofficial Patch zeigen}"
BASE="${RL_SCRIPT_BASE:-1309}"
OUT="${OUT:-$ROOT/build/scripts}"
mkdir -p "$OUT"

FLAGS=(-q -l -p -O2 -I"$FO2_SCRIPTS_SRC/headers" -I"$ROOT/scripts_src/headers" "-mRL_SCRIPT_BASE=$BASE")
if [ "${RL_SELBSTTEST:-0}" = "1" ]; then
  FLAGS+=("-mRL_SELBSTTEST")
fi
if [ "${RL_DEBUG:-0}" = "1" ]; then
  FLAGS+=("-mRL_DEBUG")
fi

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
done < <(find "$ROOT/scripts_src" -name '*.ssl' | sort)

# Texte: UTF-8-Quellen nach Windows-1252 (Kodierung der deutschen Fallout-2-Schrift)
TEXT_OUT="${TEXT_OUT:-$ROOT/build/text}"
while IFS= read -r msg; do
  rel="${msg#$ROOT/text_src/}"
  mkdir -p "$TEXT_OUT/$(dirname "$rel")"
  if iconv -f UTF-8 -t WINDOWS-1252 "$msg" > "$TEXT_OUT/$rel"; then
    echo "OK    $rel"
  else
    echo "FEHLER $rel (Zeichen ausserhalb von Windows-1252?)"
    status=1
  fi
done < <(find "$ROOT/text_src" -name '*.msg' | sort)
exit $status
