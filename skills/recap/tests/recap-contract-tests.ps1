param([string]$SkillRoot = '')

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($SkillRoot)) { $SkillRoot = Split-Path -Parent $PSScriptRoot }
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path
$script:failures = [System.Collections.Generic.List[string]]::new()
$script:assertions = 0

function Assert-RecapContract {
    param([bool]$Condition, [string]$Name)
    $script:assertions++
    if (-not $Condition) { $script:failures.Add($Name) }
}

function Test-RecapSafetyContract {
    param([string]$Text)
    $forbidsCompaction = $Text -match '(?is)(do not|does not|never)[^\r\n]{0,120}compact'
    $forbidsImplicitHandoff = $Text -match '(?is)`recap` never invokes either capability'
    return $forbidsCompaction -and $forbidsImplicitHandoff
}

$skill = Get-Content -LiteralPath (Join-Path $SkillRoot 'SKILL.md') -Raw
$metadata = Get-Content -LiteralPath (Join-Path $SkillRoot 'agents/openai.yaml') -Raw

Assert-RecapContract ($skill -match '(?m)^name:\s*recap\s*$') 'frontmatter name is recap'
Assert-RecapContract ($skill -match '(?m)^disable-model-invocation:\s*true\s*$') 'Claude metadata disables model invocation'
Assert-RecapContract ($skill -match 'explicit `\$recap`|explicit \$recap') 'contract requires explicit invocation'
Assert-RecapContract ($skill -match 'exactly one non-empty line') 'contract requires one non-empty line'
Assert-RecapContract ($skill -match 'Do not call tools') 'contract forbids tool calls'
Assert-RecapContract (Test-RecapSafetyContract $skill) 'contract forbids compaction and implicit handoffs'
$unsafeMutation = $skill.Replace('`recap` never invokes either capability', '`recap` invokes either capability automatically')
Assert-RecapContract (-not (Test-RecapSafetyContract $unsafeMutation)) 'opposite-polarity handoff mutation is rejected'
Assert-RecapContract ($skill -match '`review-loop`') 'contract preserves explicit final-review handoff'
Assert-RecapContract ($metadata -match 'display_name:\s*"Session Recap"') 'metadata has display name'
Assert-RecapContract ($metadata -match 'short_description:\s*"[^"]{25,64}"') 'metadata has bounded short description'
Assert-RecapContract ($metadata -match 'default_prompt:\s*"Use \$recap') 'metadata default prompt invokes recap explicitly'
Assert-RecapContract ($metadata -match 'allow_implicit_invocation:\s*false') 'Codex metadata disables implicit invocation'

if ($script:assertions -eq 0) {
    throw 'RECAP_CONTRACT=FAIL (zero assertions)'
}

if ($script:failures.Count -gt 0) {
    $script:failures | ForEach-Object { "FAIL: $_" }
    throw "RECAP_CONTRACT=FAIL ($($script:failures.Count) failures, $script:assertions assertions)"
}

"RECAP_CONTRACT_ASSERTIONS=$script:assertions"
"RECAP_CONTRACT=PASS"
