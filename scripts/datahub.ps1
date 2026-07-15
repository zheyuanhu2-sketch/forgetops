[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('start', 'stop', 'check', 'status', 'restore')]
    [string]$Action,

    [switch]$Approve,

    [switch]$AllowPull
)

$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$runtimeDistro = 'forgetops-runtime'
$runtimeStorage = Join-Path $projectRoot '.runtime-wsl'
$linuxVenv = Join-Path $projectRoot '.venv-wsl\bin\datahub'
$composeFile = Join-Path $projectRoot 'infra\datahub\quickstart-v1.6.0.yml'
$imageArchive = Join-Path $projectRoot '.runtime-home\docker-backup\forgetops-datahub-images.tar'
$preflightImageArchive = Join-Path $projectRoot '.runtime-home\docker-backup\forgetops-preflight-alpine.tar'
$keepAlivePidFile = Join-Path $projectRoot '.runtime-home\forgetops-wsl-keepalive.pid'

$drive = $projectRoot.Substring(0, 1).ToLowerInvariant()
$relativeRoot = $projectRoot.Substring(3).Replace('\', '/')
$linuxProjectRoot = "/mnt/$drive/$relativeRoot"
$linuxRuntimeHome = "$linuxProjectRoot/.runtime-home"
$linuxComposeFile = "$linuxProjectRoot/infra/datahub/quickstart-v1.6.0.yml"
$linuxImageArchive = "$linuxRuntimeHome/docker-backup/forgetops-datahub-images.tar"
$linuxPreflightImageArchive = "$linuxRuntimeHome/docker-backup/forgetops-preflight-alpine.tar"
$linuxVolumeBackupRoot = "$linuxRuntimeHome/docker-backup/volumes"

$requiredImages = @(
    'acryldata/datahub-actions:v1.6.0-slim',
    'acryldata/datahub-frontend-react:v1.6.0',
    'acryldata/datahub-gms:v1.6.0',
    'acryldata/datahub-upgrade:v1.6.0',
    'confluentinc/cp-kafka:8.0.0',
    'mysql:8.2',
    'opensearchproject/opensearch:2.19.3',
    'alpine:latest'
)

$runtimeEnvironment = @(
    "HOME=$linuxRuntimeHome",
    "USERPROFILE=$linuxRuntimeHome",
    'DATAHUB_COMPOSE_PROJECT_NAME=forgetops-datahub',
    'DATAHUB_TELEMETRY_ENABLED=false',
    "FORCE_LOCAL_QUICKSTART_MAPPING=$linuxProjectRoot/infra/datahub/quickstart-version-mapping.yml",
    'PYTHONUTF8=1',
    'PYTHONIOENCODING=utf-8'
)

function Invoke-WslNative {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Command,

        [switch]$AllowFailure
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

    $script:LastWslExitCode = $exitCode
    $standardOutput = @(
        $combinedOutput | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] }
    )
    $standardError = @(
        $combinedOutput |
            Where-Object { $_ -is [System.Management.Automation.ErrorRecord] } |
            ForEach-Object { $_.ToString() }
    )
    if (-not $AllowFailure -and $exitCode -ne 0) {
        $detail = @($standardOutput + $standardError) -join [Environment]::NewLine
        throw "ForgetOps runtime command failed with exit code ${exitCode}: $($Command -join ' ')`n$detail"
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

function Get-KeepAliveProcess {
    if (-not (Test-Path -LiteralPath $keepAlivePidFile)) {
        return $null
    }

    $pidText = [System.IO.File]::ReadAllText($keepAlivePidFile).Trim()
    $processId = 0
    if (-not [int]::TryParse($pidText, [ref]$processId)) {
        return $null
    }

    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $processId" -ErrorAction SilentlyContinue
    if (
        $null -eq $process -or
        $process.Name -ne 'wsl.exe' -or
        $process.CommandLine -notmatch 'forgetops-runtime' -or
        $process.CommandLine -notmatch 'sleep\s+infinity'
    ) {
        return $null
    }
    return $process
}

function Start-KeepAlive {
    if ($null -ne (Get-KeepAliveProcess)) {
        return
    }

    $process = Start-Process `
        -FilePath 'wsl.exe' `
        -ArgumentList @('-d', $runtimeDistro, '--', 'sleep', 'infinity') `
        -WindowStyle Hidden `
        -PassThru
    [System.IO.File]::WriteAllText(
        $keepAlivePidFile,
        $process.Id.ToString(),
        [System.Text.UTF8Encoding]::new($false)
    )
    Start-Sleep -Seconds 1
    if ($null -eq (Get-KeepAliveProcess)) {
        throw "Unable to keep WSL distribution '$runtimeDistro' running."
    }
}

function Stop-KeepAlive {
    $process = Get-KeepAliveProcess
    if ($null -ne $process) {
        Stop-Process -Id $process.ProcessId -Force
    }
    if (Test-Path -LiteralPath $keepAlivePidFile) {
        Remove-Item -LiteralPath $keepAlivePidFile -Force
    }

    $previousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & wsl.exe --terminate $runtimeDistro 2>$null
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    if ($exitCode -ne 0) {
        throw "Unable to terminate WSL distribution '$runtimeDistro'."
    }
}

function Start-RuntimeEngine {
    Invoke-RuntimeCommand -Command @('systemctl', 'start', 'docker')
    $dockerRoot = (Invoke-WslNative -Command @('docker', 'info', '--format', '{{.DockerRootDir}}')) -join ''
    if ($dockerRoot.Trim() -ne '/var/lib/docker') {
        throw "Unexpected Docker root in '$runtimeDistro': '$dockerRoot'."
    }
}

function Assert-IsolatedRuntime {
    if (-not (Test-Path -LiteralPath $runtimeStorage)) {
        throw "Missing E-drive runtime at '$runtimeStorage'. Run the runtime setup first."
    }

    $registration = Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' |
        ForEach-Object { Get-ItemProperty $_.PSPath } |
        Where-Object { $_.DistributionName -eq $runtimeDistro } |
        Select-Object -First 1
    if ($null -eq $registration) {
        throw "WSL distribution '$runtimeDistro' is not registered."
    }

    $registeredPath = [System.IO.Path]::GetFullPath([string]$registration.BasePath)
    $expectedPath = [System.IO.Path]::GetFullPath($runtimeStorage)
    if (-not $registeredPath.Equals($expectedPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing runtime outside the repository: '$registeredPath'."
    }

    if (-not (Test-Path -LiteralPath $composeFile)) {
        throw "Missing pinned compose file '$composeFile'."
    }

    $composeText = [System.IO.File]::ReadAllText($composeFile)
    $publishedPortCount = ([regex]::Matches($composeText, '(?m)^\s+published:\s+')).Count
    $loopbackBindingCount = ([regex]::Matches($composeText, '(?m)^\s+host_ip:\s+127\.0\.0\.1\s*$')).Count
    if ($publishedPortCount -eq 0 -or $publishedPortCount -ne $loopbackBindingCount) {
        throw "Refusing a quickstart whose published ports are not all bound to 127.0.0.1."
    }

}

function Get-MissingImages {
    $missing = @()
    foreach ($image in $requiredImages) {
        Invoke-WslNative -Command @('docker', 'image', 'inspect', $image) -AllowFailure | Out-Null
        if ($script:LastWslExitCode -ne 0) {
            $missing += $image
        }
    }
    return $missing
}

function Restore-Volumes {
    $backups = @(
        [pscustomobject]@{
            Volume = 'forgetops-datahub-broker'
            Archive = 'datahub_broker.tar.gz'
            ComposeVolume = 'broker'
        },
        [pscustomobject]@{
            Volume = 'forgetops-datahub-mysqldata'
            Archive = 'datahub_mysqldata.tar.gz'
            ComposeVolume = 'mysqldata'
        },
        [pscustomobject]@{
            Volume = 'forgetops-datahub-osdata'
            Archive = 'datahub_osdata.tar.gz'
            ComposeVolume = 'osdata'
        }
    )

    foreach ($backup in $backups) {
        $windowsArchive = Join-Path (Split-Path $imageArchive) "volumes\$($backup.Archive)"
        if (-not (Test-Path -LiteralPath $windowsArchive)) {
            throw "Missing volume backup '$windowsArchive'."
        }
    }

    if (-not $Approve) {
        Write-Host 'Dry run: the following E-drive backups would be restored:'
        $backups | ForEach-Object { Write-Host "  $($_.Archive) -> $($_.Volume)" }
        Write-Host 'Re-run with -Approve to create and populate these volumes.'
        return
    }

    foreach ($backup in $backups) {
        Invoke-WslNative -Command @('docker', 'volume', 'inspect', $backup.Volume) -AllowFailure | Out-Null
        if ($script:LastWslExitCode -eq 0) {
            throw "Refusing to overwrite existing volume '$($backup.Volume)'."
        }

        Invoke-RuntimeCommand -Command @(
            'docker', 'volume', 'create',
            '--label', 'com.docker.compose.project=forgetops-datahub',
            '--label', "com.docker.compose.volume=$($backup.ComposeVolume)",
            $backup.Volume
        )
        Invoke-RuntimeCommand -Command @(
            'docker', 'run', '--rm',
            '--name', "forgetops-restore-$($backup.ComposeVolume)",
            '--entrypoint', '/bin/sh',
            '--mount', "type=volume,src=$($backup.Volume),dst=/target",
            '--mount', "type=bind,src=$linuxVolumeBackupRoot,dst=/backup,readonly",
            'mysql:8.2',
            '-c', "tar -xzf /backup/$($backup.Archive) -C /target"
        )
    }
}

Assert-IsolatedRuntime

switch ($Action) {
    'start' {
        $keepAliveWasRunning = $null -ne (Get-KeepAliveProcess)
        try {
            Start-KeepAlive
            Start-RuntimeEngine
            if (-not (Test-Path -LiteralPath $linuxVenv)) {
                throw "Missing Linux DataHub environment '$linuxVenv'. Run the runtime setup first."
            }

            $missingImages = @(Get-MissingImages)
            $pullImages = $false
            if ($missingImages.Count -gt 0 -and (Test-Path -LiteralPath $imageArchive)) {
                Write-Host 'Loading pinned DataHub images from the E-drive archive...'
                Invoke-RuntimeCommand -Command @(
                    'docker', 'image', 'load', '--input', $linuxImageArchive
                )
                $missingImages = @(Get-MissingImages)
            }
            if (
                $missingImages -contains 'alpine:latest' -and
                (Test-Path -LiteralPath $preflightImageArchive)
            ) {
                Write-Host 'Loading the pinned Alpine preflight image from the E-drive archive...'
                Invoke-RuntimeCommand -Command @(
                    'docker', 'image', 'load', '--input', $linuxPreflightImageArchive
                )
                $missingImages = @(Get-MissingImages)
            }
            if ($missingImages.Count -gt 0) {
                if (-not $AllowPull) {
                    throw "Missing images: $($missingImages -join ', '). Use -AllowPull to download them into the E-drive runtime."
                }
                $pullImages = $true
            }

            $pullArgument = if ($pullImages) { '--pull-images' } else { '--no-pull-images' }
            $command = @('env') + $runtimeEnvironment + @(
                '.venv-wsl/bin/datahub', 'docker', 'quickstart',
                '--version', 'v1.6.0',
                '--quickstart-compose-file', $linuxComposeFile,
                $pullArgument,
                '--dump-logs-on-failure'
            )
            Invoke-RuntimeCommand -Command $command
        }
        catch {
            $startFailure = $_
            if (-not $keepAliveWasRunning) {
                Invoke-WslNative -Command @('systemctl', 'stop', 'docker') -AllowFailure | Out-Null
                try {
                    Stop-KeepAlive
                }
                catch {
                    Write-Warning "Runtime startup failed and cleanup also failed: $($_.Exception.Message)"
                }
            }
            throw $startFailure
        }
    }
    'stop' {
        if ($null -eq (Get-KeepAliveProcess)) {
            Write-Host 'ForgetOps runtime is already stopped.'
            break
        }
        $command = @('env') + $runtimeEnvironment + @(
            'docker', 'compose',
            '--project-name', 'forgetops-datahub',
            '--file', $linuxComposeFile,
            '--profile', 'quickstart',
            'down'
        )
        Invoke-RuntimeCommand -Command $command
        Invoke-RuntimeCommand -Command @('systemctl', 'stop', 'docker')
        Stop-KeepAlive
    }
    'check' {
        if ($null -eq (Get-KeepAliveProcess)) {
            throw 'ForgetOps runtime is stopped. Run datahub.ps1 start first.'
        }
        if (-not (Test-Path -LiteralPath $linuxVenv)) {
            throw "Missing Linux DataHub environment '$linuxVenv'."
        }
        $command = @('env') + $runtimeEnvironment + @('.venv-wsl/bin/datahub', 'docker', 'check')
        Invoke-RuntimeCommand -Command $command
    }
    'status' {
        if ($null -eq (Get-KeepAliveProcess)) {
            Write-Host 'ForgetOps runtime is stopped.'
            break
        }
        Invoke-RuntimeCommand -Command @(
            'docker', 'ps', '-a',
            '--filter', 'label=com.docker.compose.project=forgetops-datahub',
            '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
        )
    }
    'restore' {
        if ($Approve) {
            Start-KeepAlive
            Start-RuntimeEngine
        }
        Restore-Volumes
    }
}
