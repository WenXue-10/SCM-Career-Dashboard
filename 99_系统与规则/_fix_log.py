# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\Obsidian\SCM-Career\99_系统与规则\求职知识库问题日志.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

new_entry = '''
| #132 | 2026-08-29 | 通用简历版式模板从单一 template_jd.docx 改为四份方向 docx 通过 --template 参数动态指定 | gen_resume.py 默认 TEMPLATE 写死导致无法支持不同方向简历的版式差异（用户已手动修改四份通用简历 docx 为不同布局） | ① gen_resume.py：删除默认 TEMPLATE，改为 --template 必填参数，不传则报错退出；② 系统关联清单 6 处更新（目录索引表拆为 md+docx 两行、3.1表改 --template、调用链更新、检查清单C更新、脆弱点1更新）；③ MEMORY.md 模板描述更新；④ .workbuddy/template_jd.docx 已删除（备份为 template_jd_bak3.docx） | ① gen_resume.py --template 必填验证通过；② 系统关联清单 6 处均已更新；③ MEMORY.md 已更新；④ template_jd.docx 已删除 | .workbuddy/gen_resume.py、99_系统与规则/系统关联清单.md、.workbuddy/memory/MEMORY.md | ✅ 已处理 |'''

# Insert before the closing section (after #131 row)
# Find the last table row
last_row_marker = '| #131 |'
idx = content.rfind(last_row_marker)
if idx > 0:
    # Find end of this line
    line_end = content.find('\n', idx)
    content = content[:line_end+1] + new_entry + content[line_end+1:]
    print('Added #132 entry')
else:
    print('WARNING: last row not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('问题日志 done')
