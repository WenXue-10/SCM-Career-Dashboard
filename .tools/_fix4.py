path = r"D:\Obsidian\SCM-Career\.tools\gen_resume.py"
with open(path, encoding="utf-8") as f:
    content = f.read()

# Fix edu regex: make trailing ** optional
old = r'm = re.match(r"\*\*([^*]+)\*\*\s*[\u2016|]\s*([^*]+)\s*[\u2016|]\s*([^*]+)\s*[\u2016|]\s*([^*]+)\*\*", s)'
new = r'm = re.match(r"\*\*([^*]+)\*\*\s*[\u2016|]\s*([^*]+)\s*[\u2016|]\s*([^*]+)\s*[\u2016|]\s*(.+?)\*\?", s)'
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed edu regex")
