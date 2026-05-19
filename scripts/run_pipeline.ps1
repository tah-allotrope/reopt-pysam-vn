<#
.SYNOPSIS
Master orchestration pipeline for a complete case study evaluation.

.DESCRIPTION
Runs a case study through 5 stages: materialize → solve → financial analysis
→ BESS dispatch → report generation. Stages are cached via .done markers;
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
.\scripts\run_pipeline.ps1 --case-study ninhsim --regime decision_14_2025_legacy --skip-solve
.\scripts\run_pipeline.ps1 --case-study north_thuan --regime decision_963_2026_current --dry-run
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
$CacheDir = Join-Path $RepoRoot "artifacts" "pipeline_cache"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$CaseSlug = "$CaseStudy-$Regime"

if ($Force -and (Test-Path $CacheDir)) {
    Write-Host "Clearing pipeline cache (--force)..." -ForegroundColor Yellow
    Remove-Item -Path (Join-Path $CacheDir "$CaseSlug*") -ErrorAction SilentlyContinue
}

# ---------------------------------------------------------------------------
# Stage mapping: case study → build script
# ---------------------------------------------------------------------------
$BuildScripts = @{
    saigon18   = "scripts/python/reopt/build_saigon18_reopt_input.py"
    ninhsim    = "scripts/python/integration/build_ninhsim_reopt_input.py"
    north_thuan = "scripts/python/integration/build_north_thuan_reopt_input.py"
}

# ---------------------------------------------------------------------------
# Input hashing for cache invalidation
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Stage helpers
# ---------------------------------------------------------------------------
function Get-StageMarker { param([string]$Stage) => Join-Path $CacheDir "$CaseSlug-$Stage.done" }

function Is-StageCached {
    param([string]$Stage, [string]$Hash)
    $marker = Get-StageMarker $Stage
    if (-not (Test-Path $marker)) { return $false }
    $cachedHash = (Get-Content $marker -Raw).Trim()
    return $cachedHash -eq $Hash
}

function Write-StageCache {
    param([string]$Stage, [string]$Hash)
    $marker = Get-StageMarker $Stage
    New-Item -ItemType Directory -Path (Split-Path $marker -Parent) -Force | Out-Null
    Set-Content -Path $marker -Value $Hash
}

