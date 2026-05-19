<#
.SYNOPSIS
Master orchestration pipeline for a complete case study evaluation.

.DESCRIPTION
Runs a case study through 5 stages: materialize -> solve -> financial analysis
-> BESS dispatch -> report generation. Stages are cached via .done markers;
re-runs skip cached stages unless --force is used.

.PARAMETER CaseStudy
Name of the case study (saigon18|ninhsim|north_thuan).

.PARAMETER Regime
Regime ID (decision_963_2026_current|decision_14_2025_legacy).

.PARAMETER Config
Path to deal defaults JSON.

.PARAMETER SkipSolve
Skip Julia/API solve and use existing results.

.PARAMETER Force
Clear cache and re-run all stages.

.PARAMETER DryRun
Print pipeline plan without executing.

.PARAMETER Fallback
Use NREL API instead of local Julia for solve.

.EXAMPLE
.\scripts\run_pipeline.ps1 --case-study saigon18 --regime decision_963_2026_current
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("saigon18", "ninhsim", "north_thuan")]
    [string]$CaseStudy,
    [Parameter(Mandatory = $true)]
    [string]$Regime,
    [string]$Config,
    [switch]$SkipSolve,
    [switch]$Force,
    [switch]$DryRun,
    [switch]$Fallback
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$CacheDir = Join-Path $RepoRoot "pipeline_cache" | Join-Path -ChildPath "artifacts"
$CacheDir = Join-Path $RepoRoot "artifacts" | Join-Path -ChildPath "pipeline_cache"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$CaseSlug = "$CaseStudy-$Regime"

if ($Force -and (Test-Path $CacheDir)) {
    Write-Host "Clearing pipeline cache (--force)..." -ForegroundColor Yellow
    Remove-Item -Path (Join-Path $CacheDir "$CaseSlug*") -ErrorAction SilentlyContinue
}

# Stage mapping
$BuildScripts = @{
    saigon18   = "scripts\python\reopt\build_saigon18_reopt_input.py"
    ninhsim    = "scripts\python\integration\build_ninhsim_reopt_input.py"
    north_thuan = "scripts\python\integration\build_north_thuan_reopt_input.py"
}

# Resolve common paths
$PythonExe = "python"
$VenvPython = Join-Path $RepoRoot ".venv" | Join-Path -ChildPath "Scripts" | Join-Path -ChildPath "python.exe"
if (Test-Path $VenvPython) { $PythonExe = $VenvPython }

$buildScript = Join-Path $RepoRoot $BuildScripts[$CaseStudy]
$configArg = @()
if ($Config) { $configArg = @("--config", $Config) }

# Input hashing
function Get-InputHash {
    param([string[]]$Paths)
    $hashInput = ""
    foreach ($p in $Paths) {
        if (Test-Path $p) {
            $hashInput += (Get-FileHash -Path $p -Algorithm SHA256).Hash
        }
    }
    $provider = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($hashInput)
    return [System.BitConverter]::ToString($provider.ComputeHash($bytes)) -replace '-', ''
}

# Stage helpers
function Get-StageMarkerPath {
    param([string]$StageName, [string]$CacheDirPath, [string]$Slug)
    return Join-Path $CacheDirPath "$Slug-$StageName.done"
}

function Is-StageCached {
    param([string]$Stage, [string]$Hash, [string]$CacheDirPath, [string]$Slug)
    $marker = Get-StageMarkerPath $Stage $CacheDirPath $Slug
    if (-not (Test-Path $marker)) { return $false }
    $cachedHash = (Get-Content $marker -Raw).Trim()
    return $cachedHash -eq $Hash
}

function Write-StageCache {
    param([string]$Stage, [string]$Hash, [string]$CacheDirPath, [string]$Slug)
    $marker = Get-StageMarkerPath $Stage $CacheDirPath $Slug
    $parent = Split-Path $marker -Parent
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    Set-Content -Path $marker -Value $Hash
}

