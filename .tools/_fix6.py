path = r"D:\Obsidian\SCM-Career\.tools\gen_resume.py"
with open(path, encoding="utf-8") as f:
    content = f.read()

# The f-strings have {{{NS}}} which in f-string produces {NS_value}
# But the colon in NS value (http://...) causes issues
# Fix: use string concatenation instead
content = content.replace('f".//{NS}}}t"', '".//" + NS + "}t"')
content = content.replace('f".//{NS}}}p"', '".//" + NS + "}p"')

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed")
