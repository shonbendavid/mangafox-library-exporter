# Build script for Windows: creates a venv, installs deps, and runs PyInstaller to bundle the GUI app.
param(
    [string]$entry = "src\mangadex_scrapper\gui.py",
    [string]$name = "mangadex-scrapper",
    [string]$icon = "",
    [switch]$windowed
)

Write-Host "Creating virtual environment..."
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
Write-Host "Installing requirements..."
pip install -r requirements.txt

# Resolve entry if user specified a module with -m syntax
if ($entry -like "-m *") {
    $module = $entry.Substring(3).Trim()
    # Convert module path to file under src (e.g. pkg.module -> src\pkg\module.py)
    $modulePath = $module -replace '\\.', '\\'
    $scriptPath = Join-Path -Path (Get-Location) -ChildPath "src\$modulePath.py"
} else {
    $scriptPath = if ($entry -like "*:*") { $entry } else { Join-Path -Path (Get-Location) -ChildPath $entry }
}

if (-not (Test-Path $scriptPath)) {
    Write-Error "Entry script not found: $scriptPath"
    exit 1
}

# Stop running instance and remove previous build artifacts to avoid PermissionError
Write-Host "Checking for running process '$name'..."
try {
    $proc = Get-Process -Name $name -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "Stopping running process $name..."
        $proc | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Warning "Could not stop process: $_"
}

$distExe = Join-Path (Get-Location) "dist\$name.exe"
if (Test-Path $distExe) {
    Write-Host "Removing existing executable: $distExe"
    try { Remove-Item -Path $distExe -Force } catch { Write-Warning ("Failed to remove " + $distExe + ": " + $_) }
}

$buildDir = Join-Path (Get-Location) "build"
if (Test-Path $buildDir) {
    Write-Host "Removing previous build directory: $buildDir"
    try { Remove-Item -Path $buildDir -Recurse -Force } catch { Write-Warning "Failed to remove build dir: $_" }
}

$specFile = Join-Path (Get-Location) "$name.spec"
if (Test-Path $specFile) {
    Write-Host "Removing spec file: $specFile"
    try { Remove-Item -Path $specFile -Force } catch { Write-Warning "Failed to remove spec file: $_" }
}

# Build PyInstaller args
$pyArgs = @("--onefile", "--clean", "--log-level=INFO", "--name", $name)
if ($windowed) { $pyArgs += "--noconsole" }
if ($icon) { $pyArgs += "--icon"; $pyArgs += $icon }
$pyArgs += $scriptPath

Write-Host "Running PyInstaller with args: $($pyArgs -join ' ')"
# Use the call operator to invoke pyinstaller with an argument array so PowerShell expands args correctly
$cmd = "pyinstaller"
Write-Host "Executing: & $cmd $($pyArgs -join ' ')"
& $cmd @pyArgs

Write-Host "Build finished. Check the 'dist' folder for the bundled executable: dist\$name.exe"
