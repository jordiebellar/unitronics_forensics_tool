# Pi -> PC data sync. Copies only run folders you do not already have. Usage: .\tools\sync_data.ps1
. "$PSScriptRoot\_pi.ps1"
$Repo = Split-Path -Parent $PSScriptRoot
$Local = Join-Path $Repo "data\runs"
New-Item -ItemType Directory -Force $Local | Out-Null
$remote = ssh $Pi.Target "ls -1 $($Pi.PI_REPO)/data/runs 2>/dev/null"
$new = 0
foreach ($r in ($remote -split "`n" | Where-Object { $_.Trim() })) {
    $r = $r.Trim()
    if (-not (Test-Path (Join-Path $Local $r))) {
        Write-Host "Pulling $r"
        scp -r "$($Pi.Target):$($Pi.PI_REPO)/data/runs/$r" $Local
        $new++
    }
}
Write-Host "Done. $new new run folder(s)."
