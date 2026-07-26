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
$readmeZh = Get-Content -LiteralPath (Join-Path $Root "README.zh-CN.md") -Raw -ErrorAction SilentlyContinue
$catalogZh = Get-Content -LiteralPath (Join-Path $Root "CATALOG.zh-CN.md") -Raw -ErrorAction SilentlyContinue

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
Assert-Collection ($installation -match "npx skills add LightDevCoder/skills#v0\.1\.1") "Installation guide is missing the pinned whole-repository release command."
Assert-Collection ($installation -match "npx skills add LightDevCoder/skills#v0\.1\.1 --skill review-loop") "Installation guide is missing the pinned per-Skill release command."
Assert-Collection ($installation -match "#ref|fragment|default revision") "Installation guide must explain revision semantics rather than overclaim shorthand immutability."
Assert-Collection ($installation -notmatch "commands target the immutable v0\.1\.0 release") "Installation guide must not claim the old shorthand is permanently immutable."
Assert-Collection ($installation -notmatch "not a verified command|<owner>/<repository>") "Installation guide still contains unresolved pre-release command wording."
Assert-Collection ($installation -match "Manual fallback") "Installation guide must retain a manual fallback."
Assert-Collection ($installation -match '\$sourceRoot' -and $installation -match '\$skillName' -and $installation -match '\$destinationRoot') "Manual fallback must use valid PowerShell variables."

