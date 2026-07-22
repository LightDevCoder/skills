[CmdletBinding()]
param(
    [string]$SkillRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($SkillRoot)) {
    $scriptDirectory = if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        $PSScriptRoot
    }
    else {
        Split-Path -Parent $MyInvocation.MyCommand.Path
    }
    $SkillRoot = Split-Path -Parent $scriptDirectory
}
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path

$failures = [System.Collections.Generic.List[string]]::new()

function Require-File {
    param([string]$Label, [string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        $script:failures.Add("$($Label): missing file $Path")
    }
}

function Require-Match {
    param([string]$Label, [string]$Text, [string]$Pattern)
    $normalized = $Text -replace "`r`n", "`n"
    if ($normalized -notmatch $Pattern) {
        $script:failures.Add("$($Label): expected /$Pattern/")
    }
}

function Require-NoMatch {
    param([string]$Label, [string]$Text, [string]$Pattern)
    $normalized = $Text -replace "`r`n", "`n"
    if ($normalized -match $Pattern) {
        $script:failures.Add("$($Label): must not contain /$Pattern/")
    }
}

$skillPath = Join-Path $SkillRoot 'SKILL.md'
$metadataPath = Join-Path $SkillRoot 'agents/openai.yaml'
$profilePath = Join-Path $SkillRoot 'references/profiles/software.md'
$genericPath = Join-Path $SkillRoot 'references/profiles/generic.md'
$findingPath = Join-Path $SkillRoot 'references/finding-schema.md'
$evidencePath = Join-Path $SkillRoot 'references/evidence-protocol.md'
$stoppingPath = Join-Path $SkillRoot 'references/stopping-rules.md'
$rolesPath = Join-Path $SkillRoot 'references/subagent-protocol.md'

@(
    @{ Label = 'Skill'; Path = $skillPath }
    @{ Label = 'Agent metadata'; Path = $metadataPath }
    @{ Label = 'Software Profile'; Path = $profilePath }
    @{ Label = 'Generic Profile'; Path = $genericPath }
    @{ Label = 'Finding Schema'; Path = $findingPath }
    @{ Label = 'Evidence Protocol'; Path = $evidencePath }
    @{ Label = 'Stopping Rules'; Path = $stoppingPath }
    @{ Label = 'Role Protocol'; Path = $rolesPath }
) | ForEach-Object { Require-File $_.Label $_.Path }

if ($failures.Count -eq 0) {
    $skill = Get-Content -Raw -LiteralPath $skillPath
    $metadata = Get-Content -Raw -LiteralPath $metadataPath
    $profile = Get-Content -Raw -LiteralPath $profilePath
    $generic = Get-Content -Raw -LiteralPath $genericPath
    $finding = Get-Content -Raw -LiteralPath $findingPath
    $evidence = Get-Content -Raw -LiteralPath $evidencePath
    $stopping = Get-Content -Raw -LiteralPath $stoppingPath
    $roles = Get-Content -Raw -LiteralPath $rolesPath

    # TC-SW-001: software Profile is discoverable without weakening generic.
    Require-Match 'TC-SW-001 profile link' $skill '(?im)\[software\.md\]\(references/profiles/software\.md\)'
    Require-Match 'TC-SW-001 profile heading' $profile '(?im)^# Software Profile$'
    Require-Match 'TC-SW-001 implicit invocation' $metadata '(?im)^\s*allow_implicit_invocation:\s*true\s*$'
    Require-Match 'TC-SW-001 generic preserved' $generic '(?im)^# Generic Profile$'
    Require-NoMatch 'TC-SW-001 generic remains empty' $generic '(?i)code-review|Standards findings|Spec findings'

    # TC-SW-002: all required software-specific Profile dimensions exist.
    Require-Match 'TC-SW-002 review axes' $profile '(?im)^## Review axes$'
    Require-Match 'TC-SW-002 evidence requirements' $profile '(?im)^## Evidence requirements$'
    Require-Match 'TC-SW-002 specialist reviewer' $profile '(?im)^## Specialist reviewer: `code-review`$'
    Require-Match 'TC-SW-002 severity guidance' $profile '(?im)^## Severity guidance$'
    Require-Match 'TC-SW-002 acceptance conditions' $profile '(?im)^## Acceptance conditions$'
    Require-Match 'TC-SW-002 failure cases' $profile '(?im)^## Artifact-specific failure cases$'
    Require-Match 'TC-SW-002 standards axis' $profile '(?is)\*\*Standards\*\*.*code-review'
    Require-Match 'TC-SW-002 spec axis' $profile '(?is)\*\*Spec fidelity\*\*.*code-review'
    Require-Match 'TC-SW-002 behavioral axis' $profile '(?i)\*\*Behavioral correctness\*\*'
    Require-Match 'TC-SW-002 safety axis' $profile '(?i)\*\*Operational safety\*\*'
    Require-Match 'TC-SW-002 severity values' $profile '(?is)\*\*Critical\*\*.*\*\*High\*\*.*\*\*Medium\*\*.*\*\*Low\*\*'

    # TC-SW-003: specialist outputs enter the generic lifecycle as candidates.
    Require-Match 'TC-SW-003 specialist evidence' $profile '(?i)code-review.*findings.*review.*evidence'
    Require-Match 'TC-SW-003 generic schema' $profile '(?i)generic finding schema|Finding Schema'
    Require-Match 'TC-SW-003 stable IDs' $profile '(?i)stable.*F-###|stable.*Finding ID'
    Require-Match 'TC-SW-003 dispositions' $profile '(?is)confirmed.*rejected.*duplicate.*out-of-scope'
    Require-Match 'TC-SW-003 evidence class' $evidence '(?i)`review`'
    Require-Match 'TC-SW-003 core flow' $skill '(?is)code-review.*Standards.*Spec.*findings.*generic lifecycle'

    # TC-SW-004: code-review cannot issue the Program verdict.
    Require-Match 'TC-SW-004 specialist boundary' $profile '(?is)code-review.*never.*Program.*acceptance verdict'
    Require-Match 'TC-SW-004 Core ownership' $profile '(?is)final `PASS`, `FAIL`, or `BLOCKED`.*review-loop\s+Core'
    Require-Match 'TC-SW-004 Core ownership in Skill' $skill '(?is)code-review.*never issues.*final.*review-loop Core owns'
    Require-Match 'TC-SW-004 generic verdicts preserved' $stopping '(?i)`PASS`.*`FAIL`.*`BLOCKED`'
    Require-Match 'TC-SW-004 read-only specialist boundary' $roles '(?i)Critic.*read-only|Evaluator.*read-only'

    # TC-SW-005: only confirmed, bounded, in-scope findings may be repaired.
    Require-Match 'TC-SW-005 bounded repair' $profile '(?is)confirmed.*blocking finding.*resolved|bounded repair'
    Require-Match 'TC-SW-005 scope stop' $profile '(?i)scope|architecture.*decision|multiple new implementation tickets'
    Require-Match 'TC-SW-005 generic stop' $skill '(?i)Stop scope expansion'
    Require-Match 'TC-SW-005 no lifecycle duplication' $profile '(?i)does not replace.*state machine|generic lifecycle.*stopping rules'
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output 'SOFTWARE_PROFILE_CONTRACT_TESTS=PASS'
Write-Output 'Evidence class: structural contract test (not host-runtime proof).'
