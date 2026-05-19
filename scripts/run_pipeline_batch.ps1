<#
.SYNOPSIS
Run the pipeline for all case studies × all regimes (6 combinations).

.DESCRIPTION
Invokes run_pipeline.ps1 for each (case-study, regime) combination.
Useful for cross-study comparison after solves complete.

.PARAMETER SkipSolve
Skip solve stage (use existing results).

.PARAMETER Force
Clear cache and re-run all stages.

.PARAMETER DryRun
Print the pipeline plan without executing.

.PARAMETER Fallback
Use NREL API instead of local Julia.

.PARAMETER Config
Path to deal defaults JSON.

.EXAMPLE
.\scripts\run_pipeline_batch.ps1
.\scripts\run_pipeline_batch.ps1 -SkipSolve
.\scripts\run_pipeline_batch.ps1 -DryRun
#>

param(
    [switch]$SkipSolve,
    [switch]$Force,
    [switch]$DryRun,
    [switch]$Fallback,
    [string]$Config = "data/vietnam/vn_deal_defaults_2026.json"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$PipelineScript = Join-Path $RepoRoot "scripts" "run_pipeline.ps1"

$CaseStudies = @("saigon18", "ninhsim", "north_thuan")
$Regimes = @("decision_963_2026_current", "decision_14_2025_legacy")

$TotalCombos = $CaseStudies.Count * $Regimes.Count
$Current = 0

Write-Host "=== Batch Pipeline: $TotalCombos combinations ===" -ForegroundColor Cyan
Write-Host ""

foreach ($cs in $CaseStudies) {
    foreach ($reg in $Regimes) {
        $Current++
        Write-Host "--- [$Current/$TotalCombos] $cs / $reg ---" -ForegroundColor Magenta

        $args = @(
            "--case-study", $cs,
            "--regime", $reg,
            "--config", $Config
        )
        if ($SkipSolve) { $args += "--skip-solve" }
        if ($Force) { $args += "--force" }
        if ($DryRun) { $args += "--dry-run" }
        if ($Fallback) { $args += "--fallback" }

        & $PipelineScript @args
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Pipeline failed for $cs / $reg (exit $LASTEXITCODE)"
        }
        Write-Host ""
    }
}

Write-Host "=== Batch pipeline complete: $Current/$TotalCombos ===" -ForegroundColor Green
