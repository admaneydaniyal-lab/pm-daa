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
# Screenshots are capped short of a full page so their caption (added by
# wrap_figures_with_captions) always has room to sit on the same page.
SCREENSHOT_MAX_HEIGHT = r"0.78\textheight"
# A longtable with at least this many columns is treated as "wide".
WIDE_TABLE_COLS = 6
# Per-diagram display width overrides (default \linewidth).
DIAGRAM_WIDTHS = {"3.20": "0.85\\linewidth"}


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
    # Strip stray characters Word left glued to an image line (e.g. a lone
    # "-" or "1" before \includegraphics) — they render as debris in the PDF.
    text = re.sub(r"(?m)^[-\d]\s*(?=\\includegraphics)", "", text)
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
                r"max totalheight=%s]{%s}" % (SCREENSHOT_MAX_HEIGHT, path))

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


def _rebalance_columns(block, ncols, char_frac=0.0095):
    """Reassign p{} column widths in proportion to each column's longest cell.

    Cell lengths are capped so a wall-of-text column (which wraps anyway)
    doesn't starve the short ID/value columns beside it. Each column is also
    floored at the width of its longest unbreakable word (roughly char_frac
    of the text width per character), so headers like "Participant" or
    "Breakdowns" can't poke into the next column.
    """
    cells = _CELL_RE.findall(block)
    if not cells or len(cells) % ncols != 0:
        return block  # unexpected shape; leave Pandoc's widths alone
    maxlen = [0] * ncols
    maxword = [0] * ncols
    for i, cell in enumerate(cells):
        col = i % ncols
        maxlen[col] = max(maxlen[col], min(_visual_len(cell), 60))
        plain = re.sub(r"\\[a-zA-Z]+\s*|[{}]", "", cell)
        for w in plain.split():
            maxword[col] = max(maxword[col], len(w))
    pad = 3  # smooths out very short columns so they keep a sane minimum
    weights = [m + pad for m in maxlen]
    total = float(sum(weights))
    fracs = [w / total * 0.98 for w in weights]

    # enforce longest-word floors, taking the excess from the roomier columns
    floors = [(w + 1) * char_frac for w in maxword]
    for _ in range(3):  # a few passes are plenty to converge
        deficit = sum(max(f, fl) for f, fl in zip(fracs, floors)) - 0.98
        fracs = [max(f, fl) for f, fl in zip(fracs, floors)]
        if deficit <= 0:
            break
        slack = [max(f - fl, 0.0) for f, fl in zip(fracs, floors)]
        s = sum(slack)
        if s <= 0:
            break
        fracs = [f - deficit * (sl / s) for f, sl in zip(fracs, slack)]
    fracs = [round(f, 4) for f in fracs]

    it = iter(fracs)
    new_block, n = _REAL_RE.subn(
        lambda mm: mm.group(1) + format(next(it), ".4f") + mm.group(3), block
    )
    return new_block if n == ncols else block


def align_cells_top(text):
    """Top-align table cells. Pandoc bottom-aligns minipage cells, which makes
    wrapped text float above its row line in text-heavy tables (Appendix J)."""
    return text.replace(r"\begin{minipage}[b]", r"\begin{minipage}[t]")


# A table+caption reservation bigger than this many lines is skipped: forcing
# it would either fail outright (content taller than a page) or just push a
# near-empty page for no benefit, so genuinely huge tables are left to flow.
MAX_TABLE_NEEDSPACE_LINES = 36


def _table_needspace(block, cap_above, cap_below, ncols):
    """Estimate a \\Needspace reservation covering a table plus its caption,
    so document-wide, a caption is never stranded on a different page than
    its table. Returns "" when the estimate is too large to be worth forcing.
    """
    cells = _CELL_RE.findall(block)
    nrows = len(cells) // ncols if ncols else 0
    cap_text = (cap_above or "") + (cap_below or "")
    plain_cap = re.sub(r"\\[a-zA-Z]+|[{}]", "", cap_text)
    cap_lines = max(1.0, len(plain_cap) / (95 if ncols < 10 else 150))
    body_lines = nrows * 1.55 + 1.6  # body rows + header/rule allowance
    total = body_lines + cap_lines + 1.5  # small buffer
    if total > MAX_TABLE_NEEDSPACE_LINES:
        return ""
    return "\\Needspace{%.1f\\baselineskip}\n" % total


