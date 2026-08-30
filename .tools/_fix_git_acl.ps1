$userSID = 'S-1-5-21-737071003-2362557348-2204673784-4080492002'
$path = 'D:\Obsidian\SCM-Career\.git\index'
$acl = Get-Acl $path
$denyRules = $acl.Access | Where-Object { $_.IdentityReference -eq $userSID -and $_.AccessControlType -eq 'Deny' }
Write-Host ("Found " + $denyRules.Count + " deny rules on index")
if ($denyRules.Count -gt 0) {
    $newRules = @()
    foreach ($rule in $acl.Access) {
        if ($rule.IdentityReference -eq $userSID -and $rule.AccessControlType -eq 'Deny') {
            Write-Host ("  Removing: " + $rule.FileSystemRights)
        } else {
            $newRules += $rule
        }
    }
    $acl.SetAccessRuleProtection($false, $false)
    foreach ($rule in $newRules) {
        $acl.AddAccessRule($rule)
    }
    Set-Acl -Path $path -AclObject $acl
    Write-Host 'Index ACL updated'
}
