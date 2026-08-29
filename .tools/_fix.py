path = r"D:\Obsidian\SCM-Career\.tools\gen_resume.py"
with open(path, encoding="utf-8") as f:
    lines = f.readlines()

fixed = 0
for i in range(len(lines)):
    line = lines[i]
    # Fix colon at end of findall calls: }": -> })
    if 'findall' in line and line.strip().endswith('":'):
        lines[i] = line.rstrip()[:-1] + ')\n'
        fixed += 1
    # Fix missing // in f-string
    elif '.://{NS}' in line:
        lines[i] = line.replace('.://{NS}', './/{NS}')
        fixed += 1

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Fixed " + str(fixed) + " lines")
