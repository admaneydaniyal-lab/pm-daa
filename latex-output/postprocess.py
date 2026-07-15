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
# A portrait table with at least this many rows is dropped to \footnotesize so
# it (plus its heading and caption) has a chance of fitting on a single page.
TALL_TABLE_ROWS = 22


def shrink_wide_tables(text):
    """Rebalance every longtable's column widths by content and step dense
    tables down in size: 10+ columns rotate onto landscape pages, 6+ columns
    (or 22+ rows) drop to \\footnotesize. Reservation to keep a table with its
    caption/heading on one page is handled separately by reserve_table_units,
    which runs afterwards on the transformed text."""
    lt_re = re.compile(
        r"(?:(\\textbf\{Table\s[^\n]*)\n\n)?"          # caption above (opt.)
        r"(\\begin\{longtable\}.*?\\end\{longtable\})"  # the table
        r"(?:\n\n(\\textbf\{Table\s[^\n]*))?",          # caption below (opt.)
        re.DOTALL)

    def repl(m):
        cap_above, block, cap_below = m.group(1), m.group(2), m.group(3)
        ncols = block.count(r"\arraybackslash}p{")  # one per Pandoc p-column
        if ncols >= 2:
            block = _rebalance_columns(
                block, ncols, char_frac=0.0075 if ncols >= 10 else 0.0095)
        cells = _CELL_RE.findall(block)
        nrows = len(cells) // ncols if ncols else 0
        longest_cell = max((_visual_len(c) for c in cells), default=0)
        if ncols >= 10:  # per-participant data tables: rotate to landscape
            inner = "\n\n".join(p for p in (cap_above, block, cap_below) if p)
            return ("\\begin{landscape}\n"
                    "\\begingroup\\let\\small\\footnotesize"
                    "\\setlength{\\tabcolsep}{4pt}\n" + inner +
                    "\n\\endgroup\n\\end{landscape}")
        if ncols >= WIDE_TABLE_COLS or nrows >= TALL_TABLE_ROWS:
            block = ("\\begingroup\\let\\small\\footnotesize"
                     "\\setlength{\\tabcolsep}{4pt}\n" + block + "\n\\endgroup")
        elif longest_cell >= 120:
            # text-heavy tables (e.g. J.4's Rationale column): widen the row
            # gaps so the walls of text are easier to read.
            block = ("\\begingroup\\renewcommand{\\longtablestretch}{1.6}\n"
                     + block + "\n\\endgroup")
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
    """Word styled some table captions as headings (Table K.2/K.3 are
    \\subsubsections, Table J.3 a \\paragraph). Demote them to normal caption
    paragraphs — bolding only the "Table X.Y" label, per the caption
    convention — so they don't pollute the generated table of contents."""
    pat = re.compile(
        r"\\hypertarget\{[^}]*\}\{%\n"
        r"\\(?:(?:sub)+section|paragraph)\{"
        r"(?:\\texorpdfstring\{)?"          # optional Word linebreak wrapper
        r"(Table\s+[A-Z0-9]+\.\d+)([^{}]*)"
        r"(?:\}\{[^{}]*\})?"                # ...its second (PDF-bookmark) arg
        r"\}\\label\{[^}]*\}\}")
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
    # Figure 3.26: drop the "[NEED TO UPDATE IMAGE]" author tag.
    text = text.replace("{[}NEED TO UPDATE IMAGE{]} ", "")
    # Section 2.6: fill the "[For bio sensors...]" placeholder.
    text = text.replace(
        "{[}For bio sensors\\ldots{]}",
        "For biosensors, a comparable dependence on setup quality applies, "
        "though it is handled differently. Biosignal quality is not fixed once "
        "a sensor is attached: it depends on operator-performed steps such as "
        "skin preparation, correct electrode placement, and stable skin "
        "contact, and it must be verified per channel before recording begins "
        "rather than assumed (Aloi et al., 2024, p. 3). In practice this "
        "verification is performed through the sensor's own acquisition "
        "software, which may report a per-channel quality indicator; Aloi et "
        "al. (2024, p. 3), for example, assessed EEG electrode quality through "
        "a dedicated indicator and verified GSR acquisition quality separately "
        "before recording.")
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
    # Appendix B: drop the sentence about which items informed analysis.
    text = text.replace(
        " The prior-experience items (questions 8 and 9) are the source of "
        "the descriptive experience data reported in Chapter 4.2; the contact "
        "and availability items were used for scheduling only and did not "
        "inform analysis.", "")
    # Appendix C/D study title: match the canonical thesis title (the docx's
    # consent/info-sheet copy used an older, shorter wording).
    text = text.replace(
        "Designing and Evaluating Usability-Centred Calibration Workflows in "
        "Multi-Modal Physiological Research Platforms",
        "Designing and Evaluating Usability-Centred Onboarding and Calibration "
        "Workflows in Multi-Modal Research Platforms")
    return text


