path = r'D:\Obsidian\SCM-Career\.tools\gen_resume.py'
content = open(path, encoding='utf-8').read()
content = content.replace('f".//{{{NS}}}}t"', '".//" + NS + "}t"')
content = content.replace('f".://{NS}}}}t"', '".//" + NS + "}t"')
open(path, 'w', encoding='utf-8').write(content)
print('Fixed t patterns')
