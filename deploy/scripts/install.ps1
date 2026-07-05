$ErrorActionPreference = "Stop"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message"
}

function Write-Fail {
    param([string]$Message)
    Write-Error "[ERROR] $Message"
    exit 1
}

if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
    Write-Info "Installing Scoop for the current user..."
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Invoke-RestMethod get.scoop.sh | Invoke-Expression
}

foreach ($tool in @("git", "uv")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Info "Installing $tool..."
        scoop install $tool
    }
}

if (Test-Path -LiteralPath "./backend/main.py") {
    Write-Info "Using current Omni Gateway checkout."
}
elseif (Test-Path -LiteralPath "./omni-gateway/backend/main.py") {
    Set-Location ./omni-gateway
}
else {
    Write-Info "Cloning Omni Gateway..."
    git clone https://github.com/nguywnben/omni-gateway.git
    Set-Location ./omni-gateway
}

if (-not (Test-Path -LiteralPath ".venv/Scripts/python.exe")) {
    Write-Info "Creating virtual environment..."
    uv venv
}

Write-Info "Installing Python dependencies..."
uv pip install -r requirements.txt

Write-Info "Starting Omni Gateway..."
& ".venv/Scripts/python.exe" "backend/main.py"
