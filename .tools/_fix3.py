path = r'D:\\Obsidian\\SCM-Career\\.tools\\gen_resume.py'
lines = open(path, encoding='utf-8').readlines()
lines[19] = 'def clear_para(para):\n'
lines[20] = '    for run in para.runs:\n'
lines[21] = '        run.text = '\''\n'
for i in range(23, 35):
    if i < len(lines):
        lines[i] = ''
lines[23] = 'def add_run(para, text, bold=False, size=10.5):\n'
lines[24] = '    run = para.add_run(text)\n'
lines[25] = '    run.bold = bold\n'
lines[26] = '    run.font.size = Pt(size)\n'
for i in range(35, 44):
    if i < len(lines):
        lines[i] = ''
lines[35] = 'def set_cell(cell, text, bold=False, size=10.5):\n'
lines[36] = '    if cell.paragraphs:\n'
lines[37] = '        clear_para(cell.paragraphs[0])\n'
lines[38] = '        add_run(cell.paragraphs[0], text, bold=bold, size=size)\n'
lines[39] = '    else:\n'
lines[40] = '        cell.text = text\n'
open(path, 'w', encoding='utf-8').writelines(lines)
print('Done')