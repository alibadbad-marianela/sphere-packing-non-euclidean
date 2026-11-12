"""make_code_listing.py -- builds Code_Listing.docx (all code, syntax-colored, line-numbered)."""
import os
import sys
import json
import platform
import importlib.metadata as md
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token
from docbuilder import *
from docx.enum.text import WD_LINE_SPACING

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # folder that contains code/ and out/
OUT = os.path.join(ROOT, "out")
CODE = os.path.join(ROOT, "code")
LISTING_DATE = "December 3, 2026"
MONO = "Courier New"
SIZE = 9
GAP_ABOVE = 4.0      # extra space (pt) between the code above and the text
GAP_BELOW = 13.9      # extra space (pt) between the text and the code below
WIDTH = 112          # code characters per line in landscape (9 in at 9 pt Courier New, minus line numbers)

FILES = [
    ("build_all.py", "Master script. Runs the unit tests, all experiments, the statistics, the figures, and builds every deliverable."),
    ("geometry.py", "Geometry of the sphere, the hyperbolic plane (hyperboloid model), and the Euclidean plane: distances, gradients, exponential maps, sampling."),
    ("algorithms.py", "The packing problems and the three optimizers: gradient descent on a soft-minimum energy, simulated annealing, and compression."),
    ("tests.py", "Validation tests: closed-form distances, metric axioms, finite-difference gradients, and the known Tammes optima for 4, 6, and 12 points."),
    ("experiments.py", "Runs every condition with 30 paired seeds under an equal budget and writes the raw CSV files."),
    ("analyze.py", "Summary statistics, Friedman and Wilcoxon tests with Holm correction, effect sizes, and the hypothesis tests."),
    ("make_figures.py", "All figures, drawn only from the CSV files, with the mathematical accuracy assertions."),
    ("docbuilder.py", "Shared APA 7 document builder used for the plan, paper, and this listing."),
    ("make_plan.py", "Builds the Research Plan (written before the experiments)."),
    ("make_paper.py", "Builds the Research Paper; every number and table value is read from the CSV files."),
    ("make_code_listing.py", "Builds this code listing."),
    ("make_package.py", "Builds the data package: README, seed list, SHA-256 manifest, and the ZIP file."),
    ("supplementary.py", "Supplementary exploratory analyses of the first study: equal area, sensitivity, polished gradient descent, timing, checks."),
    ("supp_section.py", "Writes the Supplementary Exploratory Analyses section of the paper from the supplementary CSV files."),
    ("omml.py", "Native Word equations and their image versions."),
    ("newalgs.py", "Added baselines of the confirmatory round: SciPy L-BFGS-B and basin hopping on the soft-minimum energy."),
    ("confirm_design.py", "Conditions, reference densities, boundary share, and density deficit of the confirmatory round."),
    ("record_env.py", "Records hardware and software versions."),
    ("confirm_tune.py", "Equal-effort pilot tuning of all six methods on pilot seeds 9101 to 9104."),
    ("confirm_run.py", "Runs the confirmatory round: fresh seeds 101 to 120, three budgets, six methods."),
    ("confirm_count.py", "Count-based version of the disk problem (exploratory)."),
    ("confirm_analyze.py", "Analysis of the confirmatory round exactly as preregistered."),
    ("conf_figures.py", "Figures of the confirmatory round."),
    ("conf_section.py", "Writes the Confirmatory Round section of the paper from the conf_* files."),
    ("confirm_configs.py", "Reruns the confirmatory round with the same seeds and saves every final configuration (configs/cfg_<cid>.npz) and the wall metrics."),
    ("confirm_retune.py", "Extended candidate grids for compression and L-BFGS-B on the pilot conditions (ADDENDUM 1)."),
    ("confirm_run_retuned.py", "Reruns compression and L-BFGS-B on the confirmatory conditions with the re-tuned parameters."),
    ("confirm_extra.py", "Post-hoc analyses of ADDENDUM 1 (re-tuned baselines, wall metrics) and the boundary-loss model."),
    ("confirm_mini.py", "Matched-boundary mini-round: design, runs, and rules M1 to M3."),
    ("confirm_followup.py", "Follow-up to the mini-round: two methods, rules F1 to F3, and L-BFGS-B on the mini-round conditions."),
    ("confirm_round3.py", "Final preregistered round: equal-area balls (part A) and the predictive rule for the number of disks (part B)."),
    ("r3_section.py", "Writes the Final Round section of the paper from the round-3 files."),
    ("checks.py", "Automated checks of the final DOCX and PDF files."),
    ("fill.py", "Helper that reports unused space at the bottom of each PDF page."),
    ("pilot.py", "Pilot runs on separate seeds used to check speed and sanity before tuning."),
    ("tune.py", "Pilot tuning of gradient descent and simulated annealing on seeds 9001 to 9004."),
    ("tune2.py", "Further pilot tuning of gradient descent and compression."),
    ("tune3.py", "Final pilot tuning of the compression method."),
]

