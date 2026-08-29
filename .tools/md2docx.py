#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将背调报告 Markdown 转为规范 Word（封面/页眉/页脚/标题层级/表格/宋体小四1.5倍）。"""
import re, sys
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

CN_FONT = "宋体"
EN_FONT = "Times New Roman"

def set_run_font(run, size=12, bold=False, color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = EN_FONT
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    rfonts.set(qn('w:ascii'), EN_FONT)
    rfonts.set(qn('w:hAnsi'), EN_FONT)
    rfonts.set(qn('w:eastAsia'), CN_FONT)
    if color:
        run.font.color.rgb = color

def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("第 ")
    set_run_font(run, 9)
    # PAGE field
    fld1 = OxmlElement('w:fldSimple'); fld1.set(qn('w:instr'), 'PAGE')
    run._element.addnext(fld1)
    r2 = p.add_run(" 页 / 共 ")
    set_run_font(r2, 9)
    fld2 = OxmlElement('w:fldSimple'); fld2.set(qn('w:instr'), 'NUMPAGES')
    r2._element.addnext(fld2)
    r3 = p.add_run(" 页")
    set_run_font(r3, 9)

def add_header(section, text):
    hdr = section.header
    p = hdr.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    set_run_font(run, 9, color=RGBColor(0x80,0x80,0x80))

def parse_inline(paragraph, text, base_size=12):
    # split on **bold**
    parts = re.split(r'\*\*(.+?)\*\*', text)
    for i, seg in enumerate(parts):
        if not seg:
            continue
        run = paragraph.add_run(seg)
        set_run_font(run, base_size, bold=(i % 2 == 1))

def convert(md_path, docx_path):
    with open(md_path, encoding='utf-8') as f:
        lines = f.read().split('\n')

    doc = Document()
    # base style
    style = doc.styles['Normal']
    style.font.name = EN_FONT
    style.font.size = Pt(12)
    style._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), CN_FONT)
    pf = style.paragraph_format
    pf.line_spacing = 1.5

    # extract title (first '# ') and date
    title = "背调报告"
    date = ""
    for ln in lines:
        if ln.startswith('# '):
            title = ln[2:].strip()
            break
    for ln in lines:
        m = re.search(r'报告日期\s*\|\s*([\d\-]+)', ln)
        if m:
            date = m.group(1)
            break

    # cover page
    sec = doc.sections[0]
    add_header(sec, "📋 内部使用 · 面试调研报告")
    add_page_number_footer(sec)

    sp = doc.add_paragraph(); sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sp.paragraph_format.space_before = Pt(120)
    cr = sp.add_run(title); set_run_font(cr, 22, bold=True)
    sub = doc.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = sub.add_run("内部使用 · 求职调研"); set_run_font(sr, 14, color=RGBColor(0x60,0x60,0x60))
    if date:
        dp = doc.add_paragraph(); dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        dr = dp.add_run(f"报告日期：{date}"); set_run_font(dr, 12)
    doc.add_page_break()

    i = 0
    n = len(lines)
    in_table = False
    table_rows = []
    while i < n:
        line = lines[i]
        # skip the leading header line and footer end marker
        if line.strip().startswith("📋 内部使用") or line.strip().startswith("— 内部使用"):
            i += 1; continue
        if line.startswith('# '):
            i += 1; continue  # title already on cover
        if line.startswith('## '):
            h = doc.add_heading(level=1)
            parse_inline(h, line[3:].strip())
            i += 1; continue
        if line.startswith('### '):
            h = doc.add_heading(level=2)
            parse_inline(h, line[4:].strip())
            i += 1; continue
        if line.strip().startswith('|'):
            # collect table
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                rows.append(cells)
                i += 1
            # remove separator row like |:---|:---|
            data = [r for r in rows if not all(set(c) <= set(': -') and c for c in r) and not re.fullmatch(r'[:\-\s|]+', '|'.join(r))]
            # simpler: drop rows that are pure separator
            clean = []
            for r in rows:
                if all(re.fullmatch(r':?-+:?', c) for c in r if c != ''):
                    continue
                clean.append(r)
            if clean:
                t = doc.add_table(rows=len(clean), cols=max(len(r) for r in clean))
                t.style = 'Light Grid Accent 1'
                for ri, r in enumerate(clean):
                    for ci, c in enumerate(r):
                        cell = t.cell(ri, ci)
                        cell.text = ''
                        parse_inline(cell.paragraphs[0], c, 10)
            continue
        if line.startswith('> '):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            parse_inline(p, line[2:].strip())
            i += 1; continue
        if line.strip() == '':
            i += 1; continue
        p = doc.add_paragraph()
        parse_inline(p, line.strip())
        i += 1

    doc.save(docx_path)
    print(f"Saved: {docx_path}")

if __name__ == '__main__':
    for pair in sys.argv[1:]:
        md, docx = pair.split('::')
        convert(md, docx)
