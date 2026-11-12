"""checks.py -- automated final checks on the DOCX and PDF files (Section 9)."""
import os
import re
import sys
import zipfile
import pdfplumber
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn
from lxml import etree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # folder that contains code/ and out/
OUT = os.path.join(ROOT, "out")
TITLE = "Algorithmic Optimization of Dense Sphere Packings in Non-Euclidean Spaces"
res = []


def rec(name, ok, detail=""):
    res.append((name, ok, detail))
    print(("PASS  " if ok else "FAIL  ") + name + ("  [" + detail + "]" if detail else ""))


def pdf_checks(path, label, is_paper):
    with pdfplumber.open(path) as pdf:
        pages = pdf.pages
        texts = [p.extract_text() or "" for p in pages]
        # margins: all words within 1 inch (72 pt) except header number
        bad = 0
        for i, p in enumerate(pages):
            for w in p.extract_words():
                if w["top"] < 72 and w["x0"] > 72:   # header zone (page number)
                    continue
                if w["x0"] < 71.5 or w["x1"] > 612 - 71.5 or w["bottom"] > 792 - 71.5:
                    bad += 1
        rec(f"{label}: no body text outside the 1-inch margins", bad == 0, f"{bad} words outside")
        # blank pages
        short = [i + 1 for i, t in enumerate(texts) if i > 0 and len(t.strip()) < 100]
        rec(f"{label}: no blank or near-empty pages (>=100 characters)", not short, f"short pages: {short}")
        # page numbers at top right
        okn = True
        for i, p in enumerate(pages):
            ws = [w for w in p.extract_words() if w["top"] < 60]
            if not ws or ws[-1]["text"] != str(i + 1) or ws[-1]["x1"] < 612 - 80:
                okn = False
        rec(f"{label}: page number at top right on every page (including title page)", okn)
        # title page lines
        t1 = [l.strip() for l in texts[0].split("\n")][1:]
        rec(f"{label}: title page contains title (wrapped), name, region, category, date and nothing else",
            " ".join(t1[:-4]).replace("  ", " ") == TITLE and t1[-4:] == ["Marian Ela J. Alibadbad", "Region VIII",
            "Mathematics and Computational Science \u2013 Individual Category (MCS-I)", t1[-1]], str(t1))
        # body page fill check (between required breaks)
        fills = []
        start = None
        for i, t in enumerate(texts):
            if t.split("\n")[1:2] and t.split("\n")[1].strip().startswith("Algorithmic Optimization") and i > 1:
                start = i
                break
        stop = None
        for i, t in enumerate(texts):
            ls = [l.strip() for l in t.split("\n")[1:3]]
            if i > (start or 0) and ls and ls[0] in ("References",):
                stop = i
                break
        stop = stop or len(pages)
        for i in range(start or 0, stop - 1):     # last body page before References may be short
            p = pages[i]
            ws = [w for w in p.extract_words() if w["top"] > 72]
            lowest = max(w["bottom"] for w in ws)
            imgs = p.images
            if imgs:
                lowest = max(lowest, max(im["bottom"] for im in imgs))
            free = (792 - 72 - lowest) / 72
            if free > 3.0:
                fills.append((i + 1, round(free, 2)))
        rec(f"{label}: no body page has more than 3 inches of unused space at the bottom", not fills, f"pages: {fills}")
        return texts


