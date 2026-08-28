# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\Obsidian\SCM-Career\99_系统与规则\系统关联清单.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 更新检查清单中剩余的 TEMPLATE 提法
old1 = '- [ ] `gen_resume.py`的`TEMPLATE`路径是否正确？'
new1 = '- [ ] gen_resume.py 的 --template 参数是否正确指向对应方向的通用简历 docx？'
if old1 in content:
    content = content.replace(old1, new1)
    print('Updated line 165')
else:
    print('WARNING: line 165 not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('done')
