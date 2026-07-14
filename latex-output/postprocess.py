#!/usr/bin/env python3
"""Post-process the Pandoc-generated document.tex.

Applies the layout fixes that Pandoc can't do on its own, driven by the actual
content so they survive re-conversion of an updated .docx:

  1. Image sizing by type. Small raster images (charts/plots) are shrunk and
     centred; large ones (screenshots) are capped to the text area. The cutoff
     is pixel width: plots in this project are <=~590px, screenshots >=~1280px.
  2. Wide tables (6+ columns) are dropped to \\footnotesize and given tighter
     column spacing so their cells stop wrapping.

Usage:  python3 postprocess.py document.tex
"""
import os
import re
import struct
import sys

# Images narrower than this many pixels are treated as charts/plots and shrunk.
SMALL_IMAGE_PX = 900
# Display width for those small plots, as a fraction of the text width.
PLOT_WIDTH = r"0.62\linewidth"
# A longtable with at least this many columns is treated as "wide".
WIDE_TABLE_COLS = 6


def png_width(path):
    """Return the pixel width of a PNG, or None if unreadable / not a PNG."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(24)
    except OSError:
        return None
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None  # not a PNG (e.g. jpg/emf) -> caller treats as "large"
    return struct.unpack(">II", head[16:24])[0]


def resize_images(text, base_dir):
    """Size every \\includegraphics by whether its image is a plot or a shot."""
    img_re = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")

    def repl(m):
        path = m.group(1)
        if "media/" not in path:
            return m.group(0)  # leave Pandoc's commented example line alone
        width = png_width(os.path.join(base_dir, path))
        if width is not None and width < SMALL_IMAGE_PX:
            return (r"\begin{center}\includegraphics[width=%s]{%s}\end{center}"
                    % (PLOT_WIDTH, path))
        return (r"\includegraphics[max width=\linewidth,"
                r"max totalheight=0.9\textheight]{%s}" % path)

    text = img_re.sub(repl, text)
    # A stray "\\" left immediately after a centred image would break the box.
    text = text.replace(r"\end{center}\\", r"\end{center}")
    return text


_CELL_RE = re.compile(
    r"\\begin\{minipage\}\[[bt]\]\{[^}]*\}\\raggedright\s*(.*?)\s*\\end\{minipage\}",
    re.DOTALL,
)
_REAL_RE = re.compile(r"(\\real\{)([0-9.]+)(\})")


def _visual_len(cell):
    """Rough printed length of a cell, ignoring LaTeX markup."""
    t = cell
    t = re.sub(r"\\textbf\{([^{}]*)\}", r"\1", t)      # keep bold text
    t = t.replace(r"{[}", "[").replace(r"{]}", "]")     # pandoc-escaped brackets
    t = t.replace(r"\%", "%").replace(r"\&", "&")
    t = re.sub(r"\\[a-zA-Z]+\s*", "", t)                # drop remaining commands
    t = re.sub(r"[{}]", "", t)                          # drop braces
    return len(t.strip())


def _rebalance_columns(block, ncols):
    """Reassign p{} column widths in proportion to each column's longest cell.

    Cell lengths are capped so a wall-of-text column (which wraps anyway)
    doesn't starve the short ID/value columns beside it — it still gets the
    lion's share, just not everything.
    """
    cells = _CELL_RE.findall(block)
    if not cells or len(cells) % ncols != 0:
        return block  # unexpected shape; leave Pandoc's widths alone
    maxlen = [0] * ncols
    for i, cell in enumerate(cells):
        col = i % ncols
        maxlen[col] = max(maxlen[col], min(_visual_len(cell), 60))
    pad = 3  # smooths out very short columns so they keep a sane minimum
    weights = [m + pad for m in maxlen]
    total = float(sum(weights))
    fracs = [round(w / total * 0.98, 4) for w in weights]

    it = iter(fracs)
    new_block, n = _REAL_RE.subn(
        lambda mm: mm.group(1) + format(next(it), ".4f") + mm.group(3), block
    )
    return new_block if n == ncols else block


def align_cells_top(text):
    """Top-align table cells. Pandoc bottom-aligns minipage cells, which makes
    wrapped text float above its row line in text-heavy tables (Appendix J)."""
    return text.replace(r"\begin{minipage}[b]", r"\begin{minipage}[t]")


def shrink_wide_tables(text):
    """Rebalance every longtable's column widths by content; step wide tables
    down in size, and rotate the very widest (10+ columns) onto landscape
    pages together with their captions."""
    lt_re = re.compile(
        r"(?:(\\textbf\{Table\s[^\n]*)\n\n)?"          # caption above (opt.)
        r"(\\begin\{longtable\}.*?\\end\{longtable\})"  # the table
        r"(?:\n\n(\\textbf\{Table\s[^\n]*))?",          # caption below (opt.)
        re.DOTALL)

    def repl(m):
        cap_above, block, cap_below = m.group(1), m.group(2), m.group(3)
        ncols = block.count(r"\arraybackslash}p{")  # one per Pandoc p-column
        if ncols >= 2:
            block = _rebalance_columns(block, ncols)
        if ncols >= 10:  # per-participant data tables: rotate to landscape
            inner = "\n\n".join(p for p in (cap_above, block, cap_below) if p)
            return ("\\begin{landscape}\n"
                    "\\begingroup\\let\\small\\footnotesize"
                    "\\setlength{\\tabcolsep}{4pt}\n" + inner +
                    "\n\\endgroup\n\\end{landscape}")
        if ncols >= WIDE_TABLE_COLS:
            block = ("\\begingroup\\let\\small\\footnotesize"
                     "\\setlength{\\tabcolsep}{4pt}\n" + block + "\n\\endgroup")
        parts = [p for p in (cap_above, block, cap_below) if p]
        return "\n\n".join(parts)

    return lt_re.sub(repl, text)


def fix_url_breaking(text):
    """Turn \\href{URL}{\\ul{URL}} (Word's underlined self-links) into \\url{URL}
    so long DOIs/links can break across lines instead of overflowing. The
    display text may carry escaped underscores (\\_), so compare unescaped."""
    pat = re.compile(r"\\href\{([^}]*)\}\{\\ul\{([^}]*)\}\}")
    return pat.sub(
        lambda m: "\\url{%s}" % m.group(1)
        if m.group(1) == m.group(2).replace("\\_", "_") else m.group(0),
        text)


def demote_caption_headings(text):
    """Word styled some table captions as headings (e.g. Table K.2/K.3 are
    \\subsubsection). Demote them to plain bold caption paragraphs so they
    don't pollute the generated table of contents."""
    pat = re.compile(
        r"\\hypertarget\{[^}]*\}\{%\n"
        r"\\(?:sub)+section\{(Table\s+[A-Z0-9]+\.\d+[^{}]*)\}"
        r"\\label\{[^}]*\}\}")
    return pat.sub(lambda m: "\\textbf{%s}" % m.group(1), text)


def fix_formulas(text):
    """Style the plain-text accuracy/precision formulas as display math."""
    subs = [
        (re.compile(r"^error = √.*$", re.MULTILINE),
         r"\[ \text{error} = \sqrt{(\text{meanGazeX} - \text{targetX})^{2}"
         r" + (\text{meanGazeY} - \text{targetY})^{2}} \]"),
        (re.compile(r"^accuracy \(°\) = arctan.*$", re.MULTILINE),
         r"\[ \text{accuracy}\,(^{\circ}) = \arctan\!\left("
         r"\frac{\text{error} \times W}{d}\right) \]"),
        (re.compile(r"^spread = √.*$", re.MULTILINE),
         r"\[ \text{spread} = \sqrt{\frac{1}{N} \sum \left("
         r"(\text{sampleX} - \text{meanGazeX})^{2}"
         r" + (\text{sampleY} - \text{meanGazeY})^{2}\right)} \]"),
        (re.compile(r"^precision \(°\) = arctan.*$", re.MULTILINE),
         r"\[ \text{precision}\,(^{\circ}) = \arctan\!\left("
         r"\frac{\text{spread} \times W}{d}\right) \]"),
    ]
    for pat, repl in subs:
        text = pat.sub(lambda m, r=repl: r, text)
    return text


_CAPTION_RE = re.compile(
    r"^\\textbf\{(Figure|Table)\s+(\d+\.\d+)[^\n]*", re.MULTILINE)


def insert_diagrams(text, base_dir):
    """Insert diagrams/figure-X.Y.pdf before its caption if no image is there.

    The flowcharts are native Word drawings that Pandoc drops, so the caption
    survives conversion but the graphic doesn't. Any diagrams/figure-X.Y.pdf
    is inserted (centred, capped to the text area) directly above the matching
    "Figure X.Y" caption unless an \\includegraphics already sits within the
    few preceding lines.
    """
    inserted = []

    def repl(m):
        kind, num = m.group(1), m.group(2)
        if kind != "Figure":
            return m.group(0)
        pdf = os.path.join(base_dir, "diagrams", "figure-%s.pdf" % num)
        if not os.path.exists(pdf):
            return m.group(0)
        # look back a few lines for an existing image
        before = text[:m.start()].rsplit("\n", 7)[1:]
        if any("includegraphics" in ln for ln in before):
            return m.group(0)
        inserted.append(num)
        return ("\\begin{center}\\includegraphics[max width=\\linewidth,"
                "max totalheight=0.85\\textheight]{diagrams/figure-%s.pdf}"
                "\\end{center}\n\n%s" % (num, m.group(0)))

    return _CAPTION_RE.sub(repl, text), inserted


def add_figure_table_lists(text):
    """Feed every Figure/Table caption into the .lof/.lot files and replace
    the docx's empty "List of Figures / List of Tables" placeholder section
    with real \\listoffigures / \\listoftables."""

    def entry(m):
        kind, num = m.group(1), m.group(2)
        # first sentence of the caption as plain text (LaTeX-safe for .lof/.lot)
        cap = m.group(0)
        cap = re.sub(r"^\\textbf\{(Figure|Table)\s+[\d.]+\s*", "", cap)
        cap = cap.split(". ")[0]
        cap = cap.replace("\\%", "%")              # unescape first,
        cap = re.sub(r"\\[a-zA-Z]+\s*", "", cap)   # drop \textbf etc.
        cap = re.sub(r"[{}]", "", cap)             # drop stray braces
        cap = cap.replace("%", r"\%").strip(".} \\") + "."
        listname = "lof" if kind == "Figure" else "lot"
        # trailing %% eats the newline so the caption paragraph doesn't start
        # with a stray space (it was visible as an indent before Figure 3.2)
        return ("\\phantomsection\\addcontentsline{%s}{%s}"
                "{\\protect\\numberline{%s}%s}%%\n%s"
                % (listname, kind.lower(), num, cap, m.group(0)))

    text = _CAPTION_RE.sub(entry, text)

    # swap the placeholder section for the generated lists
    placeholder = re.compile(
        r"\\hypertarget\{list-of-figures-list-of-tables\}\{%\n"
        r"\\section\{[^\n]*List of Figures[^\n]*\}"
        r"\\label\{list-of-figures-list-of-tables\}\}")
    lists = (
        "\\clearpage\n"
        "\\hypertarget{list-of-figures-list-of-tables}{}%\n"
        "\\phantomsection\\addcontentsline{toc}{section}{List of Figures}\n"
        "\\listoffigures\n"
        "\\phantomsection\\addcontentsline{toc}{section}{List of Tables}\n"
        "\\listoftables\n")
    text, n = placeholder.subn(lambda _: lists, text)
    return text, n


def inject_abbreviations(text, base_dir):
    """Fill the empty "List of Abbreviations" placeholder section with the
    table maintained in pandoc/abbreviations.tex."""
    path = os.path.join(base_dir, "pandoc", "abbreviations.tex")
    if not os.path.exists(path):
        return text, False
    with open(path, encoding="utf-8") as fh:
        table = fh.read()
    # keep only the content (drop comment header lines)
    table = "\n".join(ln for ln in table.split("\n")
                      if not ln.lstrip().startswith("%"))
    anchor = re.search(r"\\label\{list-of-abbreviations\}\}\n", text)
    if not anchor:
        return text, False
    pos = anchor.end()
    return text[:pos] + "\n" + table.strip() + "\n" + text[pos:], True


def format_references(text):
    """Give the docx's own "List of References" section an APA-7 hanging
    indent by wrapping its body in a group."""
    m = re.search(
        r"(\\section\{[^\n]*List of References[^\n]*\}"
        r"\\label\{list-of-references\}\})\n", text)
    if not m:
        return text, False
    start = m.end()
    nxt = re.search(r"\\hypertarget\{[^}]*\}\{%\n\\section", text[start:])
    end = start + (nxt.start() if nxt else len(text) - start)
    body = text[start:end]
    # LaTeX suppresses \parindent on the first paragraph after a heading, so
    # pull the first entry's opening line back by hand to keep its hang.
    body = re.sub(r"^(\s*)(\S)", r"\1\\hspace*{-0.5in}\2", body, count=1)
    wrapped = ("\n\\begingroup\n"
               "\\setlength{\\parindent}{-0.5in}"
               "\\setlength{\\leftskip}{0.5in}"
               "\\setlength{\\parskip}{6pt plus 2pt minus 1pt}\n"
               + body +
               "\n\\endgroup\n")
    return text[:start] + wrapped + text[end:], True


def attach_appendix_pdfs(text, base_dir):
    """Replace "[add PDF]" markers with \\includepdf of appendix/<letter>.pdf.

    The letter comes from the closest preceding "Appendix X" heading. When the
    file isn't in appendix/ yet, leave a visible note saying what to drop in.
    """
    marker = re.compile(r"\{\[\}add PDF\s*\{\]\}")
    out, last, attached, missing = [], 0, [], []
    for m in marker.finditer(text):
        head = None
        for hm in re.finditer(r"Appendix\s+([A-Z])[:\s]", text[:m.start()]):
            head = hm.group(1)
        pdf_rel = "appendix/appendix-%s.pdf" % (head or "X")
        if head and os.path.exists(os.path.join(base_dir, pdf_rel)):
            repl = ("\\includepdf[pages=-,width=\\textwidth,pagecommand={}]"
                    "{%s}" % pdf_rel)
            attached.append(head)
        else:
            repl = ("\\emph{{[}Placeholder: drop the PDF into %s and re-run "
                    "convert.sh{]}}" % pdf_rel)
            missing.append(pdf_rel)
        out.append(text[last:m.start()])
        out.append(repl)
        last = m.end()
    out.append(text[last:])
    return "".join(out), attached, missing


def restructure_front_matter(text):
    """Thesis layout: standalone title page; live LaTeX TOC replacing Word's
    static one; roman page numbers for the front matter; arabic numbering
    restarting at the Introduction; every chapter/appendix on a new page."""
    notes = []

    # 1. Drop Word's empty spacer headings (they'd become blank TOC entries).
    text, n = re.subn(
        r"\\hypertarget\{section-\d+\}\{%\n"
        r"\\(?:sub)*(?:section|paragraph)\{(?:\\texorpdfstring\{\\hfill\\break"
        r"\s*\}\{ \})?\s*\}\\label\{section-\d+\}\}\n?",
        "", text)
    notes.append("%d spacer headings removed" % n)

    # 2. Strip \hfill\break out of real section titles (Word linebreak relics).
    text = re.sub(
        r"\\section\{\\texorpdfstring\{\\hfill\\break\n([^{}]*?)\s*\}"
        r"\{\s*([^{}]*?)\s*\}\}",
        lambda m: "\\section{%s}" % m.group(2).strip(), text)

    # 3. Turn the opening block into a real title page.
    title_pat = re.compile(
        r"(\\begin\{document\}\n)\n?"
        r"\\textbf\{Masters Thesis\}\n\n"
        r"([^\n]+)\n\n"
        r"([^\n]+)\n\n"
        r"(\{\[\}Citation standard[^\n]*)\n",
        re.DOTALL)

    def title_repl(m):
        return (m.group(1) +
                "\n\\begin{titlepage}\n\\centering\n\\vspace*{4cm}\n"
                "{\\Large\\textbf{Masters Thesis}}\\\\[2cm]\n"
                "{\\huge\\bfseries " + m.group(2).strip() + "\\par}\n"
                "\\vspace{2.5cm}\n"
                "{\\large " + m.group(3).strip() + "}\\\\[1cm]\n"
                + m.group(4).strip() + "\n"
                "\\vfill\n\\end{titlepage}\n")

    text, n = title_pat.subn(title_repl, text)
    notes.append("title page: %s" % bool(n))

    # 4. Replace Word's static TOC (stale page numbers) with a live one.
    toc_pat = re.compile(
        r"\\hypertarget\{table-of-contents\}\{%\n"
        r"\\section\{[^\n]*\}\\label\{table-of-contents\}\}\n"
        r".*?(?=\\hypertarget\{abstract\})",
        re.DOTALL)
    text, n = toc_pat.subn(
        "\\\\pagenumbering{roman}\n"
        "\\\\setcounter{tocdepth}{3}\n"
        "\\\\tableofcontents\n\n", text)
    notes.append("live TOC: %s" % bool(n))

    # 5. Arabic page numbers from the Introduction onwards.
    text, n = re.subn(
        r"(\\hypertarget\{introduction\})",
        "\\\\clearpage\n\\\\pagenumbering{arabic}\n\\1", text, count=1)
    notes.append("arabic at introduction: %s" % bool(n))

    # 6. Every chapter-level section starts on a fresh page...
    text = re.sub(r"(?<!\\clearpage\n)(\\hypertarget\{[^}]+\}\{%\n\\section\b)",
                  "\\\\clearpage\n\\1", text)
    # ...and so does every appendix (they are subsections in the docx).
    text = re.sub(r"(\\hypertarget\{appendix-[^}]*\}\{%\n\\subsection\b)",
                  "\\\\clearpage\n\\1", text)
    return text, "; ".join(notes)


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 postprocess.py document.tex")
    tex = sys.argv[1]
    base_dir = os.path.dirname(os.path.abspath(tex))
    with open(tex, encoding="utf-8") as fh:
        text = fh.read()

    text = fix_url_breaking(text)
    text = demote_caption_headings(text)
    text = fix_formulas(text)
    text = align_cells_top(text)
    text = resize_images(text, base_dir)
    text = shrink_wide_tables(text)
    text, diagrams = insert_diagrams(text, base_dir)
    text, lists_done = add_figure_table_lists(text)
    text, abbr_done = inject_abbreviations(text, base_dir)
    text, refs_done = format_references(text)
    text, appendices, missing = attach_appendix_pdfs(text, base_dir)
    text, fm_notes = restructure_front_matter(text)

    with open(tex, "w", encoding="utf-8") as fh:
        fh.write(text)

    n_plots = text.count(r"\includegraphics[width=" + PLOT_WIDTH)
    n_shots = text.count(r"\includegraphics[max width=\linewidth")
    n_wide = text.count(r"\begingroup\let\small\footnotesize")
    print("postprocess: %d plots shrunk, %d screenshots capped, "
          "%d wide tables set to footnotesize" % (n_plots, n_shots, n_wide))
    print("postprocess: diagrams inserted: %s" % (", ".join(diagrams) or "none"))
    print("postprocess: LoF/LoT placeholder replaced: %s" % bool(lists_done))
    print("postprocess: abbreviations injected: %s" % abbr_done)
    print("postprocess: references hanging indent: %s" % refs_done)
    print("postprocess: appendix PDFs attached: %s"
          % (", ".join(appendices) or "none"))
    print("postprocess: front matter: %s" % fm_notes)
    for p in missing:
        print("postprocess: NOTE - awaiting %s" % p)


if __name__ == "__main__":
    main()
