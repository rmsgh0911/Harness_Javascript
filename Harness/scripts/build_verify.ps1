param(
    [ValidateSet("Install", "Check", "Typecheck", "Lint", "Test", "Build")]
    [string]$Mode = "Check"
)

$ErrorActionPreference = "Stop"

function Fail($Message) {
    throw $Message
}

function Get-ProjectDir {
    return (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Read-ProjectConfig {
    $projectDir = Get-ProjectDir
    $configPath = Join-Path $projectDir "Harness\config\project.json"
    if (-not (Test-Path $configPath)) {
        Fail "Missing Harness config: $configPath"
    }

    return Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Resolve-PackageManager($ProjectDir, $Config) {
    if ($Config.package_manager -and $Config.package_manager -ne "auto") {
        return $Config.package_manager
    }

    if (Test-Path (Join-Path $ProjectDir "pnpm-lock.yaml")) {
        return "pnpm"
    }

    if (Test-Path (Join-Path $ProjectDir "yarn.lock")) {
        return "yarn"
    }

    return "npm"
}

function Test-CommandExists($CommandName) {
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

function Get-PackageJson($ProjectDir, $Config) {
    $packageJson = if ($Config.package_json) { $Config.package_json } else { "package.json" }
    $path = Join-Path $ProjectDir $packageJson
    if (-not (Test-Path $path)) {
        Fail "Missing package.json: $path"
    }

    return Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Resolve-ScriptName($Mode, $Config) {
    $commands = $Config.commands
    $key = $Mode.ToLowerInvariant()
    if ($commands -and $commands.$key) {
        return $commands.$key
    }

    switch ($Mode) {
        "Check" { return "check" }
        "Typecheck" { return "typecheck" }
        "Lint" { return "lint" }
        "Test" { return "test" }
        "Build" { return "build" }
        default { return "" }
    }
}

function Invoke-PackageManager($PackageManager, [string[]]$Arguments) {
    if (-not (Test-CommandExists $PackageManager)) {
        Fail "Package manager is not available on PATH: $PackageManager"
    }

    & $PackageManager @Arguments
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

$projectDir = Get-ProjectDir
$config = Read-ProjectConfig
$packageManager = Resolve-PackageManager -ProjectDir $projectDir -Config $config

Push-Location $projectDir
try {
    if ($Mode -eq "Install") {
        if ($packageManager -eq "npm") {
            if (Test-Path (Join-Path $projectDir "package-lock.json")) {
                Invoke-PackageManager $packageManager @("ci")
            } else {
                Invoke-PackageManager $packageManager @("install")
            }
        } elseif ($packageManager -eq "pnpm") {
            Invoke-PackageManager $packageManager @("install", "--frozen-lockfile")
        } elseif ($packageManager -eq "yarn") {
            Invoke-PackageManager $packageManager @("install", "--frozen-lockfile")
        } else {
            Fail "Unsupported package manager: $packageManager"
        }

        Write-Host "Install verification passed with $packageManager."
        exit 0
    }

    $package = Get-PackageJson -ProjectDir $projectDir -Config $config
    $scriptName = Resolve-ScriptName -Mode $Mode -Config $config
    if (-not $scriptName) {
        Fail "No script mapping for mode: $Mode"
    }

    if (-not $package.scripts -or -not $package.scripts.$scriptName) {
        Fail "Missing package.json script for $Mode`: $scriptName"
    }

    if ($packageManager -eq "npm") {
        Invoke-PackageManager $packageManager @("run", $scriptName)
    } elseif ($packageManager -eq "pnpm") {
        Invoke-PackageManager $packageManager @("run", $scriptName)
    } elseif ($packageManager -eq "yarn") {
        Invoke-PackageManager $packageManager @($scriptName)
    } else {
        Fail "Unsupported package manager: $packageManager"
    }

    Write-Host "$Mode verification passed with $packageManager script '$scriptName'."
} finally {
    Pop-Location
}
