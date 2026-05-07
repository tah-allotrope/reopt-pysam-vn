<#
.SYNOPSIS
    Run the full TOU comparison workflow: materialize, extract deltas, generate report.

.DESCRIPTION
    Chains run_tou_comparison.py -> tou_financial_delta.py -> tou_comparison_report.py
    with default arguments pointing to the three representative case study scenarios.

.PARAMETER Solve
    Run the Julia solve path instead of dry-run mode.

.PARAMETER Force
    Re-run even if cached results exist.

.EXAMPLE
    .\scripts\run_tou_comparison.ps1
    .\scripts\run_tou_comparison.ps1 -Solve
    .\scripts\run_tou_comparison.ps1 -Force
#>
param(
    [switch]$Solve,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot ".." "..")

$Scenarios = @(
    "$RepoRoot\scenarios\case_studies\saigon18\2026-03-20_scenario-a_fixed-sizing_evntou.json",
    "$RepoRoot\scenarios\case_studies\ninhsim\2026-04-01_ninhsim_scenario-a_baseline-evn.json",
    "$RepoRoot\scenarios\case_studies\north_thuan\north_thuan_scenario_a.json"
)

# Filter to existing scenario files
$ExistingScenarios = $Scenarios | Where-Object { Test-Path $_ }

if ($ExistingScenarios.Count -eq 0) {
    Write-Error "No scenario files found. Expected files at: $($Scenarios -join ', ')"
    exit 1
}

Write-Host "`n=== TOU Comparison Workflow ===" -ForegroundColor Cyan
Write-Host "Scenarios: $($ExistingScenarios.Count) files" -ForegroundColor Gray
Write-Host "Solve mode: $(if ($Solve) { 'Yes (Julia)' } else { 'No (dry-run)' })" -ForegroundColor Gray

# Step 1: Run comparison
Write-Host "`n--- Step 1: Materialize and run scenarios ---" -ForegroundColor Yellow
$SolveFlag = if ($Solve) { "--solve" } else { "" }
$ForceFlag = if ($Force) { "--force" } else { "" }

$Args1 = @("scripts\python\reopt\run_tou_comparison.py", "--scenarios") + $ExistingScenarios
if ($Solve) { $Args1 += "--solve" }
if ($Force) { $Args1 += "--force" }

& python @Args1
if ($LASTEXITCODE -ne 0) {
    Write-Error "run_tou_comparison.py failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

# Step 2: Extract financial deltas
Write-Host "`n--- Step 2: Extract financial deltas ---" -ForegroundColor Yellow
& python "scripts\python\reopt\tou_financial_delta.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "tou_financial_delta.py failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

# Step 3: Generate HTML report
Write-Host "`n--- Step 3: Generate HTML report ---" -ForegroundColor Yellow
& python "scripts\python\reopt\tou_comparison_report.py"
if ($LASTEXITCODE -ne 0) {
    Write-Error "tou_comparison_report.py failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Host "`n=== TOU Comparison Workflow Complete ===" -ForegroundColor Green
$ReportPath = Join-Path $RepoRoot "artifacts\reports\tou_comparison\tou_comparison_report.html"
if (Test-Path $ReportPath) {
    Write-Host "Report: $ReportPath" -ForegroundColor Green
}