COL = {Token.Keyword: "0033B3", Token.Literal.String: "067D17", Token.Comment: "7A7A7A", Token.Literal.Number: "1750EB",
       Token.Name.Builtin: "871094", Token.Name.Function: "00627A", Token.Name.Class: "00627A", Token.Name.Decorator: "9E880D",
       Token.Operator.Word: "0033B3"}


def color_of(tt):
    while tt is not None:
        if tt in COL:
            return COL[tt], tt in (Token.Comment,) or str(tt).startswith("Token.Comment")
        tt = tt.parent
    return None, False


def shade(p):
    ppr = p._p.get_or_add_pPr()
    bd = OxmlElement("w:pBdr")
    for edge in ("top", "left", "bottom", "right"):
        e = OxmlElement("w:" + edge)
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), "4")
        e.set(qn("w:space"), "3")
        e.set(qn("w:color"), "BFBFBF")
        bd.append(e)
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), "F2F2F2")
    after = ("tabs", "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN",
             "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
             "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange")
    nxt = next((c for c in ppr if c.tag in [qn("w:" + t) for t in after]), None)
    for el in (bd, sh):
        if nxt is not None:
            nxt.addprevious(el)
        else:
            ppr.append(el)
    # the box edge sits on the page margin: indent the text by the border space plus the line width
    p.paragraph_format.left_indent = Pt(3.5)
    p.paragraph_format.right_indent = Pt(3.5)


def line_runs(src):
    """Return a list (one per source line) of lists of (text, color, italic)."""
    lines = [[]]
    for tt, val in lex(src, PythonLexer()):
        c, it = color_of(tt)
        parts = val.split("\n")
        for k, part in enumerate(parts):
            if k > 0:
                lines.append([])
            if part:
                lines[-1].append((part.replace("\t", "    "), c, it))
    if lines and not lines[-1]:
        lines.pop()
    return lines


def add_code(d, src):
    lines = line_runs(src)
    for no, runs in enumerate(lines, 1):
        chunks, cur, n = [], [], 0
        for text, c, it in runs:
            while text:
                room = WIDTH - n
                if room <= 0:
                    chunks.append(cur)
                    cur, n = [], 0
                    continue
                piece, text = text[:room], text[room:]
                cur.append((piece, c, it))
                n += len(piece)
        chunks.append(cur)
        for k, ch in enumerate(chunks):
            p = d.doc.add_paragraph()
            pf = p.paragraph_format
            pf.line_spacing = 1.0
            pf.space_after = Pt(0)
            pf.space_before = Pt(0)
            pf.first_line_indent = Inches(0)
            pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
            shade(p)
            lab = f"{no:>4}  " if k == 0 else "    \u21b3 "
            r = p.add_run(lab)
            set_run_font(r, name=MONO, size=SIZE, color="8C8C8C")
            for text, c, it in ch:
                r = p.add_run(text)
                set_run_font(r, name=MONO, size=SIZE, color=c if c else "000000", italic=it or None)
    return len(lines)


def between(p, before=0.0, after=0.0):
    """Text between code blocks: exact double spacing, with equal room above and below."""
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(27.6)
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)


def landscape_section(d):
    d.doc.add_section(WD_SECTION.NEW_PAGE)
    sec = d.doc.sections[-1]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Inches(11), Inches(8.5)
    sec.header.is_linked_to_previous = True


REPORTED = [("Python", "3.12.3"), ("numpy", "2.4.4"), ("scipy", "1.17.1"), ("pandas", "3.0.2"), ("matplotlib", "3.10.8"),
            ("python-docx", "1.2.0"), ("Pygments", "2.20.0"), ("pdfplumber", "0.11.9"), ("Pillow", "12.1.1")]


def versions():
    return REPORTED


