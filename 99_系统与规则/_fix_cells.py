# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\Obsidian\SCM-Career\99_系统与规则\求职知识库问题日志.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove trailing empty cells |     |     | at end of lines
import re
content = re.sub(r'\| +\| +\| *$', '|', content)
content = content.rstrip() + '\n'

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Cleaned trailing empty cells')