_AI_DISCLOSURE = r"""\clearpage
\phantomsection\addcontentsline{toc}{section}{Information on the use of AI-based tools}
\section*{Information on the use of AI-based tools}

In accordance with the Guidelines on How to Handle AI in Teaching and Learning at Rhine-Waal University of Applied Sciences (November 2024), this section discloses all uses of AI tools as aids in this thesis. In each case the author defined the objectives, verified the outputs, and retains full responsibility for the work. No AI tool generated the research data, statistical results, or findings. The quantitative analysis was performed by the author in JASP, and the qualitative data are participants' own written responses, analysed by the author.

\textbf{Consensus (Consensus NLP Inc.)} was used as an aid for concept-based literature searching (Chapter 2.1). All results were screened, read, and selected by the author. No output was reproduced without verification against the primary source.

\textbf{Claude Code (Anthropic)} was used as an aid for pair-programming of the author's own contributions to the prototype. These were the eye-tracking validation layer and the electrodermal-activity signal-quality indicators within the onboarding and calibration workflow (Chapters 3.3 and 3.3.4.4). The methods were designed by the author and verified against the literature and the hardware output. The tool assisted with code, not with method design.

\textbf{Claude (Anthropic)} was used as an aid during the qualitative analysis (reflexive thematic analysis). It helped organise and document the codes and surface candidate groupings for the author's consideration (Chapter 4.6.2.3). The author generated the codes and themes through their own reflexive engagement with the data and made all final decisions. Where the tool suggested a grouping or framing, the author evaluated it, accepted or rejected it, and reworked it rather than adopting it as given.

\textbf{Claude (Anthropic)} was also used as an aid for editing and revising the text. This included assistance in restructuring passages for clarity, reducing repetition, and checking APA 7 formatting and cross-chapter consistency. Where the tool helped draft specific passages, these were guided, reviewed, revised, and integrated by the author. The content, arguments, results, and conclusions are the author's own.

The tools were used interactively throughout the project rather than through a fixed set of prompts.

\clearpage
\phantomsection\addcontentsline{toc}{section}{Declaration}
\section*{Declaration}

I, Daniyal Admany, hereby declare that the work submitted is the result of my own independent work. No sources or aids other than those explicitly mentioned have been used in its preparation. All materials, ideas, and statements taken from the works of others have been properly cited and acknowledged in the reference list. Direct quotations have been clearly indicated as such, and all other references have been appropriately identified according to their relevance and contribution to this study.

This work has neither been published nor submitted previously for evaluation in the same or substantially similar form.

\vfill
\noindent Daniyal Admany
\\[0.4cm]
\noindent Duisburg, 15.07.2026
\vspace{1cm}

"""


def update_disclosure_declaration(text):
    """Replace DRAFT_10's placeholder AI-disclosure/declaration block (an
    empty "AI Usage Disclosure" section and a "Please attach the following
    text..." stub) with the author's finalised content from the separately
    supplied docx, each on its own page. Keyed on the placeholder wording, so
    it no-ops once the main docx carries the final text itself."""
    pat = re.compile(
        r"\\hypertarget\{ai-usage-disclosure\}.*?(?=\\end\{document\})",
        re.DOTALL)
    if not pat.search(text):
        return text, False
    return pat.sub(lambda _: _AI_DISCLOSURE, text), True


def replace_figure_326_image(text, base_dir):
    """Point Figure 3.26 at assets/figure-3.26.png when that file exists (the
    updated Calibration Overview screenshot, supplied separately from the
    docx). Matches the \\includegraphics that immediately precedes the
    "Figure 3.26" caption, so it tracks whichever media file Pandoc assigned."""
    if not os.path.exists(os.path.join(base_dir, "assets", "figure-3.26.png")):
        return text, False
    pat = re.compile(
        r"(\\includegraphics\[[^\]]*\]\{)[^}]+(\}\s*\n\s*\n"
        r"\\textbf\{Figure 3\.26\})")
    text, n = pat.subn(r"\1assets/figure-3.26.png\2", text)
    return text, bool(n)


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