def shrink_wide_tables(text):
    """Rebalance every longtable's column widths by content; step wide tables
    down in size, rotate the very widest (10+ columns) onto landscape pages,
    and reserve enough space that each table stays on one page with its
    caption wherever that's a reasonable amount of space to reserve."""
    lt_re = re.compile(
        r"(?:(\\textbf\{Table\s[^\n]*)\n\n)?"          # caption above (opt.)
        r"(\\begin\{longtable\}.*?\\end\{longtable\})"  # the table
        r"(?:\n\n(\\textbf\{Table\s[^\n]*))?",          # caption below (opt.)
        re.DOTALL)

    def repl(m):
        cap_above, block, cap_below = m.group(1), m.group(2), m.group(3)
        ncols = block.count(r"\arraybackslash}p{")  # one per Pandoc p-column
        needspace = ""
        if ncols >= 2:
            # landscape pages are wider, so a character eats a smaller
            # fraction of the line there
            block = _rebalance_columns(
                block, ncols, char_frac=0.0075 if ncols >= 10 else 0.0095)
            # Skip reservation if a heading immediately above (e.g. Appendix
            # J's "Deductive codes...") already reserved space via
            # keep_captions_with_tables — avoid double-reserving right after
            # a heading and forcing it (rather than just the table tail)
            # onto a fresh page.
            already_reserved = ("\\Needspace{" in
                                 text[max(0, m.start() - 400):m.start()])
            if not already_reserved:
                needspace = _table_needspace(block, cap_above, cap_below, ncols)
        if ncols >= 10:  # per-participant data tables: rotate to landscape
            inner = "\n\n".join(p for p in (cap_above, block, cap_below) if p)
            return (needspace + "\\begin{landscape}\n"
                    "\\begingroup\\let\\small\\footnotesize"
                    "\\setlength{\\tabcolsep}{4pt}\n" + inner +
                    "\n\\endgroup\n\\end{landscape}")
        if ncols >= WIDE_TABLE_COLS:
            block = ("\\begingroup\\let\\small\\footnotesize"
                     "\\setlength{\\tabcolsep}{4pt}\n" + block + "\n\\endgroup")
        parts = [p for p in (cap_above, block, cap_below) if p]
        return needspace + "\n\n".join(parts)

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
    """Word styled some table captions as headings (Table K.2/K.3 are
    \\subsubsections, Table J.3 a \\paragraph). Demote them to normal caption
    paragraphs — bolding only the "Table X.Y" label, per the caption
    convention — so they don't pollute the generated table of contents."""
    pat = re.compile(
        r"\\hypertarget\{[^}]*\}\{%\n"
        r"\\(?:(?:sub)+section|paragraph)\{(Table\s+[A-Z0-9]+\.\d+)"
        r"([^{}]*)\}\\label\{[^}]*\}\}")
    text = pat.sub(
        lambda m: "\\textbf{%s}%s" % (m.group(1), m.group(2).rstrip()), text)
    # Word sometimes indents a caption, which Pandoc turns into a quote
    # environment (renders centred-ish). Unwrap those.
    text = re.sub(
        r"\\begin\{quote\}\n(\\textbf\{Table\s[^\n]*)\n\\end\{quote\}",
        lambda m: m.group(1), text)
    return text