function Run-Stage {
    param([string]$Stage, [string]$Description, [scriptblock]$ScriptBlock)
    if ($DryRun) {
        Write-Host "  [DRY-RUN] Stage $Stage - $Description" -ForegroundColor Cyan
        return
    }
    Write-Host "`n=== [$Stage] $Description ===" -ForegroundColor Cyan
    & $ScriptBlock
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Stage $Stage failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
    Write-Host "  [OK] Stage $Stage completed." -ForegroundColor Green
}

# Print plan
Write-Host "=== REopt Pipeline: $CaseStudy / $Regime ===" -ForegroundColor Cyan
Write-Host "Stages:"
Write-Host "  1. Materialize scenario"
Write-Host "  2. Solve ($(if ($SkipSolve) { 'skipped' } else { 'Julia' }))"
Write-Host "  3. Financial analysis (equity IRR + DPPA settlement)"
Write-Host "  4. BESS dispatch analysis"
Write-Host "  5. Report generation"
Write-Host "Cache: $CacheDir"
if ($DryRun) {
    Write-Host "`n[DRY-RUN] Pipeline plan printed. No execution."
    exit 0
}

# STAGE 1: Materialize scenario
$s1 = "01-materialize"
$h1 = Get-InputHash @($buildScript, (Join-Path (Join-Path (Join-Path (Join-Path $RepoRoot "src") "python") "reopt_pysam_vn") "reopt" | Join-Path -ChildPath "preprocess.py"))
if (-not (Is-StageCached $s1 $h1 $CacheDir $CaseSlug)) {
    Run-Stage $s1 "Materialize $CaseStudy scenario for $Regime" {
        & $PythonExe $buildScript "--regime" $Regime @configArg
    }
    Write-StageCache $s1 $h1 $CacheDir $CaseSlug
} else {
    Write-Host "  [CACHED] Stage 1 already complete." -ForegroundColor Gray
}

# STAGE 2: Solve
$solveScript = Join-Path (Join-Path $RepoRoot "scripts") "run_solve.ps1"
$generatedScenario = Get-ChildItem -Path (Join-Path $RepoRoot "scenarios" | Join-Path -ChildPath "generated") -Recurse -Filter "*.json" | Select-Object -First 1
$solveOutputDir = Join-Path (Join-Path (Join-Path $RepoRoot "artifacts") "results") $CaseSlug

if (-not $SkipSolve -and $generatedScenario) {
    $s2 = "02-solve"
    $h2 = Get-InputHash @($generatedScenario.FullName)
    if (-not (Is-StageCached $s2 $h2 $CacheDir $CaseSlug) -or $Force) {
        Run-Stage $s2 "Solve $CaseStudy under $Regime" {
            $solveArgs = @("--scenario", $generatedScenario.FullName, "--output-dir", $solveOutputDir)
            if ($Fallback) { $solveArgs += "--fallback" }
            & $solveScript @solveArgs
        }
        Write-StageCache $s2 $h2 $CacheDir $CaseSlug
    } else {
        Write-Host "  [CACHED] Stage 2 already complete." -ForegroundColor Gray
    }
} elseif (-not $SkipSolve -and -not $generatedScenario) {
    Write-Host "  [SKIP] No generated scenario found." -ForegroundColor Yellow
} else {
    Write-Host "  [SKIP] --skip-solve flag set." -ForegroundColor Yellow
}

