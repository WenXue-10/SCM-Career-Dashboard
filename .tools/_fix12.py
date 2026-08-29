path = r'D:\Obsidian\SCM-Career\.tools\gen_resume.py'
lines = open(path, encoding='utf-8').readlines()
for i in range(len(lines)):
    if 'def find_text' in lines[i]:
        lines[i] = 'def find_text(el):\n'
        lines[i+1] = '    return el.text or ""\n'
        break
open(path, 'w', encoding='utf-8').writelines(lines)
print('Fixed')