foreach ($package in $expected) {
    $packageRoot = Join-Path $skillRoot $package
    $skillFile = Join-Path $packageRoot "SKILL.md"
    $metadataFile = Join-Path $packageRoot "agents/openai.yaml"
    $body = ''
    Assert-Collection (Test-Path -LiteralPath $skillFile) "$package is missing SKILL.md."
    Assert-Collection (Test-Path -LiteralPath $metadataFile) "$package is missing agents/openai.yaml."

    if (Test-Path -LiteralPath $skillFile) {
        $body = Get-Content -LiteralPath $skillFile -Raw
        Assert-Collection ($body -match "(?m)^name:\s*$([regex]::Escape($package))\s*$") "$package SKILL.md name metadata is inconsistent."
    }

    if (Test-Path -LiteralPath $metadataFile) {
        $metadata = Get-Content -LiteralPath $metadataFile -Raw
        foreach ($field in @('display_name:', 'short_description:', 'default_prompt:', 'allow_implicit_invocation:')) {
            Assert-Collection ($metadata -match [regex]::Escape($field)) "$package metadata is missing $field."
        }
        $frontExplicit = $body -match '(?m)^disable-model-invocation:\s*true\s*$'
        $expectedPolicy = if ($frontExplicit) { 'false' } else { 'true' }
        Assert-Collection ($metadata -match ('allow_implicit_invocation:\s*' + $expectedPolicy)) "$package invocation policy disagrees with SKILL.md."
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
    Assert-Collection ($readme -match "\| \[$([regex]::Escape($package))\].*\| (User-invoked|Model-invoked)") "$package README invocation type is missing."
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

$retired = @(Get-ChildItem -LiteralPath (Join-Path $Root "skills") -Recurse -File |
    Select-String -Pattern "project-workflow|to-manuscript-spec")
Assert-Collection ($retired.Count -eq 0) "Retired orchestration references remain under skills/."

foreach ($required in @(
    "AGENTS.md",
    "CATALOG.md",
    "CHANGELOG.md",
    "docs/INSTALLATION.md",
    "docs/MAINTENANCE.md",
    "docs/REVIEW_POLICY.md",
    "docs/SKILL_ADMISSION.md",
    "docs/workflows/README.md",
    "skills/docs/assets/skills-header.json",
    "README.zh-CN.md",
    "CATALOG.zh-CN.md",
    "CHANGELOG.zh-CN.md",
    "docs/evidence/releases/v0.1.1/RELEASE_RECEIPT.md",
    ".github/workflows/quality.yml"
)) {
    Assert-Collection (Test-Path -LiteralPath (Join-Path $Root $required)) "Required documentation path is missing: $required"
}

foreach ($pair in @(
    @('README.md', 'README.zh-CN.md'),
    @('CATALOG.md', 'CATALOG.zh-CN.md'),
    @('CHANGELOG.md', 'CHANGELOG.zh-CN.md'),
    @('docs/INSTALLATION.md', 'docs/INSTALLATION.zh-CN.md'),
    @('docs/MAINTENANCE.md', 'docs/MAINTENANCE.zh-CN.md'),
    @('docs/REVIEW_POLICY.md', 'docs/REVIEW_POLICY.zh-CN.md'),
    @('docs/SKILL_ADMISSION.md', 'docs/SKILL_ADMISSION.zh-CN.md')
)) {
    $englishPath = Join-Path $Root $pair[0]; $chinesePath = Join-Path $Root $pair[1]
    Assert-Collection (Test-Path -LiteralPath $englishPath -PathType Leaf) "English/Chinese pair is missing: $($pair[0])"
    Assert-Collection (Test-Path -LiteralPath $chinesePath -PathType Leaf) "English/Chinese pair is missing: $($pair[1])"
    if ((Test-Path -LiteralPath $englishPath) -and (Test-Path -LiteralPath $chinesePath)) {
        $englishText = Get-Content -LiteralPath $englishPath -Raw
        $chineseText = Get-Content -LiteralPath $chinesePath -Raw
        Assert-Collection ($englishText -match [regex]::Escape($pair[1].Split('/')[-1])) "$($pair[0]) does not link its Chinese counterpart."
        Assert-Collection ($chineseText -match [regex]::Escape($pair[0].Split('/')[-1])) "$($pair[1]) does not link its English counterpart."
    }
}

$parityMatrix = @(
    [pscustomobject]@{ English = 'README.md'; Chinese = 'README.zh-CN.md'; Markers = @('Quick Start', 'ask-light', 'v0.1.1') },
    [pscustomobject]@{ English = 'CATALOG.md'; Chinese = 'CATALOG.zh-CN.md'; Markers = @('review-loop', 'v0.1.0', 'skills/') },
    [pscustomobject]@{ English = 'CHANGELOG.md'; Chinese = 'CHANGELOG.zh-CN.md'; Markers = @('v0.1.1', '0.1.0', 'release') },
    [pscustomobject]@{ English = 'docs/INSTALLATION.md'; Chinese = 'docs/INSTALLATION.zh-CN.md'; Markers = @('npx skills add', 'fresh-install', 'SKILL.md') },
    [pscustomobject]@{ English = 'docs/MAINTENANCE.md'; Chinese = 'docs/MAINTENANCE.zh-CN.md'; Markers = @('README', 'review-loop', 'release') },
    [pscustomobject]@{ English = 'docs/REVIEW_POLICY.md'; Chinese = 'docs/REVIEW_POLICY.zh-CN.md'; Markers = @('review-loop', 'PASS', 'BLOCKED') },
    [pscustomobject]@{ English = 'docs/SKILL_ADMISSION.md'; Chinese = 'docs/SKILL_ADMISSION.zh-CN.md'; Markers = @('review-loop', 'PASS', 'BLOCKED') }
)
foreach ($pair in $parityMatrix) {
    $englishText = Get-Content -LiteralPath (Join-Path $Root $pair.English) -Raw
    $chineseText = Get-Content -LiteralPath (Join-Path $Root $pair.Chinese) -Raw
    foreach ($marker in $pair.Markers) {
        Assert-Collection ($englishText -match [regex]::Escape($marker) -and $chineseText -match [regex]::Escape($marker)) "$($pair.English) and $($pair.Chinese) are missing the synchronized semantic marker: $marker"
    }
}

$semanticParityMatrix = @(
    [pscustomobject]@{ English = 'README.md'; Chinese = 'README.zh-CN.md'; Pairs = @(
        @('Install the whole first-party collection', '安装目标版本的整个第一方集合'),
        @('Install one Skill at the same target revision', '只安装同一目标版本下的一个 Skill'),
        @('fresh-install evidence', 'fresh-install 证据')
    ) },
    [pscustomobject]@{ English = 'CATALOG.md'; Chinese = 'CATALOG.zh-CN.md'; Pairs = @(
        @('Current state', '当前状态'),
        @('Stable release', '稳定版本'),
        @('Installation authority', '安装权威')
    ) },
    [pscustomobject]@{ English = 'CHANGELOG.md'; Chinese = 'CHANGELOG.zh-CN.md'; Pairs = @(
        @('Release-candidate evidence', 'Release candidate 证据'),
        @('Historical installation details', '历史安装明细')
    ) },
    [pscustomobject]@{ English = 'docs/INSTALLATION.md'; Chinese = 'docs/INSTALLATION.zh-CN.md'; Pairs = @(
        @('Revision semantics', 'Revision 语义'),
        @('Historical v0.1.0 verification', '历史 v0.1.0 验证'),
        @('Manual fallback', '手动 fallback')
    ) },
    [pscustomobject]@{ English = 'docs/MAINTENANCE.md'; Chinese = 'docs/MAINTENANCE.zh-CN.md'; Pairs = @(
        @('Authoritative records', '权威记录'),
        @('Synchronization matrix', '变更流程与同步矩阵'),
        @('closeout', 'closeout')
    ) },
    [pscustomobject]@{ English = 'docs/REVIEW_POLICY.md'; Chinese = 'docs/REVIEW_POLICY.zh-CN.md'; Pairs = @(
        @('Review triggers', 'Review triggers'),
        @('final acceptance', 'final acceptance'),
        @('BLOCKED', 'BLOCKED')
    ) },
    [pscustomobject]@{ English = 'docs/SKILL_ADMISSION.md'; Chinese = 'docs/SKILL_ADMISSION.zh-CN.md'; Pairs = @(
        @('Admission questions', 'Admission questions'),
        @('Required evidence', '必需 evidence'),
        @('review-loop', 'review-loop')
    ) }
)
foreach ($pair in $semanticParityMatrix) {
    $englishText = Get-Content -LiteralPath (Join-Path $Root $pair.English) -Raw
    $chineseText = Get-Content -LiteralPath (Join-Path $Root $pair.Chinese) -Raw
    foreach ($semanticPair in $pair.Pairs) {
        Assert-Collection ($englishText -match [regex]::Escape($semanticPair[0]) -and $chineseText -match [regex]::Escape($semanticPair[1])) "$($pair.English) and $($pair.Chinese) are missing the semantic pair: $($semanticPair[0]) / $($semanticPair[1])"
    }
}

foreach ($name in @('review-loop', 'project-init', 'ask-light', 'learn-anything', 'manuscript-ops')) {
    $englishPath = Join-Path $Root "docs/skills/$name.md"
    $chinesePath = Join-Path $Root "docs/zh-CN/skills/$name.md"
    Assert-Collection (Test-Path -LiteralPath $englishPath -PathType Leaf) "Skill guide is missing: docs/skills/$name.md"
    Assert-Collection (Test-Path -LiteralPath $chinesePath -PathType Leaf) "Chinese Skill guide is missing: docs/zh-CN/skills/$name.md"
    if ((Test-Path -LiteralPath $englishPath) -and (Test-Path -LiteralPath $chinesePath)) {
        Assert-Collection ((Get-Content -LiteralPath $englishPath -Raw) -match [regex]::Escape("../zh-CN/skills/$name.md")) "$name English guide does not link its Chinese guide."
        Assert-Collection ((Get-Content -LiteralPath $chinesePath -Raw) -match [regex]::Escape("../../skills/$name.md")) "$name Chinese guide does not link its English guide."
    }
}
foreach ($pair in @(
    @('docs/workflows/README.md', 'docs/zh-CN/workflows/README.md'),
    @('docs/workflows/first-party-composition.md', 'docs/zh-CN/workflows/first-party-composition.md'),
    @('docs/workflows/recipes.md', 'docs/zh-CN/workflows/recipes.md')
)) {
    $englishPath = Join-Path $Root $pair[0]; $chinesePath = Join-Path $Root $pair[1]
    Assert-Collection (Test-Path -LiteralPath $englishPath -PathType Leaf) "Workflow document is missing: $($pair[0])"
    Assert-Collection (Test-Path -LiteralPath $chinesePath -PathType Leaf) "Chinese workflow document is missing: $($pair[1])"
    if ((Test-Path -LiteralPath $englishPath) -and (Test-Path -LiteralPath $chinesePath)) {
        Assert-Collection ((Get-Content -LiteralPath $englishPath -Raw) -match [regex]::Escape((Split-Path $pair[1] -Leaf))) "$($pair[0]) does not link its Chinese counterpart."
        Assert-Collection ((Get-Content -LiteralPath $chinesePath -Raw) -match [regex]::Escape((Split-Path $pair[0] -Leaf))) "$($pair[1]) does not link its English counterpart."
    }
}

$guideParityMarkers = @('SKILL.md', 'BLOCKED', 'review-loop', 'user-invoked')
foreach ($name in @('review-loop', 'project-init', 'ask-light', 'learn-anything', 'manuscript-ops')) {
    $englishPath = Join-Path $Root "docs/skills/$name.md"
    $chinesePath = Join-Path $Root "docs/zh-CN/skills/$name.md"
    if ((Test-Path -LiteralPath $englishPath -PathType Leaf) -and (Test-Path -LiteralPath $chinesePath -PathType Leaf)) {
        $englishText = Get-Content -LiteralPath $englishPath -Raw
        $chineseText = Get-Content -LiteralPath $chinesePath -Raw
        foreach ($marker in $guideParityMarkers) {
            Assert-Collection ($englishText -match [regex]::Escape($marker) -and $chineseText -match [regex]::Escape($marker)) "$name Skill guides are missing the synchronized semantic marker: $marker"
        }
    }
}

$secondaryParity = @(
    [pscustomobject]@{ English = 'docs/workflows/first-party-composition.md'; Chinese = 'docs/zh-CN/workflows/first-party-composition.md'; Markers = @('review-loop', 'ask-light') },
    [pscustomobject]@{ English = 'docs/workflows/recipes.md'; Chinese = 'docs/zh-CN/workflows/recipes.md'; Markers = @('review-loop', 'ask-light', 'PASS', 'FAIL', 'BLOCKED', 'handoff', 'stop') }
)
foreach ($pair in $secondaryParity) {
    $englishText = Get-Content -LiteralPath (Join-Path $Root $pair.English) -Raw
    $chineseText = Get-Content -LiteralPath (Join-Path $Root $pair.Chinese) -Raw
    foreach ($marker in $pair.Markers) {
        Assert-Collection ($englishText -match [regex]::Escape($marker) -and $chineseText -match [regex]::Escape($marker)) "$($pair.English) and $($pair.Chinese) are missing the synchronized semantic marker: $marker"
    }
}

foreach ($name in @('RELEASE_RECEIPT', 'TEST_SUMMARY', 'INSTALLATION_VERIFICATION', 'DISCOVERY_VERIFICATION', 'LIMITATIONS')) {
    $englishText = Get-Content -LiteralPath (Join-Path $Root "docs/evidence/releases/v0.1.1/$name.md") -Raw
    $chineseText = Get-Content -LiteralPath (Join-Path $Root "docs/evidence/releases/v0.1.1/$name.zh-CN.md") -Raw
    foreach ($marker in @('v0.1.1', 'NOT TESTED', 'fresh')) {
        Assert-Collection ($englishText -match [regex]::Escape($marker) -and $chineseText -match [regex]::Escape($marker)) "$name release evidence is missing the synchronized semantic marker: $marker"
    }
}

Assert-Collection ($readme -match 'Drive your creativity') 'README About description is missing.'

$workflowText = Get-Content -LiteralPath (Join-Path $Root 'skills/ask-light/SKILL.md') -Raw
$workflowScript = Get-Content -LiteralPath (Join-Path $Root 'skills/ask-light/scripts/ask-light.ps1') -Raw
Assert-Collection ($workflowText -match '\$ask-light next' -and $workflowText -match '\$ask-light workflow') 'ask-light must document both explicit modes.'
Assert-Collection ($workflowText -match 'entryCondition' -and $workflowText -match 'missing dependency' -and $workflowText -match 'finalAuthority') 'ask-light workflow output contract is incomplete.'
Assert-Collection ($workflowScript -match "ValidateSet\('next', 'workflow'\)" -and $workflowScript -match 'Get-WorkflowRecipes') 'ask-light scanner lacks explicit workflow mode implementation.'
Assert-Collection ((Get-Content -LiteralPath (Join-Path $Root 'skills/learn-anything/agents/openai.yaml') -Raw) -match 'allow_implicit_invocation:\s*false') 'learn-anything must declare explicit-only metadata policy.'

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
