path = r"D:\Obsidian\SCM-Career\.tools\gen_resume.py"
with open(path, encoding="utf-8") as f:
    content = f.read()

# The patterns in the file use raw strings with \u escapes that don't work in regex
# Need to replace with actual Chinese characters and correct pattern order

# Fix intent: **求职意向**： (星号在关键词两侧，冒号在后)
content = content.replace(
    r"re.match(r\"^\*\*求职意向[：:]\*\*\", s)",
    r"re.match(r\"^\\*\\*求职意向\\*\\*[：:]\", s)"
)
content = content.replace(
    r"re.sub(r\"\\*\\*求职意向[：:]\\*\\*\", \"\", s)",
    r"re.sub(r\"\\*\\*求职意向\\*\\*[：:]\", \"\", s)"
)
content = content.replace(
    r"re.match(r\"^\*\*个人优势[：:]\*\*\", s)",
    r"re.match(r\"^\\*\\*个人优势\\*\\*[：:]\", s)"
)
content = content.replace(
    r"re.sub(r\"\\*\\*个人优势[：:]\\*\\*\", \"\", s)",
    r"re.sub(r\"\\*\\*个人优势\\*\\*[：:]\", \"\", s)"
)
# Fix courses/honors: strip **keyword**： prefix
content = content.replace(
    r"re.sub(r\"^\*\*[^*]*\*\*\s*\", \"\", s)",
    r"re.sub(r\"^\\*\\*[^*]*\\*\\*[：:]\\s*\", \"\", s)"
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
