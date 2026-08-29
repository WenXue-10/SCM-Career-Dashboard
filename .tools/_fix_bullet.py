import re

path = r'D:\Obsidian\SCM-Career\.tools\gen_resume.py'
content = open(path, encoding='utf-8').read()

# 1. Add import re at top (if not present)
if 'import re' not in content:
    content = content.replace('import sys, os, re, shutil, tempfile', 'import sys, os, re, shutil, tempfile')

# 2. Add add_formatted_text function after add_run function
# Find the end of add_run and insert after it
func_to_add = '''

def add_formatted_text(par, text, size=9.5):
    """Write text with **bold** support. Parses **keyword**: rest into two runs."""
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            bold_text = part[2:-2]
            add_run(par, bold_text, bold=True, size=size)
        else:
            add_run(par, part, bold=False, size=size)
'''

# Insert after the add_run function's closing line
# Find the pattern: add_run(par, text, bold=bold, size=size) followed by blank line
target = '    add_run(paras[0], text, bold=bold, size=size)\n\n\ndef parse_md'
replacement = '    add_run(paras[0], text, bold=bold, size=size)' + func_to_add + '\n\ndef parse_md'
content = content.replace(target, replacement)

# 3. Replace bullet writes
content = content.replace('add_run(paras[0], "\\u2022 " + b, size=9.5)', 'add_formatted_text(paras[0], "\\u2022 " + b, size=9.5)')
content = content.replace('add_run(paras[0], "\\u2022 " + s, size=9.5)', 'add_formatted_text(paras[0], "\\u2022 " + s, size=9.5)')

open(path, 'w', encoding='utf-8').write(content)
print('Done')
