[CmdletBinding()]
param(
    [string]$SkillRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'protocol-test-helpers.ps1')

if ([string]::IsNullOrWhiteSpace($SkillRoot)) { $SkillRoot = Split-Path -Parent $PSScriptRoot }
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path

$root = Join-Path ([IO.Path]::GetTempPath()) ("review-loop-specification-" + [guid]::NewGuid().ToString('N'))
$script:caseRoot = $null
$script:passed = 0

function Assert-True {
    param([bool]$Condition, [string]$Name)
    if (-not $Condition) { throw "FAIL: $Name" }
    $script:passed++
    Write-Output "PASS: $Name"
}

function Get-State { return Get-ReviewState -CaseRoot $script:caseRoot }

function Start-Case {
    param([string]$Name)
    $script:caseRoot = New-ReviewCase -Root $root -Name $Name -Profile specification
}

function Initialize-SpecificationCase {
    param(
        [string]$AcceptanceSource,
        [string]$Authority = 'spec-source-2026-07-22-r4'
    )
    if (-not (Test-Path -LiteralPath $AcceptanceSource -PathType Leaf)) {
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round 0 -NextAction 'record missing authoritative source' -Profile specification -CharterRevision specification-fixture-1 -VerdictOwner 'review-loop Core' -LastCompletedAction 'specification source check' -Blocker 'missing approved authoritative Spec/brief/ticket'
        return
    }
    @(
        '# Acceptance Charter'
        '- Approval state: approved'
        '- Profile: specification'
        '- Charter revision: approved-specification-r4'
        "- Authority identity: $Authority"
        '- Authority precedence: approved source register entry 001'
        '- Target: frozen acceptance contract fixture'
        '- Scope: in-scope criteria AC-1..AC-7; exclusions: implementation and release'
        '- Acceptance source: acceptance.md'
    ) | Set-Content -LiteralPath (Join-Path $script:caseRoot '.review-loop/charter.md')
    Set-ReviewState -CaseRoot $script:caseRoot -Status READY -Round 0 -NextAction 'collect Producer evidence' -Profile specification -CharterRevision approved-specification-r4 -VerdictOwner 'review-loop Core' -LastCompletedAction 'specification Charter freeze'
}

function Start-SpecificationRound {
    param(
        [bool]$Ambiguous = $false,
        [bool]$Contradictory = $false,
        [bool]$TraceabilityComplete = $true
    )
    $evidence = @(
        'Scope: frozen Spec/brief/ticket and approved acceptance Charter'
        'Profile: specification'
        'Authority: spec-source-2026-07-22-r4; revision and approval state recorded'
        'Source precedence: approved source register entry 001'
        'Target and exclusions: acceptance contract only; implementation and release excluded'
        'Scope map: each in-scope outcome and non-goal linked to authoritative source location'
        'Acceptance matrix: stable AC-1..AC-7 IDs link source, observable outcome, owner, and evidence class'
        'Terminology register: terms, units, qualifiers, audience, and preconditions reviewed'
        'Dependencies and hand-offs: owners, gates, assumptions, and downstream seams recorded'
        'Evidence labels: source; structural; behavioral; manual; review'
    )
    if (-not $TraceabilityComplete) {
        $evidence += 'Traceability defect: criterion AC-4 has no authoritative source link or owner'
    }
    if ($Ambiguous) {
        $evidence += 'Unresolved ambiguity: "fast" has no measurable threshold or audience context; clarification owner is missing'
    }
    else {
        $evidence += 'Ambiguity audit: no unresolved terms or materially different interpretations'
    }
    if ($Contradictory) {
        $evidence += 'Unresolved contradiction: source-register-001 requires PASS while approved-brief-r4 requires BLOCKED; no precedence decision'
    }
    else {
        $evidence += 'Contradiction audit: competing sources agree or precedence decision is recorded'
    }
    return New-ReviewRound -CaseRoot $script:caseRoot -Profile specification -NextAction 'request read-only specification-domain specialists' -ProducerEvidence $evidence
}

function Start-NextSpecificationRound {
    return New-ReviewNextRound -CaseRoot $script:caseRoot -Profile specification -NextAction 'recheck stable specification findings' -ProducerEvidence @(
        'Scope: same frozen specification target; next bounded round'
        'Profile: specification'
        'Authority and Charter revision unchanged: approved-specification-r4'
        'Evidence labels: structural; source; review'
        'Traceability and acceptance matrix rechecked against the same source'
    )
}

