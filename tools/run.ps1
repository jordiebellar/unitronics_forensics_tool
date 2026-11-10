# Same as run.sh but for the PC. Usage (from the repo root):  .\tools\run.ps1 src\pcom_gui.py
param([Parameter(Mandatory=$true)][string]$Script, [Parameter(ValueFromRemainingArguments=$true)]$Rest)
$Repo = Split-Path -Parent $PSScriptRoot
$ScriptFull = (Resolve-Path $Script).Path
$Name = [IO.Path]::GetFileNameWithoutExtension($ScriptFull)
$Run = Join-Path $Repo ("data\runs\" + (Get-Date -Format "yyyy-MM-dd_HHmmss") + "_" + $Name)
New-Item -ItemType Directory -Force $Run | Out-Null
$commit = git -C $Repo rev-parse --short HEAD
@("script:  $ScriptFull", "args:    $Rest", "commit:  $commit", "started: $(Get-Date -Format o)", "host:    $env:COMPUTERNAME") | Set-Content (Join-Path $Run "meta.txt")
Write-Host "Run folder: $Run"
Push-Location $Run
$env:PYTHONPATH = Join-Path $Repo "src"
python $ScriptFull @Rest
Pop-Location
