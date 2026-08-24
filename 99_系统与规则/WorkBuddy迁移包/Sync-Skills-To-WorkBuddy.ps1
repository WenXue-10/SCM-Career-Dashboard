# 同步脚本：知识库真源(Skill安装版备份) → WorkBuddy 适配版
# 用法：powershell -ExecutionPolicy Bypass -File Sync-Skills-To-WorkBuddy.ps1 [-Install]
#   -Install 参数会把生成的适配版直接复制到 ~/.workbuddy/skills（建议先退出 WorkBuddy）
param([switch]$Install)
$ErrorActionPreference = "Stop"
$root = "D:\Obsidian\SCM-Career"
$src  = Join-Path $root "99_系统与规则\Skill安装版备份"
$pkg  = Join-Path $root "99_系统与规则\WorkBuddy迁移包"
$out  = Join-Path $pkg "skills"

$repls = @(
  @('$CODEX_HOME/automations/daily-brief/memory.md','WorkBuddy 自动化记忆文件（~/.workbuddy 下对应自动化的 memory；不存在则按 07_原始材料库 与岗位汇总表去重恢复）'),
  @('Codex Chrome 扩展','WorkBuddy Web Access（浏览器自动化，CDP 复用 Chrome 已登录会话）'),
  @('Codex Chrome扩展','WorkBuddy Web Access'),
  @('Codex 自动提取','AI 自动提取'),
  @('Codex 直接抓详情','AI 直接抓详情'),
  @('Codex 自动 OCR','AI 自动 OCR'),
  @('由 Codex 代写','由 AI 代写'),
  @('"C:/Users/22814/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"','<WorkBuddy 可用的 python 完整路径，优先系统 python/py>'),
  @('load_workspace_dependencies','WorkBuddy 运行时依赖工具'),
  @('（Windows 已知 bug：受限权限线程命令可能全被 blocked by policy）','（沙箱/权限限制）'),
  @('命令被策略拦截降级','命令被权限/沙箱限制拦截降级'),
  @('自动化线程已允许写知识库（`D:\Obsidian\SCM-Career` 可写），直接用普通写文件命令，无需提权、无需等待批准。','自动化环境已授权写知识库（D:\Obsidian\SCM-Career），直接用普通写文件命令；若首次提示需要授权，申请一次即可。')
)

$utf8bom = New-Object System.Text.UTF8Encoding($true)
Get-ChildItem -Directory -LiteralPath $src | Sort-Object Name | ForEach-Object {
  $skill = $_.Name
  $content = Get-Content -Raw -Encoding UTF8 (Join-Path $_.FullName "SKILL.md")
  foreach($r in $repls){ $content = $content.Replace($r[0], $r[1]) }
  $outDir = Join-Path $out $skill
  New-Item -ItemType Directory -Force -Path $outDir | Out-Null
  [System.IO.File]::WriteAllText((Join-Path $outDir "SKILL.md"), $content, $utf8bom)
  Write-Output "生成: $skill"
}
if($Install){
  $wbSkills = Join-Path $env:USERPROFILE ".workbuddy\skills"
  Get-ChildItem -Directory -LiteralPath $out | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $wbSkills $_.Name) -Recurse -Force
    Write-Output "已安装: $($_.Name) -> $wbSkills"
  }
}else{
  Write-Output "（未加 -Install，仅生成到迁移包；确认无误后加 -Install 安装到 WorkBuddy）"
}