# Shared helpers for the start / stop / check scripts.
#
# Everything a first-timer sees comes out of here, so the rules are:
#   - say what happened, then say what to do about it
#   - never print a raw stack trace as the only message
#   - never leave the window closing before the message can be read
#
# Dot-source it:  . "$PSScriptRoot\lib.ps1"

$script:DASHBOARD_URL = 'http://localhost:8080'
$script:API_URL       = 'http://localhost:8000'

function Write-Step   { param([string]$Text) Write-Host "`n==> $Text" -ForegroundColor Cyan }
function Write-Ok     { param([string]$Text) Write-Host "    OK  $Text" -ForegroundColor Green }
function Write-Warn   { param([string]$Text) Write-Host "    !   $Text" -ForegroundColor Yellow }
function Write-Info   { param([string]$Text) Write-Host "    $Text" -ForegroundColor Gray }

function Write-Problem {
    param([string]$Title, [string[]]$Fix)
    Write-Host "`n  X  $Title" -ForegroundColor Red
    if ($Fix) {
        Write-Host ""
        Write-Host "     How to fix it:" -ForegroundColor Yellow
        foreach ($line in $Fix) { Write-Host "       $line" }
    }
}

# The repo root, whichever folder the user double-clicked from.
function Get-RepoRoot { Split-Path -Parent $PSScriptRoot }

function Test-CommandExists {
    param([string]$Name)
    $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Test-PortInUse {
    param([int]$Port)
    try {
        $null -ne (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop)
    } catch {
        # Get-NetTCPConnection is missing on some older builds; fall back to a connect attempt.
        try {
            $client = New-Object Net.Sockets.TcpClient
            $client.Connect('127.0.0.1', $Port)
            $client.Close()
            $true
        } catch { $false }
    }
}

function Get-PortOwner {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop | Select-Object -First 1
        (Get-Process -Id $connection.OwningProcess -ErrorAction Stop).ProcessName
    } catch { 'another program' }
}

# True once the URL answers. Used to wait for the API instead of guessing with a sleep.
function Test-UrlReady {
    param([string]$Url, [int]$TimeoutSec = 2)
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec
        return $response.StatusCode -eq 200
    } catch { return $false }
}

function Wait-ForUrl {
    param([string]$Url, [int]$TimeoutSec = 180, [string]$What = 'the app')

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    $spinner = '|', '/', '-', '\'
    $i = 0
    while ((Get-Date) -lt $deadline) {
        if (Test-UrlReady -Url $Url) {
            Write-Host "`r    OK  $What is ready.                        " -ForegroundColor Green
            return $true
        }
        Write-Host "`r    $($spinner[$i % 4]) waiting for $What ..." -NoNewline -ForegroundColor Gray
        $i++
        Start-Sleep -Milliseconds 700
    }
    Write-Host "`r                                                  " -NoNewline
    return $false
}

function Open-Browser {
    param([string]$Url)
    try { Start-Process $Url | Out-Null } catch { Write-Info "Open $Url in your browser." }
}

# Batch files close their window the moment the script ends, taking any error with them.
function Pause-BeforeExit {
    param([string]$Message = 'Press Enter to close this window')
    Write-Host ""
    Read-Host $Message | Out-Null
}
