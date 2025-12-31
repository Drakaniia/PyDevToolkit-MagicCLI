# ============================================================
# PyDevToolkit-MagicCLI Global Installer (Windows)
# ============================================================
# Complete installation script for Windows that handles:
# - Python installation (if needed)
# - Package installation
# - Global command setup
# - PowerShell/CMD support
# ============================================================

#Requires -Version 5.1

# ============================================================
# CONFIGURATION
# ============================================================

$PackageName = "magic-cli"
$PackageVersion = "1.0.0"
$GitHubRepo = "Drakaniia/PyDevToolkit-MagicCLI"
$InstallDir = Join-Path $env:USERPROFILE ".magic-cli"
$MinPythonVersion = "3.8.0"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

function Write-ColorOutput {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        [ValidateSet("Green", "Blue", "Yellow", "Red", "Cyan", "Magenta")]
        [string]$Color = "White"
    )
    
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    Clear-Host
    Write-ColorOutput "" "White"
    Write-ColorOutput "  PyDevToolkit-MagicCLI Global Installer                  " "Blue"
    Write-ColorOutput "" "White"
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput $Title "Cyan"
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput " $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput " $Message" "Red"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "! $Message" "Yellow"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" "Blue"
}

function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-PythonCommand {
    $commands = @("python", "python3", "py")
    
    foreach ($cmd in $commands) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) {
            $version = & $cmd --version 2>&1
            if ($version -match "Python 3\.(\d+)") {
                $minorVersion = [int]$matches[1]
                if ($minorVersion -ge 8) {
                    return $cmd
                }
            }
        }
    }
    return $null
}

function Install-Python {
    Write-Section "Python Installation"
    
    # Check if Python is already installed
    $pythonCmd = Get-PythonCommand
    if ($pythonCmd) {
        $version = & $pythonCmd --version 2>&1
        Write-Success "Python found: $pythonCmd ($version)"
        return $pythonCmd
    }
    
    Write-Warning "Python 3.8+ not found on this system"
    
    if (-not (Test-AdminRights)) {
        Write-Warning "Administrator privileges required for Python installation"
        Write-Info "Please run PowerShell as Administrator and try again"
        Write-Info "Or install Python manually from: https://www.python.org/downloads/"
        return $null
    }
    
    # Try winget first
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Info "Using Windows Package Manager (winget) to install Python..."
        
        try {
            $result = winget install --id Python.Python.3 -e --accept-source-agreements --accept-package-agreements 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Python installed successfully via winget"
                Start-Sleep -Seconds 5
                $pythonCmd = Get-PythonCommand
                if ($pythonCmd) {
                    return $pythonCmd
                }
            }
        } catch {
            Write-Warning "Winget installation failed"
        }
    }
    
    # Try Chocolatey
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Info "Using Chocolatey to install Python..."
        
        try {
            choco install python -y
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Python installed successfully via Chocolatey"
                Start-Sleep -Seconds 5
                $pythonCmd = Get-PythonCommand
                if ($pythonCmd) {
                    return $pythonCmd
                }
            }
        } catch {
            Write-Warning "Chocolatey installation failed"
        }
    }
    
    # Fallback to web download
    Write-Info "Downloading Python installer from python.org..."
    
    try {
        $installerPath = "$env:TEMP\python-installer.exe"
        $pythonUrl = "https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
        
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Info "Installing Python (this may take a few minutes)..."
        $process = Start-Process -FilePath $installerPath -ArgumentList "/quiet", "PrependPath=1", "Include_test=0" -Wait -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Success "Python installed successfully"
            Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 5
            $pythonCmd = Get-PythonCommand
            if ($pythonCmd) {
                return $pythonCmd
            }
        } else {
            Write-Error "Python installer failed with exit code: $($process.ExitCode)"
            Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
        }
    } catch {
        Write-Error "Failed to download/install Python: $_"
    }
    
    Write-Error "Could not install Python automatically"
    Write-Info ""
    Write-Info "Please install Python manually:"
    Write-Info "  1. Download from: https://www.python.org/downloads/"
    Write-Info "  2. Run the installer and check 'Add Python to PATH'"
    Write-Info "  3. Restart this terminal after installation"
    Write-Info "  4. Verify: python --version"
    return $null
}

