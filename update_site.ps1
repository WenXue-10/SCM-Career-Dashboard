# 文雪求职小窝 · 电脑自动同步脚本
# 流程：拉取远端(GitHub) → 重新生成网站 → 提交本地改动 → 推送
$ErrorActionPreference = "Continue"
$vault  = "D:\Obsidian\SCM-Career"
$git    = "C:\Users\22814\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe"
$gitBin = "C:\Users\22814\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\mingw64\bin"
$py     = "C:\Users\22814\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$log    = Join-Path $env:TEMP "scm_site_sync.log"
$env:Path = "$gitBin;$env:Path"
Set-Location $vault

function Log($m){ Add-Content -Path $log -Value ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m) -Encoding UTF8 }

try {
    # 1) 拉取远端（手机/GitHub 改动 → 本地），失败不中断
    & $git -c rebase.autoStash=true pull --rebase origin main *>> $log

    # 2) 重新生成网站
    & $py "$vault\build_site.py" *>> $log

    # 3) 提交本地改动
    & $git add -A *>> $log
    $status = (& $git status --porcelain) -join ""
    if($status){
        & $git commit -m "auto-sync: vault update -> site update" *>> $log
        # 4) 推送（网络不稳，重试）
        for($i=1; $i -le 5; $i++){
            & $git push origin main *>> $log
            if($LASTEXITCODE -eq 0){ break }
            Start-Sleep -Seconds 6
        }
        Log "pushed update"
    } else {
        Log "no change, skip commit"
    }
} catch {
    Log ("error: " + $_.Exception.Message)
}