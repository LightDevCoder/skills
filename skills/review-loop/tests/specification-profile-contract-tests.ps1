[CmdletBinding()]
param(
    [string]$SkillRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($SkillRoot)) {
    $scriptDirectory = if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
    $SkillRoot = Split-Path -Parent $scriptDirectory
}
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path

$failures = [System.Collections.Generic.List[string]]::new()

function Require-File {
    param([string]$Label, [string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { $script:failures.Add("$($Label): missing file $Path") }
}

function Require-Match {
    param([string]$Label, [string]$Text, [string]$Pattern)
    $normalized = $Text -replace "`r`n", "`n"
    if ($normalized -notmatch $Pattern) { $script:failures.Add("$($Label): expected /$Pattern/") }
}

function Require-NoMatch {
    param([string]$Label, [string]$Text, [string]$Pattern)
    $normalized = $Text -replace "`r`n", "`n"
    if ($normalized -match $Pattern) { $script:failures.Add("$($Label): must not contain /$Pattern/") }
}

$skillPath = Join-Path $SkillRoot 'SKILL.md'
$metadataPath = Join-Path $SkillRoot 'agents/openai.yaml'
$profilePath = Join-Path $SkillRoot 'references/profiles/specification.md'
$behaviorPath = Join-Path $SkillRoot 'tests/specification-profile-behavior-tests.ps1'
$genericPath = Join-Path $SkillRoot 'references/profiles/generic.md'
$findingPath = Join-Path $SkillRoot 'references/finding-schema.md'
$evidencePath = Join-Path $SkillRoot 'references/evidence-protocol.md'
$stoppingPath = Join-Path $SkillRoot 'references/stopping-rules.md'
$rolesPath = Join-Path $SkillRoot 'references/subagent-protocol.md'

@(
    @{ Label = 'Skill'; Path = $skillPath }
    @{ Label = 'Agent metadata'; Path = $metadataPath }
    @{ Label = 'Specification Profile'; Path = $profilePath }
    @{ Label = 'Specification behavior tests'; Path = $behaviorPath }
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
    $behavior = Get-Content -Raw -LiteralPath $behaviorPath
    $generic = Get-Content -Raw -LiteralPath $genericPath
    $finding = Get-Content -Raw -LiteralPath $findingPath
    $evidence = Get-Content -Raw -LiteralPath $evidencePath
    $stopping = Get-Content -Raw -LiteralPath $stoppingPath
    $roles = Get-Content -Raw -LiteralPath $rolesPath

    # TC-SP-001: the narrow Profile is discoverable and generic remains empty.
    Require-Match 'TC-SP-001 profile link' $skill '(?im)\[specification\.md\]\(references/profiles/specification\.md\)'
    Require-Match 'TC-SP-001 profile heading' $profile '(?im)^# Specification Profile$'
    Require-Match 'TC-SP-001 implicit invocation' $metadata '(?im)^\s*allow_implicit_invocation:\s*true\s*$'
    Require-Match 'TC-SP-001 generic preserved' $generic '(?im)^# Generic Profile$'
    Require-NoMatch 'TC-SP-001 generic remains empty' $generic '(?i)specification|traceability|ambiguity|contradiction'

    # TC-SP-002: every specification-specific axis is present.
    Require-Match 'TC-SP-002 review axes' $profile '(?im)^## Review axes$'
    foreach ($axis in @(
        'Authority and baseline', 'Scope and target', 'Criteria and acceptance',
        'Terminology and ambiguity', 'Contradiction and decision',
        'Testability and evidence', 'Version, change, and hand-off'
    )) {
        Require-Match "TC-SP-002 axis $axis" $profile "(?i)\*\*$axis"
    }
    Require-Match 'TC-SP-002 severity guidance' $profile '(?im)^## Severity guidance$'
    Require-Match 'TC-SP-002 acceptance conditions' $profile '(?im)^## Acceptance conditions$'
    Require-Match 'TC-SP-002 failure cases' $profile '(?im)^## Artifact-specific failure cases$'
    Require-Match 'TC-SP-002 severity values' $profile '(?is)\*\*Critical\*\*.*\*\*High\*\*.*\*\*Medium\*\*.*\*\*Low\*\*'

    # TC-SP-003: authority, traceability, ambiguity, contradiction, and evidence seams.
    Require-Match 'TC-SP-003 authority evidence' $profile '(?i)immutable authoritative source|approval state|source precedence'
    Require-Match 'TC-SP-003 traceability evidence' $profile '(?i)scope.*exclusion.*map|acceptance matrix|stable criterion|source link'
    Require-Match 'TC-SP-003 ambiguity boundary' $profile '(?i)ambiguity|undefined terms|multiple materially different interpretations'
    Require-Match 'TC-SP-003 contradiction boundary' $profile '(?i)contradiction|competing authorities|precedence decision'
    Require-Match 'TC-SP-003 source and criteria evidence' $profile '(?i)Evidence Protocol|success.*boundary.*failure|missing-source'
    Require-Match 'TC-SP-003 valid labels retained' $evidence '(?is)source.*structural.*behavioral.*runtime.*manual.*review'
    Require-NoMatch 'TC-SP-003 unsupported primary labels absent' $profile '(?im)(?:Evidence label|Label):\s*(?:render|visual)\b'
    Require-NoMatch 'TC-SP-003 behavior runner unsupported labels absent' $behavior '(?im)(?:Evidence label|Label):\s*(?:render|visual)\b'

    # TC-SP-004: specialists are read-only and hand off to the generic Core.
    Require-Match 'TC-SP-004 specialist boundary' $profile '(?is)read-only.*candidate findings|never edit.*never issue|Specialist.*never edits'
    Require-Match 'TC-SP-004 generic schema' $profile '(?i)generic finding schema|stable.*finding.*ID'
    Require-Match 'TC-SP-004 Core verdict ownership' $profile '(?is)generic Core.*final.*verdict|Core.*owns.*final.*`PASS`.*`FAIL`.*`BLOCKED`'
    Require-Match 'TC-SP-004 dispositions' $profile '(?is)`confirmed`.*`rejected`.*`duplicate`.*`out-of-scope`'

    # TC-SP-005: no second state machine or generic stop rule was introduced.
    Require-Match 'TC-SP-005 lifecycle delegation' $profile '(?is)does not replace.*finding.*repair.*state.*independence.*verdict'
    Require-NoMatch 'TC-SP-005 no duplicate state section' $profile '(?im)^## (State|Repair rounds|Finding Registry|Stopping Rules)$'
    Require-NoMatch 'TC-SP-005 no duplicate transitions' $profile '(?i)INIT\s*->\s*READY|READY\s*->\s*CRITIC'
    Require-Match 'TC-SP-005 canonical finding schema unchanged' $finding '(?im)^# Finding Registry$'
    Require-Match 'TC-SP-005 canonical stop outcomes unchanged' $stopping '(?i)`PASS`.*`FAIL`.*`BLOCKED`'
    Require-Match 'TC-SP-005 read-only roles' $roles '(?i)Critic.*read-only|Evaluator.*read-only'
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output 'SPECIFICATION_PROFILE_CONTRACT_TESTS=PASS'
Write-Output 'Evidence class: structural contract test (not host-runtime proof).'
