# Runs the app WITHOUT Docker, for locked-down laptops where Docker Desktop can't be installed.
#
# Instead of Postgres in a container, the data goes into a SQLite file (data/local/tip.db).
# SQLite ships inside Python, so there is no database to install. Same gold schema, same API,
# same dashboard - see docs/RUN-WITHOUT-DOCKER.md.
#
# You still need Python 3.12+ and Node.js 20+.

. "$PSScriptRoot\lib.ps1"
$root = Get-RepoRoot
Set-Location $root

$webUrl = 'http://localhost:5173'

Write-Host ""
Write-Host "  Running without Docker (Python + Node)" -ForegroundColor White

# ---------------------------------------------------------------- prerequisites

Write-Step 'Checking Python'
$python = $null
foreach ($candidate in 'py', 'python', 'python3') {
    if (Test-CommandExists $candidate) {
        # Not $args - that's a PowerShell automatic variable and overwriting it bites later.
        $versionArgs = if ($candidate -eq 'py') { @('-3', '--version') } else { @('--version') }
        $version = & $candidate @versionArgs 2>&1
        if ($LASTEXITCODE -eq 0 -and "$version" -match 'Python 3\.(\d+)' -and [int]$Matches[1] -ge 10) {
            $python = $candidate
            Write-Ok "$version"
            break
        }
    }
}

if (-not $python) {
    Write-Problem 'Python 3.10 or newer was not found.' @(
        'Install it from https://www.python.org/downloads',
        'IMPORTANT: on the first screen of the installer, tick',
        '  "Add python.exe to PATH"',
        'before clicking Install. Missing that tick is the usual cause of this message.',
        'Then close this window and run START-HERE.bat again.'
    )
    Pause-BeforeExit
    exit 1
}

Write-Step 'Checking Node.js'
if (-not (Test-CommandExists 'npm')) {
    Write-Problem 'Node.js was not found.' @(
        'Install the LTS version from https://nodejs.org',
        'Then close this window and run START-HERE.bat again.'
    )
    Pause-BeforeExit
    exit 1
}
Write-Ok "Node $(node --version)"

Write-Step 'Checking ports 8000 and 5173'
foreach ($port in 8000, 5173) {
    if (Test-PortInUse -Port $port) {
        Write-Problem "Port $port is already in use by $(Get-PortOwner -Port $port)." @(
            'Close that program (or a previous run of this app), then try again.',
            'A leftover run usually shows up as a "python" or "node" window - close it.'
        )
        Pause-BeforeExit
        exit 1
    }
}
Write-Ok 'Both ports are free.'

# ---------------------------------------------------------------- python packages

$venv = Join-Path $root '.venv'
$venvPython = Join-Path $venv 'Scripts\python.exe'

if (-not (Test-Path $venvPython)) {
    Write-Step 'Creating a private Python environment (.venv)'
    Write-Info 'This keeps the project packages separate from the rest of your machine.'
    if ($python -eq 'py') { & py -3 -m venv $venv } else { & $python -m venv $venv }
    if (-not (Test-Path $venvPython)) {
        Write-Problem 'Could not create the Python environment.' @(
            'Delete the .venv folder in the project, then run START-HERE.bat again.'
        )
        Pause-BeforeExit
        exit 1
    }
    Write-Ok 'Created.'
}

Write-Step 'Installing Python packages'
& $venvPython -m pip install --quiet --upgrade pip
& $venvPython -m pip install --quiet -r (Join-Path $root 'api\requirements.txt')
if ($LASTEXITCODE -ne 0) {
    Write-Problem 'Installing the Python packages failed.' @(
        'Usually a connection problem. Check your internet and try again.',
        'On a corporate network you may need a proxy - ask the lead.'
    )
    Pause-BeforeExit
    exit 1
}
Write-Ok 'Python packages ready.'

# ---------------------------------------------------------------- data

Write-Step 'Building the local database from synthetic seed data'
$env:DATABASE_URL = 'sqlite:///data/local/tip.db'
& $venvPython (Join-Path $root 'data-platform\load_seed.py')
if ($LASTEXITCODE -ne 0) {
    Write-Problem 'Could not build the local database.' @('Copy the error above into the team chat.')
    Pause-BeforeExit
    exit 1
}

# ---------------------------------------------------------------- web packages

if (-not (Test-Path (Join-Path $root 'web\node_modules'))) {
    Write-Step 'Installing the dashboard packages (first time only, a few minutes)'
    Push-Location (Join-Path $root 'web')
    npm install
    $npmExit = $LASTEXITCODE
    Pop-Location
    if ($npmExit -ne 0) {
        Write-Problem 'Installing the dashboard packages failed.' @(
            'Usually a connection problem. Check your internet and try again.'
        )
        Pause-BeforeExit
        exit 1
    }
    Write-Ok 'Dashboard packages ready.'
}

# ---------------------------------------------------------------- run

# Two separate windows on purpose: you can see each one's log, and closing a window stops
# that part of the app. Titles make them easy to find in the taskbar.
Write-Step 'Starting the API and the dashboard'

# Launched through cmd /k so each window keeps a readable title and stays open on a crash -
# otherwise the error scrolls past and the window vanishes before anyone can read it.
Start-Process -FilePath 'cmd.exe' `
    -ArgumentList '/k', "title TIP API && `"$venvPython`" -m uvicorn app.main:app --app-dir api --port 8000 --reload" `
    -WorkingDirectory $root

Start-Process -FilePath 'cmd.exe' `
    -ArgumentList '/k', 'title TIP dashboard && npm run dev' `
    -WorkingDirectory (Join-Path $root 'web')

if (-not (Wait-ForUrl -Url 'http://localhost:8000/health' -TimeoutSec 90 -What 'the API')) {
    Write-Problem 'The API did not start.' @(
        'Look at the window titled "TIP API" - the error is in there.'
    )
    Pause-BeforeExit
    exit 1
}

if (-not (Wait-ForUrl -Url $webUrl -TimeoutSec 120 -What 'the dashboard')) {
    Write-Warn 'The dashboard is taking a while. Check the "TIP dashboard" window for its address.'
}

Write-Host ""
Write-Host "  The app is running." -ForegroundColor Green
Write-Host ""
Write-Host "    Dashboard   $webUrl" -ForegroundColor White
Write-Host "    API docs    http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Both restart automatically when you save a file." -ForegroundColor Gray
Write-Host "  To stop: close the two windows that just opened, or double-click STOP.bat" -ForegroundColor Gray

Open-Browser $webUrl
Pause-BeforeExit