# Caption rewrites: give over-long first sentences a short title sentence so
# the List of Tables stays scannable. Content is preserved, just re-punctuated.
CAPTION_REWRITES = [
    ("\\textbf{Table 5.2} Shapiro-Wilk tests of normality on the "
     "within-participant difference scores, with the test applied to each "
     "measure.",
     "\\textbf{Table 5.2} Shapiro-Wilk tests of normality. The tests were "
     "applied to the within-participant difference scores of each measure."),
    ("\\textbf{Table 5.3} Interaction breakdowns by category and condition "
     "(N = 12 per condition).",
     "\\textbf{Table 5.3} Interaction breakdowns by category and condition. "
     "Counts cover N = 12 participants per condition."),
    ("\\textbf{Table 5.4} First-pass calibration success: two-by-two "
     "contingency of first-attempt outcomes in the fragmented and unified "
     "conditions, with the exact McNemar test (N = 12; six discordant "
     "pairs).",
     "\\textbf{Table 5.4} First-pass calibration success. Two-by-two "
     "contingency of first-attempt outcomes in the fragmented and unified "
     "conditions, with the exact McNemar test (N = 12; six discordant "
     "pairs)."),
    ("\\textbf{Table 5.5} Paired comparisons between conditions, with exact "
     "p-values, effect sizes and their 95 percent confidence intervals, "
     "family-wise thresholds, and outcomes after per-hypothesis Bonferroni "
     "correction (N = 12).",
     "\\textbf{Table 5.5} Paired comparisons between conditions. Reported "
     "are exact p-values, effect sizes with 95 percent confidence "
     "intervals, family-wise thresholds, and the outcomes after "
     "per-hypothesis Bonferroni correction (N = 12)."),
]


def apply_text_edits(text):
    """Small content edits requested on the thesis text. Each is keyed on the
    docx wording, so it applies cleanly after every re-conversion and simply
    no-ops once the docx itself is updated."""
    for old, new in CAPTION_REWRITES:
        text = text.replace(old, new)
    # Figure 5.4: drop the author's leftover note from the caption.
    text = text.replace("{[}add a line dash for 68?{]}", "")
    # Chapter 7.1: bold the research-question lead-ins.
    for i in "1234":
        text = re.sub(r"(?m)^For RQ%s," % i,
                      r"\\textbf{For RQ%s,}" % i, text)
    # Stray space before a closing paren in a page-number citation.
    text = text.replace("(Dell Inc., 2016, p. 6 )", "(Dell Inc., 2016, p. 6)")
    # Chapter 7.2: bold each contribution's lead-in clause.
    text = re.sub(
        r"(?m)^The (first|second|third|fourth) contribution is ([^:\n]+):",
        r"\\textbf{The \1 contribution is \2:}", text)
    return text


def move_figure_318(text):
    """Move Figure 3.18 (image + caption) to after the 3.3.4.5 result-
    visualisation paragraph, where the text first discusses it."""
    block_pat = re.compile(
        r"\n\\includegraphics\[[^\]]*\]\{media/[^}]*\}\n\n"
        r"\\textbf\{Figure 3\.18\}[^\n]*\n")
    m = block_pat.search(text)
    anchor = "visibility of system status (Nielsen, 1994)."
    if not m or anchor not in text:
        return text, False
    block = m.group(0)
    text = block_pat.sub("\n", text, count=1)
    pos = text.find(anchor) + len(anchor)
    return text[:pos] + "\n" + block + text[pos:], True


_TABLE_5_1_ROWS = [
    # (measure, F mean, F sd, F min, F max, U mean, U sd, U min, U max)
    ("Setup time (s)", "1226", "292.7", "779", "1645",
     "998.4", "193.4", "599", "1256"),
    ("Calibration time (s)", "925.9", "262.2", "533", "1317",
     "666.6", "187.5", "407", "1039"),
    ("NASA-TLX", "43.61", "20.01", "13.33", "73.33",
     "22.22", "18.83", "0.00", "61.67"),
    ("SUS", "46.46", "30.22", "0.00", "90.00",
     "73.33", "20.57", "32.50", "100.00"),
    ("Calibration confidence (1--7)", "5.08", "2.02", "1", "7",
     "5.75", "1.42", "2", "7"),
    ("Interaction breakdowns", "20.00", "4.61", "12", "26",
     "8.17", "4.06", "2", "13"),
    ("Gaze accuracy (deg)", "2.03", "2.25", "0.64", "9.07",
     "1.28", "0.66", "0.19", "2.37"),
    ("Gaze precision (deg)", "0.65", "0.33", "0.19", "1.24",
     "1.29", "1.27", "0.29", "3.89"),
    (r"Valid data yield (\%)", "99.54", "1.13", "96.40", "100.00",
     "99.21", "1.21", "96.30", "100.00"),
    ("EDA baseline (uS)", "4.53", "3.20", "0.64", "11.15",
     "5.56", "4.28", "0.60", "14.55"),
]


