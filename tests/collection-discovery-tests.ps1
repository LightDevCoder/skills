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
$installation = Get-Content -LiteralPath (Join-Path $Root "docs/INSTALLATION.md") -Raw

Assert-Collection ($readme -match "skills/docs/assets/skills-header\.png") "README must display the repository-local header image."
$firstNonEmptyReadmeLine = @($readme -split "\r?\n" | Where-Object { $_.Trim() } | Select-Object -First 1)
Assert-Collection (($firstNonEmptyReadmeLine.Count -eq 1) -and ($firstNonEmptyReadmeLine[0] -match "^!\[[^\]]+\]\(skills/docs/assets/skills-header\.png\)")) "README header image must be the first non-empty line with alt text."
$svgPath = Join-Path $Root "skills/docs/assets/skills-header.svg"
$pngPath = Join-Path $Root "skills/docs/assets/skills-header.png"
Assert-Collection (Test-Path -LiteralPath $svgPath) "Editable skills-header.svg is missing."
Assert-Collection (Test-Path -LiteralPath $pngPath) "Rendered skills-header.png is missing."
if ((Test-Path -LiteralPath $svgPath) -and (Test-Path -LiteralPath $pngPath)) {
    $svgText = Get-Content -LiteralPath $svgPath -Raw
    $pngBytes = [IO.File]::ReadAllBytes($pngPath)
    Assert-Collection (($svgText -match "<svg\b") -and ((Get-Item -LiteralPath $svgPath).Length -gt 100)) "Header SVG is not a non-empty SVG document."
    Assert-Collection (($pngBytes.Length -gt 100) -and ($pngBytes[0] -eq 137) -and ($pngBytes[1] -eq 80) -and ($pngBytes[2] -eq 78) -and ($pngBytes[3] -eq 71)) "Header PNG does not have a valid PNG signature."
}
Assert-Collection ($installation -match "npx skills add <owner>/<repository>") "Installation guide is missing the whole-repository release template."
Assert-Collection ($installation -match "--skill <skill-name>") "Installation guide is missing the per-Skill release template."
Assert-Collection ($installation -match "not a verified command") "Installation guide must label pre-release commands accurately."
Assert-Collection ($installation -match "Manual fallback") "Installation guide must retain a manual fallback."
Assert-Collection ($installation -match '\$sourceRoot' -and $installation -match '\$skillName' -and $installation -match '\$destinationRoot') "Manual fallback must use valid PowerShell variables."

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
    $sectionMatch = [regex]::Match($catalog, "(?ms)^### " + [regex]::Escape($package) + "\r?\n(?<section>.*?)(?=^### |\z)")
    $section = $sectionMatch.Groups["section"].Value
    Assert-Collection $sectionMatch.Success "$package is missing a catalog section."
    Assert-Collection ($section -match [regex]::Escape("- **Invocation:**")) "$package catalog invocation field is missing."
    Assert-Collection ($section -match [regex]::Escape("- **Status:**")) "$package catalog status field is missing."
    Assert-Collection ($section -match [regex]::Escape("- **Installation path:**")) "$package catalog installation field is missing."
    Assert-Collection ($section -match [regex]::Escape("- **Evidence:**")) "$package catalog evidence field is missing."
}

$markdownFiles = @(Get-ChildItem -LiteralPath $Root -Recurse -Filter "*.md" -File |
    ForEach-Object { $_.FullName.Substring($Root.Length + 1).Replace("\", "/") })
foreach ($file in $markdownFiles) {
    $path = Join-Path $Root $file
    $text = Get-Content -LiteralPath $path -Raw
    foreach ($match in [regex]::Matches($text, "\[[^\]]+\]\(([^)]+)\)")) {
        $link = $match.Groups[1].Value.Split("#")[0]
        if ($link -match "^https?://" -or [string]::IsNullOrWhiteSpace($link)) {
            continue
        }
        $resolved = Join-Path (Split-Path -Parent $path) $link
        Assert-Collection (Test-Path -LiteralPath $resolved) "$file contains an unresolved Markdown link: $link"
    }
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

$documentationFiles = @("README.md", "CATALOG.md", "CHANGELOG.md", "AGENTS.md") + @(
    Get-ChildItem -LiteralPath (Join-Path $Root "docs") -Recurse -Filter "*.md" -File |
    ForEach-Object { $_.FullName.Substring($Root.Length + 1).Replace("\", "/") }
)
foreach ($file in $documentationFiles) {
    $path = Join-Path $Root $file
    if (-not (Test-Path -LiteralPath $path)) {
        Assert-Collection $false "Required documentation file is missing: $file"
        continue
    }
    $text = Get-Content -LiteralPath $path -Raw
    foreach ($match in [regex]::Matches($text, "\[[^\]]+\]\(([^)]+)\)")) {
        $link = $match.Groups[1].Value.Split("#")[0]
        if ($link -match "^https?://" -or [string]::IsNullOrWhiteSpace($link)) {
            continue
        }
        $resolved = Join-Path (Split-Path -Parent $path) $link
        Assert-Collection (Test-Path -LiteralPath $resolved) "$file contains an unresolved relative link: $link"
    }
}

if ($script:failures.Count -gt 0) {
    $script:failures | ForEach-Object { "FAIL: $_" }
    throw "COLLECTION_DISCOVERY=FAIL ($($script:failures.Count) failures, $($script:assertions) assertions)"
}

"COLLECTION_DISCOVERY_ASSERTIONS=$($script:assertions)"
"COLLECTION_DISCOVERY=PASS"
