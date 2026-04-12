param(
    [Parameter(Mandatory = $true)][string]$RootDir,
    [Parameter(Mandatory = $true)][string]$ApiDir,
    [Parameter(Mandatory = $true)][string]$WebDir,
    [Parameter(Mandatory = $true)][string]$ConfigFile,
    [Parameter(Mandatory = $true)][string]$ConfigExample,
    [Parameter(Mandatory = $true)][string]$ToolsDir,
    [Parameter(Mandatory = $true)][string]$DownloadsDir,
    [Parameter(Mandatory = $true)][string]$PythonDir,
    [Parameter(Mandatory = $true)][string]$NodeDir
)

$ErrorActionPreference = "Stop"

$pythonVersion = "3.11.9"
$pythonInstallerName = "python-3.11.9-amd64.exe"
$pythonInstallerUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"

$nodeVersion = "20.20.2"
$nodeArchiveName = "node-v20.20.2-win-x64.zip"
$nodeArchiveUrl = "https://nodejs.org/dist/v20.20.2/node-v20.20.2-win-x64.zip"

function Write-Step {
    param([string]$Message)
    Write-Host "[bootstrap] $Message"
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Download-File {
    param(
        [string]$Url,
        [string]$Destination,
        [string]$Label
    )

    if (Test-Path -LiteralPath $Destination) {
        Write-Step "$Label already downloaded"
        return
    }

    Write-Step "Downloading $Label"
    Invoke-WebRequest -Uri $Url -OutFile $Destination
}

function Get-PythonCommand {
    $localPython = Join-Path $PythonDir "python.exe"
    if (Test-Path -LiteralPath $localPython) {
        return $localPython
    }

    $systemPython = Get-Command python -ErrorAction SilentlyContinue
    if ($systemPython) {
        return $systemPython.Source
    }

    $launcher = Get-Command py -ErrorAction SilentlyContinue
    if ($launcher) {
        return "py -3"
    }

    return $null
}

function Ensure-ConfigFile {
    if (Test-Path -LiteralPath $ConfigFile) {
        Write-Step "config.yaml already exists"
        return
    }

    if (-not (Test-Path -LiteralPath $ConfigExample)) {
        throw "Missing config example: $ConfigExample"
    }

    Copy-Item -LiteralPath $ConfigExample -Destination $ConfigFile
    Write-Step "Created config.yaml from config.example.yaml"
}

function Ensure-Python {
    if (Get-PythonCommand) {
        Write-Step "Python runtime already available"
        return
    }

    $installerPath = Join-Path $DownloadsDir $pythonInstallerName
    Download-File -Url $pythonInstallerUrl -Destination $installerPath -Label "Python $pythonVersion installer"

    Write-Step "Installing local Python $pythonVersion"
    $arguments = @(
        "/quiet",
        "InstallAllUsers=0",
        "Include_pip=1",
        "Include_test=0",
        "Include_launcher=0",
        "AssociateFiles=0",
        "Shortcuts=0",
        "PrependPath=0",
        "TargetDir=$PythonDir"
    )
    $process = Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        throw "Python installer exited with code $($process.ExitCode)"
    }

    $localPython = Join-Path $PythonDir "python.exe"
    if (-not (Test-Path -LiteralPath $localPython)) {
        throw "Python installation finished, but python.exe was not found in $PythonDir"
    }

    Write-Step "Local Python installed at $PythonDir"
}

function Ensure-Node {
    $localNode = Join-Path $NodeDir "node.exe"
    $localNpm = Join-Path $NodeDir "npm.cmd"
    if ((Test-Path -LiteralPath $localNode) -and (Test-Path -LiteralPath $localNpm)) {
        Write-Step "Local Node.js runtime already available"
        return
    }

    $systemNode = Get-Command node -ErrorAction SilentlyContinue
    $systemNpm = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if ($systemNode -and $systemNpm) {
        Write-Step "Node.js runtime already available"
        return
    }

    $archivePath = Join-Path $DownloadsDir $nodeArchiveName
    Download-File -Url $nodeArchiveUrl -Destination $archivePath -Label "Node.js $nodeVersion archive"

    Write-Step "Extracting local Node.js $nodeVersion"
    Expand-Archive -Path $archivePath -DestinationPath $ToolsDir -Force

    if (-not (Test-Path -LiteralPath $localNode)) {
        throw "Node.js extraction finished, but node.exe was not found in $NodeDir"
    }
    if (-not (Test-Path -LiteralPath $localNpm)) {
        throw "Node.js extraction finished, but npm.cmd was not found in $NodeDir"
    }

    Write-Step "Local Node.js installed at $NodeDir"
}

function Ensure-Venv {
    $venvPython = Join-Path $ApiDir ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        Write-Step "Backend virtual environment already exists"
        return
    }

    $pythonCommand = Get-PythonCommand
    if (-not $pythonCommand) {
        throw "Python is unavailable, so the backend virtual environment cannot be created"
    }

    Write-Step "Creating backend virtual environment"
    if ($pythonCommand -eq "py -3") {
        $process = Start-Process -FilePath "py" -ArgumentList @("-3", "-m", "venv", (Join-Path $ApiDir ".venv")) -Wait -PassThru -NoNewWindow
    } else {
        $process = Start-Process -FilePath $pythonCommand -ArgumentList @("-m", "venv", (Join-Path $ApiDir ".venv")) -Wait -PassThru -NoNewWindow
    }

    if ($process.ExitCode -ne 0) {
        throw "Virtual environment creation failed with code $($process.ExitCode)"
    }

    if (-not (Test-Path -LiteralPath $venvPython)) {
        throw "Virtual environment creation finished, but python.exe was not found in .venv"
    }

    Write-Step "Backend virtual environment ready"
}

Ensure-Directory -Path $ToolsDir
Ensure-Directory -Path $DownloadsDir

Ensure-ConfigFile
Ensure-Python
Ensure-Node
Ensure-Venv

Write-Step "Bootstrap completed"
