param([string]$SkillRoot = '')

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($SkillRoot)) { $SkillRoot = Split-Path -Parent $PSScriptRoot }
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path
$script:failures = [System.Collections.Generic.List[string]]::new()
function Assert-True { param([bool]$Condition, [string]$Name); if (-not $Condition) { $script:failures.Add($Name) } }

function Select-InstructionTarget {
    param([string]$Root)
    $agents = Join-Path $Root 'AGENTS.md'; $claude = Join-Path $Root 'CLAUDE.md'
    if (Test-Path -LiteralPath $agents) { return $agents }
    if (Test-Path -LiteralPath $claude) { return $claude }
    return $agents
}
function Merge-InitializationSection {
    param([string]$Existing, [string]$Block)
    if ($Existing -match '(?ms)^## Project Initialization\s*$') {
        $parts = [regex]::Split($Existing, '(?ms)^## Project Initialization\s*$', 2)
        $tail = [regex]::Match($parts[1], '(?ms)\r?\n## (?!#)').Index
        if ($tail -gt 0) { $suffix = $parts[1].Substring($tail).TrimStart() } else { $suffix = '' }
        return (($parts[0].TrimEnd() + "`r`n`r`n" + $Block.Trim() + $(if ($suffix) { "`r`n`r`n$suffix" } else { '' })).Trim() + "`r`n")
    }
    return (($Existing.TrimEnd() + "`r`n`r`n" + $Block.Trim()).Trim() + "`r`n")
}

$skill = Get-Content -Raw -LiteralPath (Join-Path $SkillRoot 'SKILL.md')
$presets = Get-Content -Raw -LiteralPath (Join-Path $SkillRoot 'references/presets.md')
$contract = Get-Content -Raw -LiteralPath (Join-Path $SkillRoot 'references/initialization-contract.md')

foreach ($preset in @('generic','software','manuscript','skill-development','research','knowledge-base','data-analysis')) {
    Assert-True ($presets -match "(?m)^\| $([regex]::Escape($preset)) \|.+\|.+\|") "preset plan is selectable: $preset"
}
Assert-True ($skill -match 'one short question at a time' -and $skill -match 'six answers') 'grilling stays lightweight'

$fixture = Join-Path ([IO.Path]::GetTempPath()) ('project-init-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $fixture | Out-Null
try {
    $agents = Join-Path $fixture 'AGENTS.md'; $claude = Join-Path $fixture 'CLAUDE.md'
    Set-Content -LiteralPath $agents -Value "# Existing rules`r`n`r`nKeep this line."
    Set-Content -LiteralPath $claude -Value '# Do not replace this file.'
    Assert-True ((Select-InstructionTarget $fixture) -eq $agents) 'existing AGENTS.md is preferred without duplicate'
    Assert-True ($skill -match 'When existing instruction files disagree' -and $contract -match 'If `AGENTS.md` and `CLAUDE.md` conflict') 'conflicting instructions are preserved and reported'
    $merged = Merge-InitializationSection -Existing (Get-Content -Raw -LiteralPath $agents) -Block "## Project Initialization`r`n`r`n- Type: software`r`n- Goal: test"
    Set-Content -LiteralPath $agents -Value $merged
    Assert-True ((Get-Content -Raw -LiteralPath $agents) -match 'Keep this line\.' -and (Get-Content -Raw -LiteralPath $claude) -match 'Do not replace') 'existing instructions are preserved'
    $again = Merge-InitializationSection -Existing (Get-Content -Raw -LiteralPath $agents) -Block "## Project Initialization`r`n`r`n- Type: software`r`n- Goal: test"
    Assert-True (([regex]::Matches($again, '(?m)^## Project Initialization\s*$')).Count -eq 1) 'rerun keeps one initialization section'
    Remove-Item -LiteralPath $agents
    Assert-True ((Select-InstructionTarget $fixture) -eq $claude) 'CLAUDE.md is used when AGENTS.md is absent'
    Remove-Item -LiteralPath $claude
    Assert-True ((Select-InstructionTarget $fixture) -eq $agents) 'new AGENTS.md is default when neither exists'
} finally { Remove-Item -LiteralPath $fixture -Recurse -Force }

Assert-True ($skill -match 'If no preset matches' -and $skill -match 'only after `confirm` may the fallback plan write') 'research fallback requires confirmation'
Assert-True ($skill -match 'on `reject`, write nothing' -and $contract -match 'empty write set') 'research rejection has no write set'
Assert-True ($skill -match 'requested modification' -and $skill -match 'confirmation again') 'research modification re-enters confirmation'
foreach ($marker in @('inside the requested project root','exactly one instruction target','existing instruction text remains present','declared capability','forbidden workflow')) {
    Assert-True ($skill -match [regex]::Escape($marker)) "validation covers $marker"
}
foreach ($forbidden in @('to-spec','to-tickets','implement','final review','review-loop','ask-light','learn-anything')) {
    Assert-True ($skill -match [regex]::Escape($forbidden)) "boundary names $forbidden"
}
Assert-True ($skill -match 'must not invoke another user-invoked Skill' -or $skill -match 'never invoke') 'initializer does not invoke user Skills'

if ($script:failures.Count -gt 0) { throw "project-init behavior failed: $($script:failures -join '; ')" }
Write-Output 'PASS — project-init behavior (presets, instruction merge, fallback gate, validation, boundaries)'