def _k_table_latex(number, title, col_labels, rows, landscape):
    """Build one Appendix K longtable (Participant + given metric columns)."""
    ncols = len(col_labels) + 1
    # Fractions sum to 1.0 and the tabcolsep gaps are subtracted from
    # \columnwidth first (as Pandoc does), so rows never overrun the margin.
    if landscape:
        p_frac = 0.065
    elif ncols <= 3:
        p_frac = 0.24          # 2-metric table (K.4): give participant room
    else:
        p_frac = 0.11          # multi-metric portrait table (K.1, K.2)
    per_col = (1.0 - p_frac) / (ncols - 1)
    fracs = [p_frac] + [per_col] * (ncols - 1)
    gaps = 2 * ncols
    colspec = "".join(
        r">{\raggedright\arraybackslash}"
        r"p{(\columnwidth - %d\tabcolsep) * \real{%.4f}}" % (gaps, f)
        for f in fracs)
    header_cells = " & ".join([r"\textbf{Participant}"] +
                               [r"\textbf{%s}" % c for c in col_labels])
    body = "\n".join(" & ".join(row) + r" \\" for row in rows)
    table = (
        r"\begin{longtable}[]{@{}" + colspec + r"@{}}" "\n"
        r"\toprule\noalign{}" "\n" + header_cells + r" \\" "\n"
        r"\midrule\noalign{}" "\n"
        r"\endhead" "\n"
        r"\bottomrule\noalign{}" "\n"
        r"\endlastfoot" "\n" + body + "\n"
        r"\end{longtable}")
    # Deliberately no \phantomsection\addcontentsline here: add_figure_table_
    # lists() adds that uniformly for every "\textbf{Table X.Y}" caption
    # later in the pipeline. Adding it here too would duplicate the LoT entry.
    caption = r"\textbf{Table K.%s} %s" % (number, title)
    if not landscape:
        # portrait multi-column data tables need footnotesize to fit
        body_wrap = (r"\begingroup\let\small\footnotesize"
                     r"\setlength{\tabcolsep}{4pt}" "\n" + table +
                     "\n\\endgroup") if ncols > 3 else table
        return "\\Needspace{%d\\baselineskip}\n%s\n\n%s" % (
            min(10 + len(rows), 40), body_wrap, caption)
    # pdflscape forces a page break at \end{landscape}: anything after it
    # lands on a different (portrait) page. Keep the caption INSIDE the
    # landscape block, right after the table, so both stay together on the
    # same rotated page.
    return "\\Needspace{%d\\baselineskip}\n\\begin{landscape}\n" \
           "\\begingroup\\let\\small\\footnotesize" \
           "\\setlength{\\tabcolsep}{4pt}\n%s\n\n%s\n" \
           "\\endgroup\n\\end{landscape}" % (
               min(10 + len(rows), 34), table, caption)


def restructure_appendix_k(text):
    """Regroup Appendix K's three per-participant tables into four, splitting
    K.1 (efficiency+subjective+eye-tracking mixed together) by measure type:

      K.1 Efficiency & breakdowns:  Setup time, Calibration time, Breakdowns
      K.2 Subjective measures:      NASA-TLX, SUS, Confidence
      K.3 Eye-tracking calibration: Gaze accuracy, precision, valid data
                                     yield, first-pass success
      K.4 EDA baseline:             unchanged, renumbered from K.3

    Parsed from the three original longtables (by header fingerprint) rather
    than hand-copied, so the 12 participants' actual values flow through
    unchanged; only the grouping and captions change. No-ops once the docx's
    own Appendix K is restructured to match.
    """
    k_open = re.search(
        r"\\hypertarget\{appendix-k[^}]*\}\{%\n\\subsection\b", text)
    if not k_open:
        return text, False
    tables = list(re.finditer(
        r"\\begin\{longtable\}.*?\\end\{longtable\}", text, re.DOTALL))
    tables = [m for m in tables if m.start() > k_open.start()]
    parsed = []
    for m in tables:
        block = m.group(0)
        ncols = block.count(r"\arraybackslash}p{")
        if ncols < 2:
            continue
        cells = [c.strip() for c in _CELL_RE.findall(block)]
        if len(cells) < ncols:
            continue
        header = [re.sub(r"\\textbf\{([^{}]*)\}", r"\1", c)
                  for c in cells[:ncols]]
        if header[0] != "Participant":
            continue
        body = cells[ncols:]
        if len(body) % ncols:
            continue
        rows = [body[i:i + ncols] for i in range(0, len(body), ncols)]
        parsed.append((m, header, rows))

    def find(*required):
        for entry in parsed:
            if all(r in entry[1] for r in required):
                return entry
        return None

    t1 = find("Setup time (s) F", "Confidence (1-7) U")
    t2 = find("Breakdowns F", "First-pass U")
    t3 = find(r"EDA baseline (uS) F")
    if not (t1 and t2 and t3):
        return text, False

    def col(entry, name):
        _, header, rows = entry
        idx = header.index(name)
        return [row[idx] for row in rows]

    participants = col(t1, "Participant")

    def pick(entry, names):
        cols = [col(entry, n) for n in names]
        return [list(vals) for vals in zip(participants, *cols)]

    k1_labels = ["Setup time (s) F", "Setup time (s) U",
                 "Calibration time (s) F", "Calibration time (s) U",
                 "Breakdowns F", "Breakdowns U"]
    k1_rows = pick(t1, ["Setup time (s) F", "Setup time (s) U",
                        "Calibration time (s) F", "Calibration time (s) U"])
    k1_bd = pick(t2, ["Breakdowns F", "Breakdowns U"])
    k1_rows = [r + b[1:] for r, b in zip(k1_rows, k1_bd)]

    k2_labels = ["NASA-TLX F", "NASA-TLX U", "SUS F", "SUS U",
                 "Confidence (1-7) F", "Confidence (1-7) U"]
    k2_rows = pick(t1, k2_labels)

    k3_labels = ["Gaze accuracy (deg) F", "Gaze accuracy (deg) U",
                 "Gaze precision (deg) F", "Gaze precision (deg) U",
                 r"Valid data yield (\%) F", r"Valid data yield (\%) U",
                 "First-pass F", "First-pass U"]
    k3_rows = pick(t2, k3_labels)

    k4_labels = [r"EDA baseline (uS) F", r"EDA baseline (uS) U"]
    k4_rows = pick(t3, k4_labels)

    new_tables = "\n\n".join([
        _k_table_latex("1",
            "Per-participant efficiency and interaction breakdowns. Setup "
            "time, calibration time, and interaction breakdown counts for "
            "each participant (N = 12) in both conditions.",
            k1_labels, k1_rows, landscape=False),
        _k_table_latex("2",
            "Per-participant subjective measures. Raw NASA-TLX, System "
            "Usability Scale, and calibration confidence for each "
            "participant (N = 12) in both conditions.",
            k2_labels, k2_rows, landscape=False),
        _k_table_latex("3",
            "Per-participant eye-tracking calibration quality. Gaze "
            "accuracy, gaze precision, valid data yield, and first-pass "
            "calibration success for each participant (N = 12) in both "
            "conditions.",
            k3_labels, k3_rows, landscape=True),
        _k_table_latex("4",
            "Per-participant mean resting EDA baseline. Mean resting "
            "electrodermal activity in microsiemens for each participant "
            "(N = 12) in both conditions.",
            k4_labels, k4_rows, landscape=False),
    ])

    start = t1[0].start()
    # the span to replace runs from t1's table through t3's trailing caption
    t3_end = t3[0].end()
    tail = text[t3_end:]
    cap_m = re.match(r"\n\n\\textbf\{Table[^\n]*\n", tail)
    end = t3_end + (cap_m.end() if cap_m else 0)

    return text[:start] + new_tables + "\n" + text[end:], True


