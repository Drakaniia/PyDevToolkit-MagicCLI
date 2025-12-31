# ============================================================
# PyDevToolkit-MagicCLI Global Uninstaller (Windows)
# ============================================================
# This script completely removes PyDevToolkit-MagicCLI
# installed via the automated PowerShell installer.
# ============================================================

#Requires -Version 5.1

# ============================================================
# CONFIGURATION
# ============================================================

$PackageName = "magic-cli"
$InstallDir = Join-Path $env:USERPROFILE ".magic-cli"

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
    Write-ColorOutput "  PyDevToolkit-MagicCLI Global Uninstaller                " "Blue"
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

function Get-PythonCommands {
    $commands = @("python", "python3", "py")
    $foundCommands = @()
    
    foreach ($cmd in $commands) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) {
            $version = & $cmd --version 2>&1
            if ($version -match "Python 3\.") {
                $foundCommands += $cmd
            }
        }
    }
    
    return $foundCommands
}

function Test-PackageInstalled {
    param([string]$PythonCmd, [string]$PackageName)
    
    try {
        $result = & $PythonCmd -m pip show $PackageName 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Uninstall-Package {
    param([string]$PythonCmd, [string]$PackageName)
    
    Write-Info "Uninstalling $PackageName using $PythonCmd..."
    
    try {
        $result = & $PythonCmd -m pip uninstall --yes $PackageName 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Successfully uninstalled $PackageName"
            return $true
        }
    } catch {
        Write-Error "Failed to uninstall $PackageName using $PythonCmd: $_"
    }
    return $false
}

function Clear-PipCache {
    Write-Info "Cleaning pip cache..."
    
    $pythonCmds = Get-PythonCommands
    $cacheCleaned = $false
    
    foreach ($cmd in $pythonCmds) {
        try {
            $result = & $cmd -m pip cache purge 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Cleaned pip cache for $cmd"
                $cacheCleaned = $true
            }
        } catch {
            # Ignore cache cleanup errors
        }
    }
    
    if (-not $cacheCleaned) {
        Write-Warning "Could not clean pip cache (this is usually not a problem)"
    }
}

function Remove-FromPath {
    param([string]$PathToRemove)
    
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    if ($currentPath -like "*$PathToRemove*") {
        # Remove the path from the user PATH
        $newPath = ($currentPath -split ';' | Where-Object { $_ -ne $PathToRemove }) -join ';'
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Success "Removed $PathToRemove from user PATH"
        return $true
    }
    
    return $false
}

# ============================================================
# MAIN UNINSTALLATION LOGIC
# ============================================================

Write-Header

Write-ColorOutput "This uninstaller will:" "Cyan"
Write-ColorOutput "  • Remove the installation directory ($InstallDir)" "White"
Write-ColorOutput "  • Remove PyDevToolkit-MagicCLI from PATH" "White"
Write-ColorOutput "  • Optionally uninstall Python packages" "White"
Write-ColorOutput "  • Clean up pip cache" "White"
Write-Host ""

$response = Read-Host "Continue with uninstallation? [Y/n] (Y default)"
if ($response -and $response -ne "Y" -and $response -ne "y") {
    Write-Host ""
    Write-ColorOutput "Uninstallation cancelled by user." "Yellow"
    exit 0
}

Write-Section "Checking Installation"

$foundInstallation = $false

if (Test-Path $InstallDir) {
    $foundInstallation = $true
    Write-Success "Found installation directory: $InstallDir"
} else {
    Write-Warning "Installation directory not found: $InstallDir"
}

# Check if magic command exists
$binDir = Join-Path $InstallDir "bin"
$magicCmd = Join-Path $binDir "magic.cmd"
if (Test-Path $magicCmd) {
    Write-Success "Found 'magic' command wrapper"
} else {
    Write-Info "'magic' command wrapper not found"
}

if (-not $foundInstallation) {
    Write-Warning "No installation found to remove"
    $response = Read-Host "Continue with Python package cleanup anyway? [Y/n] (Y default)"
    if ($response -and $response -ne "Y" -and $response -ne "y") {
        Write-ColorOutput "Uninstallation cancelled." "Yellow"
        exit 0
    }
    Write-Info "Proceeding with Python package cleanup..."
}

Write-Section "Removing Installation Directory"

if (Test-Path $InstallDir) {
    try {
        Remove-Item -Path $InstallDir -Recurse -Force -ErrorAction Stop
        Write-Success "Removed installation directory: $InstallDir"
    } catch {
        Write-Error "Failed to remove installation directory: $_"
        Write-Info "You may need to run this script as Administrator"
    }
}

Write-Section "Cleaning PATH"

$pathRemoved = Remove-FromPath -PathToRemove $binDir

if (-not $pathRemoved) {
    Write-Info "PyDevToolkit-MagicCLI not found in PATH"
}

Write-Section "Python Package Cleanup"

$pythonCmds = Get-PythonCommands

if ($pythonCmds.Count -gt 0) {
    Write-Info "Found Python installations: $($pythonCmds -join ', ')"
    
    $packageFound = $false
    foreach ($cmd in $pythonCmds) {
        if (Test-PackageInstalled -PythonCmd $cmd -PackageName $PackageName) {
            $packageFound = $true
            Write-Info "Found package installed with $cmd"
            
            $response = Read-Host "Uninstall Python package from $cmd? [Y/n] (Y default)"
            if (-not $response -or $response -eq "Y" -or $response -eq "y") {
                if (Uninstall-Package -PythonCmd $cmd -PackageName $PackageName) {
                    Write-Success "Uninstalled package from $cmd"
                }
            }
        }
    }
    
    if (-not $packageFound) {
        Write-Info "No Python packages found to uninstall"
    }
    
    # Clean pip cache
    Clear-PipCache
} else {
    Write-Info "No Python installations found"
}

Write-Section "Verification"

# Check if everything is cleaned up
if (-not (Test-Path $InstallDir)) {
    Write-Success "Installation directory removed"
} else {
    Write-Warning "Installation directory still exists: $InstallDir"
}

$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$binDir*") {
    Write-Success "PyDevToolkit-MagicCLI removed from PATH"
} else {
    Write-Warning "PyDevToolkit-MagicCLI still in PATH (restart terminal to refresh)"
}

Write-Section "Uninstallation Complete"

Write-ColorOutput "PyDevToolkit-MagicCLI has been uninstalled!" "Green"
Write-Host ""
Write-ColorOutput "What was removed:" "Cyan"
Write-ColorOutput "  • Installation directory: $InstallDir" "White"
Write-ColorOutput "  • PATH entries" "White"
Write-ColorOutput "  • Python packages (if selected)" "White"
Write-ColorOutput "  • Pip cache cleaned" "White"
Write-Host ""

Write-ColorOutput "Note:" "Yellow"
Write-ColorOutput "  • Restart your terminal for PATH changes to take effect" "White"
Write-ColorOutput "  • The 'magic' command will no longer be available" "White"
Write-Host ""

Write-ColorOutput "Reinstall anytime with:" "Cyan"
Write-ColorOutput "  powershell -ExecutionPolicy Bypass -File install.ps1" "Green"
Write-Host ""

Write-ColorOutput "Thank you for using PyDevToolkit-MagicCLI!" "Green"