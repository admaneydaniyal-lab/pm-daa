#!/usr/bin/env bash
# ============================================================================
# One-command DOCX -> LaTeX/PDF pipeline for this thesis.
#
#   ./convert.sh path/to/new_version.docx [--no-references]
#
# It regenerates document.tex (and the media/ images) from the given .docx and
# compiles document.pdf, re-applying all the project's formatting automatically:
#   * wider margins, capped images, dense-table handling, Unicode symbols
#     (via pandoc/preamble.tex)
#   * plots shrunk/centred, screenshots kept full width, wide tables set to
#     \footnotesize (via postprocess.py, driven by the real content)
#   * an APA-7 References section appended (via pandoc/references.tex), unless
#     --no-references is passed
#
# NOTE: this overwrites document.tex and the media/ folder in this directory.
# ============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INCLUDE_REFS=1
SRC=""
for arg in "$@"; do
  case "$arg" in
    --no-references) INCLUDE_REFS=0 ;;
    *) SRC="$arg" ;;
  esac
done

if [[ -z "$SRC" ]]; then
  echo "usage: ./convert.sh path/to/file.docx [--no-references]" >&2
  exit 1
fi
if [[ ! -f "$SRC" ]]; then
  echo "error: no such file: $SRC" >&2
  exit 1
fi
SRC="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"  # absolute path

for tool in pandoc python3 pdflatex; do
  command -v "$tool" >/dev/null 2>&1 || { echo "error: '$tool' not found on PATH" >&2; exit 1; }
done

cd "$HERE"

echo ">> Converting $SRC with Pandoc ..."
PANDOC_ARGS=(
  "$SRC"
  --standalone
  --wrap=preserve
  --extract-media=media
  -H pandoc/preamble.tex
  -o document.tex
)
if [[ "$INCLUDE_REFS" -eq 1 ]]; then
  PANDOC_ARGS+=(-A pandoc/references.tex)
fi
pandoc "${PANDOC_ARGS[@]}"

echo ">> Post-processing (image sizing, wide-table handling) ..."
python3 postprocess.py document.tex

echo ">> Compiling (two passes for TOC/links) ..."
pdflatex -interaction=nonstopmode document.tex >/dev/null
pdflatex -interaction=nonstopmode document.tex >/dev/null

# Clean LaTeX aux files, keep .tex/.pdf/media
rm -f document.aux document.log document.out document.toc document.lof document.lot

pages="$(command -v pdfinfo >/dev/null 2>&1 && pdfinfo document.pdf 2>/dev/null | awk '/Pages/{print $2}')"
echo ">> Done: document.pdf${pages:+ ($pages pages)}"
