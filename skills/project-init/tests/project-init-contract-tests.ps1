param([string]$SkillRoot = '')

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($SkillRoot)) { $SkillRoot = Split-Path -Parent $PSScriptRoot }
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path
$script:failures = [System.Collections.Generic.List[string]]::new()
function Assert-True { param([bool]$Condition, [string]$Name); if (-not $Condition) { $script:failures.Add($Name) } }

$skillPath = Join-Path $SkillRoot 'SKILL.md'
$metadataPath = Join-Path $SkillRoot 'agents/openai.yaml'
$presetPath = Join-Path $SkillRoot 'references/presets.md'
$contractPath = Join-Path $SkillRoot 'references/initialization-contract.md'
foreach ($path in @($skillPath,$metadataPath,$presetPath,$contractPath)) { Assert-True (Test-Path -LiteralPath $path) "required path exists: $path" }
$skill = Get-Content -Raw -LiteralPath $skillPath
$metadata = Get-Content -Raw -LiteralPath $metadataPath
$presets = Get-Content -Raw -LiteralPath $presetPath
$contract = Get-Content -Raw -LiteralPath $contractPath

Assert-True ($skill -match '(?ms)^---\s*\r?\nname: project-init\s*\r?\ndescription: .+?\r?\n---') 'frontmatter has name and description only'
Assert-True ($metadata -match 'allow_implicit_invocation:\s*false') 'Skill is explicit-only'
foreach ($preset in @('generic','software','manuscript','skill-development','research','knowledge-base','data-analysis')) {
    Assert-True ($presets -match "\| $([regex]::Escape($preset)) \|") "preset supported: $preset"
}
foreach ($marker in @('project type','user-visible goal','expected outputs','collaboration mode','important constraints','required review level')) {
    Assert-True ($skill -match [regex]::Escape($marker)) "lightweight question captured: $marker"
}
foreach ($marker in @('existing `AGENTS.md`','existing `CLAUDE.md`','research','confirm','reject','created path','declared capability','Project Initialization')) {
    Assert-True (($skill + $contract) -match [regex]::Escape($marker)) "initialization contract marker: $marker"
}
foreach ($forbidden in @('to-spec','to-tickets','implement','final review','another user-invoked Skill')) {
    Assert-True ($skill -match [regex]::Escape($forbidden)) "boundary names forbidden operation: $forbidden"
}
Assert-True ($skill -match 'does not run' -and ($skill -match 'never invoke' -or $skill -match 'must not invoke')) 'boundaries prohibit execution'
Assert-True ($skill -notmatch 'TODO|\[TODO') 'no template placeholders remain'

if ($script:failures.Count -gt 0) { throw "project-init contract failed: $($script:failures -join '; ')" }
Write-Output 'PASS — project-init contract'
