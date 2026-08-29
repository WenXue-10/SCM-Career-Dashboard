path = r"D:\Obsidian\SCM-Career\.tools\gen_resume.py"
with open(path, encoding="utf-8") as f:
    content = f.read()

# Fix colon at end of findall calls
content = content.replace('f".//{NS}}}t":', 'f".//{NS}}}t")')
content = content.replace('f".//{NS}}}p":', 'f".//{NS}}}p")')
# Fix missing { in f-string
content = content.replace('f".://{NS}}}p"', 'f".//{NS}}}p"')

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed")
