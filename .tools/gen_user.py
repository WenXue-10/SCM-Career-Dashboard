# -*- coding: utf-8 -*-
"""基于用户定稿 template_user.docx 填充生成各方向简历。
用法: python gen_user.py <md> <out.docx>
"""
import sys, copy, os, re
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from gen_resume import parse_md

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template_user.docx')


def set_cell_text(tc, lines):
    """清空单元格所有段落并填多行文本（保持 rFonts: ascii=Times New Roman, eastAsia=宋体, sz=21）。
    lines: [str]。首行填原 p0，其余新增段落（复制 p0 的 pPr）。"""
    ps = tc.findall(W + 'p')
    p0 = ps[0]
    tpl = copy.deepcopy(p0)
    for r in tpl.findall(W + 'r'):
        tpl.remove(r)
    for extra in ps[1:]:
        tc.remove(extra)
    for r in p0.findall(W + 'r'):
        p0.remove(r)
    def addline(par, text):
        r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        rf = OxmlElement('w:rFonts')
        rf.set(qn('w:ascii'), 'Times New Roman'); rf.set(qn('w:hAnsi'), 'Times New Roman'); rf.set(qn('w:eastAsia'), '宋体')
        sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '21')
        szcs = OxmlElement('w:szCs'); szcs.set(qn('w:val'), '21')
        rPr.append(rf); rPr.append(sz); rPr.append(szcs)
        r.append(rPr)
        txt = OxmlElement('w:t'); txt.text = text; txt.set(qn('xml:space'), 'preserve')
        r.append(txt)
        par.append(r)
    addline(p0, lines[0])
    for ln in lines[1:]:
        np = copy.deepcopy(tpl)
        tc.append(np)
        addline(np, ln)


def set_para_text(p, text):
    """清空单段 run 并填文本，保留段落格式。"""
    for r in p.findall(W + 'r'):
        p.remove(r)
    r = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rf = OxmlElement('w:rFonts')
    rf.set(qn('w:ascii'), 'Times New Roman'); rf.set(qn('w:hAnsi'), 'Times New Roman'); rf.set(qn('w:eastAsia'), '宋体')
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '21')
    szcs = OxmlElement('w:szCs'); szcs.set(qn('w:val'), '21')
    rPr.append(rf); rPr.append(sz); rPr.append(szcs)
    r.append(rPr)
    txt = OxmlElement('w:t'); txt.text = text; txt.set(qn('xml:space'), 'preserve')
    r.append(txt)
    p.append(r)


def table_cell(tbl, ri, ci):
    tr = tbl._tbl.findall(W + 'tr')[ri]
    tcs = tr.findall(W + 'tc')
    return tcs[ci] if ci < len(tcs) else tcs[-1]


def fill_table3_projects(tbl, projects):
    """表3：项目经历。模板含 3 个项目行(标题+内容)，不足时复制模板组动态扩展。"""
    trs = tbl._tbl.findall(W + 'tr')
    # 结构: trs[0]=项目经历标题, 之后每项目2行(标题行+内容行), 末行=实践经历标题
    anchor = trs[7]  # 实践经历标题行（固定第8行）
    for i, proj in enumerate(projects):
        if i < 3:
            title_tr = trs[1 + i * 2]
            content_tr = trs[2 + i * 2]
        else:
            # 复制最后一组模板行，插入到实践经历标题行之前
            title_tr = copy.deepcopy(trs[5])
            content_tr = copy.deepcopy(trs[6])
            anchor.addprevious(title_tr)
            anchor.addprevious(content_tr)
        tcs = title_tr.findall(W + 'tc')
        set_cell_text(tcs[1], [proj['title']])
        if len(tcs) > 2:
            set_cell_text(tcs[2], [proj['role']])
        if len(tcs) > 3:
            set_cell_text(tcs[3], [proj['date']])
        tcs2 = content_tr.findall(W + 'tc')
        set_cell_text(tcs2[1], proj['bullets'])


def fill_table4_practices(tbl, practices):
    """表4：实践经历。模板含 2 个项目行(鱼跃/瑞幸)，直接按序填充。"""
    trs = tbl._tbl.findall(W + 'tr')
    for i, pra in enumerate(practices):
        title_tr = trs[i * 2]
        content_tr = trs[i * 2 + 1]
        tcs = title_tr.findall(W + 'tc')
        set_cell_text(tcs[1], [pra['title']])
        set_cell_text(tcs[2], [pra['role']])
        set_cell_text(tcs[3], [pra['date']])
        tcs2 = content_tr.findall(W + 'tc')
        set_cell_text(tcs2[1], pra['bullets'])


def main():
    md_path, out_path = sys.argv[1], sys.argv[2]
    line = int(sys.argv[3]) if len(sys.argv) > 3 else 280
    d = parse_md(md_path)
    doc = docx.Document(TEMPLATE)
    T = doc.tables
    # 表0: 求职意向(行2) + 个人优势(行3)
    set_cell_text(table_cell(T[0], 2, 0), ['求职意向： ' + d['intent']])
    set_cell_text(table_cell(T[0], 3, 0), ['个人优势：' + d['adv'][0]])
    # 表1: 教育背景(保持山东大学行, 不覆盖)
    # 表2: 核心课程(行0) + 荣誉(行1)
    set_cell_text(table_cell(T[2], 0, 1), ['核心课程：' + d['courses']])
    set_cell_text(table_cell(T[2], 1, 1), ['荣誉奖励：' + d['honor']])
    # 表3: 项目经历(动态)
    fill_table3_projects(T[3], d['projects'])
    # 表4: 实践经历
    fill_table4_practices(T[4], d['practices'])
    # 表5: 校园学生工作(保持3条)
    # 表7: 综合技能(行0) + 自我评价(行2)
    skill_lines = []
    for name, desc in d['skills']:
        if name:
            skill_lines.append(name + '：' + desc)
        else:
            skill_lines.append(desc)
    set_cell_text(table_cell(T[7], 0, 1), skill_lines)
    # 全局行距压缩（内容较多，确保 1 页）
    for tbl in T:
        for tr in tbl._tbl.findall(W + 'tr'):
            for tc in tr.findall(W + 'tc'):
                for pp in tc.findall(W + 'p'):
                    pPr = pp.find(W + 'pPr')
                    if pPr is None:
                        pPr = OxmlElement('w:pPr'); pp.insert(0, pPr)
                    sp = pPr.find(W + 'spacing')
                    if sp is None:
                        sp = OxmlElement('w:spacing'); pPr.append(sp)
                    sp.set(qn('w:line'), str(line))
                    sp.set(qn('w:lineRule'), 'atLeast')
    doc.save(out_path)
    print('OK', out_path, '项目数:', len(d['projects']), '技能条数:', len(d['skills']), '自我评价条数:', len(d['summary']))


if __name__ == '__main__':
    main()
