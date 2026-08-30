$userSID = 'S-1-5-21-737071003-2362557348-2204673784-4080492002'

function Fix-Acl($path) {
    $acl = Get-Acl $path
    $denyRules = $acl.Access | Where-Object { $_.IdentityReference -eq $userSID -and $_.AccessControlType -eq 'Deny' }
    Write-Host ("Found " + $denyRules.Count + " deny rules on " + $path)
    if ($denyRules.Count -gt 0) {
        # Remove each deny rule by creating a new AccessRule that replaces it
        $newRules = @()
        foreach ($rule in $acl.Access) {
            if ($rule.IdentityReference -eq $userSID -and $rule.AccessControlType -eq 'Deny') {
                Write-Host ("  Removing deny: " + $rule.FileSystemRights)
            } else {
                $newRules += $rule
            }
        }
        $acl.SetAccessRuleProtection($false, $false)
        foreach ($rule in $newRules) {
            $acl.AddAccessRule($rule)
        }
        Set-Acl -Path $path -AclObject $acl
        Write-Host "  Updated ACL"
    }
}

Fix-Acl 'D:\Obsidian\SCM-Career\.git'
Fix-Acl 'D:\Obsidian\SCM-Career\.git\index'
Write-Host "Done"
