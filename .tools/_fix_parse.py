import re

path = r'D:\Obsidian\SCM-Career\.tools\gen_resume.py'
with open(path, encoding='utf-8') as f:
    content = f.read()

# Fix 1: Move intent/summary checks before contact check
# The current order has contact check before intent check
# Need to swap them

# Find and replace the parse_md function entirely
old_func_start = content.index('def parse_md(path):')
old_func_end = content.index('\n\ndef update_header', old_func_start)
old_func = content[old_func_start:old_func_end]

new_func = '''def parse_md(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    d = dict(name="", contact="", intent="", summary="",
             edu_school="", edu_major="", edu_degree="", edu_dates="",
             courses="", honors="",
             projects=[], practices=[], campus=[], skills=[])
    section = None
    item = None
    for line in text.split("\\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith("# "):
            d["name"] = s[2:].strip()
        elif re.match(r"^\\*\\*\\u6c42\\u804c\\u610f\\u5411[：:]\\*\\*", s):
            d["intent"] = re.sub(r"\\*\\*\\u6c42\\u804c\\u610f\\u5411[：:]\\*\\*", "", s).strip()
        elif re.match(r"^\\*\\*\\u4e2a\\u4eba\\u4f18\\u52bf[：:]\\*\\*", s):
            d["summary"] = re.sub(r"\\*\\*\\u4e2a\\u4eba\\u4f18\\u52bf[：:]\\*\\*", "", s).strip()
        elif ("\\u2016" in s or "|" in s) and not s.startswith("**") and not d["contact"]:
            d["contact"] = s
        elif s == "## \\u6559\\u80b2\\u80cc\\u666f":
            section = "edu"
        elif s == "## \\u9879\\u76ee\\u7ecf\\u5386":
            section = "projects"
        elif s == "## \\u5b9e\\u8df5\\u7ecf\\u5386":
            section = "practices"
        elif s == "## \\u6821\\u56ed\\u7ecf\\u5386":
            section = "campus"
        elif s == "## \\u7efc\\u5408\\u6280\\u80fd":
            section = "skills"
        elif section == "edu":
            m = re.match(r"\\*\\*([^*]+)\\*\\*\\s*[\\u2016|]\\s*([^*]+)\\s*[\\u2016|]\\s*([^*]+)\\s*[\\u2016|]\\s*([^*]+)\\*\\*", s)
            if m:
                d["edu_school"] = m.group(1).strip()
                d["edu_major"] = m.group(2).strip()
                d["edu_degree"] = m.group(3).strip()
                d["edu_dates"] = m.group(4).replace("**", "").strip()
            elif "\\u6838\\u5fc3\\u8bfe\\u7a0b" in s:
                d["courses"] = re.sub(r"^\\*\\*[^*]*\\*\\*\\s*", "", s).strip()
            elif "\\u8363\\u8a89\\u5956\\u52b1" in s:
                d["honors"] = re.sub(r"^\\*\\*[^*]*\\*\\*\\s*", "", s).strip()
        elif s.startswith("### "):
            if section in ("projects", "practices", "campus"):
                item = dict(title=s[4:].strip(), role="", dates="", bullets=[])
                d[section].append(item)
        elif s.startswith("**") and ("\\u2016" in s or "|" in s) and item is not None:
            parts = re.split(r"\\*\\*[^*]+\\*\\*\\s*[\\u2016|]\\s*", s, maxsplit=1)
            if len(parts) >= 2:
                item["role"] = parts[0].replace("**", "").strip()
                item["dates"] = parts[1].replace("**", "").strip()
        elif s.startswith("- ") and item is not None:
            item["bullets"].append(s[2:].strip())
        elif section == "skills" and s.startswith("- "):
            d["skills"].append(s[2:].strip())
    return d
'''

content = content[:old_func_start] + new_func + content[old_func_end:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('parse_md fixed')
