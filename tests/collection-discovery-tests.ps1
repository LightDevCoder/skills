param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"
$script:assertions = 0
$script:failures = @()

function Assert-Collection {
    param(
        [bool]$Condition,
        [string]$Message
    )

    $script:assertions++
    if (-not $Condition) {
        $script:failures += $Message
    }
}

$expected = @("ask-light", "learn-anything", "manuscript-ops", "project-init", "review-loop")
$skillRoot = Join-Path $Root "skills"
$actual = @(Get-ChildItem -LiteralPath $skillRoot -Directory |
    Where-Object { $_.Name -ne "docs" } |
    Select-Object -ExpandProperty Name |
    Sort-Object)

Assert-Collection (($actual -join ",") -eq ($expected -join ",")) "skills/ must contain exactly the five admitted package directories."

$readme = Get-Content -LiteralPath (Join-Path $Root "README.md") -Raw
$catalog = Get-Content -LiteralPath (Join-Path $Root "CATALOG.md") -Raw

Assert-Collection ($readme -match "skills/docs/assets/skills-header\.png") "README must display the repository-local header image."
Assert-Collection (Test-Path -LiteralPath (Join-Path $Root "skills/docs/assets/skills-header.svg")) "Editable skills-header.svg is missing."
Assert-Collection (Test-Path -LiteralPath (Join-Path $Root "skills/docs/assets/skills-header.png")) "Rendered skills-header.png is missing."

foreach ($package in $expected) {
    $packageRoot = Join-Path $skillRoot $package
    $skillFile = Join-Path $packageRoot "SKILL.md"
    $metadataFile = Join-Path $packageRoot "agents/openai.yaml"
    Assert-Collection (Test-Path -LiteralPath $skillFile) "$package is missing SKILL.md."
    Assert-Collection (Test-Path -LiteralPath $metadataFile) "$package is missing agents/openai.yaml."

    if (Test-Path -LiteralPath $skillFile) {
        $body = Get-Content -LiteralPath $skillFile -Raw
        Assert-Collection ($body -match "(?m)^name:\s*$([regex]::Escape($package))\s*$") "$package SKILL.md name metadata is inconsistent."
    }

    Assert-Collection ($readme -match [regex]::Escape("skills/$package/")) "$package is missing from README."
    Assert-Collection ($catalog -match [regex]::Escape("skills/$package/")) "$package is missing from CATALOG.md."
}

$retired = rg -n "project-workflow|to-manuscript-spec" (Join-Path $Root "skills") 2>$null
Assert-Collection ($LASTEXITCODE -eq 1) "Retired orchestration references remain under skills/."

foreach ($required in @(
    "AGENTS.md",
    "CATALOG.md",
    "CHANGELOG.md",
    "docs/INSTALLATION.md",
    "docs/MAINTENANCE.md",
    "docs/REVIEW_POLICY.md",
    "docs/SKILL_ADMISSION.md",
    "docs/workflows/README.md"
)) {
    Assert-Collection (Test-Path -LiteralPath (Join-Path $Root $required)) "Required documentation path is missing: $required"
}

if ($script:failures.Count -gt 0) {
    $script:failures | ForEach-Object { "FAIL: $_" }
    throw "COLLECTION_DISCOVERY=FAIL ($($script:failures.Count) failures, $($script:assertions) assertions)"
}

"COLLECTION_DISCOVERY_ASSERTIONS=$($script:assertions)"
"COLLECTION_DISCOVERY=PASS"
