# -*- coding: utf-8 -*-
"""Resume generator with PDF export.
用法: python -X utf8 gen_resume.py <md_path> <out_docx_path> --template <template_docx>
"""
import sys, os, re, shutil, tempfile
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import docx
    from docx import Document
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    print("ERROR: python-docx not installed", file=sys.stderr)
    sys.exit(1)

CJK = re.compile(r'[\u2e80-\u9fff\u3000-\u303f\uff00-\uffef]+')
TITLE_MAX = 15


def shorten_title(t):
    m = re.search(r'[（(].*?[）)]', t)
    if m and len(t) > TITLE_MAX:
        return t[:m.start()].strip()
    return t


def parse_md(md_path):
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    d = {"name": "", "contact": "", "intent": "", "summary": "",
         "edu_school": "", "edu_major": "", "edu_degree": "", "edu_dates": "",
         "courses": "", "honors": "",
         "projects": [], "practices": [], "campus": [], "skills": []}
    cur_section = None
    cur_item = None
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith("# "):
            d["name"] = s[2:].strip()
        elif "｜" in s and not s.startswith("**") and not d["contact"]:
            d["contact"] = s
        elif s.startswith("**求职意向**") or s.startswith("**求职意向：**"):
            d["intent"] = re.sub(r"\*\*求职意向[：:]\*\*", "", s).strip()
        elif s.startswith("**个人优势**") or s.startswith("**个人优势：**"):
            d["summary"] = re.sub(r"\*\*个人优势[：:]\*\*", "", s).strip()
        elif s == "## 教育背景":
            cur_section = "edu"
        elif s == "## 项目经历":
            cur_section = "projects"
        elif s == "## 实践经历":
            cur_section = "practices"
        elif s == "## 校园经历":
            cur_section = "campus"
        elif s == "## 综合技能":
            cur_section = "skills"
        elif cur_section == "edu":
            if "**山东大学**" in s or "山东大学" in s:
                m = re.match(r"\*\*([^*]+)\*\*\s*[｜|]\s*([^*]+)\s*[｜|]\s*([^*]+)\s*[｜|]\s*([^*]+)\*\*", s)
                if m:
                    d["edu_school"] = m.group(1).strip()
                    d["edu_major"] = m.group(2).strip()
                    d["edu_degree"] = m.group(3).strip()
                    d["edu_dates"] = m.group(4).replace("**", "").strip()
                else:
                    parts = re.split(r"[｜|]", s)
                    if len(parts) >= 4:
                        d["edu_school"] = parts[0].replace("**", "").strip()
                        d["edu_major"] = parts[1].strip()
                        d["edu_degree"] = parts[2].strip()
                        d["edu_dates"] = parts[3].replace("**", "").strip()
            elif "**核心课程**" in s or "**荣誉奖励**" in s:
                if "**核心课程**" in s:
                    d["courses"] = re.sub(r"\*\*核心课程[：:]\*\*", "", s).strip()
                else:
                    d["honors"] = re.sub(r"\*\*荣誉奖励[：:]\*\*", "", s).strip()
        elif s.startswith("### "):
            if cur_section in ("projects", "practices", "campus"):
                cur_item = {"title": s[4:].strip(), "role": "", "dates": "", "bullets": []}
                d[cur_section].append(cur_item)
        elif s.startswith("**") and "｜" in s and cur_item is not None:
            parts = re.split(r"\*\*[^\*]+\*\*\s*[｜|]\s*", s, maxsplit=1)
            if len(parts) == 2:
                cur_item["role"] = parts[0].replace("**", "").strip()
                cur_item["dates"] = parts[1].replace("**", "").strip()
            else:
                cur_item["role"] = s.replace("**", "").replace("｜", "｜").strip()
        elif s.startswith("- ") and cur_item is not None:
            cur_item["bullets"].append(s[2:].strip())
        elif cur_section == "skills" and s.startswith("- "):
            d["skills"].append(s[2:].strip())
    return d


def set_run_font(run, size=10.5, bold=False):
    run.font.size = docx.shared.Pt(size)
    run.font.bold = bold
    run.font.name = "Times New Roman"
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), "Times New Roman")
    rfonts.set(qn("w:hAnsi"), "Times New Roman")
    rfonts.set(qn("w:eastAsia"), "宋体")


def add_inline(par, text, size=10.5, bold_color=None):
    parts = re.split(r"\*\*(.+?)\*\*", text)
    for i, seg in enumerate(parts):
        if not seg:
            continue
        run = par.add_run(seg)
        set_run_font(run, size, bold=(i % 2 == 1))


def find_cell_by_keyword(tbl, keyword):
    for row in tbl.findall(".//w:tr", ns):
        for cell in row.findall(".//w:tc", ns):
            text = "".join(t.text or "" for t in cell.findall(".//w:t", ns))
            if keyword in text:
                return cell
    return None


def clear_cell_text(cell):
    for p in cell.findall(".//w:p", ns):
        for r in p.findall(".//w:r", ns):
            t = r.find("w:t", ns)
            if t is not None:
                t.text = ""


def set_cell_text(cell, text, bold=False, size=10.5):
    clear_cell_text(cell)
    p = cell.paragraphs[0] if cell.paragraphs else cell.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, size, bold)
    return p


def update_header(doc, d):
    tbl = doc.tables[0]
    # Row 0: name
    set_cell_text(tbl.rows[0].cells[0], d["name"], bold=True, size=14)
    # Row 1: contact
    set_cell_text(tbl.rows[1].cells[0], d["contact"], size=9)
    # Row 2: intent
    if d["intent"]:
        set_cell_text(tbl.rows[2].cells[0], "求职意向：" + d["intent"], size=10)
    # Row 3: summary
    if d["summary"]:
        set_cell_text(tbl.rows[3].cells[0], "个人优势：" + d["summary"], size=9)


