# -*- coding: utf-8 -*-
import sys, os, re, shutil, tempfile
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.shared import Pt
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.enum.table import WD_ROW_HEIGHT_RULE
except ImportError:
    print("ERROR: python-docx not installed", file=sys.stderr)
    sys.exit(1)

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def find_text(el):
    return el.text or ""

def clear_para(para):
    for run in para.runs:
        run.text = ''

def add_run(par, text, bold=False, size=10.5):
    run = par.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    return run

def set_cell(cell, text, bold=False, size=10.5):
    if cell.paragraphs:
        clear_para(cell.paragraphs[0])
        add_run(cell.paragraphs[0], text, bold=bold, size=size)
    else:
        cell.text = text
def add_formatted_text(par, text, size=9.5):
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            bold_text = part[2:-2]
            add_run(par, bold_text, bold=True, size=size)
        else:
            add_run(par, part, bold=False, size=size)


def parse_md(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    d = dict(name="", contact="", intent="", summary="",
             edu_school="", edu_major="", edu_degree="", edu_dates="",
             courses="", honors="",
             projects=[], practices=[], campus=[], skills=[])
    section = None
    item = None
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith("# "):
            d["name"] = s[2:].strip()
        elif re.match(r"^\*\*求职意向\*\*[：:]", s):
            d["intent"] = re.sub(r"\*\*求职意向\*\*[：:]", "", s).strip()
        elif re.match(r"^\*\*个人优势\*\*[：:]", s):
            d["summary"] = re.sub(r"\*\*个人优势\*\*[：:]", "", s).strip()
        elif ("｜" in s or "|" in s) and not s.startswith("**") and not d["contact"]:
            d["contact"] = s
        elif s == "## 教育背景":
            section = "edu"
        elif s == "## 项目经历":
            section = "projects"
        elif s == "## 实践经历":
            section = "practices"
        elif s == "## 校园经历":
            section = "campus"
        elif s == "## 综合技能":
            section = "skills"
        elif section == "edu":
            if "**" in s and "｜" in s:
                parts = s.split("｜")
                if len(parts) >= 3:
                    d["edu_school"] = parts[0].replace("**", "").strip()
                    d["edu_major"] = parts[1].strip()
                    d["edu_degree"] = ""
                    d["edu_dates"] = parts[2].replace("**", "").strip()
                elif len(parts) == 2:
                    d["edu_school"] = parts[0].replace("**", "").strip()
                    d["edu_major"] = parts[1].replace("**", "").strip()
            elif "核心课程" in s:
                d["courses"] = re.sub(r"^\*\*[^*]*\*\*[：:]\s*", "", s).strip()
            elif "荣誉奖励" in s:
                d["honors"] = re.sub(r"^\*\*[^*]*\*\*[：:]\s*", "", s).strip()
        elif s.startswith("### "):
            if section in ("projects", "practices", "campus"):
                item = dict(title=s[4:].strip().replace("**", ""), role="", dates="", bullets=[])
                d[section].append(item)
        elif s.startswith("**") and ("｜" in s or "|" in s) and item is not None:
            parts = s.split("｜")
            if len(parts) >= 2:
                item["role"] = parts[0].replace("**", "").strip()
                item["dates"] = parts[1].replace("**", "").strip()
        elif s.startswith("- ") and item is not None:
            item["bullets"].append(s[2:].strip())
        elif section == "skills" and s.startswith("- "):
            d["skills"].append(s[2:].strip())
    return d


def update_header(doc, d):
    tbl = doc.tables[0]
    set_cell(tbl.rows[0].cells[0], d["name"], bold=True, size=14)
    set_cell(tbl.rows[1].cells[0], d["contact"], size=9)
    if d["intent"]:
        set_cell(tbl.rows[2].cells[0], "求职意向：" + d["intent"], size=10)
    if d["summary"]:
        paras = list(tbl.rows[3].cells[0].paragraphs)
        if paras:
            p = paras[0]
            clear_para(p)
            add_run(p, "个人优势：", bold=True, size=9)
            add_run(p, d["summary"], bold=False, size=9)


def update_edu(doc, d):
    tbl = doc.tables[1]
    for row in tbl.rows[1:]:
        for c in row.cells:
            for p in c.paragraphs:
                clear_para(p)
    cells = tbl.rows[1].cells
    if len(cells) >= 1:
        set_cell(cells[0], d["edu_school"], bold=True, size=11)
    if len(cells) >= 2:
        set_cell(cells[1], d["edu_major"], size=10.5)
    if len(cells) >= 3:
        set_cell(cells[2], d["edu_degree"], size=10.5)
    if len(cells) >= 4:
        set_cell(cells[3], d["edu_dates"], size=10.5)
    tbl2 = doc.tables[2]
    cells = tbl2.rows[0].cells
    if d["courses"] and len(cells) > 0:
        set_cell(cells[0], "核心课程：" + d["courses"], size=9.5)
    if d["honors"] and len(cells) > 1:
        set_cell(cells[1], "荣誉奖励：" + d["honors"], size=9.5)


def update_section(doc, tidx, items, kwds):
    tbl = doc.tables[tidx]
    hi = None
    for i, row in enumerate(tbl.rows):
        for c in row.cells:
            txt = find_text(c._element)
            if any(k in txt for k in kwds):
                hi = i
                break
        if hi is not None:
            break
    if hi is None:
        return
    for row in tbl.rows[hi + 1:]:
        for c in row.cells:
            for p in c.paragraphs:
                clear_para(p)
    ri = hi + 1
    for it in items:
        if ri >= len(tbl.rows):
            break
        row = tbl.rows[ri]
        cells = row.cells
        # 修复列索引：模板结构是 cells[1]=标题, cells[2]=角色, cells[3]=日期, cells[4+]=bullet
        if len(cells) > 1:
            paras = list(cells[1].paragraphs)
            if paras:
                clear_para(paras[0])
                add_formatted_text(paras[0], it["title"], size=10.5)
        if len(cells) > 2 and it.get("role"):
            paras = list(cells[2].paragraphs)
            if paras:
                clear_para(paras[0])
                add_formatted_text(paras[0], it["role"], size=9.5)
        if len(cells) > 3 and it.get("dates"):
            paras = list(cells[3].paragraphs)
            if paras:
                clear_para(paras[0])
                add_formatted_text(paras[0], it["dates"], size=9.5)
        for bi, b in enumerate(it.get("bullets", [])):
            ci = 4 + bi
            if ci < len(cells):
                paras = list(cells[ci].paragraphs)
                if paras:
                    clear_para(paras[0])
                    add_formatted_text(paras[0], "\u2022 " + b, size=9.5)
        ri += 1


def update_skills(doc, d):
    tbl = doc.tables[-1]
    for row in tbl.rows:
        for c in row.cells:
            for p in c.paragraphs:
                clear_para(p)
    cells = tbl.rows[0].cells
    for i, s in enumerate(d.get("skills", [])):
        if i < len(cells):
            paras = list(cells[i].paragraphs)
            if paras:
                clear_para(paras[0])
                add_formatted_text(paras[0], "\u2022 " + s, size=9.5)


def build(md_path, out_path, template=None):
    if not template:
        print("ERROR: --template parameter required", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(template):
        print("ERROR: template not found: " + template, file=sys.stderr)
        sys.exit(1)
    d = parse_md(md_path)
    tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    tmp_path = tmp.name
    tmp.close()
    shutil.copy2(template, tmp_path)
    print("  template: " + os.path.basename(template))
    doc = Document(tmp_path)
    update_header(doc, d)
    update_edu(doc, d)
    # 修复表格索引：3=项目经历, 4=实践经历, 5=校园经历
    update_section(doc, 3, d["projects"], ["项目经历"])
    update_section(doc, 4, d["practices"], ["实践经历"])
    update_section(doc, 5, d["campus"], ["校园经历"])
    update_skills(doc, d)
    doc.save(out_path)
    os.unlink(tmp_path)
    print("  docx: " + os.path.basename(out_path))
    return d


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Resume generator")
    p.add_argument("md_path", help="Path to resume markdown file")
    p.add_argument("out_path", help="Output docx path")
    p.add_argument("--template", required=True, help="Template docx path")
    args = p.parse_args()
    build(args.md_path, args.out_path, template=args.template)
