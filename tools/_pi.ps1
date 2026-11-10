# Shared helper: reads tools/pi.conf into $Pi
$conf = Join-Path $PSScriptRoot "pi.conf"
if (-not (Test-Path $conf)) { throw "Missing tools/pi.conf. Copy tools/pi.conf.example to tools/pi.conf and edit it." }
$Pi = @{}
Get-Content $conf | Where-Object { $_ -match '^\s*[A-Z_]+=' } | ForEach-Object {
    $k, $v = $_ -split '=', 2; $Pi[$k.Trim()] = $v.Trim()
}
$Pi.Target = "$($Pi.PI_USER)@$($Pi.PI_HOST)"
