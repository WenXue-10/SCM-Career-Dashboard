# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from docx import Document

doc = Document(r'D:\Obsidian\SCM-Career\02_定制简历库\通用简历\文雪_山东大学_供应链数据方向.docx')
# Table 0 has personal info
for ri, row in enumerate(doc.tables[0].rows):
    cells = [c.text.strip() for c in row.cells]
    full = ' '.join(cells)
    if '个人优势' in full or '求职意向' in full:
        print(f'R{ri}: {full[:200]}')
