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
$profilePath = Join-Path $SkillRoot 'references/profiles/agent-skill.md'
$behaviorPath = Join-Path $SkillRoot 'tests/agent-skill-profile-behavior-tests.ps1'
$genericPath = Join-Path $SkillRoot 'references/profiles/generic.md'
$findingPath = Join-Path $SkillRoot 'references/finding-schema.md'
$evidencePath = Join-Path $SkillRoot 'references/evidence-protocol.md'
$stoppingPath = Join-Path $SkillRoot 'references/stopping-rules.md'
$rolesPath = Join-Path $SkillRoot 'references/subagent-protocol.md'

@(
    @{ Label = 'Skill'; Path = $skillPath }
    @{ Label = 'Agent metadata'; Path = $metadataPath }
    @{ Label = 'Agent-Skill Profile'; Path = $profilePath }
    @{ Label = 'Agent-Skill behavior tests'; Path = $behaviorPath }
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

    # TC-AS-001: Profile is discoverable while generic remains the empty fallback.
    Require-Match 'TC-AS-001 profile link' $skill '(?im)\[agent-skill\.md\]\(references/profiles/agent-skill\.md\)'
    Require-Match 'TC-AS-001 profile heading' $profile '(?im)^# Agent-Skill Profile$'
    Require-Match 'TC-AS-001 implicit invocation' $metadata '(?im)^\s*allow_implicit_invocation:\s*true\s*$'
    Require-Match 'TC-AS-001 generic preserved' $generic '(?im)^# Generic Profile$'
    Require-NoMatch 'TC-AS-001 generic remains empty' $generic '(?i)agent-skill|installation|invocation|composition'

    # TC-AS-002: all package acceptance axes are present.
    Require-Match 'TC-AS-002 review axes' $profile '(?im)^## Review axes$'
    foreach ($axis in @('Package structure', 'Installation', 'Invocation', 'Reusable behavior', 'Interaction', 'Executable artifact')) {
        Require-Match "TC-AS-002 axis $axis" $profile "(?i)\*\*$axis"
    }
    Require-Match 'TC-AS-002 severity guidance' $profile '(?im)^## Severity guidance$'
    Require-Match 'TC-AS-002 acceptance conditions' $profile '(?im)^## Acceptance conditions$'
    Require-Match 'TC-AS-002 failure cases' $profile '(?im)^## Artifact-specific failure cases$'
    Require-Match 'TC-AS-002 severity values' $profile '(?is)\*\*Critical\*\*.*\*\*High\*\*.*\*\*Medium\*\*.*\*\*Low\*\*'

    # TC-AS-003: required evidence scenarios use only generic protocol labels.
    Require-Match 'TC-AS-003 evidence requirements' $profile '(?im)^## Evidence requirements$'
    foreach ($term in @('structural', 'fresh-install|clean-copy installation', 'discovery', 'success', 'boundary', 'failure', 'missing-dependency', 'invocation', 'interaction', 'assertion-bearing', 'negative|adversarial', 'code-review', 'fresh independent Evaluator')) {
        Require-Match "TC-AS-003 evidence $term" $profile "(?i)$term"
    }
    Require-Match 'TC-AS-003 protocol labels retained' $evidence '(?is)source.*structural.*behavioral.*installation.*invocation.*review'
    Require-NoMatch 'TC-AS-003 unsupported primary labels absent' $profile '(?im)(?:Evidence label|Label):\s*(?:render|visual)\b'
    Require-NoMatch 'TC-AS-003 behavior runner unsupported labels absent' $behavior '(?im)(?:Evidence label|Label):\s*(?:render|visual)\b'

    # TC-AS-004: executable scripts remain under the software specialist boundary.
    Require-Match 'TC-AS-004 focused tests' $profile '(?i)focused automated tests'
    Require-Match 'TC-AS-004 negative tests' $profile '(?i)negative or adversarial'
    Require-Match 'TC-AS-004 code review reports' $profile '(?is)code-review.*Standards.*Spec'
    Require-Match 'TC-AS-004 specialist read-only' $profile '(?is)read-only.*never edits|never edits.*never issues'
    Require-Match 'TC-AS-004 specialist evidence class' $profile '(?i)`review` evidence'

    # TC-AS-005: generic finding lifecycle, state, repair and verdict stay in Core.
    Require-Match 'TC-AS-005 generic schema handoff' $profile '(?i)generic finding schema|finding identity'
    Require-Match 'TC-AS-005 generic dispositions' $profile '(?is)confirmed.*rejected.*duplicate.*out-of-scope'
    Require-Match 'TC-AS-005 Core verdict ownership' $profile '(?is)generic Core.*final verdict|Core.*owns.*final.*`PASS`.*`FAIL`.*`BLOCKED`'
    Require-Match 'TC-AS-005 Core lifecycle delegation' $profile '(?is)does not replace.*finding.*repair.*state.*independence.*final verdict'
    Require-NoMatch 'TC-AS-005 no duplicate state section' $profile '(?im)^## (State|Repair rounds|Finding Registry|Stopping Rules)$'
    Require-NoMatch 'TC-AS-005 no duplicate lifecycle transitions' $profile '(?i)INIT\s*->\s*READY|READY\s*->\s*CRITIC'
    Require-Match 'TC-AS-005 canonical finding schema unchanged' $finding '(?im)^# Finding Registry$'
    Require-Match 'TC-AS-005 canonical stop outcomes unchanged' $stopping '(?i)`PASS`.*`FAIL`.*`BLOCKED`'
    Require-Match 'TC-AS-005 read-only role boundary' $roles '(?i)Critic.*read-only|Evaluator.*read-only'
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output 'AGENT_SKILL_PROFILE_CONTRACT_TESTS=PASS'
Write-Output 'Evidence class: structural contract test (not host-runtime proof).'
