# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    用 Word COM 把 docx 转换成 PDF，格式跟 Word 里看到的一模一样。
.DESCRIPTION
    - 直接双击运行：转换 02_定制简历库 文件夹里所有 docx
    - 拖拽 docx 文件到脚本上：只转换拖拽的文件
    - 转换完成后自动 git add + commit + push（定时任务模式）
#>

$ErrorActionPreference = 'Stop'

# 简历库路径
$resumeDir = 'D:\Obsidian\SCM-Career\02_定制简历库'
$repoDir = 'D:\Obsidian\SCM-Career'

# 判断是否是交互模式（用户双击运行）还是定时任务模式
$isInteractive = [Environment]::UserInteractive -and ($args.Count -eq 0)

Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  简历转 PDF 工具（Word 原生转换）' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''

# 收集要转换的文件
$files = @()
if ($args.Count -gt 0) {
    # 拖拽模式：只转换拖拽的 docx 文件
    Write-Host '📂 拖拽模式：转换指定文件' -ForegroundColor Yellow
    $files = $args | Where-Object { $_ -like '*.docx' -and $_ -notlike '~$*' }
} else {
    # 双击/定时模式：转换整个简历库
    Write-Host '📂 全库模式：转换 02_定制简历库 所有 docx' -ForegroundColor Yellow
    if (Test-Path $resumeDir) {
        $files = Get-ChildItem $resumeDir -Recurse -Filter '*.docx' |
            Where-Object { $_.Name -notlike '~$*' } |
            ForEach-Object { $_.FullName }
    } else {
        Write-Host "❌ 找不到简历库目录：$resumeDir" -ForegroundColor Red
        if ($isInteractive) { Read-Host '按回车键退出' }
        exit 1
    }
}

if ($files.Count -eq 0) {
    Write-Host '❌ 没有找到可转换的 docx 文件' -ForegroundColor Red
    if ($isInteractive) { Read-Host '按回车键退出' }
    exit 1
}

Write-Host "找到 $($files.Count) 个 docx 文件，开始转换..." -ForegroundColor Green
Write-Host ''

# 启动 Word
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
} catch {
    Write-Host "❌ 无法启动 Word：$($_.Exception.Message)" -ForegroundColor Red
    if ($isInteractive) { Read-Host '按回车键退出' }
    exit 1
}

$success = 0
$failed = 0
$failedFiles = @()

foreach ($f in $files) {
    $name = [System.IO.Path]::GetFileName($f)
    try {
        $pdf = [System.IO.Path]::ChangeExtension($f, '.pdf')
        $doc = $word.Documents.Open($f)
        $doc.SaveAs([ref]$pdf, [ref]17)  # 17 = wdFormatPDF
        $doc.Close($false)
        Write-Host "  ✅ $name" -ForegroundColor Green
        $success++
    } catch {
        Write-Host "  ❌ $name - $($_.Exception.Message)" -ForegroundColor Red
        $failed++
        $failedFiles += $name
    }
}

# 关闭 Word
try {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
} catch {
    # 忽略关闭错误
}

Write-Host ''
Write-Host '========================================' -ForegroundColor Cyan
Write-Host "  转换完成：成功 $success 个，失败 $failed 个" -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan

if ($failedFiles.Count -gt 0) {
    Write-Host ''
    Write-Host '失败文件：' -ForegroundColor Red
    $failedFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}

# ========== 自动 git commit + push（定时任务模式）==========
if (-not $isInteractive) {
    Write-Host ''
    Write-Host '=== 自动同步到 git ===' -ForegroundColor Cyan
    
    try {
        Set-Location $repoDir
        
        # 清理可能残留的锁文件
        $lockFile = Join-Path $repoDir '.git\index.lock'
        if (Test-Path $lockFile) {
            Remove-Item $lockFile -Force
            Write-Host '  🔓 已清理残留的 git 锁文件' -ForegroundColor Yellow
        }
        
        # 检查是否有变更
        $status = git status --porcelain 2>&1
        if ([string]::IsNullOrWhiteSpace($status)) {
            Write-Host '  ✅ 没有新的变更，无需提交' -ForegroundColor Green
        } else {
            $changedCount = ($status | Measure-Object -Line).Lines
            Write-Host "  📝 发现 $changedCount 个变更文件，开始提交..." -ForegroundColor Yellow
            
            # git add
            git add -A 2>&1 | Out-Null
            
            # git commit
            $commitMsg = "auto: 定时任务转换简历PDF ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))"
            git commit -m $commitMsg 2>&1 | Out-Null
            Write-Host "  ✅ 已提交：$commitMsg" -ForegroundColor Green
            
            # git push
            $pushResult = git push origin main 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host '  ✅ 已推送到远程仓库' -ForegroundColor Green
            } else {
                Write-Host "  ⚠️ 推送失败（可能是网络问题）：$pushResult" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "  ⚠️ git 同步出错：$($_.Exception.Message)" -ForegroundColor Yellow
        # git 操作失败不影响主流程
    }
}

Write-Host ''
if ($isInteractive) {
    Read-Host '按回车键退出'
}
