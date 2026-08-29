import os
lines = []
lines.append('# -*- coding: utf-8 -*-')
lines.append('"""Resume generator with PDF export.')
lines.append('Usage: python -X utf8 gen_resume.py <md_path> <out_docx_path> --template <template_docx>')
lines.append('"""')
lines.append('import sys, os, re, shutil, tempfile')
lines.append("if hasattr(sys.stdout, 'reconfigure'):")
lines.append("    sys.stdout.reconfigure(encoding='utf-8')")
lines.append('try:')
lines.append('    from docx import Document')
lines.append('    from docx.oxml.ns import qn')
lines.append('    from docx.oxml import OxmlElement')
lines.append('    from docx.shared import Pt')
lines.append('except ImportError:')
lines.append("    print('ERROR: python-docx not installed', file=sys.stderr)")
lines.append('    sys.exit(1)')
lines.append("")
lines.append("NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'")
lines.append('')
# Write to file
path = r'D:\Obsidian\SCM-Career\.tools\gen_resume.py'
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f'Part 1 written: {len(lines)} lines')
