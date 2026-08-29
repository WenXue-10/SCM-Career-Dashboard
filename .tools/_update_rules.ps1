$path = "D:\Obsidian\SCM-Career\99_系统与规则\求职Skill规则.md"
$content = Get-Content $path -Raw -Encoding UTF8

# 修改规则7：让它更强制
$old7 = '7. 执行过程中发现问题（工具异常、规则缺口、数据/文件/链接异常等），即时补充到 `99_系统与规则/求职知识库问题日志.md`（问题/原因/处理/状态），并在对话中告知。'
$new7 = '7. **问题日志强制记录（所有 Skill 通用）**：执行过程中发现任何问题（工具异常、规则缺口、数据/文件/链接异常、格式错误、生成失败等），**必须立即**补充到 `99_系统与规则/求职知识库问题日志.md`（编号/日期/问题/原因/处理/状态），**不得等待用户提醒**。记录格式：`| #编号 | 日期 | 问题 | 原因 | 处理 | 状态 | 影响范围 | 状态 |`。并在对话中告知用户已记录。'

if ($content -match [regex]::Escape($old7)) {
    $content = $content -replace [regex]::Escape($old7), $new7
    Write-Host "Rule 7 updated"
} else {
    Write-Host "Rule 7 not found, searching..."
    $content | Select-String -Pattern "问题日志" | Select-Object LineNumber, Line
}

# 在规则10后面加一条：执行后检查
$after10 = '        - 日志格式：每条含 #编号、日期、问题/原因/处理/状态/影响范围，详见日志文件说明'
$before11 = '  ========================================'
$content = $content -replace [regex]::Escape($after10), $after10 + "`n`n  11. **执行后问题检查（所有 Skill 通用）**：每次 Skill 执行完成后，必须检查本次执行过程中是否有新问题需要记录到问题日志。如有，立即追加；如无，确认日志状态列保持最新。"
$content = $content -replace [regex]::Escape($before11), $before11

Set-Content -Path $path -Value $content -Encoding UTF8 -NoNewline
Write-Host "Done"
