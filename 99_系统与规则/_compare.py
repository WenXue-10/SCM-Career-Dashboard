# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

base = r'D:\Obsidian\SCM-Career\02_定制简历库\通用简历'

files = [
    ('文雪_山东大学_供应链数据方向.docx', '简历-供应链数据方向.md'),
    ('文雪_山东大学_管培通用方向.docx', '简历-管培通用方向.md'),
    ('文雪_山东大学_项目采购方向.docx', '简历-项目采购方向.md'),
    ('文雪_山东大学_运营管理方向.docx', '简历-运营管理方向.md'),
]

for docx_name, md_name in files:
    doc = Document(base + '\\' + docx_name)
    print(f'\n{"="*60}')
    print(f'【{docx_name}】TABLE STRUCTURE')
    print('='*60)
    for ti, table in enumerate(doc.tables):
        print(f'\nTable {ti}: {len(table.rows)} rows x {len(table.columns)} cols')
        for ri, row in enumerate(table.rows):
            cells = [c.text.strip() for c in row.cells]
            print(f'  R{ri}: {cells}')
