# Thesis: DOCX → LaTeX pipeline

`document.tex` is generated from the Word manuscript by a one-command pipeline,
with images and tables preserved and the project's formatting re-applied
automatically. You never have to redo images or tables when the content changes
— just re-run the pipeline on the new `.docx`.

## Regenerate from an updated .docx

```sh
./convert.sh path/to/new_version.docx
```

That single command:
1. **Converts** the `.docx` with Pandoc — extracting all images to `media/` and
   turning every table into a LaTeX `longtable`.
2. **Re-applies the formatting** (see below).
3. **Compiles** `document.pdf` (two pdfLaTeX passes for the TOC and links).

The thesis docx now carries its own "List of References" section, so the
appended scaffold is off by default (pass `--add-references` to restore it).

> Running `convert.sh` overwrites `document.tex` and the `media/` folder — they
> are build outputs. Put manual formatting changes in `pandoc/preamble.tex`, not
> in the generated `document.tex`, or they'll be lost on the next run.

## What the pipeline fixes automatically

| Fix | Where | Notes |
|-----|-------|-------|
| Wider margins, dense-table spacing, Unicode math/Greek (√ α Σ μ × − …) | `pandoc/preamble.tex` | Injected into every conversion via `pandoc -H` |
| Images never overflow the margins | `pandoc/preamble.tex` + `postprocess.py` | `adjustbox` safety net + explicit per-image sizing |
| Plots shrunk & centred; screenshots kept full width | `postprocess.py` | Decided by pixel width (< 900px ⇒ plot). No manual tagging |
| Wide tables (6+ cols → `\footnotesize`, 10+ cols → `\scriptsize`) with **content-proportional column widths** | `postprocess.py` | Each column gets width in proportion to its longest cell |
| **TikZ flowcharts auto-inserted** where Word drawings were dropped | `diagrams/` + `postprocess.py` | Any `diagrams/figure-X.Y.pdf` slots in above the matching "Figure X.Y" caption; diagrams recompile automatically when their `.tex` changes |
| **List of Figures / List of Tables** generated from the captions | `postprocess.py` | Replaces the docx placeholder section, with page numbers |
| **List of Abbreviations** injected | `pandoc/abbreviations.tex` | Edit that file to add/remove entries |
| **References** formatted with APA-7 hanging indent | `postprocess.py` | Formats the docx's own "List of References" section |
| **Appendix PDFs attached** | `appendix/` + `postprocess.py` | Each "[add PDF]" marker becomes `\includepdf` of `appendix/appendix-<letter>.pdf`; a visible placeholder note appears until the file exists |
| Long URLs/DOIs break across lines | `postprocess.py` | Converts Word's underlined self-links to `\url{}` |

## Files

- `convert.sh` — the pipeline entry point
- `pandoc/preamble.tex` — LaTeX injected into every conversion (edit this to
  change global formatting)
- `pandoc/references.tex` — the References scaffold appended at the end
- `postprocess.py` — content-driven image sizing and wide-table handling
- `document.tex` — generated LaTeX (overwritten by `convert.sh`)
- `media/media/` — images extracted from the `.docx`

## Adding references

Paste each reference as its own paragraph inside the `\begingroup … \endgroup`
block in `pandoc/references.tex` (APA-7, hanging indent). They'll appear at the
end of the document on the next `convert.sh` run. To keep references in the
generated file only, you can instead edit that block directly in `document.tex`.

## Requirements

`pandoc`, `python3`, and a TeX Live install with `pdflatex` (packages:
`geometry`, `adjustbox`, `newunicodechar`, `booktabs`, `longtable`, `lmodern`,
`soul`). On Debian/Ubuntu:

```sh
sudo apt-get install pandoc texlive-latex-recommended texlive-latex-extra \
     texlive-fonts-recommended lmodern
```

## Manual touch-ups

The pipeline handles the common cases. A table with genuinely pathological
proportions (many wide columns that can't all fit even at `\footnotesize`) may
still need a manual width nudge in `document.tex`; that's the only case that
isn't fully automatic.
