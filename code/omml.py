"""omml.py -- real Word equation objects (Office Math, OMML) for every displayed equation.

Each entry of EQUATIONS is keyed by the marked-up text that docbuilder.equation() receives, so call sites
need no change.  Output is native OMML: Word shows it as an editable equation; LibreOffice renders it as a formula.
"""
from xml.sax.saxutils import escape

NS = ('xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
      'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"')
FONT = '<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math" w:cs="Cambria Math"/><w:sz w:val="24"/></w:rPr>'


def R(t, sty=None):
    """Run.  sty: None (italic variable), 'p' (upright), 'b' (bold), 'bi' (bold italic)."""
    pr = f'<m:rPr><m:sty m:val="{sty}"/></m:rPr>' if sty else ""
    return f'<m:r>{pr}{FONT}<m:t xml:space="preserve">{escape(t)}</m:t></m:r>'


def P(t):      # upright text (function names, words)
    return R(t, "p")


def V(t):      # bold italic vector symbol
    return R(t, "bi")


def sub(b, s):
    return f"<m:sSub><m:e>{b}</m:e><m:sub>{s}</m:sub></m:sSub>"


def sup(b, s):
    return f"<m:sSup><m:e>{b}</m:e><m:sup>{s}</m:sup></m:sSup>"


def subsup(b, s, u):
    return f"<m:sSubSup><m:e>{b}</m:e><m:sub>{s}</m:sub><m:sup>{u}</m:sup></m:sSubSup>"


def frac(n, d):
    return f"<m:f><m:num>{n}</m:num><m:den>{d}</m:den></m:f>"


def delim(beg, end, *items, sep=None):
    s = f'<m:sepChr m:val="{sep}"/>' if sep else ""
    es = "".join(f"<m:e>{i}</m:e>" for i in items)
    return f'<m:d><m:dPr><m:begChr m:val="{beg}"/>{s}<m:endChr m:val="{end}"/></m:dPr>{es}</m:d>'


def nary(ch, lo, body):
    return (f'<m:nary><m:naryPr><m:chr m:val="{ch}"/><m:limLoc m:val="undOvr"/><m:supHide m:val="1"/></m:naryPr>'
            f"<m:sub>{lo}</m:sub><m:sup/><m:e>{body}</m:e></m:nary>")


def minlim(lo, body):
    return (f"<m:func><m:fName><m:limLow><m:e>{P('min')}</m:e><m:lim>{lo}</m:lim></m:limLow></m:fName>"
            f"<m:e>{body}</m:e></m:func>")


def fn(name, arg):
    return f"<m:func><m:fName>{P(name)}</m:fName><m:e>{arg}</m:e></m:func>"


def wrap(*parts):
    return f"<m:oMath {NS}>" + "".join(parts) + "</m:oMath>"


ell, d_, x_, y_, z_, w_, r_, R_, rho = R("ℓ"), R("d"), V("x"), V("y"), R("z"), R("w"), R("r"), R("R"), R("ρ")
i_, j_, k_, p_, m_ = R("i"), R("j"), R("k"), R("p"), R("m")
bar = lambda t: delim("|", "|", t)

EQUATIONS = {
    # Equation 1: sphere distance
    "cos <i>d</i> = <b><i>x</i></b> · <b><i>y</i></b>": wrap(P("cos"), R(" "), d_, R("="), x_, R("·"), y_),
    # Equation 2: hyperboloid distance
    "cosh <i>d</i> = −[<b><i>x</i></b>, <b><i>y</i></b>]": wrap(P("cosh"), R(" "), d_, R("=−"), delim("[", "]", x_, y_, sep=",")),
    # Equation 3: Poincare disk distance
    "cosh <i>d</i> = 1 + 2|<i>z</i> − <i>w</i>|<sup>2</sup> / [(1 − |<i>z</i>|<sup>2</sup>)(1 − |<i>w</i>|<sup>2</sup>)]":
        wrap(P("cosh"), R(" "), d_, R("=1+"),
             frac(R("2") + sup(bar(z_ + R("−") + w_), R("2")),
                  delim("(", ")", R("1−") + sup(bar(z_), R("2"))) + delim("(", ")", R("1−") + sup(bar(w_), R("2"))))),
    # Equation 4: areas
    "Area(<i>r</i>) = 2π(1 − cos <i>r</i>) on <i>S</i><sup>2</sup>;  π<i>r</i><sup>2</sup> on <i>R</i><sup>2</sup>;  2π(cosh <i>r</i> − cosh0) on <i>H</i><sup>2</sup>": None,
    # Equation 5: l_min
    "<i>ℓ</i><sub>min</sub> = min{ min<sub><i>i</i> < <i>j</i></sub> <i>d</i><sub><i>ij</i></sub>, min<sub><i>i</i></sub> 2(<i>R</i> − <i>ρ</i><sub><i>i</i></sub>) }":
        wrap(sub(ell, P("min")), R("="), delim("{", "}",
             minlim(i_ + R("<") + j_, sub(d_, i_ + j_)),
             minlim(i_, R("2") + delim("(", ")", R_ + R("−") + sub(rho, i_))), sep=",")),
    # Equation 6: soft minimum energy
    "<i>E<sub>p</sub></i> = (1/<i>p</i>) ln Σ<sub><i>k</i></sub> <i>ℓ<sub>k</sub></i><sup>−<i>p</i></sup>":
        wrap(sub(R("E"), p_), R("="), frac(R("1"), p_), fn("ln", nary("∑", k_, subsup(ell, k_, R("−") + p_)))),
    # Equation 7: bounds
    "−ln <i>ℓ</i><sub>min</sub> ≤ <i>E<sub>p</sub></i> ≤ −ln <i>ℓ</i><sub>min</sub> + (ln <i>m</i>)/<i>p</i>":
        wrap(R("−"), fn("ln", sub(ell, P("min"))), R("≤"), sub(R("E"), p_), R("≤−"), fn("ln", sub(ell, P("min"))),
             R("+"), frac(fn("ln", m_), p_)),
}
# Equation 4 is written explicitly (the key above is a placeholder removed here).
EQUATIONS.pop([k for k in EQUATIONS if k.startswith("Area(")][0])
EQUATIONS["Area(<i>r</i>) = 2π(1 − cos <i>r</i>) on <i>S</i><sup>2</sup>;  π<i>r</i><sup>2</sup> on <i>R</i><sup>2</sup>;  2π(cosh <i>r</i> − 1) on <i>H</i><sup>2</sup>"] = wrap(
    P("Area"), delim("(", ")", r_), R("="), R("2π"), delim("(", ")", R("1−") + P("cos") + R(" ") + r_), P("  on  "), sup(R("S"), R("2")),
    R(";   "), R("π") + sup(r_, R("2")), P("  on  "), sup(R("R"), R("2")),
    R(";   "), R("2π"), delim("(", ")", P("cosh") + R(" ") + r_ + R("−1")), P("  on  "), sup(R("H"), R("2")))


