path = r'D:\Obsidian\SCM-Career\.tools\gen_resume.py'
lines = open(path, encoding='utf-8').readlines()
lines[176] = '           paras = cells[0]._element.findall(".//" + NS + chr(125)+"p")\n'
lines[179] = '                add_formatted_text(paras[0], it["title"], size=10.5)\n'
lines[181] = '           paras = cells[1]._element.findall(".//" + NS + chr(125)+"p")\n'
lines[184] = '                add_formatted_text(paras[0], it["role"], size=9.5)\n'
lines[186] = '           paras = cells[2]._element.findall(".//" + NS + chr(125)+"p")\n'
open(path, 'w', encoding='utf-8').writelines(lines)
print('Done')
