$ErrorActionPreference = 'Stop'
$script:failures = [System.Collections.Generic.List[string]]::new()
$script:assertions = 0

function Assert-RecapOutputContract {
    param([bool]$Condition, [string]$Name)
    $script:assertions++
    if (-not $Condition) { $script:failures.Add($Name) }
}

function Test-RecapLine {
    param([string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return $false }
    if ($Text -match '[\r\n]') { return $false }
    if ($Text -match '^\s*(#|[-*+]\s)') { return $false }
    if ($Text -match '^\s*(?:\*\*)?[A-Za-z][A-Za-z -]{0,30}:(?:\*\*)?\s*') { return $false }
    return $true
}

$success = 'The recap Skill is installed with manual-only metadata, and repository admission checks are now in progress.'
$noContext = 'No prior session activity is available to recap.'
$multiline = "Repository files were updated.`nNext: run the test suite."
$labeled = @(
    'Recap: Repository files were updated.',
    'Status: Repository files were updated.',
    'Result: Repository files were updated.',
    '**Recap:** Repository files were updated.'
)

Assert-RecapOutputContract (Test-RecapLine $success) 'success output is one unlabeled line'
Assert-RecapOutputContract ($success -match 'installed' -and $success -match 'in progress') 'success output includes outcome and current state'
Assert-RecapOutputContract (Test-RecapLine $noContext) 'no-context boundary is a safe one-line result'
Assert-RecapOutputContract (-not (Test-RecapLine $multiline)) 'multiline output is rejected'
foreach ($candidate in $labeled) {
    Assert-RecapOutputContract (-not (Test-RecapLine $candidate)) "leading label is rejected: $candidate"
}

if ($script:assertions -eq 0) {
    throw 'RECAP_OUTPUT_CONTRACT=FAIL (zero assertions)'
}

if ($script:failures.Count -gt 0) {
    $script:failures | ForEach-Object { "FAIL: $_" }
    throw "RECAP_OUTPUT_CONTRACT=FAIL ($($script:failures.Count) failures, $script:assertions assertions)"
}

"RECAP_OUTPUT_CONTRACT_ASSERTIONS=$script:assertions"
"RECAP_OUTPUT_CONTRACT=PASS"
