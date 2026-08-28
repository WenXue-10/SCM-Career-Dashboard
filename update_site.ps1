# 文雪求职小窝 · 电脑自动同步脚本（优化版 v4）
# 流程：并发保护 → 锁文件清理 → 网络预检查 → 【本地修改自动commit】→ build → commit → push → 状态记录
# v4优化：彻底去掉git pull，知识库（本地）是唯一源头，只从本地上传到远端，杜绝远端覆盖本地

$ErrorActionPreference = "Continue"
$vault  = "D:\Obsidian\SCM-Career"
$git    = "C:\Users\22814\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe"
$gitBin = "C:\Users\22814\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\mingw64\bin"
$py     = "C:\Users\22814\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$logDir = Join-Path $vault "99_系统与规则\sync_log"
$log    = Join-Path $logDir "sync_$(Get-Date -Format 'yyyyMMdd').log"
$statusFile = Join-Path $vault "LAST_SYNC_STATUS.txt"
$pidFile = Join-Path $vault ".sync_pid"
$env:Path = "$gitBin;$env:Path"
Set-Location $vault

# 确保日志目录存在
if(-not (Test-Path $logDir)){ New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

function Log($m){
  $msg = "[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m
  Add-Content -Path $log -Value $msg -Encoding UTF8
}

function Write-Status($status, $detail){
  $content = "状态: $status`n时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n详情: $detail"
  Set-Content -Path $statusFile -Value $content -Encoding UTF8
}

try {
  Log "=== 同步开始 ==="

  # ========== 1. 并发保护（pid文件） ==========
  if(Test-Path $pidFile){
    $oldPid = (Get-Content $pidFile -Raw).Trim()
    $oldProc = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
    if($oldProc){
      Log "上一轮同步仍在运行（PID $oldPid），跳过本轮"
      Write-Status "⏳ 运行中" "上一轮同步仍在进行（PID $oldPid），本轮跳过。"
      exit 0
    } else {
      Log "发现残留pid文件（PID $oldPid，进程已不存在），清理"
      Remove-Item $pidFile -Force
    }
  }
  $PID | Out-File $pidFile -Encoding ASCII
  Log "写入pid文件: $PID"

  # ========== 2. 锁文件自动清理 ==========
  $lockFile = Join-Path $vault ".git\index.lock"
  if(Test-Path $lockFile){
    $gitProcs = Get-Process -Name "git" -ErrorAction SilentlyContinue
    if(-not $gitProcs){
      Log "发现残留 index.lock，无git进程运行，自动删除"
      Remove-Item $lockFile -Force
    } else {
      Log "发现 index.lock，但有git进程运行，不删除"
    }
  }

  # ========== 3. 网络连通性预检查 ==========
  Log "测试GitHub连通性..."
  $netOk = $false
  try {
    $test = Invoke-WebRequest -Uri "https://github.com" -Method Head -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    $netOk = $true
    Log "GitHub连通正常"
  } catch {
    Log "GitHub不可达: $($_.Exception.Message)"
  }

  if(-not $netOk){
    # 网络不可达：仍执行build（本地网页可更新），但不push
    Log "网络不可达，跳过pull/push，仅执行本地build"
    & $py "$vault\build_site.py" *>> $log
    if($LASTEXITCODE -eq 0){
      Log "本地build成功（未push）"
      Write-Status "⚠️ 本地已更新" "GitHub不可达，本地网页已重新生成，未push。网络恢复后自动同步会推送。"
    } else {
      Log "本地build失败"
      Write-Status "❌ 失败" "GitHub不可达且本地build失败。"
    }
    Remove-Item $pidFile -Force
    exit 0
  }

  # ========== 4. 本地修改自动commit（知识库为唯一源头，不从远端拉取） ==========
  # v4关键优化：彻底去掉git pull，知识库（本地）是唯一源头，只从本地上传到远端
  # 永远不会出现远端覆盖本地的情况，杜绝"回退"
  Log "检查本地修改..."
  $localChanges = & $git status --porcelain
  if($localChanges){
    Log "检测到本地未提交更改，自动commit（知识库为唯一源头）"
    & $git add -A *>> $log
    & $git commit -m "auto-commit: 知识库本地修改（$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')）" *>> $log
    if($LASTEXITCODE -eq 0){
      Log "✅ 本地修改已commit"
    } else {
      Log "自动commit无实际变更，继续build"
    }
  } else {
    Log "无本地修改，继续build"
  }

  # ========== 5. 重新生成网站（build失败保护） ==========
  Log "生成网站..."
  & $py "$vault\build_site.py" *>> $log
  $buildExit = $LASTEXITCODE

  $indexHtml = Join-Path $vault "docs\index.html"
  if($buildExit -ne 0 -or -not (Test-Path $indexHtml) -or (Get-Item $indexHtml).Length -lt 1000){
    Log "❌ build失败（exit=$buildExit，index.html存在=$(Test-Path $indexHtml)），不commit"
    Write-Status "❌ 失败" "build_site.py生成失败，未提交。请检查build脚本或查看日志。"
    Remove-Item $pidFile -Force
    exit 1
  }
  Log "网站生成成功"

  # ========== 6. 提交本地改动 ==========
  & $git add -A *>> $log
  $status = (& $git status --porcelain) -join ""
  if($status){
    & $git commit -m "auto-sync: vault update -> site update" *>> $log
    Log "已commit"

    # ========== 7. 推送（重试3次） ==========
    $pushed = $false
    for($i=1; $i -le 3; $i++){
      Log "push第 $i 次..."
      & $git push origin main *>> $log
      if($LASTEXITCODE -eq 0){
        $pushed = $true
        Log "✅ push成功"
        break
      }
      Log "push第 $i 次失败，等待5秒..."
      Start-Sleep -Seconds 5
    }

    if($pushed){
      Log "✅ 同步完成"
      Write-Status "✅ 成功" "同步完成，网页已更新。"
    } else {
      Log "❌ push失败（3次重试）"
      Write-Status "❌ 失败" "commit成功但push失败（3次重试），本地更改已保留。网络恢复后自动同步会推送。"
    }
  } else {
    Log "无更改，跳过commit/push"
    Write-Status "✅ 成功" "无新更改，无需同步。"
  }

} catch {
  Log "error: $($_.Exception.Message)"
  Write-Status "❌ 失败" "脚本异常: $($_.Exception.Message)"
} finally {
  # 清理pid文件
  if(Test-Path $pidFile){ Remove-Item $pidFile -Force }
  Log "=== 同步结束 ==="
}
