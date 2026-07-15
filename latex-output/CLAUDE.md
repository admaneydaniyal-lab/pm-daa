# Thesis build — rules & state (read me first)

This directory builds the master's thesis PDF from a Word manuscript with a
**one-command, fully reproducible pipeline**. If you are picking this up in a
fresh session, everything you need is here and committed to the repo.

## The one command

```sh
cd latex-output
./convert.sh
```

With no argument it builds from the committed manuscript `source/thesis.docx`
and writes `document.pdf` (currently **133 pages**). Clone the repo, run that
command, and you get the exact same PDF — nothing is kept only in a chat
session. Pass a path to build a different docx: `./convert.sh some.docx`.

Toolchain: `pandoc`, `python3`, and TeX Live with `pdflatex` (+ `pdfpages`,
`pdflscape`, `adjustbox`, `booktabs`, `longtable`, `lmodern`, `soul`). See
`README.md` for the exact apt packages. On Debian/Ubuntu:

```sh
sudo apt-get install -y pandoc texlive-latex-recommended texlive-latex-extra \
     texlive-fonts-recommended texlive-pictures texlive-science lmodern \
     poppler-utils
```

## How to update the thesis

1. Replace `source/thesis.docx` with the new Word export (keep the same name).
2. Run `./convert.sh`.
3. Review `document.pdf`.

**Never hand-edit `document.tex`** — it is regenerated on every run and your
edits will be lost. All formatting lives in `postprocess.py` and
`pandoc/preamble.tex`. If the new docx needs a new fix, add it to
`postprocess.py` so it stays reproducible.

## Source of truth & build outputs

| Path | Role |
|------|------|
| `source/thesis.docx` | **The manuscript.** Source of truth for all prose, tables, and images. |
| `assets/` | Files supplied outside the docx (logo, figures added in LaTeX). Committed. |
| `appendix/appendix-<LETTER>.pdf` | Appendix PDFs attached via `\includepdf` (H, I, M). |
| `diagrams/*.tex` | Hand-drawn TikZ recreations of Word drawings; compiled to `.pdf` and slotted in. |
| `pandoc/preamble.tex` | LaTeX injected into every conversion (global formatting). |
| `pandoc/abbreviations.tex` | List of Abbreviations table (edit to add entries). |
| `postprocess.py` | All content-driven fixes (see below). |
| `document.tex`, `document.pdf`, `media/` | **Build outputs** — regenerated, do not edit by hand. |

## What `postprocess.py` does (the finalization rules)

The docx now carries its own front matter (title page, Acknowledgements,
Abstract, a static Word TOC) and its own back matter, so postprocess **re-styles
what the author supplied** rather than synthesising it. Key steps, in order:

- **Front matter** (`restructure_front_matter`): wraps the docx's own title-page
  block in a centred `titlepage` (logo scaled to 40%, thesis title enlarged with
  space above/below); replaces Word's static TOC with a live `\tableofcontents`;
  roman page numbers for the front matter, arabic restarting at the
  Introduction; removes the `[added in Latex]` placeholders and the empty
  trailing section.
- **Caption bold** (`normalize_caption_bold`): restricts caption bold to just
  the `Figure X.Y` / `Table X.Y` label (Word sometimes bolds the whole prefix or
  breaks mid-word).
- **Appendix L** (`format_appendix_l`): rebuilds every Appendix L screenshot as a
  centred `figure[H]` with the caption **underneath**, a List-of-Figures entry,
  and breathing room between figures. Figure L.1 (tall portrait) is scaled down
  so it and L.2 share a page. Per-figure sizes live in `_APPENDIX_L_SIZE` /
  `_APPENDIX_L_DEFAULT`.
- **Back-matter headings** (`sectionize_backmatter`): promotes the four bold
  paragraphs the docx leaves flat — Appendix L, Appendix M, "Information on the
  use of AI-based tools", and "Declaration" — to real `\subsection`s so each
  starts on its own page and gets a ToC entry (matching Appendices A–K). Also
  pushes the Declaration signature (name + date) to the foot of its page.
- **Figure 3.18** (`insert_figure_318`): inserts `assets/figure-3.18.png` with a
  fixed caption after the "…visibility of system status (Nielsen, 1994)."
  paragraph. The docx references Figure 3.18 but omits the image. **No-ops until
  the asset exists** (see Pending below).
- **Appendix PDFs** (`attach_appendix_pdfs`): replaces `[add PDF]`/`[add pdf]`
  markers with `\includepdf` of `appendix/appendix-<LETTER>.pdf` (letter from the
  nearest "Appendix X" heading). Missing files leave a visible placeholder note.
- Plus: image sizing (plots shrunk/centred, screenshots capped), wide-table
  handling, TikZ diagram insertion, List of Figures/Tables generation, APA-7
  reference hanging indent, Appendix K table restructure, and more. Each step
  prints a status line when `convert.sh` runs — check them after every build.

## Assets & their status

- `assets/hsrw-logo.png` — present (not currently used; the docx embeds the logo).
- `appendix/appendix-M.pdf` — present (Study & Project Details template).
- `assets/figure-3.18.png` — **MISSING**. Drop the successful-validation
  screenshot here and re-run `convert.sh`; it slots in automatically with the
  correct caption.

## Pending

- **Figure 3.18 image.** The manuscript references "Figures 3.18 and 3.19"
  (3.18 = the *passed/green* validation screen, 3.19 = the *failed/red* one), but
  the docx contains only 3.19. Add `assets/figure-3.18.png` and rebuild.

## Conventions / decisions

- Section numbering is off (`secnumdepth = -\maxdimen`); headings carry their own
  numbers in the text (e.g. "1. Introduction"). New headings must follow suit.
- Appendix PDFs are named `appendix-<UPPERCASE-LETTER>.pdf`.
- The docx owns the front and back matter content; postprocess only re-styles it.
  If the author restructures the docx front/back matter, revisit
  `restructure_front_matter` and `sectionize_backmatter`.