def add_appendix_k_reference(text):
    """Point readers at the four (post-restructure) Appendix K tables from
    its own intro paragraph. No-ops if that paragraph no longer matches
    (e.g. the docx has since been edited to include its own reference)."""
    anchor = ("First-pass calibration success is recorded as pass or fail.")
    addition = (
        " Tables K.1 to K.4 report this dataset grouped by measure type: "
        "K.1 covers setup and calibration efficiency together with "
        "interaction breakdown counts; K.2 covers the subjective measures "
        "(NASA-TLX, SUS, and calibration confidence); K.3 covers "
        "eye-tracking calibration quality; and K.4 covers the EDA baseline.")
    if anchor not in text or addition in text:
        return text, False
    return text.replace(anchor, anchor + addition, 1), True


def tighten_list_quotes(text):
    """Collapse the "\\item\\n \\begin{quote} ... \\end{quote}" pattern that
    Word's list indentation produces back into a plain list item. The nested
    quote doubles the vertical space around every item, which (e.g.) pushed
    the consent-form signature block (Appendix D) onto an orphan page."""
    pat = re.compile(r"\\item\n\s*\\begin\{quote\}\n(.*?)\n\s*\\end\{quote\}",
                     re.DOTALL)
    text, n = pat.subn(
        lambda m: "\\item\n  " + m.group(1).strip(), text)
    return text, n


def frame_appendix_info_blocks(text):
    """Draw a rule above and below the reproduced-form header block (title,
    Study title/Researcher/Supervisor) that opens Appendix C and D, so it
    reads as a distinct letterhead rather than blending into the form body.
    """
    pat = re.compile(
        r"(\\textbf\{(?:Participant Information Sheet|Informed Consent Form)"
        r"\}\n\n"
        r"\\textbf\{Study title:\}[^\n]*\n\n"
        r"\\textbf\{Researcher:\}[^\n]*\n\n"
        r"\\textbf\{Supervisor:\}[^\n]*)")
    rule = r"\noindent\rule{\linewidth}{0.4pt}"
    return pat.subn(lambda m: "%s\n\n%s\n\n%s" % (rule, m.group(1), rule),
                     text)


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
        r"\\(section|subsection|subsubsection|paragraph)\{"
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
                # Word spacer headings hold only a line break (\hfill\break):
                # dropping them avoids a stray empty paragraph that forces a
                # blank page (e.g. after the Appendix H/I attached PDFs).
                if not re.sub(r"\\hfill|\\break|\\newline|\\\\|\s", "", title):
                    return ""
                count += 1
                # Start the Unified session-observation sheet on a fresh page.
                prefix = ("\\clearpage\n"
                          if "Session Observation Sheet (Unified)" in title
                          else "")
                return "%s\\textbf{%s}" % (prefix, title)
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


# Usable text lines on a page (letter, 1in margins). A unit estimated at or
# under this many normalsize-line-equivalents is forced to stay together.
PAGE_LINES = 43


