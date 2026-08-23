# -*- coding: utf-8 -*-
"""文雪求职小窝 · 站点生成器
从 Obsidian 知识库自动生成静态网站到 docs/（GitHub Pages 发布目录）。
运行：python build_site.py
"""
import os, re, json, shutil, datetime, sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import markdown

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "site_assets")
OUT = os.path.join(BASE, "docs")
FILES_DIR = os.path.join(OUT, "files")

_md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])

def md_to_html(text):
    _md.reset()
    html = _md.convert(text)
    html = re.sub(r"\[\[([^\]|]+)(\|[^\]]+)?\]\]", r"\1", html)
    return html

def strip_fm(text):
    m = re.match(r"^---\s*\n.*?\n---\s*\n?", text, re.DOTALL)
    return text[m.end():] if m else text

def parse_fm(text):
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

# ---------- 文件复制（中文名 → 安全英文名） ----------
_file_counter = 0
_file_map = {}
def copy_file(src, prefix="f"):
    global _file_counter
    if src in _file_map:
        return _file_map[src]
    _file_counter += 1
    ext = os.path.splitext(src)[1].lower()
    base = os.path.basename(src)
    dst = os.path.join(FILES_DIR, f"{prefix}{_file_counter}_{base}")
    shutil.copy2(src, dst)
    url = "files/" + os.path.basename(dst)
    _file_map[src] = url
    return url

# ---------- 生成 PDF（reportlab + 微软雅黑） ----------
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

_font_ok = None
def _reg_font():
    global _font_ok
    if _font_ok is not None:
        return _font_ok
    for cand in [("MSYH", "C:/Windows/Fonts/msyh.ttc", 0), ("MSYH", "C:/Windows/Fonts/simhei.ttf", None)]:
        try:
            if cand[2] is None:
                pdfmetrics.registerFont(TTFont(cand[0], cand[1]))
            else:
                pdfmetrics.registerFont(TTFont(cand[0], cand[1], subfontIndex=cand[2]))
            _font_ok = True
            return True
        except Exception:
            continue
    _font_ok = False
    return False

def _esc_pdf(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def md_to_pdf(md_text, out_path, title=""):
    if not _reg_font():
        return False
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=16*mm, bottomMargin=16*mm)
    st = {
        "h1": ParagraphStyle("h1", fontName="MSYH", fontSize=16, leading=23, spaceAfter=10),
        "h2": ParagraphStyle("h2", fontName="MSYH", fontSize=13, leading=19, spaceBefore=8, spaceAfter=4, textColor="#334155"),
        "body": ParagraphStyle("body", fontName="MSYH", fontSize=10.5, leading=16, spaceAfter=4),
        "quote": ParagraphStyle("quote", fontName="MSYH", fontSize=10, leading=15, leftIndent=12, textColor="#64748b"),
        "cell": ParagraphStyle("cell", fontName="MSYH", fontSize=9, leading=13),
    }
    flow = []
    if title:
        flow.append(Paragraph(_esc_pdf(title), st["h1"]))
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            flow.append(Spacer(1, 4)); i += 1; continue
        if line.startswith("|"):
            rows, j = [], i
            while j < len(lines) and lines[j].strip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append([Paragraph(_esc_pdf(c), st["cell"]) for c in cells])
                j += 1
            if rows:
                t = Table(rows)
                t.setStyle(TableStyle([
                    ("GRID", (0,0), (-1,-1), 0.4, "#e2e8f0"),
                    ("BACKGROUND", (0,0), (-1,0), "#fdf2f8"),
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("TOPPADDING", (0,0), (-1,-1), 3),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
                    ("LEFTPADDING", (0,0), (-1,-1), 5),
                    ("RIGHTPADDING", (0,0), (-1,-1), 5),
                ]))
                flow.append(t); flow.append(Spacer(1, 6))
            i = j; continue
        if line.startswith("# "):
            flow.append(Paragraph(_esc_pdf(line[2:]), st["h1"]))
        elif line.startswith("## "):
            flow.append(Paragraph(_esc_pdf(line[3:]), st["h2"]))
        elif line.startswith("### "):
            flow.append(Paragraph(_esc_pdf(line[4:]), st["h2"]))
        elif line.startswith("> "):
            flow.append(Paragraph(_esc_pdf(line[2:]), st["quote"]))
        elif line.startswith("- ") or line.startswith("* "):
            flow.append(Paragraph("• " + _esc_pdf(line[2:]), st["body"]))
        elif re.match(r"^\d+\.\s", line):
            flow.append(Paragraph(_esc_pdf(line), st["body"]))
        elif line.strip() in ("---", "***", "___"):
            flow.append(HRFlowable(width="100%", thickness=0.7, color="#f1c7d8", spaceBefore=4, spaceAfter=4))
        else:
            flow.append(Paragraph(_esc_pdf(line), st["body"]))
        i += 1
    doc.build(flow)
    return True