def update_education(doc, d):
    # Table 1: education header + data rows
    tbl = doc.tables[1]
    # Clear existing data rows (keep header row 0)
    for row in tbl.rows[1:]:
        for cell in row.cells:
            clear_cell_text(cell)
    # Add school info to first data row
    row0 = tbl.rows[1]
    cells = row0.cells
    if len(cells) >= 4:
        set_cell_text(cells[0], d["edu_school"], bold=True, size=11)
        set_cell_text(cells[1], d["edu_major"], size=10.5)
        set_cell_text(cells[2], d["edu_degree"], size=10.5)
        set_cell_text(cells[3], d["edu_dates"], size=10.5)
    # Table 2: courses + honors
    tbl2 = doc.tables[2]
    row0 = tbl2.rows[0]
    cells = row0.cells
    if d["courses"] and len(cells) > 0:
        set_cell_text(cells[0], "核心课程：" + d["courses"], size=9.5)
    if d["honors"] and len(cells) > 1:
        set_cell_text(cells[1], "荣誉奖励：" + d["honors"], size=9.5)


def update_section(doc, tbl_idx, d_key, section_name):
    tbl = doc.tables[tbl_idx]
    # Find the section header row
    header_row_idx = None
    for i, row in enumerate(tbl.rows):
        for cell in row.cells:
            text = "".join(t.text or "" for t in cell.findall(".//w:t", ns))
            if section_name in text:
                header_row_idx = i
                break
        if header_row_idx is not None:
            break
    if header_row_idx is None:
        return
    # Clear rows after header
    for row in tbl.rows[header_row_idx + 1:]:
        for cell in row.cells:
            clear_cell_text(cell)
    items = d.get(d_key, [])
    row_idx = header_row_idx + 1
    for item in items:
        if row_idx >= len(tbl.rows):
            break
        row = tbl.rows[row_idx]
        cells = row.cells
        # Title in first content cell
        if len(cells) > 0 and cells[0].paragraphs:
            p = cells[0].paragraphs[0]
            for r in p.runs:
                r.text = ""
            p.add_run(item["title"])
            for r in p.runs:
                set_run_font(r, 10.5, bold=True)
        # Role and dates
        if len(cells) > 1 and item.get("role"):
            set_cell_text(cells[1], item["role"], size=9.5)
        if len(cells) > 2 and item.get("dates"):
            set_cell_text(cells[2], item["dates"], size=9.5)
        # Bullets
        bullet_cells = [c for c in cells[3:] if c.paragraphs] if len(cells) > 3 else []
        for bi, bullet in enumerate(item.get("bullets", [])):
            if bi < len(bullet_cells):
                p = bullet_cells[bi].paragraphs[0]
                for r in p.runs:
                    r.text = ""
                p.add_run("• " + bullet)
                for r in p.runs:
                    set_run_font(r, 9.5)
        row_idx += 1
    # Clear remaining rows
    for row in tbl.rows[row_idx:]:
        for cell in row.cells:
            clear_cell_text(cell)


def update_skills(doc, d):
    tbl = doc.tables[-1]
    for row in tbl.rows:
        for cell in row.cells:
            clear_cell_text(cell)
    row0 = tbl.rows[0]
    cells = row0.cells
    for i, skill in enumerate(d.get("skills", [])):
        if i < len(cells):
            p = cells[i].paragraphs[0] if cells[i].paragraphs else cells[i].add_paragraph()
            for r in p.runs:
                r.text = ""
            p.add_run("• " + skill)
            for r in p.runs:
                set_run_font(r, 9.5)


ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def build(md_path, out_path, compact=False, gpa=False, template=None):
    if not template:
        print("ERROR: --template parameter required", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(template):
        print(f"ERROR: template not found: {template}", file=sys.stderr)
        sys.exit(1)
    d = parse_md(md_path)
    # Copy template to temp, then to output
    tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    tmp_path = tmp.name
    tmp.close()
    shutil.copy2(template, tmp_path)
    print(f"  template: {os.path.basename(template)}")
    doc = Document(tmp_path)
    update_header(doc, d)
    update_education(doc, d)
    update_section(doc, 4, "projects", "项目经历")
    update_section(doc, 5, "practices", "实践经历")
    update_section(doc, 6, "campus", "校园经历")
    update_skills(doc, d)
    doc.save(out_path)
    os.unlink(tmp_path)
    print(f"  docx: {os.path.basename(out_path)}")
    try:
        import win32com.client
        pdf_path = os.path.splitext(out_path)[0] + ".pdf"
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        wd = docx
        doc_src = word.Documents.Open(os.path.abspath(out_path))
        doc_src.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
        doc_src.Close(SaveChanges=False)
        word.Quit()
        print(f"  pdf: {os.path.basename(pdf_path)}")
    except Exception as e:
        print(f"  pdf: skipped ({e})")
    return d


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Resume generator")
    parser.add_argument("md_path", help="Path to resume markdown file")
    parser.add_argument("out_path", help="Output docx path")
    parser.add_argument("--template", required=True, help="Template docx path")
    parser.add_argument("--compact", action="store_true", help="Compact spacing")
    parser.add_argument("--gpa", action="store_true", help="Include GPA")
    args = parser.parse_args()
    build(args.md_path, args.out_path, compact=args.compact, gpa=args.gpa, template=args.template)