def restructure_table_5_1(text):
    """Table 5.1 listed each measure across two rows (one per condition),
    which roughly doubled its length versus a paired layout. Transpose it to
    one row per measure with F and U mean(SD) and range side by side — same
    ten measures, same four statistics per condition, nothing dropped.

    Matched by its exact header fingerprint (Measure/Condition/Mean/SD/
    Min/Max) rather than position, so it only fires on this specific table
    and simply no-ops if the docx's own Table 5.1 is later edited to match.
    """
    tables = list(re.finditer(
        r"\\begin\{longtable\}.*?\\end\{longtable\}", text, re.DOTALL))
    target = None
    for m in tables:
        block = m.group(0)
        if (r"\textbf{Measure}" in block and r"\textbf{Condition}" in block
                and r"\textbf{Mean}" in block and r"\textbf{SD}" in block
                and r"\textbf{Min}" in block and r"\textbf{Max}" in block
                and "Setup time (s)" in block
                and "EDA baseline (uS)" in block):
            target = m
            break
    if target is None:
        return text, False

    header = (r"\begin{longtable}[]{@{}"
              r">{\raggedright\arraybackslash}p{0.28\columnwidth}"
              r">{\raggedright\arraybackslash}p{0.16\columnwidth}"
              r">{\raggedright\arraybackslash}p{0.16\columnwidth}"
              r">{\raggedright\arraybackslash}p{0.16\columnwidth}"
              r">{\raggedright\arraybackslash}p{0.16\columnwidth}@{}}" "\n"
              r"\toprule\noalign{}" "\n"
              r"\textbf{Measure} & \textbf{F Mean (SD)} & \textbf{F Range} "
              r"& \textbf{U Mean (SD)} & \textbf{U Range} \\" "\n"
              r"\midrule\noalign{}" "\n"
              r"\endhead" "\n"
              r"\bottomrule\noalign{}" "\n"
              r"\endlastfoot" "\n")
    rows = []
    for measure, fm, fsd, fmin, fmax, um, usd, umin, umax in _TABLE_5_1_ROWS:
        rows.append(
            r"%s & %s (%s) & %s--%s & %s (%s) & %s--%s \\"
            % (measure, fm, fsd, fmin, fmax, um, usd, umin, umax))
    new_table = header + "\n".join(rows) + "\n\\end{longtable}"
    return text[:target.start()] + new_table + text[target.end():], True


def demote_appendix_subheaders(text):
    """Flatten internal headings inside each appendix artefact (A1, A2, B, C,
    D, E, F, H, I, K) to plain bold text, since these are reproduced forms/
    instruments rather than thesis chapters. Appendix G and J keep their
    internal structure (G's questionnaire sections, J's Part A-D navigation).
    Each appendix's own opening "Appendix X: ..." title is always preserved.
    """
    opener_re = re.compile(
        r"\\hypertarget\{appendix-([a-z0-9]+)[^}]*\}\{%\n"
        r"\\subsection\{(?:\\texorpdfstring\{[^{}]*\}\{[^{}]*\}|[^{}]*)\}"
        r"\\label\{[^}]*\}\}")
    openers = list(opener_re.finditer(text))
    if not openers:
        return text, 0
    header_re = re.compile(
        r"\\hypertarget\{[^}]*\}\{%\n"
        r"\\(subsection|subsubsection|paragraph)\{"
        r"(?:\\texorpdfstring\{([^{}]*)\}\{[^{}]*\}|([^{}]*))"
        r"\}\\label\{[^}]*\}\}")
    count = 0
    out = [text[:openers[0].start()]]
    for i, m in enumerate(openers):
        letter = m.group(1)
        body_start = m.end()
        body_end = openers[i + 1].start() if i + 1 < len(openers) else len(text)
        out.append(text[m.start():body_start])
        body = text[body_start:body_end]
        if letter not in ("g", "j"):
            def sub(mm):
                nonlocal count
                title = (mm.group(2) or mm.group(3) or "").strip()
                if not title:
                    return ""
                count += 1
                return "\\textbf{%s}" % title
            body = header_re.sub(sub, body)
        out.append(body)
    return "".join(out), count


_FIG_CAPTION_LINE_RE = re.compile(
    r"^\\textbf\{Figure\s+(?:\d+|[A-Z])\.\d+\}[^\n]*\n", re.MULTILINE)


