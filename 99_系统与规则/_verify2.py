# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document
import re

base = r'D:\Obsidian\SCM-Career\02_定制简历库\通用简历'
files = [
    ('文雪_山东大学_管培通用方向.docx', '简历-管培通用方向.md'),
    ('文雪_山东大学_项目采购方向.docx', '简历-项目采购方向.md'),
    ('文雪_山东大学_运营管理方向.docx', '简历-运营管理方向.md'),
]
for docx_name, md_name in files:
    doc = Document(base + '\\' + docx_name)
    docx_projects = []
    docx_practices = []
    for ti, table in enumerate(doc.tables):
        for ri, row in enumerate(table.rows):
            cells = [c.text.strip() for c in row.cells]
            for c in cells:
                if re.match(r'\d{4}\.\d{2}', c):
                    idx = cells.index(c)
                    if idx >= 1 and cells[1] and cells[1] not in docx_projects:
                        docx_projects.append(cells[1])
                    if '兼职' in str(cells) and cells[1] not in docx_practices:
                        docx_practices.append(cells[1])
    with open(base + '\\' + md_name, 'r', encoding='utf-8') as f:
        md = f.read()
    md_projects = re.findall(r'### (.+?)\n\*\*', md)
    print(f'{docx_name}: docx_proj={docx_projects}, md_proj={md_projects}')
