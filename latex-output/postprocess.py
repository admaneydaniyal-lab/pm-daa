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
    """Reassign p{} column widths in proportion to each column's longest cell."""
    cells = _CELL_RE.findall(block)
    if not cells or len(cells) % ncols != 0:
        return block  # unexpected shape; leave Pandoc's widths alone
    maxlen = [0] * ncols
    for i, cell in enumerate(cells):
        col = i % ncols
        maxlen[col] = max(maxlen[col], _visual_len(cell))
    pad = 3  # smooths out very short columns so they keep a sane minimum
    weights = [m + pad for m in maxlen]
    total = float(sum(weights))
    fracs = [round(w / total * 0.98, 4) for w in weights]

    it = iter(fracs)
    new_block, n = _REAL_RE.subn(
        lambda mm: mm.group(1) + format(next(it), ".4f") + mm.group(3), block
    )
    return new_block if n == ncols else block


def shrink_wide_tables(text):
    """Rebalance and \\footnotesize every 6+ column longtable."""
    lt_re = re.compile(r"\\begin\{longtable\}.*?\\end\{longtable\}", re.DOTALL)

    def repl(m):
        block = m.group(0)
        ncols = block.count(r"\arraybackslash}p{")  # one per Pandoc p-column
        if ncols >= WIDE_TABLE_COLS:
            block = _rebalance_columns(block, ncols)
            return ("\\begingroup\\let\\small\\footnotesize"
                    "\\setlength{\\tabcolsep}{4pt}\n" + block + "\n\\endgroup")
        return block

    return lt_re.sub(repl, text)


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 postprocess.py document.tex")
    tex = sys.argv[1]
    base_dir = os.path.dirname(os.path.abspath(tex))
    with open(tex, encoding="utf-8") as fh:
        text = fh.read()

    text = resize_images(text, base_dir)
    text = shrink_wide_tables(text)

    with open(tex, "w", encoding="utf-8") as fh:
        fh.write(text)

    n_plots = text.count(r"\includegraphics[width=" + PLOT_WIDTH)
    n_shots = text.count(r"\includegraphics[max width=\linewidth")
    n_wide = text.count(r"\begingroup\let\small\footnotesize")
    print("postprocess: %d plots shrunk, %d screenshots capped, "
          "%d wide tables set to footnotesize" % (n_plots, n_shots, n_wide))


if __name__ == "__main__":
    main()