def wrap_figures_with_captions(text):
    """Keep every figure image and its caption on one page (document-wide),
    using the float package's [H] specifier so the pair is treated as a
    single unbreakable block that moves to the next page as a unit if it
    doesn't fit. Must run after add_figure_table_lists, since it relies on
    the \\phantomsection...addcontentsline line it inserts before captions.
    """
    unit_re = re.compile(
        r"(\\begin\{center\}\\includegraphics\[[^\]]*\]\{[^}]+\}\\end\{center\}"
        r"\\?\\?|\\includegraphics\[[^\]]*\]\{[^}]+\}\\?\\?)\n\n"
        r"(\\phantomsection\\addcontentsline\{lof\}\{figure\}\{[^\n]*\}%\n)?"
        + _FIG_CAPTION_LINE_RE.pattern.lstrip("^"))

    def repl(m):
        return ("\\begin{figure}[H]\n" + m.group(0).rstrip("\n") +
                "\n\\end{figure}\n")

    return unit_re.subn(repl, text)


def keep_captions_with_tables(text):
    """Reserve space before a heading that directly precedes a longtable, so
    titles like "Inductive codes" (Appendix J) don't strand at the bottom of
    the previous page.

    Deliberately does NOT match a "\\textbf{Table X.Y}" caption here: for
    back-to-back tables with no heading between them (e.g. Appendix K's
    K.1/K.2/K.3), table N's own trailing caption sits immediately before
    table N+1's \\begin{longtable} — matching it here would misread table N's
    caption as a heading for table N+1, breaking the adjacency that
    shrink_wide_tables relies on to pair each table with its own caption
    (its own general Needspace logic already covers the caption case).
    """
    pat = re.compile(
        r"(\\hypertarget\{[^}]*\}\{%\n"
        r"\\(?:paragraph|subsubsection)\{[^\n]*\}\}\n)"
        r"(\n\\begin\{longtable\})")
    return pat.sub(lambda m: "\\Needspace{14\\baselineskip}\n"
                   + m.group(1) + m.group(2), text)


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
    r"^\\textbf\{(Figure|Table)\s+((?:\d+|[A-Z])\.\d+)[^\n]*", re.MULTILINE)


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
        width = DIAGRAM_WIDTHS.get(num, "\\linewidth")
        return ("\\begin{center}\\includegraphics[max width=%s,"
                "max totalheight=%s]{diagrams/figure-%s.pdf}"
                "\\end{center}\n\n%s"
                % (width, SCREENSHOT_MAX_HEIGHT, num, m.group(0)))

    return _CAPTION_RE.sub(repl, text), inserted


def add_figure_table_lists(text):
    """Feed every Figure/Table caption into the .lof/.lot files and replace
    the docx's empty "List of Figures / List of Tables" placeholder section
    with real \\listoffigures / \\listoftables."""

    def entry(m):
        kind, num = m.group(1), m.group(2)
        # first sentence of the caption as plain text (LaTeX-safe for .lof/.lot)
        cap = m.group(0)
        cap = re.sub(r"^\\textbf\{(Figure|Table)\s+(?:\d+|[A-Z])\.\d+\}?\s*",
                     "", cap)
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
    text, appendix_headers_demoted = demote_appendix_subheaders(text)
    text = apply_text_edits(text)
    text = fix_formulas(text)
    text = align_cells_top(text)
    text, table_5_1_done = restructure_table_5_1(text)
    text = resize_images(text, base_dir)
    text, moved_318 = move_figure_318(text)
    text = keep_captions_with_tables(text)
    text = shrink_wide_tables(text)
    text, diagrams = insert_diagrams(text, base_dir)
    text, lists_done = add_figure_table_lists(text)
    text = wrap_figures_with_captions(text)[0]
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
    print("postprocess: figure 3.18 moved: %s" % moved_318)
    print("postprocess: appendix sub-headers demoted: %d"
          % appendix_headers_demoted)
    print("postprocess: table 5.1 restructured: %s" % table_5_1_done)
    for p in missing:
        print("postprocess: NOTE - awaiting %s" % p)


if __name__ == "__main__":
    main()
