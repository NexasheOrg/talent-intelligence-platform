# "Is my laptop ready?" - run this before your first day of coding, and any time something
# stops working. It changes nothing; it only looks and reports.

. "$PSScriptRoot\lib.ps1"
$root = Get-RepoRoot
Set-Location $root

$problems = @()
$notes = @()

Write-Host ""
Write-Host "  Checking your setup" -ForegroundColor White
Write-Host "  Nothing here changes your machine - it just looks around." -ForegroundColor Gray

# ---------------------------------------------------------------- required

Write-Step 'Git'
if (Test-CommandExists 'git') {
    Write-Ok (git --version)
} else {
    Write-Warn 'Not found.'
    $problems += 'Install Git: https://git-scm.com/downloads'
}

Write-Step 'Docker Desktop (the easiest way to run the app)'
if (Test-CommandExists 'docker') {
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "Installed and running - $(docker --version)"
    } else {
        Write-Warn 'Installed, but not running right now.'
        $notes += 'Open Docker Desktop from the Start menu and wait for it to say "running".'
    }
} else {
    Write-Warn 'Not found.'
    $notes += 'Docker is the simplest route: https://www.docker.com/products/docker-desktop'
    $notes += 'If you cannot install it, the Python + Node route below works instead.'
}

# ---------------------------------------------------------------- fallback route

Write-Step 'Python (needed to run without Docker, and to work on the backend)'
$pythonFound = $false
foreach ($candidate in 'py', 'python', 'python3') {
    if (Test-CommandExists $candidate) {
        # Not $args - that's a PowerShell automatic variable and overwriting it bites later.
        $versionArgs = if ($candidate -eq 'py') { @('-3', '--version') } else { @('--version') }
        $version = & $candidate @versionArgs 2>&1
        if ($LASTEXITCODE -eq 0 -and "$version" -match 'Python 3\.(\d+)') {
            if ([int]$Matches[1] -ge 10) {
                Write-Ok "$version (via '$candidate')"
                $pythonFound = $true
            } else {
                Write-Warn "$version is too old."
            }
            break
        }
    }
}
if (-not $pythonFound) {
    Write-Warn 'Not found (or too old).'
    $notes += 'Python 3.12+: https://www.python.org/downloads - tick "Add python.exe to PATH".'
}

Write-Step 'Node.js (needed for the dashboard)'
if (Test-CommandExists 'node') {
    $nodeVersion = node --version
    if ($nodeVersion -match 'v(\d+)' -and [int]$Matches[1] -ge 18) {
        Write-Ok "Node $nodeVersion"
    } else {
        Write-Warn "Node $nodeVersion is older than we build against (20+)."
        $notes += 'Update Node.js from https://nodejs.org (LTS).'
    }
} else {
    Write-Warn 'Not found.'
    $notes += 'Node.js 20+ (LTS): https://nodejs.org'
}

# ---------------------------------------------------------------- environment

Write-Step 'Ports the app uses'
$busy = @()
foreach ($port in 8080, 8000, 5433, 5173) {
    if (Test-PortInUse -Port $port) { $busy += "$port ($(Get-PortOwner -Port $port))" }
}
if ($busy.Count -eq 0) {
    Write-Ok 'All free.'
} else {
    Write-Warn "In use: $($busy -join ', ')"
    $notes += 'If the app is already running that is fine. Otherwise close those programs.'
}

Write-Step 'Disk space'
try {
    $drive = Get-PSDrive -Name (Split-Path -Qualifier $root).TrimEnd(':') -ErrorAction Stop
    $freeGb = [math]::Round($drive.Free / 1GB, 1)
    if ($freeGb -lt 10) {
        Write-Warn "$freeGb GB free."
        $problems += "Only $freeGb GB free. Docker images need roughly 5 GB - free some space."
    } else {
        Write-Ok "$freeGb GB free."
    }
} catch {
    Write-Info 'Could not read the disk size (not a problem).'
}

Write-Step 'Project files'
$expected = 'docker-compose.yml', 'api\app\main.py', 'web\package.json', 'data-platform\load_seed.py'
$missing = @($expected | Where-Object { -not (Test-Path (Join-Path $root $_)) })
if ($missing.Count -eq 0) {
    Write-Ok 'The project looks complete.'
} else {
    Write-Warn "Missing: $($missing -join ', ')"
    $problems += 'Some project files are missing. Re-clone the repository with GitHub Desktop.'
}

# ---------------------------------------------------------------- verdict

Write-Host ""
if ($problems.Count -eq 0) {
    Write-Host "  You are ready. Double-click START-HERE.bat to run the app." -ForegroundColor Green
} else {
    Write-Host "  A few things need fixing first:" -ForegroundColor Yellow
    foreach ($problem in $problems) { Write-Host "    - $problem" }
}

if ($notes.Count -gt 0) {
    Write-Host ""
    Write-Host "  Worth knowing:" -ForegroundColor Cyan
    foreach ($note in $notes) { Write-Host "    - $note" }
}

Write-Host ""
Write-Host "  Full setup guide: docs\WINDOWS-SETUP.md" -ForegroundColor Gray
Pause-BeforeExit
