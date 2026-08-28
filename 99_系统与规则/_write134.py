# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\Obsidian\SCM-Career\99_系统与规则\求职知识库问题日志.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_entry = '''
| #134 | 2026-08-29 | 四份通用简历 md 与 docx 核对后仍有3处差异，逐一修正 | #133 修正时供应链数据方向删电商项目但其他三份未仔细核对 | ①供应链数据方向：删除「电商用户行为分析与运营策略研究」项目（docx无此项目）；②管培通用方向：互换实践经历顺序为鱼跃→瑞幸（与docx一致）；③运营管理方向：删除ERP项目（docx无）、补瑞幸「单据核对」bullet | 四份 md 项目/实践数量与顺序全部与对应 docx 一致 | 02_定制简历库/通用简历/4份 md | ✅ 已处理 |'''

last_row = content.rfind('| #133 |')
if last_row > 0:
    line_end = content.find('\n', last_row)
    content = content[:line_end+1] + new_entry + content[line_end+1:]
    print('Added #134')
else:
    print('WARNING: #133 not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('done')