function Run-Stage {
    param(
        [string]$Stage,
        [string]$Description,
        [scriptblock]$ScriptBlock
    )

    if ($DryRun) {
        Write-Host "  [DRY-RUN] Stage $Stage: $Description" -ForegroundColor Cyan
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

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
$venvPython = Join-Path $RepoRoot ".venv" "Scripts" "python.exe"
if (-not (Test-Path $venvPython)) { $venvPython = "python" }

$buildScript = Join-Path $RepoRoot $BuildScripts[$CaseStudy]
$configArg = if ($Config) { "--config", $Config } else { }

# ---------------------------------------------------------------------------
# Print plan
# ---------------------------------------------------------------------------
Write-Host "=== REopt Pipeline: $CaseStudy / $Regime ===" -ForegroundColor Cyan
Write-Host "Stages:"
Write-Host "  1. Materialize scenario"
Write-Host "  2. Solve ($(if ($SkipSolve) { 'skipped' } else { 'Julia' }) )"
Write-Host "  3. Financial analysis (equity IRR + DPPA settlement)"
Write-Host "  4. BESS dispatch analysis"
Write-Host "  5. Report generation"
Write-Host "Cache: $CacheDir"
if ($DryRun) {
    Write-Host "`n[DRY-RUN] Pipeline plan printed. No execution."
    exit 0
}

# ---------------------------------------------------------------------------
# STAGE 1: Materialize scenario
# ---------------------------------------------------------------------------
$stage = "01-materialize"
$hash = Get-InputHash @($buildScript, (Join-Path $RepoRoot "src" "python" "reopt_pysam_vn" "reopt" "preprocess.py"))
if (-not (Is-StageCached $stage $hash)) {
    Run-Stage $stage "Materialize $CaseStudy scenario for $Regime" {
        & $venvPython $buildScript --regime $Regime @configArg
    }
    Write-StageCache $stage $hash
} else {
    Write-Host "  [CACHED] Stage 1 already complete." -ForegroundColor Gray
}

# ---------------------------------------------------------------------------
# STAGE 2: Solve
# ---------------------------------------------------------------------------
$solveScript = Join-Path $RepoRoot "scripts" "run_solve.ps1"
$generatedScenario = Get-ChildItem -Path (Join-Path $RepoRoot "scenarios" "generated") -Recurse -Filter "*.json" | Select-Object -First 1
$solveOutputDir = Join-Path $RepoRoot "artifacts" "results" $CaseSlug

if (-not $SkipSolve) {
    $stage = "02-solve"
    $hash = Get-InputHash @($generatedScenario.FullName)
    if (-not (Is-StageCached $stage $hash) -or $Force) {
        Run-Stage $stage "Solve $CaseStudy under $Regime" {
            $solveArgs = @("--scenario", $generatedScenario.FullName, "--output-dir", $solveOutputDir)
            if ($Fallback) { $solveArgs += "--fallback" }
            & $solveScript @solveArgs
        }
        Write-StageCache $stage $hash
    } else {
        Write-Host "  [CACHED] Stage 2 already complete." -ForegroundColor Gray
    }
} else {
    Write-Host "  [SKIP] --skip-solve flag set." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# STAGE 3: Financial analysis
# ---------------------------------------------------------------------------
$stage = "03-financial"
$reoptResults = Join-Path $solveOutputDir "reopt-results.json"
if (Test-Path $reoptResults) {
    $hash = Get-InputHash @($reoptResults)
    if (-not (Is-StageCached $stage $hash)) {
        Run-Stage $stage "Compute equity IRR + DPPA settlement" {
            $equityOut = Join-Path $RepoRoot "artifacts" "reports" $CaseSlug "equity-irr.json"
            & $venvPython (Join-Path $RepoRoot "scripts" "python" "reopt" "equity_irr.py") `
                --reopt $reoptResults --config $Config `
                --output $equityOut

            $dppaOut = Join-Path $RepoRoot "artifacts" "reports" $CaseSlug "dppa-settlement.json"
            & $venvPython (Join-Path $RepoRoot "scripts" "python" "reopt" "dppa_settlement.py") `
                --reopt $reoptResults --config $Config `
                --output $dppaOut
        }
        Write-StageCache $stage $hash
    } else {
        Write-Host "  [CACHED] Stage 3 already complete." -ForegroundColor Gray
    }
} else {
    Write-Host "  [SKIP] No solve results at $reoptResults" -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# STAGE 4: BESS dispatch analysis
# ---------------------------------------------------------------------------
$stage = "04-bess"
$scenarioInput = if ($generatedScenario) { $generatedScenario.FullName } else { "" }
if ((Test-Path $reoptResults) -and $scenarioInput) {
    $hash = Get-InputHash @($reoptResults, $scenarioInput)
    if (-not (Is-StageCached $stage $hash)) {
        Run-Stage $stage "BESS dispatch analysis under $Regime" {
            $bessOut = Join-Path $RepoRoot "artifacts" "reports" $CaseSlug "bess-dispatch.json"
            & $venvPython (Join-Path $RepoRoot "scripts" "python" "reopt" "bess_dispatch_analysis.py") `
                --reopt $reoptResults --scenario $scenarioInput `
                --config $Config --regime $Regime --output $bessOut
        }
        Write-StageCache $stage $hash
    } else {
        Write-Host "  [CACHED] Stage 4 already complete." -ForegroundColor Gray
    }
} else {
    Write-Host "  [SKIP] Missing solve results or scenario input." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# STAGE 5: Report generation
# ---------------------------------------------------------------------------
$stage = "05-report"
$reportsDir = Join-Path $RepoRoot "artifacts" "reports" $CaseSlug
if (Test-Path $reportsDir) {
    $hash = Get-InputHash @((Get-ChildItem -Path $reportsDir -Filter "*.json" | ForEach-Object { $_.FullName }))
    if (-not (Is-StageCached $stage $hash)) {
        Run-Stage $stage "Generate summary report for $CaseStudy" {
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
            New-Item -ItemType Directory -Path (Split-Path $reportPath -Parent) -Force | Out-Null
            $summary | ConvertTo-Json -Depth 5 | Set-Content -Path $reportPath -Encoding UTF8
            Write-Host "  Report: $reportPath" -ForegroundColor Green
        }
        Write-StageCache $stage $hash
    } else {
        Write-Host "  [CACHED] Stage 5 already complete." -ForegroundColor Gray
    }
}

Write-Host "`n=== Pipeline complete: $CaseStudy / $Regime ===" -ForegroundColor Green