_pdf_cache = {}
def gen_pdf_from_md(md_path, title):
    if md_path in _pdf_cache:
        return _pdf_cache[md_path]
    text = strip_fm(read(md_path))
    base = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "_", os.path.splitext(os.path.basename(md_path))[0]).strip("_")[:36]
    out = os.path.join(FILES_DIR, f"g_{base}.pdf")
    ok = md_to_pdf(text, out, title=title)
    url = "files/" + os.path.basename(out) if ok else None
    _pdf_cache[md_path] = url
    return url

# ---------- 岗位数据 ----------
def status_key(t):
    t = t or ""
    low = t.lower()
    if "已背调" in t: return "done"
    if "offer" in low: return "done"
    if "待投递" in t or "已投递" in t: return "new"
    if "待确认" in t or "待补充" in t or "待核实" in t or "待背调" in t: return "warn"
    if "新收录" in t: return "new"
    if "面试" in t: return "interview"
    if "已挂" in t or "放弃" in t: return "dead"
    if "备选" in t: return "backup"
    return "backup"

def parse_detail_table(text):
    m = re.search(r"##\s*匹配度评分明细\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    rows = []
    if m:
        for line in m.group(1).splitlines():
            line = line.strip()
            if line.startswith("|"):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 3 and cells[0] not in ("维度", "---", "") and "总分" not in cells[0]:
                    rows.append([re.sub(r"[*`]", "", cells[0]), cells[1], cells[2]])
    return rows

def parse_summary(text):
    m = re.search(r"##\s*岗位 JD 摘要\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if not m:
        return ""
    lines = [l.strip() for l in m.group(1).splitlines() if l.strip() and not l.startswith("|")]
    return " ".join(lines)[:300]

def parse_note(text):
    m = re.search(r"##\s*备注\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    return " ".join(l.strip() for l in m.group(1).splitlines() if l.strip())[:200] if m else ""

def find_files(folder, prefixes):
    """在 folder 下找指定前缀的文件，返回 {kind: abs_path}"""
    found = {}
    if not os.path.isdir(folder):
        return found
    for fn in sorted(os.listdir(folder)):
        low = fn.lower()
        for pfx in prefixes:
            if low.startswith(pfx) and (low.endswith(".pdf") or low.endswith(".docx") or low.endswith(".doc")):
                found[pfx] = os.path.join(folder, fn)
    return found

def scan_jobs():
    jobs = []
    research = os.path.join(BASE, "01_岗位搜集与背调", "公司调研")
    if not os.path.isdir(research):
        return jobs
    for company in sorted(os.listdir(research)):
        cp = os.path.join(research, company)
        if not os.path.isdir(cp):
            continue
        for posdir in sorted(os.listdir(cp)):
            pp = os.path.join(cp, posdir)
            if not os.path.isdir(pp):
                continue
            score_file = None
            for fn in os.listdir(pp):
                if fn.startswith("评分-") and fn.endswith(".md"):
                    score_file = os.path.join(pp, fn)
                    break
            if not score_file:
                continue
            text = read(score_file)
            fm = parse_fm(text)
            score_raw = fm.get("匹配度总分", "—")
            try:
                score = int(float(score_raw))
            except Exception:
                score = "—"
            job = {
                "company": fm.get("公司名称", company),
                "pos": fm.get("岗位方向", posdir),
                "city": fm.get("城市", "未标注"),
                "salary": fm.get("薪资", "未披露"),
                "deadline": fm.get("投递截止", "未披露"),
                "score": score,
                "level": fm.get("匹配等级", "—"),
                "status": status_key(fm.get("当前状态", "")),
                "statusTxt": fm.get("当前状态", "🆕 新收录"),
                "link": fm.get("岗位链接", ""),
                "summary": parse_summary(text),
                "detail": parse_detail_table(text),
                "note": (parse_note(text) or fm.get("来源", "")),
            }
            # 背调报告
            for fn in os.listdir(pp):
                if fn.startswith("背调报告-") and fn.endswith(".md"):
                    rt_path = os.path.join(pp, fn)
                    job["report"] = {"html": md_to_html(strip_fm(read(rt_path)))}
                    for f2 in sorted(os.listdir(pp)):
                        low = f2.lower()
                        if f2.startswith("背调报告-") and low.endswith(".pdf"):
                            job["report"]["pdf"] = copy_file(os.path.join(pp, f2))
                        elif f2.startswith("背调报告-") and low.endswith((".docx", ".doc")):
                            job["report"]["doc"] = copy_file(os.path.join(pp, f2))
                    if "pdf" not in job["report"]:
                        job["report"]["pdf"] = gen_pdf_from_md(rt_path, "背调报告：" + fm.get("岗位名称", fn[:-3]))
                    break
            # 定制简历
            rp = os.path.join(BASE, "02_定制简历库", company, posdir)
            if os.path.isdir(rp):
                res = {}
                for fn in sorted(os.listdir(rp)):
                    low = fn.lower()
                    if low.endswith(".pdf") and ("文雪" in fn or "简历" in fn):
                        res["pdf"] = copy_file(os.path.join(rp, fn))
                    elif low.endswith((".docx", ".doc")) and ("文雪" in fn or "简历" in fn):
                        res["doc"] = copy_file(os.path.join(rp, fn))
                if res:
                    job["resume"] = res
            # JD 原文
            jp = os.path.join(BASE, "07_原始材料库", company, posdir)
            if os.path.isdir(jp):
                jd = {}
                pdfs = [os.path.join(jp, fn) for fn in os.listdir(jp) if fn.lower().endswith(".pdf")]
                if pdfs:
                    jd["pdf"] = copy_file(pdfs[0]) if len(pdfs) == 1 else None
                    if len(pdfs) > 1:
                        jd["pdfs"] = [copy_file(p) for p in pdfs]
                mds = [os.path.join(jp, fn) for fn in os.listdir(jp) if fn.startswith("JD-") and fn.endswith(".md")]
                if mds:
                    jd["html"] = md_to_html(strip_fm(read(mds[0])))
                if jd:
                    job["jd"] = jd
            jobs.append(job)
    return jobs

# ---------- 公司池 ----------
def scan_companies():
    p = os.path.join(BASE, "01_岗位搜集与背调", "🗂️ 目标公司池.md")
    if not os.path.exists(p):
        return []
    text = read(p)
    grades = []
    cur = None
    for line in text.splitlines():
        if line.startswith("## "):
            h = line[3:]
            if "A 级" in h:
                cur = {"title": "🅰️ A 级 · 每轮必检", "groups": []}
            elif "B 级" in h:
                cur = {"title": "🅱️ B 级 · 轮换补充", "groups": []}
            elif "剔除" in h:
                cur = {"title": "🚫 已剔除（口碑/强度不符）", "groups": []}
            else:
                cur = None
            if cur:
                grades.append(cur)
        elif line.startswith("- ") and cur and "剔除" in cur["title"]:
            m = re.match(r"-\s*\*{0,2}([^*（(]+)[（(]?([^）)]*)[）)]?\s*[：:]\s*(.*)", line)
            if m:
                cur["groups"].append({"cat": "已剔除", "name": m.group(1).strip(), "why": m.group(3).strip()})
            else:
                cur["groups"].append({"cat": "已剔除", "name": line[2:].strip(), "why": ""})
        elif line.startswith("|") and cur and "剔除" not in cur["title"]:
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3 and cells[0] not in ("类别", "") and "---" not in cells[0]:
                cur["groups"].append({"cat": cells[0], "name": cells[1], "why": cells[2]})
    return grades

# ---------- 日报 / 待办 ----------
def scan_timeline():
    p = os.path.join(BASE, "01_岗位搜集与背调", "📅 岗位日报归档.md")
    if not os.path.exists(p):
        return [], []
    text = read(p)
    entries, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^###\s*(\d{4}-\d{2}-\d{2})\s*[（(]?(.*?)[）)]?\s*$", line)
        if m:
            cur = {"date": m.group(1), "title": m.group(2) or "日报", "items": []}
            entries.append(cur)
        elif line.startswith("- ") and cur:
            cur["items"].append(line[2:].strip())
    todo = []
    for it in (entries[0]["items"] if entries else []):
        if it.startswith("待办"):
            body = re.sub(r"^待办\s*[:：]\s*", "", it)
            todo += [x.strip() for x in re.split(r"[；;]", body) if x.strip()]
    return entries, todo

# ---------- 简历库 ----------
_DOC_KEY = {
    "供应链数据": ["供应链优化", "A版"],
    "管培通用": ["管培", "D版"],
    "项目采购": ["项目采购", "C版"],
    "运营管理": ["运营管理", "B版"],
}
def scan_resumes():
    general = []
    gdir = os.path.join(BASE, "02_定制简历库", "通用简历")
    if os.path.isdir(gdir):
        for fn in sorted(os.listdir(gdir)):
            if fn.startswith("简历-") and fn.endswith(".md"):
                base = fn[:-3]
                name = "简历 · " + base.split("-", 1)[1] if "-" in base else base
                pdf = gen_pdf_from_md(os.path.join(gdir, fn), name)
                doc = None
                for k, keys in _DOC_KEY.items():
                    if k in name:
                        for d in sorted(os.listdir(gdir)):
                            if d.lower().endswith(".doc") and any(x in d for x in keys):
                                doc = copy_file(os.path.join(gdir, d))
                                break
                        break
                general.append({"name": name, "desc": "通用底版 · 适配" + (base.split("-", 1)[1] if "-" in base else ""), "pdf": pdf, "doc": doc})
    custom = []
    cdir = os.path.join(BASE, "02_定制简历库")
    if os.path.isdir(cdir):
        for company in sorted(os.listdir(cdir)):
            if company == "通用简历":
                continue
            cp = os.path.join(cdir, company)
            if not os.path.isdir(cp):
                continue
            items = []
            for posdir in sorted(os.listdir(cp)):
                pp = os.path.join(cp, posdir)
                if not os.path.isdir(pp):
                    continue
                for fn in sorted(os.listdir(pp)):
                    if fn.endswith(".md") and ("文雪" in fn or "简历" in fn):
                        pdf = gen_pdf_from_md(os.path.join(pp, fn), os.path.splitext(fn)[0])
                        doc = None
                        for d in sorted(os.listdir(pp)):
                            if d.lower().endswith((".docx", ".doc")) and ("文雪" in d or "简历" in d):
                                doc = copy_file(os.path.join(pp, d))
                                break
                        items.append({"name": os.path.splitext(fn)[0], "desc": posdir, "pdf": pdf, "doc": doc})
            if items:
                custom.append({"company": company, "items": items})
    return {"general": general, "custom": custom}

# ---------- 知识库 ----------
_KB_META = [
    ("00_战略与定位", "🐱", "战略总览、求职画像、目标与红线", "c1", True),
    ("01_岗位搜集与背调", "🐾", "岗位汇总、公司池、日报（公司调研见岗位看板）", "c2", False),
    ("02_定制简历库", "🧾", "通用底版 + 各企业定制（下载见简历库页）", "c3", True),
    ("03_笔面试题库", "✍️", "技术题、行为题、错题本", "c4", True),
    ("04_实战复盘", "🪞", "面试复盘与原始记录", "c5", True),
    ("05_供应链知识库", "📖", "专业知识卡片、英语术语卡", "c1", True),
    ("06_证书与附件", "🎓", "成绩单、获奖证书等文件", "c2", True),
    ("07_原始材料库", "🗃️", "JD 原文与登记索引", "c3", True),
    ("99_系统与规则", "⚙️", "Skill 规则、问题日志", "c4", True),
]
def scan_kb():
    kb = []
    for folder, icon, desc, cls, recursive in _KB_META:
        fp = os.path.join(BASE, folder)
        notes = []
        if os.path.isdir(fp):
            targets = []
            if recursive:
                for root, dirs, files in os.walk(fp):
                    dirs[:] = [d for d in dirs if d not in (".trash",)]
                    for fn in sorted(files):
                        targets.append(os.path.join(root, fn))
            else:
                targets = [os.path.join(fp, fn) for fn in os.listdir(fp) if os.path.isfile(os.path.join(fp, fn))]
            for t in sorted(targets):
                fn = os.path.basename(t)
                if fn.endswith(".md"):
                    if fn.startswith("评分-") or fn.startswith("背调报告-"):
                        continue
                    text = read(t)
                    notes.append({"title": os.path.splitext(fn)[0], "icon": "📄", "html": md_to_html(strip_fm(text))})
                elif fn.lower().endswith((".pdf", ".doc", ".docx", ".png", ".jpg", ".jpeg")):
                    url = copy_file(t)
                    notes.append({"title": fn, "icon": "📎", "html": f'<p><a href="{url}" target="_blank">📥 查看 / 下载文件：{fn}</a></p>'})
        kb.append({"icon": icon, "name": folder, "desc": desc, "cls": cls, "notes": notes})
    return kb

# ---------- 组装 ----------
def build():
    # 先清空旧的生成目录，避免残留文件
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(FILES_DIR, exist_ok=True)
    # 图片素材
    img_out = os.path.join(OUT, "assets")
    os.makedirs(img_out, exist_ok=True)
    img_src = os.path.join(ASSETS, "img")
    bg, av = {}, {}
    if os.path.isdir(img_src):
        for fn in sorted(os.listdir(img_src)):
            shutil.copy2(os.path.join(img_src, fn), os.path.join(img_out, fn))
            key = os.path.splitext(fn)[0]  # img1_bg / img1_avatar
            url = "assets/" + fn
            if fn.endswith("_bg.jpg"):
                bg[key.replace("_bg", "")] = url
            elif fn.endswith("_avatar.jpg"):
                av[key.replace("_avatar", "")] = url

    jobs = scan_jobs()
    companies = scan_companies()
    timeline, todo = scan_timeline()
    resumes = scan_resumes()
    kb = scan_kb()

    stats = {"jobs": len(jobs), "rec": 0, "interview": 0, "offer": 0}
    for j in jobs:
        if isinstance(j["score"], (int, float)) and j["score"] >= 70:
            stats["rec"] += 1
        if j["status"] == "interview":
            stats["interview"] += 1
        if "offer" in j["statusTxt"].lower():
            stats["offer"] += 1

    data = {
        "updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "stats": stats,
        "todo": todo,
        "jobs": jobs,
        "companies": companies,
        "timeline": timeline,
        "resumes": resumes,
        "kb": kb,
        "images": {"bg": bg, "av": av},
    }

    css = read(os.path.join(ASSETS, "style.css"))
    body = read(os.path.join(ASSETS, "body.html"))
    js = read(os.path.join(ASSETS, "app.js"))
    data_json = json.dumps(data, ensure_ascii=False, indent=1)

    html_out = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>文雪求职小窝</title>
<meta name="theme-color" content="#ffd0e2">
<style>
""" + css + """
</style>
</head>
""" + body + """
<script>
window.SITE_DATA = """ + data_json + """;
</script>
<script>
""" + js + """
</script>
</body>
</html>"""

    idx = os.path.join(OUT, "index.html")
    with open(idx, "w", encoding="utf-8") as f:
        f.write(html_out)
    print("✅ 网站已生成：", idx)
    print("   岗位:", stats["jobs"], "| 公司池分组:", len(companies), "| 日报:", len(timeline),
          "| 简历: 通用", len(resumes["general"]), "/ 定制", sum(len(c["items"]) for c in resumes["custom"]),
          "| 知识库笔记:", sum(len(k["notes"]) for k in kb))
    print("   files/ 文件数:", len(os.listdir(FILES_DIR)))

if __name__ == "__main__":
    build()