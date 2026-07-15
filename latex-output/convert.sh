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

# The thesis docx now carries its own "List of References" section, so the
# scaffold is OFF by default; pass --add-references to append it anyway.
INCLUDE_REFS=0
SRC=""
for arg in "$@"; do
  case "$arg" in
    --add-references) INCLUDE_REFS=1 ;;
    --no-references)  INCLUDE_REFS=0 ;;
    *) SRC="$arg" ;;
  esac
done

# With no argument, build from the manuscript committed to the repo. This is
# what makes the build reproducible: clone, run ./convert.sh, get this PDF.
if [[ -z "$SRC" ]]; then
  SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/source/thesis.docx"
fi
if [[ ! -f "$SRC" ]]; then
  echo "error: no such file: $SRC" >&2
  echo "usage: ./convert.sh [path/to/file.docx] [--add-references]" >&2
  echo "       (with no path, builds from source/thesis.docx)" >&2
  exit 1
fi
SRC="$(cd "$(dirname "$SRC")" && pwd)/$(basename "$SRC")"  # absolute path

for tool in pandoc python3 pdflatex; do
  command -v "$tool" >/dev/null 2>&1 || { echo "error: '$tool' not found on PATH" >&2; exit 1; }
done

cd "$HERE"

# Compile any TikZ diagrams whose PDF is missing or stale, so postprocess can
# slot them in where Pandoc dropped the native Word drawings.
if compgen -G "diagrams/*.tex" >/dev/null; then
  echo ">> Building diagrams ..."
  for d in diagrams/figure-*.tex; do
    pdf="${d%.tex}.pdf"
    if [[ ! -f "$pdf" || "$d" -nt "$pdf" || diagrams/flowstyles.tex -nt "$pdf" ]]; then
      (cd diagrams && pdflatex -interaction=nonstopmode "$(basename "$d")" >/dev/null) \
        || { echo "error: diagram $d failed to compile" >&2; exit 1; }
    fi
  done
  rm -f diagrams/*.aux diagrams/*.log
fi

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

echo ">> Compiling (three passes for TOC / List of Figures / List of Tables) ..."
pdflatex -interaction=nonstopmode document.tex >/dev/null
pdflatex -interaction=nonstopmode document.tex >/dev/null
pdflatex -interaction=nonstopmode document.tex >/dev/null

# Keep .toc/.lof/.lot so manual re-runs of pdflatex stay correct; drop the rest
rm -f document.log document.out

pages="$(command -v pdfinfo >/dev/null 2>&1 && pdfinfo document.pdf 2>/dev/null | awk '/Pages/{print $2}')"
echo ">> Done: document.pdf${pages:+ ($pages pages)}"
