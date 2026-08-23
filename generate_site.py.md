import os
import re
from datetime import datetime

# ====== 配置区域（如果你的文件夹名字不同，改这里）======
BASE_DIR = "_01_岗位搜集与背调"      # 你的岗位调研文件夹名
OUTPUT_HTML = "index.html"          # 生成的网页文件名
# =====================================================

def parse_frontmatter(content):
    """提取 --- 之间的 YAML 字段（公司、城市、总分等）"""
    match = re.search(r'---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    frontmatter = match.group(1)
    data = {}
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            data[key.strip()] = val.strip()
    return data

def scan_jobs():
    """遍历文件夹，收集所有岗位笔记的 frontmatter 数据"""
    jobs = []
    if not os.path.exists(BASE_DIR):
        print(f"❌ 错误：找不到文件夹 '{BASE_DIR}'，请检查路径")
        return jobs
    
    for company in os.listdir(BASE_DIR):
        company_path = os.path.join(BASE_DIR, company)
        if not os.path.isdir(company_path):
            continue
        for position in os.listdir(company_path):
            pos_path = os.path.join(company_path, position)
            if not os.path.isdir(pos_path):
                continue
            for file in os.listdir(pos_path):
                if file.endswith('.md'):
                    file_path = os.path.join(pos_path, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    data = parse_frontmatter(content)
                    if data:
                        # 从文件名提取方向（去掉 .md）
                        direction = file.replace('.md', '')
                        jobs.append({
                            "公司": company,
                            "岗位": position,
                            "方向": direction,
                            "城市": data.get('城市', '未标注'),
                            "总分": data.get('总分', 'N/A'),
                            "等级": data.get('等级', 'N/A'),
                            "状态": data.get('状态', '新收录'),
                            "薪资": data.get('薪资', '未披露'),
                            "链接": data.get('链接', '#'),
                        })
    return jobs

def generate_html(jobs):
    """生成手机自适应的 HTML 页面"""
    rows = ""
    for j in jobs:
        # 根据总分给分数上色
        score = j['总分']
        if score != 'N/A' and str(score).isdigit():
            score_val = int(score)
            if score_val >= 80:
                score_class = 'score-high'
            elif score_val >= 70:
                score_class = 'score-mid'
            else:
                score_class = 'score-low'
        else:
            score_class = 'score-unknown'
        
        rows += f"""
        <tr>
            <td><strong>{j['公司']}</strong></td>
            <td>{j['岗位']}</td>
            <td>{j['城市']}</td>
            <td><span class="{score_class}">{j['总分']}</span></td>
            <td>{j['等级']}</td>
            <td><span class="status">{j['状态']}</span></td>
            <td>{j['薪资']}</td>
            <td><a href="{j['链接']}" target="_blank">🔗</a></td>
        </tr>
        """
    
    html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
    <title>2027秋招 · 岗位汇总</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
            background: #f1f5f9;
            padding: 12px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 20px;
            padding: 20px 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        }}
        h1 {{
            color: #0f172a;
            font-size: 22px;
            font-weight: 700;
            border-left: 5px solid #3b82f6;
            padding-left: 14px;
            margin-bottom: 6px;
        }}
        .meta {{
            color: #64748b;
            font-size: 13px;
            margin: 8px 0 18px 0;
            padding-left: 19px;
            border-bottom: 1px solid #e9edf2;
            padding-bottom: 14px;
        }}
        .meta span {{
            background: #e2e8f0;
            padding: 2px 12px;
            border-radius: 30px;
            font-weight: 600;
            color: #1e293b;
        }}
        .table-wrap {{
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin: 0 -4px;
        }}
        table {{
            width: 100%;
            min-width: 680px;
            border-collapse: collapse;
            font-size: 13px;
        }}
        th {{
            background: #f1f5f9;
            color: #334155;
            font-weight: 600;
            padding: 10px 8px;
            text-align: left;
            border-radius: 8px;
            white-space: nowrap;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }}
        td {{
            padding: 10px 8px;
            border-bottom: 1px solid #f0f2f5;
            vertical-align: middle;
        }}
        tr:hover {{
            background: #fafbfc;
        }}
        .score-high {{
            background: #dcfce7;
            color: #166534;
            font-weight: 700;
            padding: 2px 12px;
            border-radius: 30px;
            font-size: 13px;
        }}
        .score-mid {{
            background: #fef9c3;
            color: #854d0e;
            font-weight: 700;
            padding: 2px 12px;
            border-radius: 30px;
            font-size: 13px;
        }}
        .score-low {{
            background: #fee2e2;
            color: #991b1b;
            font-weight: 700;
            padding: 2px 12px;
            border-radius: 30px;
            font-size: 13px;
        }}
        .score-unknown {{
            background: #f1f5f9;
            color: #64748b;
            padding: 2px 12px;
            border-radius: 30px;
            font-size: 12px;
        }}
        .status {{
            background: #dbeafe;
            color: #1d4ed8;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 12px;
            white-space: nowrap;
        }}
        a {{
            text-decoration: none;
            color: #3b82f6;
            font-size: 18px;
        }}
        a:hover {{
            opacity: 0.7;
        }}
        .footer {{
            text-align: center;
            color: #94a3b8;
            font-size: 11px;
            margin-top: 22px;
            padding-top: 16px;
            border-top: 1px solid #e9edf2;
        }}
        .count-badge {{
            background: #3b82f6;
            color: white;
            padding: 0 12px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 600;
            margin-left: 6px;
        }}
        @media (max-width: 600px) {{
            body {{ padding: 8px; }}
            .container {{ padding: 12px 10px; border-radius: 14px; }}
            h1 {{ font-size: 18px; padding-left: 10px; }}
            .meta {{ font-size: 12px; padding-left: 14px; }}
            th, td {{ padding: 7px 4px; font-size: 11px; }}
            th {{ font-size: 10px; }}
            .score-high, .score-mid, .score-low, .score-unknown {{ padding: 1px 8px; font-size: 11px; }}
            .status {{ font-size: 10px; padding: 1px 8px; }}
            a {{ font-size: 15px; }}
            .table-wrap {{ margin: 0 -2px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 2027届秋招 · 岗位汇总</h1>
        <div class="meta">
            📅 更新于：{datetime.now().strftime('%Y-%m-%d %H:%M')} &nbsp;·&nbsp; 
            共 <span>{len(jobs)}</span> 个岗位
        </div>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>公司</th>
                        <th>岗位</th>
                        <th>城市</th>
                        <th>总分</th>
                        <th>等级</th>
                        <th>状态</th>
                        <th>薪资</th>
                        <th>链接</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        <div class="footer">
            ⚡ 数据来源：Obsidian 知识库 · 由 Codex 自动同步
        </div>
    </div>
</body>
</html>"""
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ 网页已生成：{OUTPUT_HTML}，共 {len(jobs)} 条岗位记录")

if __name__ == "__main__":
    jobs = scan_jobs()
    if jobs:
        generate_html(jobs)
    else:
        print("⚠️ 未找到任何岗位记录，请检查文件夹路径是否正确。")