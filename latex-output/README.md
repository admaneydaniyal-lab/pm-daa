# LaTeX conversion of the thesis document

Converted from `for_latx.docx` with Pandoc, then adjusted to compile
cleanly with pdfLaTeX. Images and tables are preserved.

## Contents
- `document.tex`  – the LaTeX source (standalone, 91 pages)
- `media/media/`  – 32 images extracted from the .docx, referenced with `\includegraphics`

## Build
```sh
pdflatex document.tex
pdflatex document.tex   # run twice to resolve the table of contents / hyperlinks
```

## Adding references
The document ends with a ready-to-fill **References** section (APA-7 style,
hanging indent). Paste each reference as its own paragraph between the
`\begingroup … \endgroup` block near the end of `document.tex`.

## Notes
- Unicode math/Greek symbols (√ α Σ μ × −) are mapped to LaTeX equivalents
  in the preamble so pdfLaTeX renders them.
- A few wide tables slightly exceed the text margin (harmless "overfull hbox"
  warnings); tighten column widths if you want them fully inside the margins.
