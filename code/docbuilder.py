"""docbuilder.py -- APA 7 student-paper DOCX builder (python-docx + raw XML).

Used for Research_Paper, Research_Plan and Code_Listing.  Features: exact title
page, header page numbers, APA heading levels, APA tables (three rules), APA
figures, hanging-indent references, a Table of Contents wrapped in a real Word
TOC field, and list pages with spaced dot leaders computed from font metrics.
"""
import re
import subprocess
import os
import copy
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER, WD_BREAK
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import ImageFont

FONT = "Times New Roman"
TITLE = "Algorithmic Optimization of Dense Sphere Packings in Non-Euclidean Spaces"
AUTHOR = "Marian Ela J. Alibadbad"
CATEGORY = "Mathematics and Computational Science \u2013 Individual Category (MCS-I)"
REGION = "Region VIII"
_FDIR = "/usr/share/fonts/truetype/liberation/"
_FONTS = {}


def _font(bold=False, size=12):
    key = (bold, size)
    if key not in _FONTS:
        f = "LiberationSerif-Bold.ttf" if bold else "LiberationSerif-Regular.ttf"
        _FONTS[key] = ImageFont.truetype(_FDIR + f, size * 10)  # 10x for precision
    return _FONTS[key]


def text_width_pt(text, bold=False, size=12):
    return _font(bold, size).getlength(text) / 10.0


def set_run_font(run, name=FONT, size=12, bold=None, italic=None, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), name)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


def _style_font(style, name=FONT, size=12, bold=False, italic=False):
    style.font.name = name
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = italic
    style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.insert(0, rf)
    for a in list(rf.attrib):
        del rf.attrib[a]
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), name)


def add_field(paragraph, instr, result_text="", bold=None):
    """Insert a complex field (begin/instr/separate/result/end) into a paragraph."""
    def fc(t):
        r = paragraph.add_run()
        e = OxmlElement("w:fldChar")
        e.set(qn("w:fldCharType"), t)
        r._element.append(e)
        return r
    fc("begin")
    r = paragraph.add_run()
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = " " + instr + " "
    r._element.append(it)
    fc("separate")
    rr = paragraph.add_run(result_text)
    set_run_font(rr, bold=bold)
    fc("end")


MARK = re.compile(r"(<i>|</i>|<b>|</b>|<sup>|</sup>|<sub>|</sub>)")


