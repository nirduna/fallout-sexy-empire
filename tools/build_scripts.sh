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
#   TEXT_ENCODING    Kodierung der Texte im Spiel (Standard WINDOWS-1252; die Spieltexte
#                    sind englisch und reines ASCII, tools/check_msg.py prueft das)
#   FO2_MAPS         Kartenordner des RPU (data/maps) mit den Vorlagen fuer die Innenkarten
#                    (Standard: $FO2_SCRIPTS_SRC/../data/maps, also ein Klon des RPU-Repositorys)
#   RL_MAP_INDEX     Nummer der Gosse in maps.txt (Standard 173 = RPU, siehe install/maps.txt.add)
#   MAP_OUT          Zielordner fuer die .map-Dateien (Standard build/maps)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
: "${SSLC:?SSLC muss auf den sslc-Compiler zeigen}"
: "${FO2_SCRIPTS_SRC:?FO2_SCRIPTS_SRC muss auf scripts_src des RPU (oder Unofficial Patch) zeigen}"
BASE="${RL_SCRIPT_BASE:-1559}"
GVAR_BASE="${RL_GVAR_BASE:-791}"
TEXT_ENCODING="${TEXT_ENCODING:-WINDOWS-1252}"
OUT="${OUT:-$ROOT/build/scripts}"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"   # absolut: sslc laeuft im Ordner der Quelle

# Vorab: stimmen Katalog und Texte mit den Skripten ueberein?
if command -v python3 > /dev/null; then
  python3 "$ROOT/tools/gen_katalog.py" > /dev/null
  if ! git -C "$ROOT" diff --quiet -- scripts_src/headers/rl_katalog.h text_src/english/dialog/_rl_module.inc 2>/dev/null; then
    echo "HINWEIS: rl_katalog.h/_rl_module.inc wurden aus tools/ausbau_sim.py neu erzeugt."
  fi
  python3 "$ROOT/tools/bau_karten.py" header > /dev/null
  if ! git -C "$ROOT" diff --quiet -- scripts_src/headers/rl_karten.h 2>/dev/null; then
    echo "HINWEIS: rl_karten.h wurde aus tools/bau_karten.py neu erzeugt."
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
# Einstellungen fuer tools/paket.py festhalten
printf 'RL_SCRIPT_BASE=%s\nRL_GVAR_BASE=%s\nRL_MAP_INDEX=%s\nRL_DEBUG=%s\nRL_SELBSTTEST=%s\n' \
  "$BASE" "$GVAR_BASE" "${RL_MAP_INDEX:-173}" "${RL_DEBUG:-0}" "${RL_SELBSTTEST:-0}" > "$OUT/rl_build.txt"

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

# Karten: Innenkarten aus den Vorlagen des RPU (die Vorlagen liegen nicht im Repository)
FO2_MAPS="${FO2_MAPS:-$FO2_SCRIPTS_SRC/../data/maps}"
MAP_OUT="${MAP_OUT:-$ROOT/build/maps}"
if [ -d "$FO2_MAPS" ] && command -v python3 > /dev/null; then
  PROTOS=()
  if [ -d "$FO2_MAPS/../proto" ]; then PROTOS=(--protos "$FO2_MAPS/../proto"); fi
  if ! python3 "$ROOT/tools/bau_karten.py" bauen --karten "$FO2_MAPS" --out "$MAP_OUT" \
         --skript-basis "$BASE" --karten-index "${RL_MAP_INDEX:-173}" ${PROTOS[@]+"${PROTOS[@]}"}; then
    echo "FEHLER Karten"
    status=1
  fi
else
  echo "HINWEIS: Karten nicht gebaut (FO2_MAPS=$FO2_MAPS fehlt oder kein python3)."
fi
exit $status