def _versions_current():
    out = [("Python", platform.python_version())]
    for pk in ("numpy", "scipy", "pandas", "matplotlib", "python-docx", "Pygments", "pdfplumber", "Pillow"):
        try:
            out.append((pk, md.version(pk)))
        except md.PackageNotFoundError:
            pass
    return out


def build(pg):
    d = APADoc(title=TITLE)
    d.title_page(LISTING_DATE)
    d.new_page()
    d.contents_page("Table of Contents", "Chapter", pg["toc"], "toc", field_instr='TOC \\o "1-3" \\z \\u')
    d.new_page()
    p = d._para(align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run_font(p.add_run(TITLE), bold=True)
    d.heading("How to Run the Code", 1)
    d.body("This document lists all code used in the study. The sections below give the software environment and the exact commands that reproduce every result.")
    d.heading("Software Environment", 2)
    d.body("The reported runs used the versions below; an independent full rerun (python3 build_all.py --rerun) under Python 3.13.18 with numpy 2.5.3, scipy 1.18.1, pandas 3.0.5, and matplotlib 3.11.2 reproduced every score, test statistic, and p-value in the CSV files exactly; only the wall-clock times differ. No other libraries are needed, and the optimizers use only numpy and scipy-compatible routines from numpy.")
    for name, v in versions():
        p = d._para(indent_first=0.0, left=0.5, spacing=1.0)
        d.add_marked(p, f"{name} {v}")
    p.paragraph_format.space_after = Pt(13.8)   # the list ends one double-spaced step above the next heading
    d.heading("Commands", 2)
    d.body("Place all files listed below in one folder and run the commands in that order. The first command runs the validation tests and stops if any test fails. The second command runs the unit tests, all experiments, the statistics, the figures, and the builds of the plan, paper, listing, and data package; add --rerun to recompute every run from scratch (about 17 minutes on one core for the first study). Seeds 1 to 30 are used for evaluation and are fixed, so a rerun reproduces every value. Run them from that folder.")
    for cmd in ("python3 tests.py", "python3 build_all.py", "python3 build_all.py --rerun"):
        p = d._para(indent_first=0.0, left=0.5, spacing=1.0)
        set_run_font(p.add_run(cmd), name=MONO, size=SIZE)
    landscape_section(d)
    between(d.heading("Source Code Listing", 1))
    between(d.body("Each file is listed in full with line numbers and syntax colors. A long line continues on the next row, marked with an arrow, and its indentation is kept."))
    total = 0
    for fn, desc in FILES:
        between(d.heading(fn, 2), before=GAP_ABOVE)
        between(d.body(desc), after=GAP_BELOW)
        src = open(f"{CODE}/{fn}").read()
        total += add_code(d, src)
    between(d.heading("Unit Test Output", 1), before=GAP_ABOVE)
    between(d.body("The output below is the complete result of running python3 tests.py before the experiments."), after=GAP_BELOW)
    add_code_text = open(f"{OUT}/unit_test_output.txt").read()
    for line in add_code_text.rstrip("\n").split("\n"):
        p = d.doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.first_line_indent = Inches(0)
        shade(p)
        txt = line
        while True:
            r = p.add_run(txt[:WIDTH + 6])
            set_run_font(r, name=MONO, size=SIZE)
            txt = txt[WIDTH + 6:]
            if not txt:
                break
            p = d.doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.first_line_indent = Inches(0)
            shade(p)
    return d, total


def main():
    d0, total = build({"toc": []})
    entries = [(l, t) for l, t in d0.headings]
    pg = {"toc": [(l, t, 0) for l, t in entries]}
    for it in range(4):
        d, total = build(pg)
        path = OUT + "/Code_Listing.docx"
        d.save(path)
        pdf = to_pdf(path, OUT)
        pages = pdf_pages(pdf)
        body0 = next(i for i in range(1, len(pages)) if any(l.strip().startswith("Algorithmic Optimization") for l in pages[i].split("\n")[:4]))
        newtoc = []
        for l, t, _ in pg["toc"]:
            pnum = find_exact(pages, [t], start_page=body0)[0]
            newtoc.append((l, t, pnum))
        new = {"toc": newtoc}
        if new == pg:
            break
        pg = new
    print("listing pages:", len(pages), "| code lines:", total, "| missing:", [e for e in pg["toc"] if not e[2]])


if __name__ == "__main__":
    main()
