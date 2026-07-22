param([string]$SkillRoot = '')

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($SkillRoot)) { $SkillRoot = Split-Path -Parent $PSScriptRoot }
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path
$script:failures = [System.Collections.Generic.List[string]]::new()
function Assert-True { param([bool]$Condition, [string]$Name); if (-not $Condition) { $script:failures.Add($Name) } }

$skillPath = Join-Path $SkillRoot 'SKILL.md'
$metadataPath = Join-Path $SkillRoot 'agents/openai.yaml'
$referencePath = Join-Path $SkillRoot 'references/discovery-contract.md'
$scriptPath = Join-Path $SkillRoot 'scripts/ask-light.ps1'
foreach ($path in @($skillPath, $metadataPath, $referencePath, $scriptPath)) {
    Assert-True (Test-Path -LiteralPath $path -PathType Leaf) "required path exists: $path"
}
$skill = Get-Content -Raw -LiteralPath $skillPath
$metadata = Get-Content -Raw -LiteralPath $metadataPath
$reference = Get-Content -Raw -LiteralPath $referencePath
$script = Get-Content -Raw -LiteralPath $scriptPath

Assert-True ($skill -match '(?ms)^---\s*\r?\nname: ask-light\s*\r?\ndescription: .+?\r?\n---') 'frontmatter has name and description only'
Assert-True ($metadata -match 'allow_implicit_invocation:\s*false') 'Skill is explicit-only'
foreach ($category in @('project','global','first-party','upstream','modified-third-party','other')) {
    Assert-True (($skill + $reference) -match [regex]::Escape($category)) "source category supported: $category"
}
foreach ($field in @('goal','artifacts','blockers','projectType','taskKind','availability','invocationControl')) {
    Assert-True (($reference + $skill) -match [regex]::Escape($field)) "context field supported: $field"
}
foreach ($marker in @('metadata first','frontmatter','agents/openai.yaml','shortlist','duplicate','unreadable','Alternative','NEED-INPUT','BLOCKED','installation','never execute','never.*install','body/reference','availability','hosts','readStatus','metadataStatus: unavailable','metadataReadable','materially different next actions','equivalent')) {
    Assert-True (($skill + $reference) -match $marker) "contract marker: $marker"
}
Assert-True ($skill -notmatch 'TODO|\[TODO') 'no template placeholders remain'
Assert-True ($script -notmatch '(?i)Start-Process|Invoke-Expression|Invoke-RestMethod|Install-Module') 'scanner has no execution or installation primitive'
Assert-True ($script -match 'Get-Content -Raw.*SKILL.md' -and $script -match 'ShortlistLimit') 'scanner reads bodies after shortlist only'
Assert-True ($script -match 'ConvertTo-Json') 'scanner returns a structured result'
Assert-True ($script -match 'Test-CandidateAvailability' -and $script -match 'Get-ActionFingerprint' -and $script -match 'readableShortlist') 'scanner filters availability, distinguishes actions, and rejects unreadable reads'

if ($script:failures.Count -gt 0) { throw "ask-light contract failed: $($script:failures -join '; ')" }
Write-Output 'PASS - ask-light contract'
