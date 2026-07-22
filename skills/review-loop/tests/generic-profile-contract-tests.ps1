[CmdletBinding()]
param(
    [string]$SkillRoot
)

if ([string]::IsNullOrWhiteSpace($SkillRoot)) {
    $scriptDirectory = if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        $PSScriptRoot
    }
    else {
        Split-Path -Parent $MyInvocation.MyCommand.Path
    }
    $SkillRoot = Split-Path -Parent $scriptDirectory
}

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

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
$profilePath = Join-Path $SkillRoot 'references/profiles/generic.md'
$charterPath = Join-Path $SkillRoot 'references/acceptance-charter.md'
$evidencePath = Join-Path $SkillRoot 'references/evidence-protocol.md'
$findingPath = Join-Path $SkillRoot 'references/finding-schema.md'
$stoppingPath = Join-Path $SkillRoot 'references/stopping-rules.md'
$rolesPath = Join-Path $SkillRoot 'references/subagent-protocol.md'

@(
    @{ Label = 'Agent metadata'; Path = $metadataPath }
    @{ Label = 'Generic Profile'; Path = $profilePath }
    @{ Label = 'Acceptance Charter'; Path = $charterPath }
    @{ Label = 'Evidence Protocol'; Path = $evidencePath }
    @{ Label = 'Finding Schema'; Path = $findingPath }
    @{ Label = 'Stopping Rules'; Path = $stoppingPath }
    @{ Label = 'Role Protocol'; Path = $rolesPath }
) | ForEach-Object { Require-File $_.Label $_.Path }

if ($failures.Count -eq 0) {
    $skill = Get-Content -Raw -LiteralPath $skillPath
    $metadata = Get-Content -Raw -LiteralPath $metadataPath
    $profile = Get-Content -Raw -LiteralPath $profilePath
    $charter = Get-Content -Raw -LiteralPath $charterPath
    $evidence = Get-Content -Raw -LiteralPath $evidencePath
    $findings = Get-Content -Raw -LiteralPath $findingPath
    $stopping = Get-Content -Raw -LiteralPath $stoppingPath
    $roles = Get-Content -Raw -LiteralPath $rolesPath

    # TC-GEN-001: generic Profile has no domain-specific rules.
    Require-Match 'TC-GEN-001 generic profile' $skill 'references/profiles/generic\.md'
    Require-Match 'TC-GEN-001 generic profile' $profile '(?im)^# Generic Profile$'
    Require-NoMatch 'TC-GEN-001 generic profile' $profile '(?i)software|manuscript|agent-skill|specification|code-review'

    # TC-GEN-002: the public protocol exposes init, review, and resume, with a model-invoked/manual boundary.
    Require-Match 'TC-GEN-002 public modes' $skill '(?im)^- `init`:'
    Require-Match 'TC-GEN-002 public modes' $skill '(?im)^- `review`:'
    Require-Match 'TC-GEN-002 public modes' $skill '(?im)^- `resume`:'
    Require-Match 'TC-GEN-002 invocation' $skill '(?i)model-invoked'
    Require-Match 'TC-GEN-002 invocation' $skill '(?i)manually invoked'
    Require-Match 'TC-GEN-002 invocation metadata' $metadata '(?im)^\s*allow_implicit_invocation:\s*true\s*$'

    # TC-GEN-003: a frozen acceptance source and resolved Profile are durable state.
    Require-Match 'TC-GEN-003 baseline' $charter '(?im)^## Acceptance baseline$'
    Require-Match 'TC-GEN-003 profile' $charter '(?im)^## Review Profile$'
    Require-Match 'TC-GEN-003 state records' $skill '(?m)^\|-- findings\.md$'

    # TC-GEN-004: the same finding keeps its canonical ID across rounds.
    Require-Match 'TC-GEN-004 stable finding identity' $findings '(?i)stable.*Finding ID|Finding ID.*stable'
    Require-Match 'TC-GEN-004 stable finding identity' $findings '(?i)must not be reused'
    Require-Match 'TC-GEN-004 finding registry' $findings '(?im)^# Finding Registry$'

    # TC-GEN-005: an unsubstantiated candidate is rejected with retained evidence.
    Require-Match 'TC-GEN-005 rejected findings' $findings '`rejected`'
    Require-Match 'TC-GEN-005 rejected findings' $findings '(?i)Resolution evidence'

    # TC-GEN-006: only a confirmed, in-scope, bounded repair goes to the Producer.
    Require-Match 'TC-GEN-006 bounded repair' $skill '(?i)confirmed.*in-scope.*bounded|in-scope.*confirmed.*bounded'
    Require-Match 'TC-GEN-006 Producer ownership' $roles '(?is)Producer.*only.*modif'
    Require-Match 'TC-GEN-006 read-only reviewers' $roles '(?i)Critic.*read-only'
    Require-Match 'TC-GEN-006 read-only reviewers' $roles '(?i)Evaluator.*read-only'

    # TC-GEN-007: an absent acceptance source blocks review rather than inventing one.
    Require-Match 'TC-GEN-007 missing acceptance source' $skill '(?i)missing acceptance source.*BLOCKED|BLOCKED.*missing acceptance source'

    # TC-GEN-008: unavailable independent context blocks a required independent review.
    Require-Match 'TC-GEN-008 missing independent context' $roles '(?i)independence: unavailable'
    Require-Match 'TC-GEN-008 missing independent context' $roles '(?i)return `BLOCKED`'

    # TC-GEN-009: configured repair limits terminate rather than cycling indefinitely.
    Require-Match 'TC-GEN-009 maximum rounds' $stopping '(?i)maximum round.*BLOCKED|BLOCKED.*maximum round'

    # TC-GEN-010: all three final verdicts are part of the public state contract.
    Require-Match 'TC-GEN-010 verdicts' $stopping '`PASS`'
    Require-Match 'TC-GEN-010 verdicts' $stopping '`FAIL`'
    Require-Match 'TC-GEN-010 verdicts' $stopping '`BLOCKED`'

    # TC-GEN-011: resume preserves prior evidence and continues the documented state.
    Require-Match 'TC-GEN-011 resume' $skill '(?im)^## `resume` workflow$'
    Require-Match 'TC-GEN-011 resume' $skill '(?i)append rather than rewrite'

    # TC-GEN-012: every evidence record declares a bounded evidence label.
    Require-Match 'TC-GEN-012 evidence labels' $evidence '(?im)^- Evidence label:'
    Require-Match 'TC-GEN-012 evidence labels' $evidence '`structural`'
    Require-Match 'TC-GEN-012 evidence labels' $evidence '`behavioral`'
    Require-Match 'TC-GEN-012 evidence labels' $evidence '`runtime`'
    Require-Match 'TC-GEN-012 evidence labels' $evidence '`review`'
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output 'GENERIC_PROFILE_CONTRACT_TESTS=PASS'
Write-Output 'Evidence class: structural contract test (not host-runtime proof).'
