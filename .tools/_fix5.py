path = r"D:\Obsidian\SCM-Career\.tools\gen_resume.py"
with open(path, encoding="utf-8") as f:
    content = f.read()

# Replace f-string with string concatenation for XPath
content = content.replace('f".//{NS}}}p"', '".//" + NS + "}p"')
content = content.replace('f".//{NS}}}t"', '".//" + NS + "}t"')

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed")
