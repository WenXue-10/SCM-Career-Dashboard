# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    自动检查并修复求职知识库问题日志的表格格式问题。
.DESCRIPTION
    - 扫描表格记录之间的空行，自动删除（空行会导致 Markdown 表格被截断）
    - 检查最后一条记录后面是否有多余空行
    - 输出修复结果
#>

$ErrorActionPreference = 'Stop'

$logFile = 'D:\Obsidian\SCM-Career\99_系统与规则\求职知识库问题日志.md'

Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  问题日志格式检查与修复工具' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''

if (-not (Test-Path $logFile)) {
    Write-Host "❌ 找不到问题日志文件：$logFile" -ForegroundColor Red
    exit 1
}

# 读取文件
$lines = Get-Content $logFile -Encoding utf8
$originalCount = $lines.Count
Write-Host "📄 原始文件：$originalCount 行" -ForegroundColor Yellow
Write-Host ''

# 找到表格开始的位置（表头分隔行）
$tableStart = -1
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\| :--:' -or $lines[$i] -match '^\| #+\s*\|') {
        $tableStart = $i
        break
    }
}

if ($tableStart -lt 0) {
    Write-Host '❌ 找不到表格开始位置' -ForegroundColor Red
    exit 1
}

Write-Host "📊 表格开始于第 $($tableStart + 1) 行" -ForegroundColor Yellow
Write-Host ''

# 扫描表格记录之间的空行
$fixedLines = @()
$emptyLineCount = 0
$inTable = $false
$lastWasTableRecord = $false

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    
    # 检测表格开始
    if ($i -eq $tableStart) {
        $inTable = $true
    }
    
    if (-not $inTable) {
        # 表格之前的内容，直接保留
        $fixedLines += $line
        continue
    }
    
    # 表格内的处理
    if ($line -match '^\| #\d+') {
        # 这是一条表格记录
        if ($lastWasTableRecord -or ($line -match '^\| #1\b')) {
            # 上一条也是记录，或者这是第一条记录，直接添加
            $fixedLines += $line
        } else {
            # 上一条不是记录（可能是空行），先检查是否需要保留
            # 表格记录之间的空行要删除
            $fixedLines += $line
        }
        $lastWasTableRecord = $true
    } elseif ($line.Trim() -eq '') {
        # 空行
        if ($lastWasTableRecord) {
            # 上一条是记录，这个空行可能是记录之间的，需要检查后面是否还有记录
            # 先标记，等看到下一条记录再决定是否删除
            $emptyLineCount++
            # 暂时不添加，等确认后面是否还有记录
            continue
        } else {
            # 上一条不是记录，保留空行（可能是表格结束后的空行）
            $fixedLines += $line
        }
        $lastWasTableRecord = $false
    } else {
        # 其他行（非记录、非空行）
        if ($emptyLineCount -gt 0) {
            # 之前有暂存的空行，现在确认后面不是记录，所以保留这些空行
            for ($j = 0; $j -lt $emptyLineCount; $j++) {
                $fixedLines += ''
            }
            $emptyLineCount = 0
        }
        $fixedLines += $line
        $lastWasTableRecord = $false
    }
}

# 处理末尾暂存的空行（如果最后一条是记录，后面的空行要保留1个作为文件结尾）
if ($emptyLineCount -gt 0) {
    # 最后一条是记录，保留1个空行作为文件结尾
    $fixedLines += ''
}

# 更简单可靠的方法：重新扫描，直接删除表格记录之间的空行
Write-Host '🔍 正在扫描表格记录之间的空行...' -ForegroundColor Yellow

$simpleFixed = @()
$tableStarted = $false
$prevIsRecord = $false
$removedCount = 0

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    
    if ($i -eq $tableStart) {
        $tableStarted = $true
    }
    
    if (-not $tableStarted) {
        $simpleFixed += $line
        continue
    }
    
    $isRecord = $line -match '^\| #\d+'
    $isEmpty = $line.Trim() -eq ''
    
    if ($isRecord) {
        $simpleFixed += $line
        $prevIsRecord = $true
    } elseif ($isEmpty) {
        if ($prevIsRecord) {
            # 上一条是记录，这个空行可能是记录之间的，先暂存
            # 检查后面是否还有记录
            $hasNextRecord = $false
            for ($j = $i + 1; $j -lt $lines.Count; $j++) {
                if ($lines[$j] -match '^\| #\d+') {
                    $hasNextRecord = $true
                    break
                } elseif ($lines[$j].Trim() -ne '' -and $lines[$j] -notmatch '^\|') {
                    # 遇到非表格内容，说明表格结束了
                    break
                }
            }
            
            if ($hasNextRecord) {
                # 后面还有记录，这个空行是记录之间的，删除
                $removedCount++
                continue
            } else {
                # 后面没有记录了，这是表格结束后的空行，保留
                $simpleFixed += $line
                $prevIsRecord = $false
            }
        } else {
            # 上一条不是记录，保留空行
            $simpleFixed += $line
        }
    } else {
        # 其他行
        $simpleFixed += $line
        $prevIsRecord = $false
    }
}

# 写回文件
$newCount = $simpleFixed.Count
Write-Host ''
Write-Host "📊 修复结果：" -ForegroundColor Cyan
Write-Host "  原始行数：$originalCount"
Write-Host "  修复后行数：$newCount"
Write-Host "  删除空行：$removedCount 个"
Write-Host ''

if ($removedCount -gt 0) {
    # 备份原文件
    $backupFile = $logFile + '.bak'
    Copy-Item $logFile $backupFile -Force
    Write-Host "💾 已备份原文件到：$backupFile" -ForegroundColor Yellow
    
    # 写回修复后的内容
    $simpleFixed | Out-File $logFile -Encoding utf8
    Write-Host ''
    Write-Host '✅ 修复完成！问题日志表格格式已恢复正常。' -ForegroundColor Green
    Write-Host '   所有记录现在都在表格里，不会再出现"最后一条不在表格里"的问题。'
} else {
    Write-Host '✅ 没有发现格式问题，文件无需修改。' -ForegroundColor Green
}

Write-Host ''
Write-Host '========================================' -ForegroundColor Cyan
