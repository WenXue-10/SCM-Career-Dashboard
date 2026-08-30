$path = "C:\Users\22814\.codex\skills\scm-resume-customization\SKILL.md"
$content = Get-Content $path -Raw -Encoding UTF8

# 1. 更新 ATS 规则
$old = "- **ATS 关键词匹配检测**：定制化修改前，从 JD 提取全部关键词（技能/工具/专业术语/能力要求），与简历原文逐一比对，给出匹配百分比；匹配度 <70% 时调板块/换词提升命中，禁止为提分编造。"
$new = "- **ATS 关键词匹配检测（双阶段）**：
  1. **修改前检测**：从 JD 提取全部关键词（技能/工具/专业术语/能力要求），与简历原文逐一比对，给出匹配百分比；
  2. **修改后复检**：简历内容修改完成后，再次执行 ATS 检测，确认匹配度提升；
  3. 匹配度 <70% 时调板块/换词提升命中，禁止为提分编造；复检仍 <70% 时在修改说明中标注「需补充XX经历」。"

if ($content -match [regex]::Escape($old.Substring(0,30))) {
    $content = $content -replace [regex]::Escape($old), $new
    Write-Host "ATS rule updated"
} else {
    Write-Host "ATS pattern search failed"
}

# 2. 更新写入规则
$old2 = '- 同步更新对应评分笔记 ``01_岗位搜集与背调/公司调研/{公司名}/{岗位名}（{方向}）/评分-{公司名}-{岗位名}（{方向}）.md``：
frontmatter「定制简历」字段与正文「## 定制简历」小节写入简历链接，frontmatter「当前状态」更新为 📮 待投递。'
$new2 = '- 同步更新对应评分笔记 ``01_岗位搜集与背调/公司调研/{公司名}/{岗位名}（{方向}）/评分-{公司名}-{岗位名}（{方向}）.md``：
  1. frontmatter「定制简历」字段写入：``定制简历: "[[文雪_山东大学_{公司名}_{岗位名}（{方向}）]]"``
  2. 正文「## 定制简历」小节更新链接：``- 链接：[[文雪_山东大学_{公司名}_{岗位名}（{方向}）]]``
  3. frontmatter「当前状态」更新为 📮 待投递'

if ($content -match '同步更新对应评分笔记') {
    $content = $content -replace [regex]::Escape($old2), $new2
    Write-Host "Write rule updated"
} else {
    Write-Host "Write pattern search failed"
}

Set-Content -Path $path -Value $content -Encoding UTF8
Write-Host "Done"
