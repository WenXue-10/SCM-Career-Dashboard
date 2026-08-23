' WScript 静默启动器：运行自动同步但完全不显示窗口
Set shell = CreateObject("WScript.Shell")
shell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""D:\Obsidian\SCM-Career\update_site.ps1""", 0, False