class APADoc:
    def __init__(self, title=TITLE, landscape_code=False):
        self.title = title
        d = self.doc = Document()
        sec = d.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(sec, m, Inches(1))
        sec.header_distance = Inches(0.5)
        sec.footer_distance = Inches(0.5)
        self._styles()
        self._header(sec)
        d.core_properties.title = title
        d.core_properties.author = AUTHOR
        d.core_properties.subject = "NSTF SY 2026-2027, MCS-I"
        d.core_properties.keywords = ""
        d.core_properties.comments = ""
        self.headings = []   # (level, text)
        self.captions = []   # (kind, num, title)
        self.nfig = 0
        self.ntab = 0

    # ---------------------------------------------------------------- styles
    def _styles(self):
        st = self.doc.styles
        n = st["Normal"]
        _style_font(n)
        pf = n.paragraph_format
        pf.line_spacing = 2.0
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        pf.widow_control = True
        for lvl in (1, 2, 3, 4, 5):
            h = st["Heading %d" % lvl]
            _style_font(h, bold=True, italic=lvl in (3, 5))
            hp = h.paragraph_format
            hp.line_spacing = 2.0
            hp.space_before = Pt(0)
            hp.space_after = Pt(0)
            hp.keep_with_next = True
            hp.first_line_indent = Inches(0.5) if lvl >= 4 else Inches(0)
            hp.left_indent = Inches(0)
            hp.alignment = WD_ALIGN_PARAGRAPH.CENTER if lvl == 1 else WD_ALIGN_PARAGRAPH.LEFT
        for name in ("TOC 1", "TOC 2", "TOC 3"):
            try:
                s = st[name]
            except KeyError:
                s = st.add_style(name, 1)
            _style_font(s, bold=(name == "TOC 1"))
            s.paragraph_format.line_spacing = 2.0
            s.paragraph_format.space_after = Pt(0)
            s.paragraph_format.keep_together = True
        st["TOC 1"].paragraph_format.left_indent = Inches(0)
        st["TOC 2"].paragraph_format.left_indent = Inches(0.5)
        st["TOC 3"].paragraph_format.left_indent = Inches(1.0)
        for nm in ("TOC 1", "TOC 2", "TOC 3"):
            ts = st[nm].paragraph_format.tab_stops
            ts.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

    def _header(self, sec):
        hdr = sec.header
        hdr.is_linked_to_previous = False
        p = hdr.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.line_spacing = 1.0
        add_field(p, "PAGE", "1")
        for r in p.runs:
            set_run_font(r)

    # ----------------------------------------------------------- basic blocks
    def _para(self, style=None, align=None, indent_first=None, spacing=None, left=None,
              hanging=None, keep_next=False, space_before=None, space_after=None):
        p = self.doc.add_paragraph(style=style)
        pf = p.paragraph_format
        if align is not None:
            pf.alignment = align
        if indent_first is not None:
            pf.first_line_indent = Inches(indent_first)
        if left is not None:
            pf.left_indent = Inches(left)
        if hanging is not None:
            pf.left_indent = Inches(hanging if left is None else left)
            pf.first_line_indent = Inches(-hanging)
        if spacing is not None:
            pf.line_spacing = spacing
        if keep_next:
            pf.keep_with_next = True
        if space_before is not None:
            pf.space_before = Pt(space_before)
        if space_after is not None:
            pf.space_after = Pt(space_after)
        return p

    def add_marked(self, p, text, bold=False, italic=False, size=12):
        """Add text with <i>, <b>, <sup>, <sub> inline markup."""
        b, i, sup, sub = bold, italic, False, False
        for tok in MARK.split(text):
            if tok == "<i>": i = True
            elif tok == "</i>": i = italic
            elif tok == "<b>": b = True
            elif tok == "</b>": b = bold
            elif tok == "<sup>": sup = True
            elif tok == "</sup>": sup = False
            elif tok == "<sub>": sub = True
            elif tok == "</sub>": sub = False
            elif tok:
                r = p.add_run(tok)
                set_run_font(r, size=size, bold=b, italic=i)
                if sup: r.font.superscript = True
                if sub: r.font.subscript = True
        return p

    def body(self, text, indent=True, keep_next=False):
        p = self._para(indent_first=0.5 if indent else 0.0, align=WD_ALIGN_PARAGRAPH.LEFT, keep_next=keep_next)
        self.add_marked(p, text)
        return p

    def front_heading(self, text):
        """Centered bold heading that is NOT collected by the TOC field (no outline level)."""
        st = self.doc.styles
        try:
            fh = st["Front Heading"]
        except KeyError:
            fh = st.add_style("Front Heading", 1)
            fh.base_style = st["Normal"]
            _style_font(fh, bold=True)
            fh.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            fh.paragraph_format.keep_with_next = True
            fh.paragraph_format.line_spacing = 2.0
        p = self.doc.add_paragraph(style="Front Heading")
        set_run_font(p.add_run(text), bold=True)
        return p

    def heading(self, text, level=1):
        p = self.doc.add_paragraph(style="Heading %d" % level)
        if level >= 4:
            text = text if text.endswith(".") else text + "."
        r = p.add_run(text)
        set_run_font(r, bold=True, italic=level in (3, 5))
        self.headings.append((level, text))
        return p

    def inline_heading_body(self, text, level, body_text):
        """APA level 4/5: heading ends with a period and body continues on the same line."""
        p = self.doc.add_paragraph(style="Heading %d" % level)
        r = p.add_run(text.rstrip(".") + ".")
        set_run_font(r, bold=True, italic=level == 5)
        p.paragraph_format.keep_with_next = False
        r2 = p.add_run(" ")
        set_run_font(r2, bold=False, italic=False)
        self.add_marked(p, body_text)
        self.headings.append((level, text.rstrip(".") + "."))
        return p

    def new_page(self):
        """Next-page section break (only break type used)."""
        self.doc.add_section(WD_SECTION.NEW_PAGE)
        sec = self.doc.sections[-1]
        sec.header.is_linked_to_previous = True

    # -------------------------------------------------------------- title page
    def title_page(self, date_text):
        p = self._para(align=WD_ALIGN_PARAGRAPH.CENTER, space_before=72)
        r = p.add_run(self.title)
        set_run_font(r, bold=True)
        first = True
        for line in (AUTHOR, REGION, CATEGORY, date_text):
            p = self._para(align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24 if first else 0)
            first = False
            r = p.add_run(line)
            set_run_font(r)

    # ------------------------------------------------------------------ tables
    def _cell_border(self, cell, **kw):
        tcPr = cell._element.get_or_add_tcPr()
        b = tcPr.find(qn("w:tcBorders"))
        if b is None:
            b = OxmlElement("w:tcBorders")
            tcPr.append(b)
        for edge, val in kw.items():
            e = OxmlElement("w:" + edge)
            e.set(qn("w:val"), val)
            e.set(qn("w:sz"), "8")
            e.set(qn("w:space"), "0")
            e.set(qn("w:color"), "000000")
            b.append(e)

    def table(self, title, header, rows, note, aligns=None, widths=None, bold_cells=None, label=None, split=False):
        """APA table: number line, italic title, three horizontal rules, Note."""
        if label is None:
            self.ntab += 1
            n = self.ntab
        else:
            n = label
        self.captions.append(("Table", n, title))
        p = self._para(keep_next=True, align=WD_ALIGN_PARAGRAPH.LEFT)
        set_run_font(p.add_run("Table "), bold=True)
        if label is None:
            add_field(p, "SEQ Table \\* ARABIC", str(n), bold=True)
        else:
            set_run_font(p.add_run(str(n)), bold=True)
        p = self._para(keep_next=True, align=WD_ALIGN_PARAGRAPH.LEFT)
        set_run_font(p.add_run(title), italic=True)
        ncol = len(header)
        t = self.doc.add_table(rows=1 + len(rows), cols=ncol)
        t.autofit = False
        t.alignment = 0
        tblPr = t._element.tblPr
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        tblPr.append(lay)
        total = 6.5
        widths = widths or [total / ncol] * ncol
        aligns = aligns or ["l"] + ["c"] * (ncol - 1)
        amap = {"l": WD_ALIGN_PARAGRAPH.LEFT, "c": WD_ALIGN_PARAGRAPH.CENTER, "r": WD_ALIGN_PARAGRAPH.RIGHT}
        bold_cells = bold_cells or set()
        for ci, w_ in enumerate(widths):
            t.columns[ci].width = Inches(w_)
        for ri in range(1 + len(rows)):
            row = t.rows[ri]
            trPr = row._tr.get_or_add_trPr()
            cs = OxmlElement("w:cantSplit")
            trPr.append(cs)
            if split and ri == 0:
                trPr.append(OxmlElement("w:tblHeader"))        # header row repeats on the next page
            for ci in range(ncol):
                c = row.cells[ci]
                c.width = Inches(widths[ci])
                txt = header[ci] if ri == 0 else rows[ri - 1][ci]
                para = c.paragraphs[0]
                para.paragraph_format.line_spacing = 1.0
                para.paragraph_format.keep_with_next = (ri < 2 or ri >= len(rows) - 1) if split else (bool(note) or ri < len(rows))
                para.paragraph_format.alignment = amap["c"] if ri == 0 and aligns[ci] != "l" else amap[aligns[ci]]
                self.add_marked(para, str(txt), bold=(ri > 0 and (ri - 1, ci) in bold_cells))
                if ri == 0:
                    self._cell_border(c, top="single", bottom="single")
                if ri == len(rows):
                    self._cell_border(c, bottom="single")
        if note:
            p = self._para(align=WD_ALIGN_PARAGRAPH.LEFT)
            set_run_font(p.add_run("Note"), italic=True)
            set_run_font(p.add_run(". "))
            self.add_marked(p, note)
        return n

    # ----------------------------------------------------------------- figures
    def figure(self, title, image_path, width_in, caption, legend, alt):
        """Image, then the caption (identifies and describes the figure), then the legend
        (explains symbols, colors, lines, markers, abbreviations, units).  All three stay together."""
        self.nfig += 1
        n = self.nfig
        self.captions.append(("Figure", n, title))
        p = self._para(keep_next=True, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0)
        run = p.add_run()
        run.add_picture(image_path, width=Inches(width_in))
        dp = run._element.find(".//" + qn("wp:docPr"))
        if dp is not None:
            dp.set("descr", alt)
            dp.set("title", "Figure %d" % n)
        p = self._para(keep_next=bool(legend), align=WD_ALIGN_PARAGRAPH.LEFT)
        set_run_font(p.add_run("Figure "), bold=True)
        add_field(p, "SEQ Figure \\* ARABIC", str(n), bold=True)
        set_run_font(p.add_run("."), bold=True)
        set_run_font(p.add_run(" "))
        set_run_font(p.add_run(title + "."), italic=True)
        set_run_font(p.add_run(" "))
        self.add_marked(p, caption)
        if legend:
            p = self._para(align=WD_ALIGN_PARAGRAPH.LEFT)
            set_run_font(p.add_run("Legend."), italic=True)
            set_run_font(p.add_run(" "))
            self.add_marked(p, legend)
        return n

    def equation(self, text, number):
        p = self._para(align=WD_ALIGN_PARAGRAPH.LEFT, indent_first=0.0)
        ts = p.paragraph_format.tab_stops
        ts.add_tab_stop(Inches(3.25), WD_TAB_ALIGNMENT.CENTER)
        ts.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)
        p.add_run("\t")
        import omml
        from docx.oxml import parse_xml
        if omml.MODE == "image" and text in omml.LATEX:
            png, w_in, h_in, desc_in = omml.render_png(text, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out", "eq"))
            run = p.add_run()
            run.add_picture(png, height=Inches(h_in))
            raise_hp = int(round(desc_in * 72 * 2))                # equation number is raised to the equation baseline
        elif text in omml.EQUATIONS:
            p._p.append(parse_xml(omml.EQUATIONS[text]))     # native Word equation (OMML)
        else:
            self.add_marked(p, text)
        p.add_run("\t")
        numrun = p.add_run("(%d)" % number)
        set_run_font(numrun)
        if omml.MODE == "image" and text in omml.LATEX:
            pos = OxmlElement("w:position")
            pos.set(qn("w:val"), str(raise_hp))
            numrun._r.get_or_add_rPr().append(pos)
        for r in p.runs:
            set_run_font(r, italic=r.italic)
        return p

    def reference(self, text):
        p = self._para(hanging=0.5, align=WD_ALIGN_PARAGRAPH.LEFT)
        self.add_marked(p, text)
        return p

    # ------------------------------------------------- contents-type pages
    def _dots_line(self, p, text, page, bold, left_in, first_hang_in, num_col=None, stop_in=6.0,
                   page_col_in=6.5, title_x=None):
        """Entry with spaced dot leader.  The dots end at stop_in; the page number is
        right-aligned at page_col_in.  Handles wrapped titles by simulating word wrap."""
        unit = ". "
        uw = text_width_pt(unit)
        avail_first = (stop_in - left_in) * 72.0
        # wrap simulation for the title text
        words = text.split(" ")
        lines, cur = [], ""
        limit = (stop_in - left_in) * 72.0 - 36.0
        for w in words:
            trial = (cur + " " + w).strip()
            if text_width_pt(trial, bold) <= limit:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        last = lines[-1]
        lastw = text_width_pt(last, bold)
        offset = 0.0 if len(lines) > 1 else 0.0
        room = (stop_in - left_in) * 72.0 - lastw - text_width_pt(" ")
        if len(lines) > 1:
            room += 0  # continuation lines start at the same hanging indent
        count = max(int(room // uw), 1)
        return lines, count

    def entry(self, p, text, page, bold, left_in, hang_in, num=None, num_col_w=0.75):
        """Write one contents entry into paragraph p (already created)."""
        pf = p.paragraph_format
        pf.line_spacing = 2.0
        pf.space_after = Pt(0)
        pf.keep_together = True
        ts = pf.tab_stops
        if num is not None:
            # list-of-tables/figures entry: number at margin, title at 0.75 in hanging indent
            pf.left_indent = Inches(num_col_w)
            pf.first_line_indent = Inches(-num_col_w)
            ts.add_tab_stop(Inches(num_col_w), WD_TAB_ALIGNMENT.LEFT)
            r = p.add_run(str(num) + "\t")
            set_run_font(r, bold=False)
            left_eff = num_col_w
        else:
            pf.left_indent = Inches(left_in + hang_in)
            pf.first_line_indent = Inches(-hang_in)
            left_eff = left_in + hang_in
        ts.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)
        lines, count = self._dots_line(p, text, page, bold, left_eff, hang_in)
        # emit wrapped title as words (Word wraps on its own; widths identical in
        # Times New Roman / Liberation Serif)
        r = p.add_run(text + " ")
        set_run_font(r, bold=bold)
        r = p.add_run((". " * count).rstrip(" ") + " ")
        set_run_font(r, bold=False)
        r = p.add_run("\t" + str(page))
        set_run_font(r, bold=bold)

    def contents_page(self, heading, label, entries, kind, field_instr=None, in_toc=False):
        """kind 'toc' : entries = [(level, text, page)]
           kind 'list': entries = [(num, title, page)]"""
        if in_toc:
            self.heading(heading, 1)
        else:
            self.front_heading(heading)
        p = self._para(spacing=2.0, space_after=0, align=WD_ALIGN_PARAGRAPH.LEFT)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.5), WD_TAB_ALIGNMENT.RIGHT)
        set_run_font(p.add_run(label), bold=True)
        set_run_font(p.add_run("\t"), bold=True)
        set_run_font(p.add_run("Page"), bold=True)
        paras = []
        for e in entries:
            if kind == "toc":
                lvl, text, page = e
                p = self.doc.add_paragraph(style="TOC %d" % lvl)
                self.entry(p, text, page, bold=(lvl == 1), left_in={1: 0.0, 2: 0.5, 3: 1.0}[lvl], hang_in=0.0)
            else:
                num, title, page = e
                p = self.doc.add_paragraph()
                self.entry(p, title, page, bold=False, left_in=0.0, hang_in=0.0, num=num)
            paras.append(p)
        if kind == "toc" and field_instr and paras:
            # wrap the cached entries in a real TOC field
            first, last = paras[0], paras[-1]
            def fc(par, t, at_start):
                r = OxmlElement("w:r")
                e = OxmlElement("w:fldChar")
                e.set(qn("w:fldCharType"), t)
                r.append(e)
                if at_start:
                    par._p.insert(par._p.index(par._p.pPr) + 1 if par._p.pPr is not None else 0, r)
                else:
                    par._p.append(r)
            def instr(par):
                r = OxmlElement("w:r")
                it = OxmlElement("w:instrText")
                it.set(qn("xml:space"), "preserve")
                it.text = " " + field_instr + " "
                r.append(it)
                par._p.insert(par._p.index(par._p.pPr) + 1, r)
            # begin, instr, separate must precede the first entry text (insert in reverse)
            for t in ("separate", None, "begin"):
                if t is None:
                    instr(first)
                else:
                    fc(first, t, True)
            fc(last, "end", False)
        return paras

    def save(self, path):
        self.doc.save(path)


# ---------------------------------------------------------------- conversion
def to_pdf(docx_path, outdir):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", outdir, docx_path],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
    return os.path.join(outdir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")


def pdf_pages(pdf_path):
    import pdfplumber
    out = []
    with pdfplumber.open(pdf_path) as pdf:
        for pg in pdf.pages:
            out.append(pg.extract_text() or "")
    return out


def find_pages(pages, items, start_page=0):
    """items: list of strings.  Returns first page number (1-based, >= start_page+1) whose
    text contains each string at the start of a line; 0 if missing."""
    res = []
    for s in items:
        found = 0
        norm = " ".join(s.split())
        for i in range(start_page, len(pages)):
            for line in pages[i].split("\n"):
                if " ".join(line.split()).startswith(norm[:60]):
                    found = i + 1
                    break
            if found:
                break
        res.append(found)
    return res


def find_exact(pages, items, start_page=0):
    """First page (1-based) with a line exactly equal to each string; 0 if missing."""
    res = []
    for s in items:
        found = 0
        for i in range(start_page, len(pages)):
            if any(" ".join(l.split()) == s for l in pages[i].split("\n")):
                found = i + 1
                break
        res.append(found)
    return res