def docx_checks(path, label):
    d = Document(path)
    cp = d.core_properties
    rec(f"{label}: DOCX title property exact and author set", cp.title == TITLE and cp.author == "Marian Ela J. Alibadbad", f"{cp.title!r} / {cp.author!r}")
    # fonts: scan XML for any font other than Times New Roman in text runs (code listing excepted)
    z = zipfile.ZipFile(path)
    xml = z.read("word/document.xml").decode("utf8")
    fonts = set(re.findall(r'w:ascii="([^"]+)"', xml))
    sizes = set(re.findall(r'<w:sz w:val="(\d+)"', xml))
    rec(f"{label}: all run fonts are Times New Roman", fonts <= {"Times New Roman", "Cambria Math"}, str(fonts) + " (Cambria Math only inside native equations)")
    heads = [p.text for p in Document(path).paragraphs if p.style.name.startswith("Heading") and "Appendix" in p.text]
    rec(f"{label}: appendix headings are the two appendices of the paper or the history appendix of the plan", (len(heads) == 2) if "Paper" in label else (len(heads) == 1 and heads[0].startswith("Appendix A: History")), str(heads))
    rec(f"{label}: all explicit run sizes are 12 pt (24 half-points) or sub/superscript only", sizes <= {"24"}, str(sizes))
    sec = d.sections[0]
    rec(f"{label}: page 8.5 x 11 in with 1-inch margins", all(abs(getattr(sec, m).inches - 1.0) < 1e-6 for m in ("left_margin", "right_margin", "top_margin", "bottom_margin")) and abs(sec.page_width.inches - 8.5) < 1e-6 and abs(sec.page_height.inches - 11) < 1e-6)
    # section breaks are all next-page
    types = re.findall(r'<w:type w:val="(\w+)"', xml)
    rec(f"{label}: only next-page section breaks", all(t == "nextPage" for t in types) , str(set(types)))
    # no empty spacer paragraphs
    empties = sum(1 for p in d.paragraphs if not p.text.strip() and not p._p.xpath(".//w:drawing") and not p._p.xpath(".//w:sectPr") and not p._p.xpath(".//w:fldChar"))
    rec(f"{label}: no empty spacer paragraphs", empties == 0, f"{empties} empty")
    # headings: none is a question, none ends in period/colon (levels 1-3)
    bad = [p.text for p in d.paragraphs if p.style.name.startswith("Heading") and (p.text.strip().endswith("?") or p.text.strip().endswith(":") or p.text.strip().endswith("."))]
    rec(f"{label}: no heading is a question or ends with punctuation", not bad, str(bad))
    # tables: exactly three horizontal rules, no vertical lines, no shading
    ok = True
    for t in d.tables:
        x = etree.tostring(t._tbl).decode()
        if "<w:left" in x or "<w:right" in x or "<w:shd" in x or "<w:insideH" in x or "<w:insideV" in x:
            ok = False
        nrow = len(t.rows)
        for ri, row in enumerate(t.rows):
            rx = etree.tostring(row._tr).decode()
            has_top = "<w:top " in rx
            has_bot = "<w:bottom " in rx
            if has_top != (ri == 0) or has_bot != (ri in (0, nrow - 1)):
                ok = False
    rec(f"{label}: every table has exactly three horizontal rules, no vertical lines, no shading", ok, f"{len(d.tables)} tables")
    alt = len(re.findall(r'<wp:docPr [^>]*descr="[^"]+"', xml))
    rec(f"{label}: every picture has alt text", alt == len(d.inline_shapes), f"{alt} of {len(d.inline_shapes)}")


def mentions_before(texts, kind, nmax, start):
    """Each Table/Figure N is mentioned in the running text before its caption appears (wrapped lines handled)."""
    full = ""
    for i, t in enumerate(texts):
        if i >= start:
            full += "\n".join(l for l in t.split("\n")[1:]) + "\n"          # drop the page-number line
    flat = full.replace("\n", " ")
    ok = True
    for n in sorted(set(re.findall(rf"^{kind} ([0-9]+)(?:\.|$)", full, flags=re.M)), key=int):
        cap = re.search(rf"^{kind} {n}(?:\. |$)", full, flags=re.M)
        pos = cap.start()                       # offsets are equal because only newlines became spaces
        mention = re.search(rf"\b{kind} {n}\b", flat)
        # first mention that is not the caption itself
        found = False
        for m in re.finditer(rf"\b{kind} {n}\b", flat):
            if m.start() < pos:
                found = True
                break
        if not found:
            ok = False
            print("   not mentioned before:", kind, n)
    return ok


if __name__ == "__main__":
    t = pdf_checks(f"{OUT}/Research_Paper.pdf", "Paper PDF", True)
    docx_checks(f"{OUT}/Research_Paper.docx", "Paper DOCX")
    start = next(i for i in range(2, len(t)) if t[i].split("\n")[1].strip().startswith("Algorithmic Optimization"))
    rec("Paper: every table is mentioned in the text before it appears", mentions_before(t, "Table", 12, start))
    rec("Paper: every figure is mentioned in the text before it appears", mentions_before(t, "Figure", 8, start))
    refs = [i for i, x in enumerate(t) if x.split("\n")[1].strip() == "References" and i > start]
    rec("Paper: references start on their own page and only the two appendices follow", len(refs) == 1 and refs[0] >= len(t) - 16, f"ref page {refs[0] + 1 if refs else None} of {len(t)}")
    t2 = pdf_checks(f"{OUT}/Research_Plan.pdf", "Plan PDF", False)
    docx_checks(f"{OUT}/Research_Plan.docx", "Plan DOCX")
    bad = [r for r in res if not r[1]]
    print(f"\n{len(res) - len(bad)} of {len(res)} checks passed")
    sys.exit(0 if not bad else 1)
