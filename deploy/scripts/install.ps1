# 检测是否为管理员
$IsElevated = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).
    IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

# Skip Scoop install if already present to avoid stopping the script
if (Get-Command scoop -ErrorAction SilentlyContinue) {
    Write-Host "Scoop is already installed. Skipping installation."
} else {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    if ($IsElevated) {
        # 管理员：使用官方一行命令并传入 -RunAsAdmin
        Invoke-Expression "& {$(Invoke-RestMethod get.scoop.sh)} -RunAsAdmin"
    } else {
        # 普通用户安装
        Invoke-WebRequest -useb get.scoop.sh | Invoke-Expression
    }
}

scoop install git uv
if (Test-Path -LiteralPath "./backend/main.py") {
    # Already in target directory; skip clone and cd
}
elseif (Test-Path -LiteralPath "./omni-gateway/backend/main.py") {
    Set-Location ./omni-gateway
}
else {
    git clone https://github.com/nguywnben/omni-gateway.git
    Set-Location ./omni-gateway
}
# Create relocatable virtual environment to ensure portability
$env:UV_VENV_CLEAR = "1"
uv venv --relocatable
uv pip install -r requirements.txt
.venv/Scripts/activate.ps1
python backend/main.py