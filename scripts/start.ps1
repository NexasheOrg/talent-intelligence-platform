# Starts the whole app. Run it by double-clicking START-HERE.bat - you don't need a terminal.
#
# It prefers Docker, because that runs everything (database included) with nothing else
# installed. If Docker isn't there, it offers the Python + Node route instead rather than
# leaving you stuck.

param([switch]$NoDocker)

. "$PSScriptRoot\lib.ps1"
$root = Get-RepoRoot
Set-Location $root

Write-Host ""
Write-Host "  Talent & Delivery Intelligence Platform" -ForegroundColor White
Write-Host "  Starting your local copy of the app." -ForegroundColor Gray

# ---------------------------------------------------------------- pick a route

function Test-DockerReady {
    if (-not (Test-CommandExists 'docker')) { return 'missing' }
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { return 'not-running' }
    return 'ready'
}

if (-not $NoDocker) {
    Write-Step 'Checking Docker Desktop'
    $docker = Test-DockerReady

    if ($docker -eq 'not-running') {
        Write-Warn 'Docker is installed but not running. Trying to start it...'
        $dockerApp = Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'
        if (Test-Path $dockerApp) {
            Start-Process $dockerApp | Out-Null
            Write-Info 'Docker Desktop can take a minute or two to finish starting.'
            for ($i = 0; $i -lt 90; $i++) {
                Start-Sleep -Seconds 2
                if ((Test-DockerReady) -eq 'ready') { break }
                Write-Host "`r    . still waiting for Docker Desktop ($($i * 2)s)" -NoNewline -ForegroundColor Gray
            }
            Write-Host "`r                                                        " -NoNewline
        }
        $docker = Test-DockerReady
    }

    if ($docker -eq 'ready') {
        Write-Ok 'Docker is running.'
    } else {
        Write-Problem 'Docker Desktop is not available on this machine.' @(
            'Option 1 - install it: https://www.docker.com/products/docker-desktop',
            '  Windows may ask to enable "WSL 2". Say yes and follow its prompts.',
            '  If your laptop is locked down and you cannot install it, use option 2.',
            '',
            'Option 2 - run without Docker. You need Python and Node.js instead:',
            '  Python 3.12+   https://www.python.org/downloads   (tick "Add python.exe to PATH")',
            '  Node.js 20+    https://nodejs.org                 (choose the LTS version)'
        )
        Write-Host ""
        $answer = Read-Host '  Try running without Docker now? (y/n)'
        if ($answer -match '^[Yy]') {
            & "$PSScriptRoot\start-local.ps1"
            exit $LASTEXITCODE
        }
        Pause-BeforeExit
        exit 1
    }
} else {
    & "$PSScriptRoot\start-local.ps1"
    exit $LASTEXITCODE
}

# ---------------------------------------------------------------- ports

Write-Step 'Checking the ports the app needs'
$blocked = @()
foreach ($port in 8080, 8000, 5433) {
    if (Test-PortInUse -Port $port) { $blocked += "$port (used by $(Get-PortOwner -Port $port))" }
}

if ($blocked.Count -gt 0) {
    # An old copy of this app still running is by far the most common cause.
    Write-Warn 'Some ports are already in use:'
    foreach ($item in $blocked) { Write-Info "- $item" }
    Write-Info 'Stopping any previous run of this app...'
    docker compose down 2>&1 | Out-Null
    Start-Sleep -Seconds 2

    $stillBlocked = @(8080, 8000, 5433 | Where-Object { Test-PortInUse -Port $_ })
    if ($stillBlocked.Count -gt 0) {
        Write-Problem "Port(s) $($stillBlocked -join ', ') are still in use by another program." @(
            'Close the other program, then run START-HERE.bat again.',
            'To find it, open PowerShell and run:',
            "  Get-Process -Id (Get-NetTCPConnection -LocalPort $($stillBlocked[0])).OwningProcess"
        )
        Pause-BeforeExit
        exit 1
    }
} else {
    Write-Ok 'Ports 8080, 8000 and 5433 are free.'
}

# ---------------------------------------------------------------- build & run

Write-Step 'Building and starting the app'
Write-Info 'The first run downloads and builds things - expect 3 to 10 minutes.'
Write-Info 'Later runs take a few seconds. Leave this window open while it works.'
Write-Host ""

docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    Write-Problem 'Docker could not start the app.' @(
        'Scroll up - the real reason is in the red text above.',
        'Most common causes:',
        '  - No internet connection, so the images could not download.',
        '  - Docker Desktop ran out of disk space. Free some up and try again.',
        'Still stuck? Copy the red text into the team chat.'
    )
    Pause-BeforeExit
    exit 1
}

Write-Step 'Waiting for the app to finish starting'
if (-not (Wait-ForUrl -Url "$API_URL/health" -TimeoutSec 240 -What 'the API')) {
    Write-Problem 'The app started but the API never came up.' @(
        'See what went wrong with:',
        '  docker compose logs api',
        '  docker compose logs loader',
        'Then paste the last 20 lines into the team chat.'
    )
    Pause-BeforeExit
    exit 1
}

if (-not (Wait-ForUrl -Url $DASHBOARD_URL -TimeoutSec 60 -What 'the dashboard')) {
    Write-Warn "The dashboard is slow to answer. Try $DASHBOARD_URL in your browser anyway."
}

# ---------------------------------------------------------------- done

Write-Host ""
Write-Host "  The app is running." -ForegroundColor Green
Write-Host ""
Write-Host "    Dashboard   $DASHBOARD_URL" -ForegroundColor White
Write-Host "    API docs    $API_URL/docs" -ForegroundColor White
Write-Host ""
Write-Host "  To stop it later, double-click STOP.bat" -ForegroundColor Gray
Write-Host "  Your changes to the code need a restart: STOP.bat, then START-HERE.bat" -ForegroundColor Gray
Write-Host "  (While actively coding, use the hot-reload setup in docs/ONBOARDING.md instead.)" -ForegroundColor Gray

Open-Browser $DASHBOARD_URL
Pause-BeforeExit