function Install-Package {
    param([string]$PythonCmd)
    
    Write-Section "Package Installation"
    
    # Create installation directory
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    
    Write-Info "Installing PyDevToolkit-MagicCLI..."
    
    # Try PyPI first
    try {
        $result = & $PythonCmd -m pip install $PackageName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Package installed from PyPI"
            return $true
        }
    } catch {
        Write-Warning "PyPI installation failed: $_"
    }
    
    # Fallback to GitHub
    Write-Info "Trying GitHub installation..."
    try {
        $result = & $PythonCmd -m pip install "git+https://github.com/$GitHubRepo.git" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Package installed from GitHub"
            return $true
        }
    } catch {
        Write-Error "GitHub installation failed: $_"
    }
    
    Write-Error "Failed to install package from both PyPI and GitHub"
    Write-Info ""
    Write-Info "Troubleshooting steps:"
    Write-Info "  1. Check your internet connection"
    Write-Info "  2. Verify Python version: $PythonCmd --version"
    Write-Info "  3. Try installing manually: $PythonCmd -m pip install $PackageName"
    Write-Info "  4. Check pip is working: $PythonCmd -m pip --version"
    Write-Info ""
    Write-Info "If issues persist, try:"
    Write-Info "  $PythonCmd -m pip install --upgrade pip"
    Write-Info "  $PythonCmd -m pip install git+https://github.com/$GitHubRepo.git"
    return $false
}

function Install-WindowsWrapper {
    param([string]$PythonCmd)
    
    Write-Section "Windows Command Setup"
    
    # Create bin directory
    $binDir = Join-Path $InstallDir "bin"
    New-Item -ItemType Directory -Force -Path $binDir | Out-Null
    
    # Create PowerShell wrapper script
    $psWrapper = Join-Path $binDir "magic.ps1"
    $psContent = @"
# PyDevToolkit-MagicCLI PowerShell Wrapper
# Generated by installer on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

# Find Python command
`$pythonCmds = @("python", "python3", "py")
`$pythonCmd = `$null

foreach (`$cmd in `$pythonCmds) {
    if (Get-Command `$cmd -ErrorAction SilentlyContinue) {
        `$version = & `$cmd --version 2>&1
        if (`$version -match "Python 3\.") {
            `$pythonCmd = `$cmd
            break
        }
    }
}

if (-not `$pythonCmd) {
    Write-Error "Error: Python 3 not found. Please reinstall PyDevToolkit-MagicCLI."
    exit 1
}

# Run the magic command
& `$pythonCmd -m src.main `$args
"@
    
    Set-Content -Path $psWrapper -Value $psContent -Encoding UTF8
    Write-Success "Created PowerShell wrapper: $psWrapper"
    
    # Create CMD wrapper script
    $cmdWrapper = Join-Path $binDir "magic.cmd"
    $cmdContent = @"
@echo off
REM PyDevToolkit-MagicCLI CMD Wrapper
REM Generated by installer on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

REM Find Python command
python -m src.main %*
if errorlevel 1 (
    python3 -m src.main %*
    if errorlevel 1 (
        py -m src.main %*
    )
)
"@
    
    Set-Content -Path $cmdWrapper -Value $cmdContent -Encoding ASCII
    Write-Success "Created CMD wrapper: $cmdWrapper"
    
    # Add to PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$binDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$binDir", "User")
        Write-Success "Added PyDevToolkit-MagicCLI to user PATH"
        Write-Warning "Please restart your terminal for PATH changes to take effect"
    } else {
        Write-Info "PyDevToolkit-MagicCLI already in PATH"
    }
    
    return $true
}

