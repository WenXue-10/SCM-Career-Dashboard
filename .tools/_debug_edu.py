import re

path = r"D:\Obsidian\SCM-Career\.tools\gen_resume.py"
with open(path, encoding="utf-8") as f:
    content = f.read()

# Find the edu regex line
for i, l in enumerate(content.split("\n")):
    if "edu_school" in l and "match" in l:
        print(f"Line {i+1}: {l.strip()[:120]}")
        # Extract pattern
        m = re.search(r'r"(.*?)"', l)
        if m:
            pat_str = m.group(1)
            print(f"Pattern: {repr(pat_str)}")
            # Test
            line = "**山东大学** ｜ 管理科学与工程类-供应链管理专业 本科 ｜ 2022.09-2027.06"
            print(f"Line: {repr(line)}")
            pat = re.compile(pat_str)
            result = pat.match(line)
            print(f"Match: {result.groups() if result else None}")
        break
