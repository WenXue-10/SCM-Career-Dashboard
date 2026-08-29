# -*- coding: utf-8 -*-
"""Resume generator with PDF export.
用法: python -X utf8 gen_resume.py <md_path> <out_docx_path> --template <template_docx>
"""
import sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Import from stable pyc if available
_stable_pyc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_resume_stable.pyc")
if os.path.exists(_stable_pyc):
    import importlib.util
    _spec = importlib.util.spec_from_file_location("gr_stable", _stable_pyc)
    _gr = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_gr)
    _build = _gr.build
    for _n in dir(_gr):
        if not _n.startswith("_"):
            globals()[_n] = getattr(_gr, _n)
else:
    # Fallback: import from __pycache__
    _pyc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__pycache__", "gen_resume.cpython-312.pyc")
    if os.path.exists(_pyc):
        import importlib.util
        _spec = importlib.util.spec_from_file_location("gr_cache", _pyc)
        _gr = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_gr)
        _build = _gr.build
        for _n in dir(_gr):
            if not _n.startswith("_"):
                globals()[_n] = getattr(_gr, _n)
    else:
        print("ERROR: No gen_resume pyc found!", file=sys.stderr)
        sys.exit(1)

def build(md_path, out_path, compact=False, gpa=False):
    data = _build(md_path, out_path, compact=compact, gpa=gpa)
    try:
        import win32com.client
        pdf_path = os.path.splitext(out_path)[0] + ".pdf"
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Open(os.path.abspath(out_path))
        doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
        doc.Close(SaveChanges=False)
        word.Quit()
        print("  pdf:", os.path.basename(pdf_path))
    except Exception as e:
        print("  pdf: skipped (" + str(e) + ")")
    return data
