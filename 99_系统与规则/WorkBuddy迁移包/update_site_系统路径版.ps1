# update_site_系统路径版.ps1 —— 不依赖 Codex 运行时
# 前置：系统已安装 Git for Windows 与 Python 3，且都加入 PATH
# 若未安装，可继续用原版(update_site.ps1)的 codex-runtime 路径（只要 Codex 还在）
$ErrorActionPreference = "Continue"
$vault  = "D:\Obsidian\SCM-Career"
$git    = "git"
$py     = "python"
$log    = Join-Path $env:TEMP "scm_site_sync.log"
Set-Location $vault

function Log($m){ Add-Content -Path $log -Value ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m) -Encoding UTF8 }

try {
    & $git -c rebase.autoStash=true pull --rebase origin main *>> $log
    & $py "$vault\build_site.py" *>> $log
    & $git add -A *>> $log
    $status = (& $git status --porcelain) -join ""
    if($status){
        & $git commit -m "auto-sync: vault update -> site update" *>> $log
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