# STAGE 3: Financial analysis
$reoptResults = Join-Path $solveOutputDir "reopt-results.json"
if (Test-Path $reoptResults) {
    $s3 = "03-financial"
    $h3 = Get-InputHash @($reoptResults)
    if (-not (Is-StageCached $s3 $h3 $CacheDir $CaseSlug)) {
        Run-Stage $s3 "Compute equity IRR + DPPA settlement" {
            $reportsDir = Join-Path (Join-Path (Join-Path $RepoRoot "artifacts") "reports") $CaseSlug
            if (-not (Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir -Force | Out-Null }
            $equityOut = Join-Path $reportsDir "equity-irr.json"
            & $PythonExe (Join-Path (Join-Path (Join-Path $RepoRoot "scripts") "python") "reopt" | Join-Path -ChildPath "equity_irr.py") `
                "--reopt" $reoptResults "--config" $Config "--output" $equityOut
            $dppaOut = Join-Path $reportsDir "dppa-settlement.json"
            & $PythonExe (Join-Path (Join-Path (Join-Path $RepoRoot "scripts") "python") "reopt" | Join-Path -ChildPath "dppa_settlement.py") `
                "--reopt" $reoptResults "--config" $Config "--output" $dppaOut
        }
        Write-StageCache $s3 $h3 $CacheDir $CaseSlug
    } else {
        Write-Host "  [CACHED] Stage 3 already complete." -ForegroundColor Gray
    }
} else {
    Write-Host "  [SKIP] No solve results at $reoptResults" -ForegroundColor Yellow
}

# STAGE 4: BESS dispatch analysis
$scenarioInput = ""
if ($generatedScenario) { $scenarioInput = $generatedScenario.FullName }
if ((Test-Path $reoptResults) -and $scenarioInput) {
    $s4 = "04-bess"
    $h4 = Get-InputHash @($reoptResults, $scenarioInput)
    if (-not (Is-StageCached $s4 $h4 $CacheDir $CaseSlug)) {
        Run-Stage $s4 "BESS dispatch analysis under $Regime" {
            $reportsDir = Join-Path (Join-Path (Join-Path $RepoRoot "artifacts") "reports") $CaseSlug
            $bessOut = Join-Path $reportsDir "bess-dispatch.json"
            & $PythonExe (Join-Path (Join-Path (Join-Path $RepoRoot "scripts") "python") "reopt" | Join-Path -ChildPath "bess_dispatch_analysis.py") `
                "--reopt" $reoptResults "--scenario" $scenarioInput "--config" $Config "--regime" $Regime "--output" $bessOut
        }
        Write-StageCache $s4 $h4 $CacheDir $CaseSlug
    } else {
        Write-Host "  [CACHED] Stage 4 already complete." -ForegroundColor Gray
    }
} else {
    Write-Host "  [SKIP] Missing solve results or scenario input." -ForegroundColor Yellow
}

# STAGE 5: Report generation
$reportsDir = Join-Path (Join-Path (Join-Path $RepoRoot "artifacts") "reports") $CaseSlug
if (Test-Path $reportsDir) {
    $s5 = "05-report"
    $jsonFiles = Get-ChildItem -Path $reportsDir -Filter "*.json" | ForEach-Object { $_.FullName }
    $h5 = Get-InputHash @($jsonFiles)
    if (-not (Is-StageCached $s5 $h5 $CacheDir $CaseSlug)) {
        Run-Stage $s5 "Generate summary report for $CaseStudy" {
            $reportPath = Join-Path $reportsDir "pipeline-summary.json"
            $summary = @{
                case_study = $CaseStudy
                regime = $Regime
                timestamp = $Timestamp
                config = if ($Config) { (Get-Item $Config).Name } else { "built-in defaults" }
                stages = @{}
            }
            $doneMarkers = Get-ChildItem -Path $CacheDir -Filter "$CaseSlug-*.done" -ErrorAction SilentlyContinue
            foreach ($m in $doneMarkers) {
                $stageName = $m.BaseName -replace "^$CaseSlug-", ''
                $summary.stages[$stageName] = "completed"
            }
            $summary.stages["05-report"] = "completed"
            if (-not (Test-Path (Split-Path $reportPath -Parent))) { New-Item -ItemType Directory -Path (Split-Path $reportPath -Parent) -Force | Out-Null }
            $summary | ConvertTo-Json -Depth 5 | Set-Content -Path $reportPath -Encoding UTF8
            Write-Host "  Report: $reportPath" -ForegroundColor Green
        }
        Write-StageCache $s5 $h5 $CacheDir $CaseSlug
    } else {
        Write-Host "  [CACHED] Stage 5 already complete." -ForegroundColor Gray
    }
}

Write-Host "`n=== Pipeline complete: $CaseStudy / $Regime ===" -ForegroundColor Green
