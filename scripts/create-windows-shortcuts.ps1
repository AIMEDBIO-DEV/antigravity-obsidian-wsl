# Run in Windows PowerShell, or call from WSL with powershell.exe -File.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Distribution,
    [ValidateSet('obsidian', 'all')][string]$App = 'all',
    [switch]$VerifyOnly
)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$wsl = Join-Path $env:SystemRoot 'System32\wsl.exe'
if ($Distribution -match '\s|"') { throw 'Use a WSL distribution name without whitespace or quotes for this shortcut.' }
$linuxUser = (& $wsl --distribution $Distribution --exec id -un | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or !$linuxUser) { throw 'Cannot identify the WSL user.' }
if ($linuxUser -match '\s|"') { throw 'The WSL user name must not contain whitespace or quotes.' }
$linuxHome = (& $wsl --distribution $Distribution --user $linuxUser --exec printenv HOME | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or !$linuxHome.StartsWith('/')) { throw 'Cannot identify the WSL home directory.' }
foreach ($value in @($Distribution, $linuxUser, $linuxHome)) {
    if ($value -match '["\r\n]') { throw 'Quotes or newlines in WSL names/paths are not supported.' }
}
# Use the same supported entry point used for distribution/user validation.
# Do not directly invoke a potentially different package's wslg.exe.
$target = Join-Path $env:SystemRoot 'System32\wscript.exe'
function Write-HiddenLauncher([string]$Path, [string]$Arguments) {
    $command = '"' + $wsl + '" ' + $Arguments
    $script = 'CreateObject("WScript.Shell").Run "' + $command.Replace('"', '""') + '", 0, False'
    Set-Content -LiteralPath $Path -Value $script -Encoding Unicode
}
$desktop = [Environment]::GetFolderPath('DesktopDirectory')
$programs = Join-Path ([Environment]::GetFolderPath('Programs')) 'WSL Notes'
if (!$VerifyOnly) { New-Item -ItemType Directory -Force -Path $programs | Out-Null }
$shell = New-Object -ComObject WScript.Shell
# WSL option values are unquoted: this WSL version retains literal quotes in
# distribution/user names. The Linux command path after --exec stays quoted.
# Verify ShellExecute through a real .lnk, not merely the shortcut's saved fields.
$probeId = [Guid]::NewGuid().ToString('N')
$probeLinux = "/tmp/wsl-notes-shortcut-$probeId"
$probeWindows = Join-Path ([IO.Path]::GetTempPath()) ("wsl-notes-$probeId.lnk")
$probeVbs = Join-Path ([IO.Path]::GetTempPath()) ("wsl-notes-$probeId.vbs")
try {
    Write-HiddenLauncher $probeVbs ('--distribution ' + $Distribution + ' --user ' + $linuxUser + ' --exec /usr/bin/touch "' + $probeLinux + '"')
    $probe = $shell.CreateShortcut($probeWindows)
    $probe.TargetPath = $target
    $probe.Arguments = '//B //Nologo "' + $probeVbs + '"'
    $probe.WorkingDirectory = $env:USERPROFILE
    $probe.WindowStyle = 7
    $probe.Save()
    $process = Start-Process -FilePath $probeWindows -PassThru
    if (!$process.WaitForExit(15000)) { throw 'Shortcut probe timed out.' }
    $deadline = [DateTime]::UtcNow.AddSeconds(15)
    do {
        & $wsl --distribution $Distribution --user $linuxUser --exec test -f $probeLinux
        if ($LASTEXITCODE -eq 0) { break }
        Start-Sleep -Milliseconds 200
    } while ([DateTime]::UtcNow -lt $deadline)
    if ($LASTEXITCODE -ne 0) { throw 'Shortcut failed to execute in the selected WSL distribution.' }
    Write-Output 'Verified: hidden Windows shortcut executed a command inside WSL.'
} finally {
    Remove-Item -LiteralPath $probeWindows, $probeVbs -Force -ErrorAction SilentlyContinue
    & $wsl --distribution $Distribution --user $linuxUser --exec rm -f $probeLinux
}
if ($VerifyOnly) { return }
$launcherDirectory = Join-Path $env:LOCALAPPDATA 'WSL Notes\Launchers'
New-Item -ItemType Directory -Force -Path $launcherDirectory | Out-Null
$names = if ($App -eq 'all') { @('obsidian') } else { @($App) }
foreach ($name in $names) {
    $launcher = "$linuxHome/.local/bin/$name-wsl"
    & $wsl --distribution $Distribution --user $linuxUser --exec test -x $launcher
    if ($LASTEXITCODE -ne 0) { throw "Install the Linux app first: $launcher" }
    $title = (Get-Culture).TextInfo.ToTitleCase($name) + ' (WSL)'
    $arguments = '--distribution ' + $Distribution + ' --user ' + $linuxUser + ' --exec "' + $launcher + '"'
    $hash = [Security.Cryptography.SHA256]::Create()
    try {
        $id = [BitConverter]::ToString($hash.ComputeHash([Text.Encoding]::UTF8.GetBytes($arguments))).Replace('-', '')
    } finally { $hash.Dispose() }
    $hiddenLauncher = Join-Path $launcherDirectory ($id + '.vbs')
    Write-HiddenLauncher $hiddenLauncher $arguments
    $arguments = '//B //Nologo "' + $hiddenLauncher + '"'
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
