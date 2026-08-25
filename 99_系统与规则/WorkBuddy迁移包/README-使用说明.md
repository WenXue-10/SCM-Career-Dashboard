# WorkBuddy 迁移包（文雪求职知识库）

> 生成日期：2026-08-24
> 用途：让 WorkBuddy 与 Codex 都能执行求职全流程（Skill 1-7），产出写入同一个知识库、结果一致。
> 原则：**一套真源（`99_系统与规则/Skill安装版备份/`）+ 两套环境适配**。改规则只改真源，然后用同步脚本一键分发。

## 包内文件
| 文件/目录 | 说明 |
|---|---|
| `skills/` | 7 个 WorkBuddy 适配版 SKILL.md（已替换 Codex 专属表述） |
| `Sync-Skills-To-WorkBuddy.ps1` | 同步脚本：真源 → 适配版；加 `-Install` 直接装到 `~/.workbuddy/skills` |
| `自动化配置-每天12点.md` | WorkBuddy 定时自动化（每天 12:00 执行 Skill 7）的配置文本 |
| `update_site_系统路径版.ps1` | 网站同步脚本的系统路径版（不依赖 Codex 运行时） |

## 安装步骤（一次性）
1. 退出 WorkBuddy。
2. 运行同步脚本安装：
   `powershell -ExecutionPolicy Bypass -File "D:\Obsidian\SCM-Career\99_系统与规则\WorkBuddy迁移包\Sync-Skills-To-WorkBuddy.ps1" -Install`
3. 重启 WorkBuddy → 技能列表应出现 scm-job-matching / scm-job-due-diligence / scm-resume-customization / scm-interview-prep / scm-interview-review / scm-weekly-review / scm-auto-collect。
4. 按 `自动化配置-每天12点.md` 在 WorkBuddy「自动化」里新建每天 12:00 的任务（RRULE 与 Codex 一致）。
5. 手动触发一次 Skill 7 验证全流程（去重→归档→评分→背调→日报）。

## 日常维护（改规则时）
1. 只改真源：`99_系统与规则/Skill安装版备份/scm-*/SKILL.md`
2. 重新同步：运行上面的同步脚本（Codex 侧复制到 `C:\Users\22814\.codex\skills`，WorkBuddy 侧加 `-Install`）
   - 注意：Codex 与 WorkBuddy 的版本只有"环境专属词"不同，规则内容完全一致，保证两边结果一致。

## 差异说明（为什么结果能一致）
- 评分标准、报告六板块、文件路径、确认流程等全部规则相同 → 产出结构一致。
- 仅环境词不同：Chrome 登录态复用（Codex 扩展 ↔ WorkBuddy Web Access）、python 路径、自动化记忆路径、沙箱降级描述。
- 实际生成内容会因模型/检索结果略有差异（同一助手跑两次也会有），但流程与落盘位置完全一致。

## 重要：数据目录位置（2026-08-25 修正）
- WorkBuddy 数据目录现位于 `D:\WorkBuddyData`（junction：`C:\Users\22814\.workbuddy` → `D:\WorkBuddyData\.workbuddy`）。
- **切勿把数据目录放进应用安装目录 `D:\WorkBuddy`**：WorkBuddy 会拒绝更新（提示"应用安装目录下存在用户项目目录"），且更新/卸载可能丢数据。
## ⚠️ 关键前提：自动化执行环境（2026-08-25 发现）
- WorkBuddy 自动化默认跑在**云端沙箱**，无法访问本机 D:\Obsidian\SCM-Career（表现为 Skill 7 一直降级「待普通对话代劳」）。
- 修复：WorkBuddy → 设置 → 运行模式/执行环境 → 切「本机模式/桌面端深度执行」（本机模式要求电脑开机 + WorkBuddy 运行）。

## 当前采用：手动执行模式（2026-08-25 起）
- 定时自动化已停用（云端沙箱无法直连本机 + GitHub 网络不稳），需要时**手动让 WorkBuddy 执行**。
- 操作：打开 WorkBuddy **普通对话**（建议工作目录选 D:\Obsidian\SCM-Career，或新建 SCM-Career 项目）→ 输入"执行 Skill 7（自动岗位监控）"或"执行 Skill X"。
- 本机会话直接读写 D:\Obsidian\SCM-Career → 落库后，本地每 10 分钟自动同步会更新网页/手机。
- 手动执行要求：电脑开机 + WorkBuddy 运行。
- 也可用 Codex（本会话）执行同样的 Skill，两边结果一致。