# ---------------------------------------------------------------------------------------------
# PDF variant: LibreOffice (used to make the PDF) may lack its Math module, so for the PDF every
# displayed equation is typeset by matplotlib's mathtext (STIX fonts) and placed inline as a picture.
# The .docx keeps the native editable equations above.  MODE is "image" while the PDF is built and
# "omml" for the final .docx.
# ---------------------------------------------------------------------------------------------
MODE = "image"
LATEX = {
    "cos <i>d</i> = <b><i>x</i></b> · <b><i>y</i></b>": r"$\cos d=\mathbf{x}\cdot\mathbf{y}$",
    "cosh <i>d</i> = −[<b><i>x</i></b>, <b><i>y</i></b>]": r"$\cosh d=-[\mathbf{x},\mathbf{y}]$",
    "cosh <i>d</i> = 1 + 2|<i>z</i> − <i>w</i>|<sup>2</sup> / [(1 − |<i>z</i>|<sup>2</sup>)(1 − |<i>w</i>|<sup>2</sup>)]":
        r"$\cosh d=1+\dfrac{2\,|z-w|^{2}}{\left(1-|z|^{2}\right)\left(1-|w|^{2}\right)}$",
    "Area(<i>r</i>) = 2π(1 − cos <i>r</i>) on <i>S</i><sup>2</sup>;  π<i>r</i><sup>2</sup> on <i>R</i><sup>2</sup>;  2π(cosh <i>r</i> − 1) on <i>H</i><sup>2</sup>":
        r"$\mathrm{Area}(r)=2\pi(1-\cos r)\ \mathrm{on}\ S^{2};\ \ \pi r^{2}\ \mathrm{on}\ R^{2};\ \ 2\pi(\cosh r-1)\ \mathrm{on}\ H^{2}$",
    "<i>ℓ</i><sub>min</sub> = min{ min<sub><i>i</i> < <i>j</i></sub> <i>d</i><sub><i>ij</i></sub>, min<sub><i>i</i></sub> 2(<i>R</i> − <i>ρ</i><sub><i>i</i></sub>) }":
        r"$\ell_{\min}=\min\left\{\min_{i<j}d_{ij},\ \min_{i}\,2(R-\rho_{i})\right\}$",
    "<i>E<sub>p</sub></i> = (1/<i>p</i>) ln Σ<sub><i>k</i></sub> <i>ℓ<sub>k</sub></i><sup>−<i>p</i></sup>":
        r"$E_{p}=\dfrac{1}{p}\,\ln\sum_{k}\ell_{k}^{-p}$",
    "−ln <i>ℓ</i><sub>min</sub> ≤ <i>E<sub>p</sub></i> ≤ −ln <i>ℓ</i><sub>min</sub> + (ln <i>m</i>)/<i>p</i>":
        r"$-\ln\ell_{\min}\ \leq\ E_{p}\ \leq\ -\ln\ell_{\min}+\dfrac{\ln m}{p}$",
}


def render_png(key, outdir):
    """Typeset one equation to a transparent PNG; returns (path, width_in, height_in)."""
    import os, hashlib
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "eq_" + hashlib.md5(key.encode()).hexdigest()[:10] + ".png")
    meta = path + ".txt"
    if not (os.path.exists(path) and os.path.exists(meta)):
        plt.rcParams["mathtext.fontset"] = "stix"
        fig = plt.figure(figsize=(7, 1.2), dpi=450)
        t = fig.text(0.02, 0.5, LATEX[key], fontsize=13, va="baseline", ha="left")
        fig.canvas.draw()
        bb = t.get_window_extent(fig.canvas.get_renderer())
        base_y = 0.5 * fig.get_figheight() * 450
        descent_px = base_y - bb.y0          # extent of the equation below its baseline
        fig.savefig(path, dpi=450, transparent=True, bbox_inches="tight", pad_inches=0.03)
        plt.close(fig)
        open(meta, "w").write("%.6f" % float(descent_px / 450.0 + 0.03))
    descent_in = float(open(meta).read())
    w, h = Image.open(path).size
    return path, w / 450.0, h / 450.0, descent_in
