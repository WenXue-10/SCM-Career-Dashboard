# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

base = r'D:\Obsidian\SCM-Career\02_定制简历库\通用简历'
out = r'D:\Obsidian\SCM-Career\99_系统与规则\_md_check.py'

files = [
    ('文雪_山东大学_供应链数据方向.docx', '简历-供应链数据方向.md'),
    ('文雪_山东大学_管培通用方向.docx', '简历-管培通用方向.md'),
    ('文雪_山东大学_项目采购方向.docx', '简历-项目采购方向.md'),
    ('文雪_山东大学_运营管理方向.docx', '简历-运营管理方向.md'),
]

for docx_name, md_name in files:
    doc = Document(base + '\\' + docx_name)
    lines = []
    for ti, table in enumerate(doc.tables):
        for ri, row in enumerate(table.rows):
            cells = [c.text.strip().replace('\n', ' | ') for c in row.cells]
            line = ' | '.join(cells)
            if line.strip():
                lines.append(line)
    
    md_path = base + '\\' + md_name
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract key sections from md
    print(f'\n{"="*60}')
    print(f'【{docx_name}】vs【{md_name}】')
    print('='*60)
    
    # Show table content (first 30 lines)
    for l in lines[:35]:
        print(l)
