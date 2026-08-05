# Stops everything START-HERE.bat started, whichever way it started it.

. "$PSScriptRoot\lib.ps1"
$root = Get-RepoRoot
Set-Location $root

Write-Host ""
Write-Host "  Stopping the app" -ForegroundColor White

if (Test-CommandExists 'docker') {
    Write-Step 'Stopping the Docker containers'
    docker compose down 2>&1 | Out-Null
    Write-Ok 'Docker containers stopped.'
}

# The no-Docker route leaves a python and a node process listening. Only stop processes that
# are both (a) listening on one of our ports and (b) python or node - never anything else.
Write-Step 'Stopping any local API or dashboard processes'
$stopped = 0
foreach ($port in 8000, 5173, 5174) {
    try {
        $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction Stop
    } catch { continue }

    foreach ($connection in $connections) {
        try {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction Stop
        } catch { continue }

        if ($process.ProcessName -match '^(python|pythonw|node)$') {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            Write-Info "Stopped $($process.ProcessName) on port $port"
            $stopped++
        } else {
            Write-Warn "Left $($process.ProcessName) on port $port alone - it isn't part of this app."
        }
    }
}

if ($stopped -eq 0) { Write-Info 'Nothing else was running.' }

Write-Host ""
Write-Host "  Done. Start it again any time with START-HERE.bat" -ForegroundColor Green
Pause-BeforeExit