function Write-SpecificationSpecialistReport {
    param(
        [ValidateSet('confirmed', 'rejected')][string]$Disposition = 'confirmed',
        [string]$FindingId = 'F-001',
        [ValidateSet('Critical', 'High', 'Medium', 'Low')][string]$Severity = 'High',
        [string]$Axis = 'criteria and acceptance traceability',
        [string]$SourceReference = 'SP-AXIS-001',
        [string]$SpecialistVerdict = 'PASS'
    )
    $state = Get-State
    if ($state.Status -ne 'CRITIC') { throw 'specification specialist report requires CRITIC state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    @(
        '# Specification Specialist Report'
        '- Artifact: acceptance.md'
        '- Profile: specification'
        "- Axis: $Axis"
        "- Source finding reference: $SourceReference"
        "- Stable candidate ID: $FindingId"
        "- Severity: $Severity"
        "- Disposition candidate: $Disposition"
        "- Specialist verdict: $SpecialistVerdict"
        '- Evidence: authoritative source, scope map, acceptance matrix, and ambiguity/contradiction register'
        '- Evidence label: review'
    ) | Set-Content -LiteralPath (Join-Path $roundPath 'specification-specialist.md')
}

function Ingest-SpecificationFinding {
    param(
        [ValidateSet('confirmed', 'rejected')][string]$Disposition = 'confirmed',
        [string]$FindingId = 'F-001',
        [string]$SourceReference = 'SP-AXIS-001',
        [ValidateSet('Critical', 'High', 'Medium', 'Low')][string]$Severity = 'High'
    )
    $state = Get-State
    if ($state.Status -ne 'CRITIC') { throw 'specification finding ingestion requires CRITIC state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    $report = Get-Content -Raw -LiteralPath (Join-Path $roundPath 'specification-specialist.md')
    if ($report -notmatch "Stable candidate ID: $FindingId" -or $report -notmatch 'Evidence label: review') { throw 'specialist report lost stable ID or evidence class' }
    Add-ReviewFinding -CaseRoot $script:caseRoot -FindingId $FindingId -Source 'specification specialist' -Axis 'specification contract' -SourceFindingReference $SourceReference -Severity $Severity -Disposition $Disposition -EvidenceLabel review
    if ($Disposition -eq 'confirmed') {
        Set-ReviewState -CaseRoot $script:caseRoot -Status REPAIR -Round $state.Round -NextAction 'direct bounded specification repair to Producer' -Profile specification -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'validated specification candidate finding'
    }
    else {
        Set-ReviewState -CaseRoot $script:caseRoot -Status EVALUATE -Round $state.Round -NextAction 'request fresh Evaluator' -Profile specification -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'rejected specification candidate'
    }
}

function Apply-SpecificationRepair {
    param([bool]$InScope)
    $state = Get-State
    if ($state.Status -ne 'REPAIR') { throw 'Specification repair requires REPAIR state' }
    if (-not $InScope) {
        Set-ReviewState -CaseRoot $script:caseRoot -Status FAIL -Round $state.Round -NextAction 'scope-changing specification repair rejected' -Profile specification -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'rejected out-of-scope Producer repair'
        return
    }
    $ids = @(Get-ConfirmedReviewFindingIds -CaseRoot $script:caseRoot)
    if ($ids.Count -eq 0) { throw 'Specification repair requires a confirmed finding' }
    Write-ReviewRepairEvidence -CaseRoot $script:caseRoot -Round $state.Round -FindingIds $ids -EvidenceLines @(
        'Producer repair evidence: bounded and in-scope'
        'Changed scope: existing acceptance contract only; no new requirement or authority'
        'Validation: authority, scope map, acceptance matrix, terminology and contradiction checks'
        'Evidence label: structural'
        'Evidence label: source'
    )
    Set-ReviewState -CaseRoot $script:caseRoot -Status EVALUATE -Round $state.Round -NextAction 'request fresh Evaluator' -Profile specification -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'bounded specification Producer repair'
}

function Write-SpecificationEvaluator {
    param(
        [ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$Outcome,
        [string]$ContextIdentity,
        [ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$TraceabilityOutcome = '',
        [ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$AmbiguityOutcome = '',
        [ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$ContradictionOutcome = ''
    )
    if ([string]::IsNullOrWhiteSpace($TraceabilityOutcome)) { $TraceabilityOutcome = $Outcome }
    if ([string]::IsNullOrWhiteSpace($AmbiguityOutcome)) { $AmbiguityOutcome = $Outcome }
    if ([string]::IsNullOrWhiteSpace($ContradictionOutcome)) { $ContradictionOutcome = $Outcome }
    $state = Get-State
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    $records = @(
        '# Evaluator Verdict - Round ' + ('{0:d2}' -f $state.Round)
        "Context identity: $ContextIdentity"
        "Charter revision: $($state.CharterRevision); Profile: specification"
        "Criterion AC-1 (authority and baseline integrity): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: source | Outcome: $Outcome"
        "Criterion AC-2 (scope and target traceability): $TraceabilityOutcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: $TraceabilityOutcome"
        "Criterion AC-3 (criteria and acceptance traceability): $TraceabilityOutcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: $TraceabilityOutcome"
        "Criterion AC-4 (terminology and ambiguity control): $AmbiguityOutcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: review | Outcome: $AmbiguityOutcome"
        "Criterion AC-5 (contradiction and decision coherence): $ContradictionOutcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: review | Outcome: $ContradictionOutcome"
        "Criterion AC-6 (testability and evidence design): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: behavioral | Outcome: $Outcome"
        "Criterion AC-7 (version, change, and hand-off integrity): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: $Outcome"
    )
    foreach ($id in (Get-ReviewFindingIds -CaseRoot $script:caseRoot)) {
        $repairName = "repair-evidence-$id.md"
        if (Test-Path -LiteralPath (Join-Path $roundPath $repairName)) { $records += "- [$repairName]($repairName) | Label: structural" }
    }
    $records += @('Open blocking findings: none', "Outcome: $Outcome", "Verdict recommendation: $Outcome")
    $records | Set-Content -LiteralPath (Join-Path $roundPath 'evaluator-verdict.md')
}

function Assert-SpecificationEvaluatorRecord {
    param(
        [Parameter(Mandatory)][string]$Text,
        [Parameter(Mandatory)][ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$OverallOutcome,
        [ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$TraceabilityOutcome = '',
        [ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$AmbiguityOutcome = '',
        [ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$ContradictionOutcome = '',
        [Parameter(Mandatory)][string]$Name
    )
    if ([string]::IsNullOrWhiteSpace($TraceabilityOutcome)) { $TraceabilityOutcome = $OverallOutcome }
    if ([string]::IsNullOrWhiteSpace($AmbiguityOutcome)) { $AmbiguityOutcome = $OverallOutcome }
    if ([string]::IsNullOrWhiteSpace($ContradictionOutcome)) { $ContradictionOutcome = $OverallOutcome }
    $expected = @{
        1 = @{ Outcome = $OverallOutcome; Label = 'source' }
        2 = @{ Outcome = $TraceabilityOutcome; Label = 'structural' }
        3 = @{ Outcome = $TraceabilityOutcome; Label = 'structural' }
        4 = @{ Outcome = $AmbiguityOutcome; Label = 'review' }
        5 = @{ Outcome = $ContradictionOutcome; Label = 'review' }
        6 = @{ Outcome = $OverallOutcome; Label = 'behavioral' }
        7 = @{ Outcome = $OverallOutcome; Label = 'structural' }
    }
    $missing = [System.Collections.Generic.List[string]]::new()
    foreach ($criterion in 1..7) {
        $value = $expected[$criterion]
        $line = [regex]::Match($Text, "(?m)^Criterion AC-$criterion \([^\r\n]+\): $($value.Outcome) - Evidence: \[producer-evidence\.md\]\(producer-evidence\.md\) \| Label: ([a-z]+) \| Outcome: $($value.Outcome)\r?$")
        if (-not $line.Success) { $missing.Add("AC-$criterion missing outcome/evidence/link"); continue }
        if ($line.Groups[1].Value -ne $value.Label) { $missing.Add("AC-$criterion expected label $($value.Label), observed $($line.Groups[1].Value)") }
        if ($line.Groups[1].Value -notin @('source', 'structural', 'behavioral', 'installation', 'invocation', 'runtime', 'manual', 'review')) { $missing.Add("AC-$criterion uses unsupported primary label") }
    }
    if ($Text -notmatch "(?m)^Outcome: $OverallOutcome\r?$") { $missing.Add("overall outcome $OverallOutcome missing") }
    Assert-True ($missing.Count -eq 0) "$Name (AC-1..AC-7, links, labels, and outcomes)"
}

function Evaluate-SpecificationCase {
    param(
        [bool]$Pass,
        [bool]$IndependentContext,
        [int]$MaximumRound = 3
    )
    $state = Get-State
    if ($state.Status -ne 'EVALUATE') { throw 'Specification evaluation requires EVALUATE state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    $producer = Get-Content -Raw -LiteralPath (Join-Path $roundPath 'producer-evidence.md')
    if (-not $IndependentContext) {
        Write-SpecificationEvaluator 'BLOCKED' 'unavailable independent read-only Evaluator' 'BLOCKED' 'BLOCKED' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'obtain independent Evaluator context' -Profile specification -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'independent context check' -Blocker 'independent context unavailable'
        return
    }
    if ($producer -match 'Traceability defect:') {
        Write-SpecificationEvaluator 'BLOCKED' 'fresh independent read-only Evaluator' 'BLOCKED' 'BLOCKED' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'link every criterion to an authoritative source and owner' -Profile specification -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'scope and criteria traceability check' -Blocker 'untraceable requirement or acceptance criterion'
        return
    }
    if ($producer -match 'Unresolved ambiguity:' -or $producer -match 'Unresolved contradiction:') {
        $ambiguity = if ($producer -match 'Unresolved ambiguity:') { 'BLOCKED' } else { 'PASS' }
        $contradiction = if ($producer -match 'Unresolved contradiction:') { 'BLOCKED' } else { 'PASS' }
        Write-SpecificationEvaluator 'BLOCKED' 'fresh independent read-only Evaluator' 'BLOCKED' $ambiguity $contradiction
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'record authority decision or clarify ambiguous requirement' -Profile specification -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'authority and ambiguity boundary check' -Blocker 'unresolved specification authority boundary'
        return
    }
    if ($Pass) {
        foreach ($id in @(Get-ConfirmedReviewFindingIds -CaseRoot $script:caseRoot)) {
            $repair = Join-Path $roundPath "repair-evidence-$id.md"
            if (-not (Test-Path -LiteralPath $repair)) { throw "Missing repair evidence for $id" }
            @("Finding ${id}: Status: resolved", 'Resolution evidence: fresh independent Evaluator', "Repair evidence: rounds/round-$('{0:d2}' -f $state.Round)/repair-evidence-$id.md") | Add-Content -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')
        }
        Write-SpecificationEvaluator 'PASS' 'fresh independent read-only Evaluator'
        @('# Review Loop Verdict', 'Verdict: PASS', 'Issued by: review-loop Core', 'Evaluator: fresh independent read-only context', 'Specialist input: specification authority, traceability, ambiguity, and contradiction evidence') | Set-Content -LiteralPath (Join-Path $script:caseRoot '.review-loop/verdict.md')
        Set-ReviewState -CaseRoot $script:caseRoot -Status PASS -Round $state.Round -NextAction 'preserve Core verdict' -Profile specification -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'fresh specification Evaluator PASS'
    }
    elseif ($state.Round -lt $MaximumRound) {
        Write-SpecificationEvaluator 'FAIL' 'fresh independent read-only Evaluator' 'FAIL' 'FAIL' 'FAIL'
        Set-ReviewState -CaseRoot $script:caseRoot -Status FAIL -Round $state.Round -NextAction 'CRITIC (next round); bounded specification repair remains' -Profile specification -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'fresh specification Evaluator FAIL'
    }
    else {
        Write-SpecificationEvaluator 'BLOCKED' 'fresh independent read-only Evaluator' 'BLOCKED' 'BLOCKED' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'repair limit reached' -Profile specification -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'repair limit check' -Blocker 'maximum rounds or no permitted repair'
    }
}

try {
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    $installed = Join-Path $root 'installed-review-loop'
    Copy-Item -Recurse -Force -LiteralPath $SkillRoot -Destination $installed
    Assert-True (Test-Path -LiteralPath (Join-Path $installed 'references/profiles/specification.md')) 'fresh install includes specification Profile'

    # Success path: a specialist finding flows through generic repair and Core PASS.
    Start-Case 'integration'
    $acceptance = Join-Path $script:caseRoot 'acceptance.md'
    'Approved Spec revision 4; source register entry 001 is authoritative' | Set-Content -LiteralPath $acceptance
    Initialize-SpecificationCase $acceptance
    Assert-True ((Get-State).Profile -eq 'specification' -and (Get-State).CharterRevision -eq 'approved-specification-r4' -and (Get-State).Raw -match 'Verdict owner: review-loop Core') 'init freezes authoritative source, Profile, revision, and Core ownership'
    Start-SpecificationRound | Out-Null
    $producer = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/producer-evidence.md')
    Assert-True ($producer -match 'Authority:' -and $producer -match 'Scope map:' -and $producer -match 'Acceptance matrix:' -and $producer -match 'Evidence labels: source; structural; behavioral; manual; review') 'Producer evidence records authority and requirement traceability'
    Write-SpecificationSpecialistReport -Disposition confirmed -FindingId F-001 -SpecialistVerdict PASS
    Assert-True ((Get-State).Status -eq 'CRITIC') 'specialist PASS remains a candidate while Core is in CRITIC'
    Ingest-SpecificationFinding -Disposition confirmed -FindingId F-001
    Assert-True ((Get-State).Status -eq 'REPAIR') 'confirmed specification finding enters generic REPAIR lifecycle'
    Apply-SpecificationRepair $true
    Evaluate-SpecificationCase $true $true
    $evaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    $verdict = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/verdict.md')
    Assert-SpecificationEvaluatorRecord -Text $evaluator -OverallOutcome PASS -Name 'fresh Evaluator records all specification criteria with linked evidence'
    $registry = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')
    Assert-True ((Get-State).Status -eq 'PASS' -and $verdict -match 'Issued by: review-loop Core' -and $registry -match 'Finding F-001: Status: resolved' -and $registry -match 'Resolution evidence: fresh independent Evaluator') 'Core owns final PASS and preserves stable finding resolution'

    # Missing authoritative source blocks init without inventing a baseline.
    Start-Case 'missing-source'
    Initialize-SpecificationCase (Join-Path $script:caseRoot 'missing-acceptance.md')
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match 'missing approved authoritative Spec/brief/ticket') 'missing authoritative source blocks initialization'

    # Undefined or ambiguous language is a specification boundary blocker.
    Start-Case 'ambiguous'
    'Approved Spec revision 4' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SpecificationCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-SpecificationRound -Ambiguous $true | Out-Null
    Write-SpecificationSpecialistReport -Disposition rejected -FindingId F-002 -SpecialistVerdict PASS
    Ingest-SpecificationFinding -Disposition rejected -FindingId F-002
    Evaluate-SpecificationCase $true $true
    $ambiguousEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-SpecificationEvaluatorRecord -Text $ambiguousEvaluator -OverallOutcome BLOCKED -TraceabilityOutcome BLOCKED -AmbiguityOutcome BLOCKED -ContradictionOutcome PASS -Name 'ambiguous requirement blocks with criterion-linked evidence'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match 'unresolved specification authority boundary') 'unresolved ambiguity returns Core BLOCKED'

    # Conflicting authorities require a recorded precedence decision.
    Start-Case 'contradiction'
    'Approved Spec revision 4' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SpecificationCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-SpecificationRound -Contradictory $true | Out-Null
    Write-SpecificationSpecialistReport -Disposition rejected -FindingId F-003 -Axis 'contradiction and decision coherence' -SourceReference 'SP-CONTRADICTION-001'
    Ingest-SpecificationFinding -Disposition rejected -FindingId F-003
    Evaluate-SpecificationCase $true $true
    $contradictionEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-SpecificationEvaluatorRecord -Text $contradictionEvaluator -OverallOutcome BLOCKED -TraceabilityOutcome BLOCKED -AmbiguityOutcome PASS -ContradictionOutcome BLOCKED -Name 'contradictory authority blocks with criterion-linked evidence'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match 'unresolved specification authority boundary') 'unresolved contradiction returns Core BLOCKED'

    # An untraceable criterion cannot be promoted to PASS merely because a
    # specialist rejected a candidate finding; the Core must block AC-2/AC-3.
    Start-Case 'traceability-boundary'
    'Approved Spec revision 4' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SpecificationCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-SpecificationRound -TraceabilityComplete $false | Out-Null
    Write-SpecificationSpecialistReport -Disposition rejected -FindingId F-008 -Axis 'criteria and acceptance traceability' -SourceReference 'SP-TRACEABILITY-001'
    Ingest-SpecificationFinding -Disposition rejected -FindingId F-008
    Evaluate-SpecificationCase $true $true
    $traceabilityEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-SpecificationEvaluatorRecord -Text $traceabilityEvaluator -OverallOutcome BLOCKED -TraceabilityOutcome BLOCKED -AmbiguityOutcome BLOCKED -ContradictionOutcome BLOCKED -Name 'untraceable criterion blocks AC-2 and AC-3 before PASS'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match 'untraceable requirement or acceptance criterion' -and (Get-State).Next -match 'authoritative source and owner') 'untraceable criterion returns Core BLOCKED with smallest unblock'

    # Bounded repair retains FAIL, frozen revision, and the same finding ID.
    Start-Case 'bounded-repair'
    'Approved Spec revision 4' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SpecificationCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-SpecificationRound | Out-Null
    Write-SpecificationSpecialistReport -Disposition confirmed -FindingId F-004 -SpecialistVerdict FAIL
    Ingest-SpecificationFinding -Disposition confirmed -FindingId F-004
    Apply-SpecificationRepair $true
    Evaluate-SpecificationCase $false $true
    $failedEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-SpecificationEvaluatorRecord -Text $failedEvaluator -OverallOutcome FAIL -Name 'failed specification evaluation preserves all criterion evidence'
    $revision = (Get-State).CharterRevision
    Assert-True ((Get-State).Status -eq 'FAIL' -and $revision -eq 'approved-specification-r4' -and (Get-State).Next -match 'next round') 'failed specification round retains frozen revision and bounded next round'
    Start-NextSpecificationRound | Out-Null
    Write-SpecificationSpecialistReport -Disposition rejected -FindingId F-004 -SpecialistVerdict PASS
    Ingest-SpecificationFinding -Disposition rejected -FindingId F-004
    Evaluate-SpecificationCase $true $true
    $recheckEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/evaluator-verdict.md')
    Assert-SpecificationEvaluatorRecord -Text $recheckEvaluator -OverallOutcome PASS -Name 'rechecked specification finding reaches Core PASS'
    $recheckRegistry = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')
    Assert-True ((Get-State).Status -eq 'PASS' -and ([regex]::Matches($recheckRegistry, '(?:Finding|Re-observed) F-004')).Count -eq 2 -and $recheckRegistry -match 'Disposition: rejected') 'stable specification finding ID survives bounded recheck'

    # A scope-changing requirement repair is rejected before Producer edit.
    Start-Case 'scope-change'
    'Approved Spec revision 4' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SpecificationCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-SpecificationRound -TraceabilityComplete $false | Out-Null
    Write-SpecificationSpecialistReport -Disposition confirmed -FindingId F-005 -SpecialistVerdict FAIL
    Ingest-SpecificationFinding -Disposition confirmed -FindingId F-005
    Apply-SpecificationRepair $false
    Assert-True ((Get-State).Status -eq 'FAIL' -and (Get-State).Next -match 'scope-changing' -and -not (Test-Path -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/repair-evidence-F-005.md'))) 'scope-changing specification repair is rejected without Producer edit'

    # Missing independent context and maximum rounds remain generic blockers.
    Start-Case 'independence-block'
    'Approved Spec revision 4' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SpecificationCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-SpecificationRound | Out-Null
    Write-SpecificationSpecialistReport -Disposition rejected -FindingId F-006
    Ingest-SpecificationFinding -Disposition rejected -FindingId F-006
    Evaluate-SpecificationCase $true $false
    $independenceEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-SpecificationEvaluatorRecord -Text $independenceEvaluator -OverallOutcome BLOCKED -Name 'missing independent context blocks Core verdict'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Next -match 'independent Evaluator') 'missing independent Evaluator context returns BLOCKED'

    Start-Case 'maximum-round'
    'Approved Spec revision 4' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SpecificationCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-SpecificationRound | Out-Null
    Write-SpecificationSpecialistReport -Disposition confirmed -FindingId F-007 -SpecialistVerdict FAIL
    Ingest-SpecificationFinding -Disposition confirmed -FindingId F-007
    Apply-SpecificationRepair $true
    Evaluate-SpecificationCase $false $true 1
    $limitEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-SpecificationEvaluatorRecord -Text $limitEvaluator -OverallOutcome BLOCKED -Name 'maximum-round stop records Core BLOCKED evidence'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match 'maximum rounds') 'maximum repair round returns generic BLOCKED'

    Write-Output ("SPECIFICATION_PROFILE_BEHAVIOR_TESTS=PASS ($script:passed assertions)")
    Write-Output 'Evidence class: executable protocol runner in fresh disposable fixtures; host-model role independence remains a separate acceptance gate.'
}
finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -Recurse -Force -LiteralPath $root }
}
