# PC -> Pi code deploy. Commits must already be made. Usage: .\tools\deploy.ps1
. "$PSScriptRoot\_pi.ps1"
$Repo = Split-Path -Parent $PSScriptRoot
if (git -C $Repo status --porcelain) { Write-Warning "You have uncommitted changes. The Pi will NOT get them. Commit first." }
git -C $Repo push
if ($LASTEXITCODE -ne 0) { throw "git push failed" }
ssh $Pi.Target "cd $($Pi.PI_REPO) && git pull && git log -1 --oneline"
