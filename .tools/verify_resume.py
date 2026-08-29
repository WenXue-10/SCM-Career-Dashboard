# -*- coding: utf-8 -*-
"""
简历事实校验脚本：检查简历md中是否有不在白名单中的内容。
用法: python -X utf8 verify_resume.py <简历md路径>
"""
import re
import sys
import os

BASE = r"D:/Obsidian/SCM-Career"
WHITELIST = os.path.join(BASE, "08_个人资料库", "个人资料白名单.md")

# 从白名单提取课程列表
def load_courses():
    with open(WHITELIST, encoding="utf-8") as f:
        text = f.read()
    # 只取"一、核心课程白名单"区（避免把项目/校园等其他区的数字列表项误当课程）
    if "## 一、核心课程白名单" in text:
        sec = text.split("## 一、核心课程白名单")[1]
        sec = sec.split("## 二、项目经历白名单")[0]
    else:
        sec = text
    courses = []
    # 匹配 "数字. 课程名" 格式
    for m in re.finditer(r'^\d+\.\s+(.+)$', sec, re.MULTILINE):
        name = m.group(1).strip()
        # 去掉括号注释
        name = re.sub(r'[（(].*?[）)]', '', name).strip()
        if name and len(name) > 1:
            courses.append(name)
    return courses

# 从白名单提取项目/经历标题（含别名）
def load_experiences():
    with open(WHITELIST, encoding="utf-8") as f:
        text = f.read()
    items = []
    # 匹配 "#### 数字. 标题"
    for m in re.finditer(r'^####\s+\d*\.?\s*(.+)$', text, re.MULTILINE):
        title = m.group(1).strip()
        title = re.sub(r'[（(].*?[）)]', '', title).strip()
        if title and len(title) > 1:
            items.append(title)
    # 匹配别名行 "- **别名**：xxx、yyy、zzz"
    for m in re.finditer(r'\*\*别名\*\*[：:]\s*(.+)', text):
        aliases = re.split(r'[、,，]', m.group(1))
        for a in aliases:
            a = a.strip()
            if a and len(a) > 1:
                items.append(a)
    # 校园与社会实践白名单区（第四区）列表项：\d+. 标题（可带角色/时间/描述）
    if "## 四、校园与社会实践白名单" in text:
        sec = text.split("## 四、校园与社会实践白名单")[1]
        sec = sec.split("## 五、技能证书白名单")[0]
        for m in re.finditer(r'^\d+\.\s+(.+)$', sec, re.MULTILINE):
            title = m.group(1).strip()
            title = re.split(r'——', title)[0].strip()          # 去掉"——"后的描述
            title = re.split(r'\s*·\s*', title)[0].strip()      # 去掉" · 角色"部分
            title = re.sub(r'[（(].*?[）)]', '', title).strip() # 去掉括号注释/时间
            if title and len(title) > 1:
                items.append(title)
    return items

def verify_resume(md_path):
    if not os.path.exists(md_path):
        print(f"❌ 文件不存在: {md_path}")
        return False

    with open(md_path, encoding="utf-8") as f:
        text = f.read()

    courses_whitelist = load_courses()
    exp_whitelist = load_experiences()

    errors = []
    warnings = []

    # 1. 检查核心课程
    m = re.search(r'\*\*核心课程\*\*[：:]\s*(.+)', text)
    if m:
        course_line = m.group(1).strip()
        # 按顿号/逗号分割
        resume_courses = re.split(r'[、,，]', course_line)
        for c in resume_courses:
            c = c.strip()
            if not c:
                continue
            # 检查是否在白名单中（模糊匹配）
            found = any(c in w or w in c for w in courses_whitelist)
            if not found:
                errors.append(f"核心课程不在白名单: '{c}'")

    # 2. 检查项目/经历标题（### 开头）
    for m in re.finditer(r'^###\s+(.+)$', text, re.MULTILINE):
        title = m.group(1).strip()
        # 去掉括号注释
        title_clean = re.sub(r'[（(].*?[）)]', '', title).strip()
        found = any(title_clean in w or w in title_clean for w in exp_whitelist)
        if not found and len(title_clean) > 2:
            warnings.append(f"项目/经历标题不在白名单: '{title}'（可能是别名，请确认）")

    # 3. 检查荣誉奖励
    m = re.search(r'\*\*荣誉奖励\*\*[：:]\s*(.+)', text)
    if m:
        honor = m.group(1).strip()
        if "二等奖" in honor and "优秀等级" not in honor:
            errors.append(f"荣誉奖励口径错误: '{honor}'（应为'优秀等级（校级立项·团队成员）'，禁止写'二等奖'）")

    # 4. 检查教育背景时间
    if "2022.09" not in text and "2022.09" not in text.replace("-", "."):
        if "2022" not in text:
            warnings.append("教育背景可能缺少入学年份2022")

    # 输出报告
    print(f"\n{'='*50}")
    print(f"简历事实校验报告: {os.path.basename(md_path)}")
    print(f"{'='*50}")

    if errors:
        print(f"\n❌ 错误 ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\n✅ 无错误")

    if warnings:
        print(f"\n⚠️  警告 ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("\n✅ 无警告")

    print(f"\n白名单课程数: {len(courses_whitelist)}")
    print(f"白名单经历数: {len(exp_whitelist)}")

    return len(errors) == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python -X utf8 verify_resume.py <简历md路径>")
        print("批量校验所有简历: python -X utf8 verify_resume.py --all")
        sys.exit(1)

    if sys.argv[1] == "--all":
        # 批量校验所有简历
        resume_dir = os.path.join(BASE, "02_定制简历库")
        all_md = []
        for root, dirs, files in os.walk(resume_dir):
            for f in files:
                if f.endswith(".md") and ("文雪" in f or "简历-" in f):
                    all_md.append(os.path.join(root, f))

        print(f"找到 {len(all_md)} 份简历")
        passed = 0
        for md in sorted(all_md):
            ok = verify_resume(md)
            if ok:
                passed += 1
        print(f"\n{'='*50}")
        print(f"批量校验结果: {passed}/{len(all_md)} 通过")
        print(f"{'='*50}")
    else:
        verify_resume(sys.argv[1])
