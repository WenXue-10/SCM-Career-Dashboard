# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'D:\Obsidian\SCM-Career\02_定制简历库\通用简历\简历-供应链数据方向.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the 电商项目 section
import re
# Match from ### 电商用户行为分析... to the next ## or end
pattern = r'\n### 电商用户行为分析与运营策略研究\n\*\*个人课程项目\*\* \| 2025\.10—2025\.12\n\n- 问卷分析：基于TAM模型设计7点李克特量表问卷，回收328份有效样本，用SPSS和Python完成统计分析\n- 因素识别：验证交互性（β=0\.42）、个性化（β=0\.38）、自主性（β=0\.31）显著正向影响用户感知价值，识别问题识别准确性、智能解决能力为核心影响因素\n- 结论输出：发现用户智能体验起关键中介作用，感知增强维度贡献率63%，为电商AI客服优化提供参考\n'
content = re.sub(pattern, '\n', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Removed 电商项目 from 供应链数据方向')
