[CmdletBinding()]
param(
    [switch]$Approve,

    [ValidatePattern('^https://')]
    [string]$PythonIndexUrl = 'https://pypi.org/simple'
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$runtimeDistro = 'forgetops-runtime'
$runtimeStorage = Join-Path $projectRoot '.runtime-wsl'
$requirementsFile = Join-Path $projectRoot '.runtime-home\requirements-wsl.txt'
$wheelDirectory = Join-Path $projectRoot '.runtime-home\wheels'

$drive = $projectRoot.Substring(0, 1).ToLowerInvariant()
$relativeRoot = $projectRoot.Substring(3).Replace('\', '/')
$linuxProjectRoot = "/mnt/$drive/$relativeRoot"
$linuxPipCache = "$linuxProjectRoot/.uv-cache/pip-wsl"

function Get-RuntimeRegistration {
    return Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' |
        ForEach-Object { Get-ItemProperty $_.PSPath } |
        Where-Object { $_.DistributionName -eq $runtimeDistro } |
        Select-Object -First 1
}

function Invoke-WslNative {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Command
    )

    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $combinedOutput = & wsl.exe -d $runtimeDistro --cd $projectRoot -- @Command 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }

    $standardOutput = @(
        $combinedOutput | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] }
    )
    $standardError = @(
        $combinedOutput |
            Where-Object { $_ -is [System.Management.Automation.ErrorRecord] } |
            ForEach-Object { $_.ToString() }
    )
    if ($exitCode -ne 0) {
        $detail = @($standardOutput + $standardError) -join [Environment]::NewLine
        throw "Runtime setup command failed with exit code ${exitCode}: $($Command -join ' ')`n$detail"
    }
    return $standardOutput
}

function Invoke-RuntimeCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Command
    )

    Invoke-WslNative -Command $Command
}

$plannedSteps = @(
    "Install or verify WSL distribution '$runtimeDistro' at '$runtimeStorage'",
    'Install Docker Engine, Docker Compose, and Python inside that E-drive distribution',
    "Export exact dependencies from uv.lock to '$requirementsFile'",
    "Create the Linux virtual environment at '$projectRoot\.venv-wsl'",
    'Install hash-verified dependencies and a platform-independent ForgetOps wheel'
)

if (-not $Approve) {
    Write-Host 'Dry run only. No system or repository state was changed.'
    $plannedSteps | ForEach-Object { Write-Host "  - $_" }
    Write-Host 'Re-run with -Approve to perform these steps.'
    exit 0
}

if ($null -eq (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw 'uv is required on Windows to export the locked dependency set.'
}

$registration = Get-RuntimeRegistration
if ($null -eq $registration) {
    if (Test-Path -LiteralPath $runtimeStorage) {
        $entries = @(Get-ChildItem -LiteralPath $runtimeStorage -Force)
        if ($entries.Count -ne 0) {
            throw "Refusing to install into non-empty path '$runtimeStorage'."
        }
    }

    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & wsl.exe --install Ubuntu-24.04 `
            --name $runtimeDistro `
            --location $runtimeStorage `
            --no-launch `
            --version 2 `
            --web-download
        $installExitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    if ($installExitCode -ne 0) {
        throw "WSL installation failed with exit code $installExitCode"
    }
    $registration = Get-RuntimeRegistration
}

$registeredPath = [System.IO.Path]::GetFullPath([string]$registration.BasePath)
$expectedPath = [System.IO.Path]::GetFullPath($runtimeStorage)
if (-not $registeredPath.Equals($expectedPath, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing runtime outside the repository: '$registeredPath'."
}

Invoke-RuntimeCommand -Command @('env', 'DEBIAN_FRONTEND=noninteractive', 'apt-get', 'update')
Invoke-RuntimeCommand -Command @(
    'env', 'DEBIAN_FRONTEND=noninteractive',
    'apt-get', 'install', '-y',
    'docker.io', 'docker-compose-v2', 'python3-venv', 'python3-pip', 'ca-certificates', 'curl'
)

New-Item -ItemType Directory -Force -Path (Split-Path $requirementsFile) | Out-Null
& uv export `
    --frozen `
    --extra dev `
    --extra datahub `
    --no-emit-project `
    --format requirements-txt `
    --output-file $requirementsFile
if ($LASTEXITCODE -ne 0) {
    throw 'Unable to export the locked Linux dependency set.'
}

& uv build --wheel --out-dir $wheelDirectory
if ($LASTEXITCODE -ne 0) {
    throw 'Unable to build the ForgetOps wheel.'
}
$wheel = Get-ChildItem -LiteralPath $wheelDirectory -Filter 'forgetops-*.whl' |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
if ($null -eq $wheel) {
    throw "No ForgetOps wheel was created in '$wheelDirectory'."
}
$linuxWheel = "$linuxProjectRoot/.runtime-home/wheels/$($wheel.Name)"

Invoke-RuntimeCommand -Command @('python3', '-m', 'venv', '.venv-wsl')
Invoke-RuntimeCommand -Command @(
    'env',
    "PIP_INDEX_URL=$PythonIndexUrl",
    "PIP_CACHE_DIR=$linuxPipCache",
    'PIP_DEFAULT_TIMEOUT=180',
    'PIP_RETRIES=12',
    'PIP_DISABLE_PIP_VERSION_CHECK=1',
    '.venv-wsl/bin/python', '-m', 'pip', 'install',
    '--require-hashes', '-r', '.runtime-home/requirements-wsl.txt'
)
Invoke-RuntimeCommand -Command @(
    '.venv-wsl/bin/python', '-m', 'pip', 'install', '--no-deps', '--force-reinstall', $linuxWheel
)
Invoke-RuntimeCommand -Command @('systemctl', 'start', 'docker')
Invoke-RuntimeCommand -Command @('docker', '--version')
Invoke-RuntimeCommand -Command @('.venv-wsl/bin/python', '--version')
Invoke-RuntimeCommand -Command @('.venv-wsl/bin/datahub', 'version')

Write-Host "ForgetOps runtime is ready in '$runtimeStorage'."
