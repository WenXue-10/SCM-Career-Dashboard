with open(r'D:/Obsidian/SCM-Career/99_系统与规则/_batch1.py','r',encoding='utf-8') as f:
    content = f.read()
# Fix quadruple backslashes to double
content = content.replace('\\\\\\\\', '\\\\')
with open(r'D:/Obsidian/SCM-Career/99_系统与规则/_batch1.py','w',encoding='utf-8') as f:
    f.write(content)
print('Fixed')