function Test-Installation {
    param([string]$PythonCmd)
    
    Write-Section "Verification"
    
    # Test if magic command is available
    $magicCmd = Join-Path $InstallDir "bin\magic.cmd"
    if (Test-Path $magicCmd) {
        Write-Success "'magic' command wrapper created"
    } else {
        Write-Warning "'magic' command wrapper not found"
    }
    
    # Test package import
    try {
        & $PythonCmd -c "import src.main" 2>&1 | Out-Null
        Write-Success "Package can be imported"
        return $true
    } catch {
        Write-Error "Package import failed: $_"
        return $false
    }
}

# ============================================================
# MAIN INSTALLATION FLOW
# ============================================================

Write-Header

Write-ColorOutput "This installer will:" "Cyan"
Write-ColorOutput "  • Install Python 3.8+ (if needed)" "White"
Write-ColorOutput "  • Install PyDevToolkit-MagicCLI package" "White"
Write-ColorOutput "  • Set up the 'magic' command globally" "White"
Write-ColorOutput "  • Configure PowerShell and CMD support" "White"
Write-Host ""

$response = Read-Host "Ready to begin installation? [Y/n] (Y default)"
if ($response -and $response -ne "Y" -and $response -ne "y") {
    Write-Host ""
    Write-ColorOutput "Installation cancelled by user." "Yellow"
    exit 0
}

# Setup Python
$pythonCmd = Install-Python
if (-not $pythonCmd) {
    Write-Error "Python setup failed"
    exit 1
}

# Install package
if (-not (Install-Package -PythonCmd $pythonCmd)) {
    Write-Error "Package installation failed"
    exit 1
}

# Setup Windows command wrappers
if (-not (Install-WindowsWrapper -PythonCmd $pythonCmd)) {
    Write-Error "Command setup failed"
    exit 1
}

# Verify installation
if (-not (Test-Installation -PythonCmd $pythonCmd)) {
    Write-Error "Installation verification failed"
    exit 1
}

Write-Section "Installation Complete!"

Write-ColorOutput "PyDevToolkit-MagicCLI has been installed successfully!" "Green"
Write-Host ""
Write-ColorOutput "Installation Summary:" "Cyan"
Write-ColorOutput "  [OK] Python: $pythonCmd" "Green"
Write-ColorOutput "  [OK] Package: $PackageName" "Green"
Write-ColorOutput "  [OK] Command: magic" "Green"
Write-ColorOutput "  [OK] Location: $InstallDir" "Green"
Write-Host ""

Write-ColorOutput "IMPORTANT: Terminal Restart Required" "Yellow"
Write-ColorOutput "The 'magic' command will NOT work until you:" "Yellow"
Write-Host ""
Write-ColorOutput "REQUIRED - Choose ONE option:" "Red"
Write-ColorOutput "  1. RESTART TERMINAL (Recommended)" "Blue"
Write-ColorOutput "     • Close this terminal completely" "White"
Write-ColorOutput "     • Open a new terminal window" "White"
Write-ColorOutput "     • Type: magic" "Green"
Write-Host ""
Write-ColorOutput "  2. RELOAD ENVIRONMENT (PowerShell only)" "Blue"
Write-ColorOutput "     • Type: `$env:Path = [System.Environment]::GetEnvironmentVariable('Path','User')" "White"
Write-ColorOutput "     • Then try: magic" "Green"
Write-Host ""

Write-ColorOutput "Quick Start Guide:" "Cyan"
Write-ColorOutput "  • Git Operations: Push, pull, commit management" "White"
Write-ColorOutput "  • Project Structure: View and navigate directories" "White"
Write-ColorOutput "  • Web Development: Modern frontend/backend automation" "White"
Write-ColorOutput "  • And much more!" "White"
Write-Host ""

Write-ColorOutput "Uninstall:" "Cyan"
Write-ColorOutput "  • Run: powershell -ExecutionPolicy Bypass -File uninstall.ps1" "White"
Write-Host ""

Write-ColorOutput "" "Green"