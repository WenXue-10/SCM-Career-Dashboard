# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\22814\.codex\skills\scm-resume-customization\SKILL.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_table = """| 岗位方向关键词 | 推荐模板 | 关键依据 |
|:---|:---|:---|
| 数据/分析/预测/计划/算法/建模 | 简历-供应链数据方向.md | Python/R/SPSS、4.5万条数据、建模项目前置 |
| 采购/供应商/询价比价/P2P | 简历-项目采购方向.md | 用友U8+采购/库存模块、P2P链路经验前置 |
| 运营/库存/门店/流程/仓配 | 简历-运营管理方向.md | 瑞幸门店库存、项目助理流程经验前置 |
| 管培生/综合/不限方向 | 简历-管培通用方向.md | 综合能力强、跨领域经历前置 |
| 跨方向 JD | 选与 JD 重合度最高的 | 以项目经历匹配度为准 |"""

new_table = """| 岗位方向关键词 | 内容底版（md） | 版式模板（--template） | 关键依据 |
|:---|:---|:---|:---|
| 数据/分析/预测/计划/算法/建模 | 简历-供应链数据方向.md | 文雪_山东大学_供应链数据方向.docx | Python/R/SPSS、4.5万条数据、建模项目前置 |
| 采购/供应商/询价比价/P2P | 简历-项目采购方向.md | 文雪_山东大学_项目采购方向.docx | 用友U8+采购/库存模块、P2P链路经验前置 |
| 运营/库存/门店/流程/仓配 | 简历-运营管理方向.md | 文雪_山东大学_运营管理方向.docx | 瑞幸门店库存、项目助理流程经验前置 |
| 管培生/综合/不限方向 | 简历-管培通用方向.md | 文雪_山东大学_管培通用方向.docx | 综合能力强、跨领域经历前置 |
| 跨方向 JD | 选与 JD 重合度最高的 | 选对应方向的 docx | 以项目经历匹配度为准 |"""

if old_table in content:
    content = content.replace(old_table, new_table)
    print('Updated 2a table')
else:
    print('WARNING: 2a table not found')

old_write = """确认后写入：
- `02_定制简历库/{公司名}/{岗位名}（{方向}）/文雪_山东大学_{公司名}_{岗位名}（{方向}）.md`
- 同一文件夹/文雪_山东大学_{公司名}_{岗位名}（{方向}）.docx"""

new_write = """确认后写入：
- 用 gen_resume.py 生成 Word：`python .workbuddy/gen_resume.py <修改后的md路径> <输出docx路径> --template <对应方向的通用简历docx路径>`
  例：`python .workbuddy/gen_resume.py "02_定制简历库/通用简历/简历-供应链数据方向.md" "02_定制简历库/{公司}/{岗位（方向）}/文雪_山东大学_{公司}_{岗位}（{方向}）.docx" --template "02_定制简历库/通用简历/文雪_山东大学_供应链数据方向.docx"`
- 同文件夹同步生成同名 .pdf（Word COM 导出）
- 写入 md：`02_定制简历库/{公司名}/{岗位名}（{方向}）/文雪_山东大学_{公司名}_{岗位名}（{方向}）.md`"""

if old_write in content:
    content = content.replace(old_write, new_write)
    print('Updated 确认后写入 section')
else:
    print('WARNING: 确认后写入 section not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('SKILL.md done')