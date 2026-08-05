# File the task briefs in docs/tasks/ as GitHub issues.
#
#   .\scripts\create-issues.ps1            preview only - creates nothing
#   .\scripts\create-issues.ps1 -Create    actually create them
#
# Previewing is the default on purpose: creating thirty issues is hard to undo.
# Needs the GitHub CLI (https://cli.github.com) and write access to the repo.

param([switch]$Create)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$tasksDir = Join-Path $root 'docs\tasks'

if (-not (Test-Path $tasksDir)) {
    Write-Host "No docs\tasks directory found." -ForegroundColor Red
    exit 1
}

if ($Create) {
    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Host "The GitHub CLI (gh) is not installed: https://cli.github.com" -ForegroundColor Red
        exit 1
    }
    gh auth status 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Not signed in. Run: gh auth login" -ForegroundColor Red
        exit 1
    }
}

function Get-FrontMatter {
    <#  Pull one `key: value` out of the YAML front matter at the top of a brief.  #>
    param([string[]]$Lines, [string]$Key)

    if ($Lines[0] -ne '---') { return $null }
    for ($i = 1; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -eq '---') { break }
        if ($Lines[$i] -match "^$Key\s*:\s*(.+)$") {
            return $Matches[1].Trim().Trim('"')
        }
    }
    return $null
}

$count = 0
foreach ($brief in Get-ChildItem -Path $tasksDir -Filter *.md | Sort-Object Name) {
    $lines = Get-Content $brief.FullName

    $title = Get-FrontMatter -Lines $lines -Key 'title'
    if (-not $title) {
        Write-Host "skipping $($brief.Name) - no title in front matter" -ForegroundColor Yellow
        continue
    }

    $labels = (Get-FrontMatter -Lines $lines -Key 'labels') -replace '[\[\]]', ''

    # The brief itself is the issue body, minus the front matter.
    $end = 1
    while ($end -lt $lines.Count -and $lines[$end] -ne '---') { $end++ }
    $body = ($lines[($end + 1)..($lines.Count - 1)]) -join "`n"

    $count++

    if ($Create) {
        Write-Host "creating: $title"
        $args = @('issue', 'create', '--title', $title, '--body', $body)
        if ($labels) { $args += @('--label', $labels) }
        gh @args | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  failed - does the label exist?" -ForegroundColor Yellow
        }
    } else {
        Write-Host ("  {0,-70} [{1}]" -f $title, $labels)
    }
}

Write-Host ""
if ($Create) {
    Write-Host "Created $count issues." -ForegroundColor Green
} else {
    Write-Host "$count issues would be created. Re-run with -Create to do it."
    Write-Host "Labels must already exist in the repo, or gh will reject the issue."
}
