# Workflow Link Organizer - first-run setup.
# Non-interactive: safe to run directly or to let Claude Code run for you.
#   powershell -ExecutionPolicy Bypass -File setup.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "=== Workflow Link Organizer - Setup ===" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python ------------------------------------------------------------
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "Python is not installed." -ForegroundColor Red
    Write-Host "Download it from https://www.python.org/downloads/ and during install"
    Write-Host "check the box 'Add python.exe to PATH'. Then run this setup again."
    exit 1
}

$pyVer = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$major, $minor = $pyVer.Split('.')
if ([int]$major -lt 3 -or ([int]$major -eq 3 -and [int]$minor -lt 10)) {
    Write-Host "Python $pyVer found, but 3.10 or newer is required." -ForegroundColor Red
    Write-Host "Update from https://www.python.org/downloads/ and run this setup again."
    exit 1
}
Write-Host "[1/3] Python $pyVer found." -ForegroundColor Green

# 2. Install dependencies ----------------------------------------------------
Write-Host "[2/3] Installing dependencies (this can take a minute)..."
& python -m pip install -e $root --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependency install failed. Try running:" -ForegroundColor Red
    Write-Host "  python -m pip install -e `"$root`""
    exit 1
}
Write-Host "[2/3] Dependencies installed." -ForegroundColor Green

# 3. Create the data directory ----------------------------------------------
$dataDirName = if ($env:WLO_DATA_DIR_NAME) { $env:WLO_DATA_DIR_NAME } else { "WorkflowLinkOrganizer" }
$dataDir = Join-Path $env:LOCALAPPDATA $dataDirName
New-Item -ItemType Directory -Path $dataDir -Force | Out-Null
Write-Host "[3/3] Data folder ready: $dataDir" -ForegroundColor Green

Write-Host ""
Write-Host "=== Setup complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "To start the app, double-click Start.bat (or run .\Start.bat)." -ForegroundColor Cyan
Write-Host "It opens automatically at http://127.0.0.1:5757"
Write-Host ""
Write-Host "Tip: create named profiles in Chrome/Edge first so each link group can"
Write-Host "open in the right one. The README has step-by-step instructions."
