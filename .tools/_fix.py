path = r"D:\Obsidian\SCM-Career\.tools\gen_resume.py"
    if i < len(lines): lines[i] = ""
lines[23] = "def add_run(para, text, bold=False, size=10.5):\n"
    if i < len(lines): lines[i] = ""
lines[25] = "    run.bold = bold\n"
print("Done")
lines[37] = "        clear_para(cell.paragraphs[0])\n"
lines = open(path, encoding="utf-8").readlines()
open(path, "w", encoding="utf-8").writelines(lines)
for i in range(23, 35):
lines[26] = "    run.font.size = Pt(size)\n"
lines[40] = "        cell.text = text\n"