def _plain_lines(latex, width=95):
    """Rough number of text lines a LaTeX paragraph occupies."""
    plain = re.sub(r"\\[a-zA-Z]+\s*|[{}\\]", "", latex).strip()
    return max(1, -(-len(plain) // width)) if plain else 0


def reserve_table_units(text):
    """Keep each portrait table on one page together with its heading, intro
    sentence and caption. Runs after shrink_wide_tables, so a table already
    dropped to \\footnotesize is measured at that smaller size. Landscape
    tables are skipped — pdflscape already isolates them on their own page.

    For each portrait longtable it estimates the height of the whole unit
    (optional heading block + optional one-line intro paragraph immediately
    above + table + caption below). If that fits on a page, a single
    \\Needspace covering the unit is inserted at its top so the group moves to
    the next page as a whole rather than splitting across a page break.
    """
    lt_re = re.compile(r"\\begin\{longtable\}.*?\\end\{longtable\}", re.DOTALL)
    # process last-to-first so earlier match offsets stay valid after inserts
    for m in reversed(list(lt_re.finditer(text))):
        tstart, tend = m.start(), m.end()
        if "\\begin{landscape}" in text[max(0, tstart - 200):tstart]:
            continue
        block = m.group(0)
        ncols = block.count(r"\arraybackslash}p{")
        if ncols < 2:
            continue
        nrows = len(_CELL_RE.findall(block)) // ncols
        pre120 = text[max(0, tstart - 120):tstart]
        footnote = "\\let\\small\\footnotesize" in pre120
        wide_rows = "\\renewcommand{\\longtablestretch}" in pre120
        row_factor = 1.05 if footnote else (1.65 if wide_rows else 1.28)
        # caption directly below
        after = text[tend:tend + 500]
        cap_m = re.match(r"\n\n(\\textbf\{Table\s[^\n]*)", after)
        cap_lines = _plain_lines(cap_m.group(1)) + 0.5 if cap_m else 0
        # Grab the maximal prefix directly above the table: an optional
        # heading block, an optional one-line intro paragraph, and the
        # optional \footnotesize wrapper. \Z anchors it to the table's start.
        # (?<=\n) forces every candidate start to sit at a line boundary, so
        # search can't begin mid-token (e.g. just after the backslash of a
        # \textbf heading, which would split it and corrupt the file).
        prefix_re = re.compile(
            r"(?<=\n)"
            r"(?P<head>\\hypertarget\{[^}]*\}\{%\n"
            r"\\(?:paragraph|subsubsection)\{[^\n]*\}\}\n\n)?"
            r"(?P<intro>(?!\\)[^\n]+\n\n)?"
            r"(?P<wrap>\\begingroup"
            r"(?:\\let\\small\\footnotesize|\\renewcommand\{\\longtablestretch\})"
            r"[^\n]*\n)?\Z")
        pm = prefix_re.search(text[:tstart])
        if pm is None:
            continue
        extra = 0.0
        if pm.group("head"):
            extra += 2.6
        if pm.group("intro"):
            extra += _plain_lines(pm.group("intro")) + 0.3
        unit_start = pm.start()
        total = nrows * row_factor + 3.0 + cap_lines + extra + 1.0
        if total > PAGE_LINES:
            continue
        text = (text[:unit_start] + "\\Needspace{%.0f\\baselineskip}\n"
                % round(total) + text[unit_start:])
    return text


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


def normalize_caption_bold(text):
    """Word sometimes bolds more than the figure/table label in a caption, e.g.
    ``\\textbf{Figure 3.21 EDA calibration, Step 1:}`` (the whole prefix) or a
    mid-word ``\\textbf{Figure 5.1 S}etup`` (a stray bold run). Restrict the
    bold to just the "Figure X.Y" / "Table X.Y" label so caption styling is
    uniform and the keep-together wrapper (which keys on ``\\textbf{Figure
    X.Y}``) recognises the caption. Runs before the caption lists are built."""
    pat = re.compile(
        r"^\\textbf\{(Figure|Table) ((?:\d+|[A-Z])\.\d+)( [^}\n]*?)\}",
        re.MULTILINE)
    text, n = pat.subn(
        lambda m: "\\textbf{%s %s}%s" % (m.group(1), m.group(2), m.group(3)),
        text)
    return text, n


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
    marker = re.compile(r"\{\[\}add PDF\s*\{\]\}", re.IGNORECASE)
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


# Figure L.1 is a tall portrait screenshot; scale it down so it and L.2 share a
# page. The other Appendix L screenshots are landscape and take a taller box.
_APPENDIX_L_SIZE = {
    "L.1": r"height=0.36\textheight,max width=\linewidth,keepaspectratio",
}
_APPENDIX_L_DEFAULT = r"height=0.34\textheight,max width=\linewidth,keepaspectratio"


def format_appendix_l(text):
    """Appendix L is a run of screenshots that the docx glues inline to their
    captions, so captions don't sit under the images, most are missing from the
    List of Figures, and the figures don't break across pages cleanly. Rebuild
    every Appendix L figure as a figure[H] with the image centred and the
    caption underneath it left-aligned (matching every other figure caption in
    the thesis), a List-of-Figures entry, and breathing room between figures.
    Figure L.1 (a tall portrait screenshot) is scaled up ~20% over the other L
    figures while still sharing a page with L.2."""
    start = text.find(r"\textbf{Appendix L:")
    if start == -1:
        return text, 0
    end = text.find(r"\textbf{Appendix M:", start)
    if end == -1:
        end = len(text)
    block = text[start:end]

    # 1. Collapse any existing rebuilt figure[H] wrapper (from an earlier run,
    #    either the \centering form or the \begin{center} form) back to the
    #    inline form the other L figures use, so a single pass can rebuild
    #    them all uniformly.
    block = re.sub(
        r"\\begin\{figure\}\[H\]\s*"
        r"(?:\\centering\s*\\includegraphics\[[^\]]*\]\{(media/media/image\d+\.png)\}"
        r"|\\begin\{center\}\\includegraphics\[[^\]]*\]\{(media/media/image\d+\.png)\}"
        r"\\end\{center\})\s*"
        r"\\phantomsection\\addcontentsline\{lof\}[^\n]*\n"
        r"(\\textbf\{Figure L\.\d+\}[^\n]*)\n\\end\{figure\}",
        lambda m: "\\includegraphics{%s}%s" % (m.group(1) or m.group(2), m.group(3)),
        block, flags=re.DOTALL)

    # 2. Rebuild each inline "image + caption" pair as a figure[H] with the
    #    image centred (via a {center} environment around the image only) and
    #    the caption left-aligned underneath, matching every other figure in
    #    the thesis.
    fig_re = re.compile(
        r"\\includegraphics(?:\[[^\]]*\])?\{(media/media/image\d+\.png)\}"
        r"\\textbf\{Figure (L\.\d+)\}([^\n]*)")
    count = [0]

    def rebuild(m):
        img, num, rest = m.group(1), m.group(2), m.group(3)
        size = _APPENDIX_L_SIZE.get(num, _APPENDIX_L_DEFAULT)
        short = rest.strip().split(". ")[0]
        short = re.sub(r"\\[a-zA-Z]+\s*", "", short)
        short = re.sub(r"[{}]", "", short).strip(" .") + "."
        count[0] += 1
        return (
            "\\begin{figure}[H]\n"
            "\\begin{center}\\includegraphics[%s]{%s}\\end{center}\n\n"
            "\\phantomsection\\addcontentsline{lof}{figure}"
            "{\\protect\\numberline{%s}%s}%%\n"
            "\\textbf{Figure %s}%s\n"
            "\\end{figure}\n\n\\vspace{1.5em}\n"
            % (size, img, num, short, num, rest.rstrip()))

    block = fig_re.sub(rebuild, block)
    return text[:start] + block + text[end:], count[0]


def sectionize_backmatter(text):
    """The docx leaves four back-matter headings as plain \\textbf{} paragraphs
    (Appendix L, Appendix M, the AI-tools disclosure, and the Declaration).
    Appendix L/M are promoted to \\subsection, matching Appendices A-K (they
    nest under the "Appendices" \\section). The AI-tools disclosure and the
    Declaration are standalone back-matter chapters, not appendices, so they
    are promoted to \\section instead, matching Acknowledgements/Abstract/the
    numbered chapters/List of References/Appendices in both weight and Table
    of Contents indent. Also push the Declaration's signature (name + date)
    to the foot of its page."""
    headings = [
        (r"\textbf{Appendix L: Screenshots of Fragmented workflow tools}",
         "subsection", "appendix-l",
         "Appendix L: Screenshots of Fragmented workflow tools"),
        (r"\textbf{Appendix M: Google Doc Study Documentation template}",
         "subsection", "appendix-m",
         "Appendix M: Google Doc Study Documentation template"),
        (r"\textbf{Information on the use of AI-based tools}",
         "section", "information-on-the-use-of-ai-based-tools",
         "Information on the use of AI-based tools"),
        (r"\textbf{Declaration}", "section", "declaration-final", "Declaration"),
    ]
    n = 0
    for bold, level, tag, title in headings:
        repl = ("\\clearpage\n\\hypertarget{%s}{%%\n\\%s{%s}"
                "\\label{%s}}" % (tag, level, title, tag))
        new = text.replace(bold, repl, 1)
        if new != text:
            n += 1
            text = new

    # Declaration signature to the bottom of the page.
    text = text.replace(
        "\nDaniyal Admany\n\nDuisburg, 15.07.2026\n",
        "\n\\vfill\n\nDaniyal Admany\n\nDuisburg, 15.07.2026\n\\vspace{2cm}\n",
        1)
    return text, n


def insert_figure_318(text, base_dir):
    """Insert Figure 3.18 (the successful-validation screenshot, supplied
    separately as assets/figure-3.18.png) with its caption after the paragraph
    that introduces Figures 3.18 and 3.19. The docx references 3.18 but omits
    the figure. No-ops until the asset is present."""
    asset = "assets/figure-3.18.png"
    if not os.path.exists(os.path.join(base_dir, asset)):
        return text, False
    anchor = "visibility of system status (Nielsen, 1994)."
    idx = text.find(anchor)
    if idx == -1:
        return text, False
    pos = idx + len(anchor)
    short = ("Eye-tracking calibration, Step 4: Validation, showing a "
             "successful calibration.")
    caption = (
        "Eye-tracking calibration, Step 4: Validation, showing a successful "
        "calibration. A green success banner sits above a scatter plot of the "
        "five-point grid, showing the intended gaze target against the computed "
        "gaze position for each point. A collapsible table below reports the "
        "colour-coded metrics: gaze accuracy, gaze precision, valid data yield, "
        "points detected, recalibration attempts, the pass threshold, and the "
        "overall result.")
    block = (
        "\n\n\\begin{figure}[H]\n\\centering\n"
        "\\includegraphics[max width=\\linewidth,max totalheight=0.78"
        "\\textheight]{%s}\n\n"
        "\\phantomsection\\addcontentsline{lof}{figure}"
        "{\\protect\\numberline{3.18}%s}%%\n"
        "\\textbf{Figure 3.18} %s\n\\end{figure}" % (asset, short, caption))
    return text[:pos] + block + text[pos:], True


_TITLE_PAGE = r"""
\begin{titlepage}
\centering
{\includegraphics[width=6cm]{assets/hsrw-logo.png}\par}
\vspace{0.6cm}
{\large Hochschule Rhein-Waal\par}
{\large Rhine-Waal University of Applied Sciences\par}
\vspace{0.3cm}
{\large Faculty of Communication and Environment\par}
\vspace{1.4cm}
{\large Prof. Dr. Kai Essig\par}
{\large André Frank Krause\par}
\vspace{1.6cm}
{\LARGE\bfseries %(title)s\par}
\vspace{1.6cm}
{\large Master Thesis\par}
\vspace{0.3cm}
{\large Submitted to the Degree of Master of Science\par}
{\large in\par}
{\large Usability Engineering\par}
\vspace{1.4cm}
{\large by Daniyal Admany\par}
{\large Matriculation number: 35795\par}
\vspace{0.3cm}
{\large Submission Date: 15.07.2026\par}
\vfill
\end{titlepage}
"""


_ACKNOWLEDGEMENTS = r"""\clearpage
\hypertarget{acknowledgements}{}%
\section{Acknowledgements}

I would like to thank my supervisor, Prof. Dr. Kai Essig, whose guidance and feedback shaped this work at every stage and consistently pushed it to be clearer and more rigorous than I would have managed alone. And to my second supervisor, Dr. André Frank Krause, for his time and considered input.

Big thanks to Sarthak and Shilton, without whose efforts, the Sensa prototype would not have been built. Running from the campus to the bus stop to catch the last SB30 back to Duisburg has been a core part of my experience during this programme, and it was apt that the last few months reflected that. And to Renu for her help, snacks, and company in the lab. And of course to the twelve participants, whose patience and honesty made this study possible.

To my family, thank you for everything. To my mother especially, who always wanted me to do a Master's: this one is for you. And to my friends, thank you for always (trying to) keeping me grounded.
"""


def restructure_front_matter(text):
    """Thesis layout for the self-contained docx front matter: wrap the opening
    block (logo, faculty, supervisors, title, degree) in a real title page;
    replace Word's static TOC with a live one; roman page numbers for the front
    matter; arabic numbering restarting at the Introduction; drop the
    "[added in Latex]" placeholders and empty spacer sections; every
    chapter/appendix on a new page.

    The docx now carries its own title page, Acknowledgements, Abstract and a
    static Table of Contents, so this step re-styles what the author supplied
    rather than synthesising front matter from scratch."""
    notes = []

    # 1. Drop Word's empty numbered spacer headings (blank TOC entries).
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

    # 2b. Drop the bare empty section Word leaves before the Introduction
    #     (now that step 2 has reduced it to an empty \section{}).
    text, n = re.subn(
        r"\\hypertarget\{section\}\{%\n"
        r"\\section\{\s*\}\\label\{section\}\}\n?",
        "", text)
    notes.append("%d empty sections removed" % n)

    # 3. The docx supplies its own title page (logo, faculty, supervisors,
    #    title, degree) as the block between \begin{document} and the
    #    Acknowledgements. Wrap it in a centred {titlepage} and start roman
    #    page numbering for the rest of the front matter.
    title_pat = re.compile(
        r"(\\begin\{document\})\n+(.*?)\n+(?=\\hypertarget\{acknowledgements\})",
        re.DOTALL)

    def title_repl(m):
        body = m.group(2).strip()
        # Shrink the university logo to 32% of the text width (20% smaller
        # than the previous 40%), and add breathing room before the faculty/
        # supervisor lines that follow it.
        body = re.sub(
            r"\\includegraphics\[[^\]]*\]\{(media/media/image\d+\.png)\}",
            r"\\includegraphics[width=0.32\\linewidth]{\1}\n\n\\vspace{0.8cm}",
            body, count=1)
        # Give the thesis title breathing room above and below, and set it
        # larger than the surrounding lines.
        body = re.sub(
            r"\\textbf\{([^}]+)\}",
            r"\\vspace{1.6cm}\n\n{\\Large\\bfseries \1\\par}\n\n\\vspace{1.6cm}",
            body, count=1)
        # Add breathing room before the "by <author>" / matriculation /
        # submission-date block at the foot of the title page.
        body = re.sub(
            r"\n\n(by Daniyal Admany)",
            r"\n\n\\vspace{0.8cm}\n\n\1", body, count=1)
        return (m.group(1)
                + "\n\\begin{titlepage}\n\\centering\n\\vspace*{\\fill}\n\n"
                + body
                + "\n\n\\vspace*{\\fill}\n\\end{titlepage}\n\n"
                + "\\pagenumbering{roman}\n\\setcounter{tocdepth}{4}\n")

    text, n = title_pat.subn(title_repl, text)
    notes.append("title page: %s" % bool(n))

    # 4. Replace Word's static TOC (heading + hyperlinked entries) with a live
    #    \tableofcontents. Roman numbering is already set by step 3 above.
    toc_pat = re.compile(
        r"\\hypertarget\{table-of-contents\}\{%\n"
        r"\\section\{[^\n]*\}\\label\{table-of-contents\}\}\n"
        r".*?(?=\\hypertarget\{list-of-abbreviations\})",
        re.DOTALL)
    text, n = toc_pat.subn(
        "\\\\clearpage\n\\\\tableofcontents\n\\\\clearpage\n\n", text)
    notes.append("live TOC: %s" % bool(n))

    # 4b. Drop the "[added in Latex]" placeholder heading the author left where
    #     the generated lists go, and the stray "[added in latex]" note that
    #     sits under the List of Figures / List of Tables lists.
    text, n = re.subn(
        r"(?:\\clearpage\n)?\\hypertarget\{added-in-latex\}\{%\n"
        r"\\section\{.*?\}\\label\{added-in-latex\}\}\n?",
        "", text, flags=re.DOTALL)
    notes.append("added-in-latex heading removed: %s" % bool(n))
    text, n = re.subn(r"\n\{\[\}added in latex\{\]\}\n", "\n", text)
    notes.append("added-in-latex note removed: %s" % bool(n))

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
    text, disclosure_done = update_disclosure_declaration(text)
    text = demote_caption_headings(text)
    text, appendix_headers_demoted = demote_appendix_subheaders(text)
    text = apply_text_edits(text)
    text, captions_normalized = normalize_caption_bold(text)
    text, list_quotes_tightened = tighten_list_quotes(text)
    text = fix_formulas(text)
    text = align_cells_top(text)
    text, table_5_1_done = restructure_table_5_1(text)
    text, table_k_done = restructure_appendix_k(text)
    text, k_ref_added = add_appendix_k_reference(text)
    text, appendix_blocks_framed = frame_appendix_info_blocks(text)
    text = resize_images(text, base_dir)
    text, fig326_replaced = replace_figure_326_image(text, base_dir)
    text = shrink_wide_tables(text)
    text = reserve_table_units(text)
    text, diagrams = insert_diagrams(text, base_dir)
    text, lists_done = add_figure_table_lists(text)
    text = wrap_figures_with_captions(text)[0]
    text, fig318_inserted = insert_figure_318(text, base_dir)
    text, appendix_l_figs = format_appendix_l(text)
    text, abbr_done = inject_abbreviations(text, base_dir)
    text, refs_done = format_references(text)
    text, appendices, missing = attach_appendix_pdfs(text, base_dir)
    text, backmatter_sections = sectionize_backmatter(text)
    text, fm_notes = restructure_front_matter(text)

    with open(tex, "w", encoding="utf-8") as fh:
        fh.write(text)

    n_plots = text.count(r"\includegraphics[width=" + PLOT_WIDTH)
    n_shots = text.count(r"\includegraphics[max width=\linewidth")
    n_wide = text.count(r"\begingroup\let\small\footnotesize")
    print("postprocess: %d plots shrunk, %d screenshots capped, "
          "%d wide tables set to footnotesize" % (n_plots, n_shots, n_wide))
    print("postprocess: diagrams inserted: %s" % (", ".join(diagrams) or "none"))
    print("postprocess: caption bold normalized: %d" % captions_normalized)
    print("postprocess: LoF/LoT placeholder replaced: %s" % bool(lists_done))
    print("postprocess: abbreviations injected: %s" % abbr_done)
    print("postprocess: references hanging indent: %s" % refs_done)
    print("postprocess: appendix PDFs attached: %s"
          % (", ".join(appendices) or "none"))
    print("postprocess: front matter: %s" % fm_notes)
    print("postprocess: figure 3.18 inserted: %s" % fig318_inserted)
    print("postprocess: appendix L figures reformatted: %d" % appendix_l_figs)
    print("postprocess: back-matter sections promoted: %d" % backmatter_sections)
    print("postprocess: figure 3.26 image replaced: %s" % fig326_replaced)
    print("postprocess: appendix sub-headers demoted: %d"
          % appendix_headers_demoted)
    print("postprocess: table 5.1 restructured: %s" % table_5_1_done)
    print("postprocess: appendix K restructured (K.1-K.4): %s" % table_k_done)
    print("postprocess: appendix K body reference added: %s" % k_ref_added)
    print("postprocess: appendix C/D info blocks framed: %d"
          % appendix_blocks_framed)
    print("postprocess: AI disclosure/declaration updated: %s"
          % disclosure_done)
    print("postprocess: list-quote wrappers collapsed: %d"
          % list_quotes_tightened)
    for p in missing:
        print("postprocess: NOTE - awaiting %s" % p)


if __name__ == "__main__":
    main()
