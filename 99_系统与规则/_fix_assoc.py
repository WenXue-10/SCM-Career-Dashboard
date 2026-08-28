# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\Obsidian\SCM-Career\99_系统与规则\系统关联清单.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_idx = r"`02_定制简历库/通用简历/文雪_山东大学_供应链数据方向.docx` | 简历生成模板（京东格式版式，用通用简历作为模板） | gen_resume.py（TEMPLATE变量） |"
new_idx = """`02_定制简历库/通用简历/简历-{方向}.md`（4份md） | 内容底版（按岗位方向选择） | Skill3 选模板依据 |
`02_定制简历库/通用简历/文雪_山东大学_{方向}.docx`（4份docx） | 版式模板（--template 参数） | gen_resume.py（--template） |"""
if old_idx in content:
    content = content.replace(old_idx, new_idx)
    print('Updated line 34')
else:
    print('WARNING: line 34 not found')

old_t = '| `TEMPLATE` (行12) | `02_定制简历库/通用简历/文雪_山东大学_供应链数据方向.docx` | 简历版式模板（用通用简历作为模板，删除/移动后所有简历生成失效） |'
new_t = '| `--template` 参数（必填） | `02_定制简历库/通用简历/文雪_山东大学_{方向}.docx`（4选1） | 版式模板，按岗位方向动态指定，删除后所有简历生成失效 |'
if old_t in content:
    content = content.replace(old_t, new_t)
    print('Updated line 69')
else:
    print('WARNING: line 69 not found')

old_call = '  ↓ 调用：gen_resume.py（需要.resume_template.docx）'
new_call = '  ↓ 调用：gen_resume.py（--template 指定对应方向通用简历docx，必填）'
if old_call in content:
    content = content.replace(old_call, new_call)
    print('Updated line 99')
else:
    print('WARNING: line 99 not found')

old_check = '- [ ] `.workbuddy/resume_template.docx`是否存在且未损坏？'
new_check = '- [ ] `.workbuddy/template_jd.docx`是否存在且未损坏？（已废弃，仅作备份参考）'
if old_check in content:
    content = content.replace(old_check, new_check)
    print('Updated line 164')
else:
    print('WARNING: line 164 not found')

old_frag = '1. **简历模板依赖**：`gen_resume.py`完全依赖`.workbuddy/resume_template.docx`，模板丢失则所有简历生成失效。模板不可删除，如需更新版式必须替换此文件。'
new_frag = '1. **简历版式模板依赖**：`gen_resume.py`依赖 `--template` 指定的通用简历 docx（4选1），该 docx 丢失则对应方向简历生成失效。四份通用简历 docx 不可删除；`.workbuddy/template_jd.docx` 为旧版式备份，已不再使用。'
if old_frag in content:
    content = content.replace(old_frag, new_frag)
    print('Updated line 185')
else:
    print('WARNING: line 185 not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('系统关联清单 done')
