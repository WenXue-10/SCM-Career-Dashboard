---
title: Agent 路由
source: SCM-Career 求职知识库
date: 2026-08-29
tags: [路由, Agent, 系统]
---

# AGENTS.md · SCM-Career Agent 路由

> 本文档定义 Codex 在 SCM-Career 中所有 Skill 的触发规则、上下文加载策略和执行路径。

**Vault 路径：D:\Obsidian\SCM-Career**

---

## 渐进式上下文加载

| 任务类型 | 加载上下文 | 说明 |
|---|---|---|
| **快速任务**（评分/背调） | AGENTS.md + 00_战略与定位/文雪-求职目标画像.md | 一条JD，直接评分 |
| **常规任务**（简历定制/复盘） | 快速任务 + 99_系统与规则/系统关联清单.md | 了解目录结构约束 |
| **深度任务**（Skill 7 全量监控） | 常规任务 + 01_岗位搜集与背调/候选线索池.md | 全链路检索 |

**禁止**：全量扫描所有笔记、读取 .git/ 目录、加载已归档内容。

---

## 会话启动协议

1. 读 AGENTS.md（路由规则）
2. 读 00_战略与定位/文雪-求职目标画像.md（用户画像 + 评分规则）
3. 读 99_系统与规则/系统关联清单.md（目录结构约束）
4. 判断任务类型，按需加载更多上下文
5. 执行任务
6. git add -A && git commit && git push origin main

---

## 触发词路由表

| 用户说 | 触发 Skill | 是否自动写入 |
|---|---|---|
| 发 JD 链接/文字 | scm-job-matching（Skill 1） | ✅ 自动 |
| '执行 Skill 1' + JD | scm-job-matching（Skill 1） | ✅ 自动 |
| '执行 Skill 2' / '做背调' | scm-job-due-diligence（Skill 2） | ✅ 自动 |
| '执行 Skill 3' / '改简历' | scm-resume-customization（Skill 3） | ⚠️ 需确认 |
| '执行 Skill 4' / '准备笔试面试' | scm-interview-prep（Skill 4） | ⚠️ 需确认 |
| '执行 Skill 5' / '面试复盘' | scm-interview-review（Skill 5） | ⚠️ 需确认 |
| '执行 Skill 6' / '每周总结' | scm-weekly-review（Skill 6） | ⚠️ 需确认 |
| '执行 Skill 7' / '自动监控' | scm-auto-collect（Skill 7） | ✅ 自动 |
| '发链接/存一下/归档' | baichuan-inbox（百川智库） | ✅ 自动 |

---

## 约束

1. **git 提交**：每次操作完必须 `git add -A && git commit -m "说明" && git push origin main`，不要攒一堆修改最后一起提交
2. **PDF 转换职责划分**：codex 只负责生成 `.docx`，**不要在 codex 里尝试 Word COM 转 PDF**（沙箱环境会失败）。PDF 由 Windows 定时任务 `SCM-Career-ResumePDFSync` 每5分钟自动转换；如需手动转换，用桌面 `简历转PDF.bat`
3. **简历命名规范**：`文雪_山东大学_公司_岗位.docx`，不符合此规范的旧命名文件会被清理
4. 禁止编造：无法确认标注'未收录/未披露'
5. 届别核验：与用户2027届核对，上一届标⚠️
6. Skill 3~6 先预览后确认
7. 禁止提及'AI助手'
8. 遵守全局 `C:\Users\22814\.codex\AGENTS.md` 中的执行准则（问答模式只回答不操作、失败超2次换方案、卡住超2分钟先汇报等）

---
> 最后更新：2026-08-30