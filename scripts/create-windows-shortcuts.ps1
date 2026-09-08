# Run in Windows PowerShell, or call from WSL with powershell.exe -File.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Distribution,
    [ValidateSet('antigravity', 'obsidian', 'all')][string]$App = 'all'
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$wsl = Join-Path $env:SystemRoot 'System32\wsl.exe'
$linuxUser = (& $wsl --distribution $Distribution --exec id -un | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or !$linuxUser) { throw 'Cannot identify the WSL user.' }
$linuxHome = (& $wsl --distribution $Distribution --user $linuxUser --exec printenv HOME | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or !$linuxHome.StartsWith('/')) { throw 'Cannot identify the WSL home directory.' }
foreach ($value in @($Distribution, $linuxUser, $linuxHome)) {
    if ($value -match '["\r\n]') { throw 'Quotes or newlines in WSL names/paths are not supported.' }
}
$wslg = Join-Path $env:ProgramFiles 'WSL\wslg.exe'
$target = if (Test-Path $wslg) { $wslg } else { $wsl }
$desktop = [Environment]::GetFolderPath('DesktopDirectory')
$programs = Join-Path ([Environment]::GetFolderPath('Programs')) 'WSL Notes'
New-Item -ItemType Directory -Force -Path $programs | Out-Null
$shell = New-Object -ComObject WScript.Shell
$names = if ($App -eq 'all') { @('antigravity', 'obsidian') } else { @($App) }
foreach ($name in $names) {
    $launcher = "$linuxHome/.local/bin/$name-wsl"
    & $wsl --distribution $Distribution --user $linuxUser --exec test -x $launcher
    if ($LASTEXITCODE -ne 0) { throw "Install the Linux app first: $launcher" }
    $title = (Get-Culture).TextInfo.ToTitleCase($name) + ' (WSL)'
    $arguments = '--distribution "' + $Distribution + '" --user "' + $linuxUser + '" --exec "' + $launcher + '"'
    foreach ($folder in @($desktop, $programs)) {
        $path = Join-Path $folder ($title + '.lnk')
        if (Test-Path $path) {
            $old = $shell.CreateShortcut($path)
            if ($old.Arguments -ne $arguments -or $old.TargetPath -ne $target) {
                Copy-Item -LiteralPath $path -Destination ($path + '.backup-' + (Get-Date -Format 'yyyyMMddHHmmssfff'))
            }
        }
        $link = $shell.CreateShortcut($path)
        $link.TargetPath = $target
        $link.Arguments = $arguments
        $link.WorkingDirectory = $env:USERPROFILE
        $link.Description = "$title - $Distribution - $linuxUser"
        $link.IconLocation = "$wsl,0"
        $link.WindowStyle = 7
        $link.Save()
        $saved = $shell.CreateShortcut($path)
        if ($saved.TargetPath -ne $target -or $saved.Arguments -ne $arguments) {
            throw "Shortcut verification failed: $path"
        }
        [pscustomobject]@{ Shortcut = $path; Target = $saved.TargetPath; Arguments = $saved.Arguments }
    }
}
