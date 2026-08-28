# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\Obsidian\SCM-Career\02_定制简历库\通用简历\简历-供应链数据方向.md'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and remove the 电商 project section (lines 39-47, 0-indexed 38-46)
new_lines = []
skip = False
for i, line in enumerate(lines):
    if '### 电商用户行为分析与运营策略研究' in line:
        skip = True
        continue
    if skip:
        if line.startswith('### ') or line.startswith('## ') or (line.strip() == '' and i+1 < len(lines) and lines[i+1].startswith('### ')):
            skip = False
            new_lines.append(line)
        # else skip this line
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('done, removed 电商 project')
