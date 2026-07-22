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
$profilePath = Join-Path $SkillRoot 'references/profiles/manuscript.md'
$behaviorPath = Join-Path $SkillRoot 'tests/manuscript-profile-behavior-tests.ps1'
$genericPath = Join-Path $SkillRoot 'references/profiles/generic.md'
$findingPath = Join-Path $SkillRoot 'references/finding-schema.md'
$evidencePath = Join-Path $SkillRoot 'references/evidence-protocol.md'
$stoppingPath = Join-Path $SkillRoot 'references/stopping-rules.md'
$rolesPath = Join-Path $SkillRoot 'references/subagent-protocol.md'

@(
    @{ Label = 'Skill'; Path = $skillPath }
    @{ Label = 'Agent metadata'; Path = $metadataPath }
    @{ Label = 'Manuscript Profile'; Path = $profilePath }
    @{ Label = 'Manuscript behavior tests'; Path = $behaviorPath }
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

    # TC-MS-001: discoverable narrow Profile with generic Profile preserved.
    Require-Match 'TC-MS-001 profile link' $skill '(?im)\[manuscript\.md\]\(references/profiles/manuscript\.md\)'
    Require-Match 'TC-MS-001 profile heading' $profile '(?im)^# Manuscript Profile$'
    Require-Match 'TC-MS-001 implicit invocation' $metadata '(?im)^\s*allow_implicit_invocation:\s*true\s*$'
    Require-Match 'TC-MS-001 generic preserved' $generic '(?im)^# Generic Profile$'
    Require-NoMatch 'TC-MS-001 generic remains empty' $generic '(?i)manuscript|source authority|visual QA'

    # TC-MS-002: manuscript-specific review axes cover source and delivery seams.
    Require-Match 'TC-MS-002 review axes' $profile '(?im)^## Review axes$'
    foreach ($axis in @(
        'Reader task', 'Source authority', 'Terminology', 'Reader fit',
        'Safety', 'Format structure', 'Images and figures', 'Lifecycle',
        'Generation reproducibility', 'Compatibility'
    )) {
        Require-Match "TC-MS-002 axis $axis" $profile "(?i)\*\*$axis"
    }

    # TC-MS-003: artifact-bound evidence is explicit and uses the Core labels.
    Require-Match 'TC-MS-003 evidence requirements' $profile '(?im)^## Evidence requirements$'
    foreach ($term in @(
        'ManuscriptBrief', 'Acceptance Charter', 'SHA-256', 'source map/register',
        'lifecycle state', 'semantic batch', 'human-gate', 'locked-source',
        'structural', 'generation', 'render', 'visual', 'semantic', 'round-trip',
        'fresh independent Evaluator'
    )) {
        Require-Match "TC-MS-003 evidence $term" $profile "(?i)$term"
    }
    Require-Match 'TC-MS-003 labels use protocol' $profile '(?is)exactly one\s+primary label.*Evidence Protocol'
    Require-Match 'TC-MS-003 protocol labels retained' $evidence '(?is)source.*structural.*behavioral.*review'
    Require-NoMatch 'TC-MS-003 unsupported primary labels absent' $profile '(?im)(?:Evidence label|Label):\s*(?:render|visual)\b'
    Require-NoMatch 'TC-MS-003 behavior runner rejects unsupported primary labels' $behavior '(?im)(?:Evidence label|Label):\s*(?:render|visual)\b'
    Require-Match 'TC-MS-003 behavior runner uses allowed format labels' $behavior '(?im)(?:Evidence label|Label):\s*(?:runtime|manual)\b'
    Require-Match 'TC-MS-003 reusable Evaluator assertion' $behavior '(?im)^function Assert-ManuscriptEvaluatorRecord\s*\{'
    Require-Match 'TC-MS-003 Evaluator assertion covers all criteria' $behavior '(?is)Assert-ManuscriptEvaluatorRecord.*1\.\.10.*Evidence.*Label'

    # TC-MS-004: specialist boundary, severity, acceptance, and failure cases.
    Require-Match 'TC-MS-004 specialist reviewers' $profile '(?im)^## Specialist reviewers$'
    Require-Match 'TC-MS-004 severity guidance' $profile '(?im)^## Severity guidance$'
    Require-Match 'TC-MS-004 severity values' $profile '(?is)\*\*Critical\*\*.*\*\*High\*\*.*\*\*Medium\*\*.*\*\*Low\*\*'
    Require-Match 'TC-MS-004 acceptance conditions' $profile '(?im)^## Acceptance conditions$'
    Require-Match 'TC-MS-004 failure cases' $profile '(?im)^## Artifact-specific failure cases$'
    Require-Match 'TC-MS-004 specialist read-only' $profile '(?is)read-only.*never\s+edits|never\s+edits.*never\s+issues'
    Require-Match 'TC-MS-004 Core verdict ownership' $profile '(?is)Core.*owns.*verdict|Core.*final verdict'

    # TC-MS-005: generic lifecycle is delegated rather than copied.
    Require-Match 'TC-MS-005 delegation statement' $profile '(?is)does not replace.*finding.*repair.*state.*independence.*verdict'
    Require-Match 'TC-MS-005 generic schema handoff' $profile '(?i)generic finding schema|stable IDs'
    Require-Match 'TC-MS-005 Core stopping rules' $profile '(?i)Core.*generic.*`FAIL`.*`BLOCKED`|generic Core.*owns'
    Require-NoMatch 'TC-MS-005 no duplicate state section' $profile '(?im)^## (State|Repair rounds|Finding Registry|Stopping Rules)$'
    Require-NoMatch 'TC-MS-005 no duplicate lifecycle transition' $profile '(?i)INIT\s*->\s*READY|READY\s*->\s*CRITIC'
    Require-Match 'TC-MS-005 canonical generic finding schema unchanged' $finding '(?im)^# Finding Registry$'
    Require-Match 'TC-MS-005 canonical generic stop outcomes unchanged' $stopping '(?i)`PASS`.*`FAIL`.*`BLOCKED`'
    Require-Match 'TC-MS-005 read-only role boundary' $roles '(?i)Critic.*read-only|Evaluator.*read-only'
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output 'MANUSCRIPT_PROFILE_CONTRACT_TESTS=PASS'
Write-Output 'Evidence class: structural contract test (not host-runtime proof).'
