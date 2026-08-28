#!/usr/bin/env python3
import sys
import os
import win32com.client
import glob
import shutil


def convert_docx_to_pdf(docx_path, pdf_path=None):
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f'文件不存在: {docx_path}')
    
    if pdf_path is None:
        base, _ = os.path.splitext(docx_path)
        pdf_path = base + '.pdf'
    
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    word.DisplayAlerts = False
    try:
        doc = word.Documents.Open(os.path.abspath(docx_path))
        doc.SaveAs2(os.path.abspath(pdf_path), FileFormat=17)  # 17 = wdFormatPDF
        doc.Close()
    finally:
        word.Quit()
    
    if not os.path.exists(pdf_path):
        raise RuntimeError(f'转换失败，PDF 未生成: {pdf_path}')
    return pdf_path


def main():
    args = sys.argv[1:]
    if not args:
        print('用法: python convert.py <input.docx> [output.pdf]')
        print('      python convert.py <目录路径>   # 批量转换')
        sys.exit(1)
    
    target = args[0]
    pdf_out = args[1] if len(args) > 1 else None
    
    if os.path.isdir(target):
        docx_files = glob.glob(os.path.join(target, '**', '*.docx'), recursive=True)
        if not docx_files:
            print(f'目录下未找到 .docx 文件: {target}')
            sys.exit(1)
        results = []
        for f in docx_files:
            try:
                out = convert_docx_to_pdf(f)
                results.append(out)
            except Exception as e:
                print(f'转换失败: {f} -> {e}')
        print(f'批量完成，共 {len(results)}/{len(docx_files)} 个文件')
        for r in results:
            print(f'  {r}')
    else:
        out = convert_docx_to_pdf(target, pdf_out)
        print(out)


if __name__ == '__main__':
    main()
