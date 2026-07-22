[CmdletBinding()]
param(
    [string]$SkillRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'protocol-test-helpers.ps1')

if ([string]::IsNullOrWhiteSpace($SkillRoot)) {
    $SkillRoot = Split-Path -Parent $PSScriptRoot
}
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path

$root = Join-Path ([IO.Path]::GetTempPath()) ("review-loop-manuscript-" + [guid]::NewGuid().ToString('N'))
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
    $script:caseRoot = New-ReviewCase -Root $root -Name $Name -Profile manuscript
}

function Initialize-ManuscriptCase {
    param([string]$AcceptanceSource)
    if (-not (Test-Path -LiteralPath $AcceptanceSource -PathType Leaf)) {
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round 0 -NextAction 'record missing acceptance source' -Profile manuscript -CharterRevision manuscript-fixture-1 -VerdictOwner 'review-loop Core' -LastCompletedAction 'manuscript source check' -Blocker 'missing approved Brief/Charter'
        return
    }
    @(
        '# Acceptance Charter'
        '- Approval state: approved'
        '- Profile: manuscript'
        '- Charter revision: approved-manuscript-brief-r3'
        '- Artifact snapshot: manuscript/frozen.md sha256: fixture-artifact-hash'
        '- Source register: .manuscript-ops/sources/source-register.tsv'
        '- Review matrix captured_at: 2026-07-22T00:00:00Z'
        '- Acceptance source: acceptance.md'
    ) | Set-Content -LiteralPath (Join-Path $script:caseRoot '.review-loop/charter.md')
    Set-ReviewState -CaseRoot $script:caseRoot -Status READY -Round 0 -NextAction 'collect Producer evidence' -Profile manuscript -CharterRevision approved-manuscript-brief-r3 -VerdictOwner 'review-loop Core' -LastCompletedAction 'manuscript Charter freeze'
}

function Start-ManuscriptRound {
    param([bool]$ImageTriggered = $false, [bool]$ImageEvidence = $true)
    $evidence = @(
        'Scope: frozen manuscript candidate and declared deliverables'
        'Profile: manuscript'
        'Artifact: manuscript/frozen.md; SHA-256: fixture-artifact-hash'
        'Brief/Charter: approved-manuscript-brief-r3'
        'Source register: authoritative source-001; use=factual; exclusions=none'
        'Lifecycle/batch: candidate batch-01; prerequisite outline accepted'
        'Locked source: manuscript/locked.md; SHA-256: fixture-locked-hash'
        'Terminology: glossary reviewed for language en-US'
        'Format evidence: DOCX structural, renderer runtime, manual visual, semantic and round-trip observations'
        'Generation: fixture renderer v1, locked input and output hashes retained'
        'Gate receipt: final-approved-fixture receipt retained'
        'Evidence label: structural; Evidence label: source; Evidence label: runtime; Evidence label: manual; Evidence label: review'
    )
    if ($ImageTriggered -and $ImageEvidence) {
        $evidence += 'Image axis: triggered by registered PPTX/image source; source/rights/placement/caption/annotation/alt-text evidence recorded; Evidence label: manual'
    }
    elseif ($ImageTriggered) {
        $evidence += 'Image axis: triggered by registered PPTX/image source; required source/rights/placement/caption/alt-text evidence missing'
    }
    else {
        $evidence += 'Image axis: not applicable; no registered image/PPTX/active-batch trigger; negative audit recorded; Evidence label: structural'
    }
    return New-ReviewRound -CaseRoot $script:caseRoot -Profile manuscript -NextAction 'request read-only manuscript-domain specialists' -ProducerEvidence $evidence
}

function Start-NextManuscriptRound {
    return New-ReviewNextRound -CaseRoot $script:caseRoot -Profile manuscript -NextAction 'recheck stable manuscript findings' -ProducerEvidence @(
        'Scope: same frozen manuscript target; next round'
        'Profile: manuscript'
        'Evidence label: structural'
        'Evidence label: runtime'
        'Evidence label: manual'
    )
}

function Write-ManuscriptSpecialistReport {
    param(
        [ValidateSet('confirmed', 'rejected')][string]$Disposition = 'confirmed',
        [string]$FindingId = 'F-001',
        [ValidateSet('Critical', 'High', 'Medium', 'Low')][string]$Severity = 'High',
        [string]$SourceReference = 'MS-AXIS-SOURCE-001',
        [string]$SpecialistVerdict = 'PASS'
    )
    $state = Get-ReviewState -CaseRoot $script:caseRoot
    if ($state.Status -ne 'CRITIC') { throw 'manuscript specialist report requires CRITIC state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    @(
        '# Manuscript Specialist Report'
        '- Artifact: manuscript/frozen.md'
        '- Profile: manuscript'
        '- Axis: Source authority, provenance, factual claims, citations, numbers, and units'
        "- Source finding reference: $SourceReference"
        "- Stable candidate ID: $FindingId"
        "- Severity: $Severity"
        "- Disposition candidate: $Disposition"
        "- Specialist verdict: $SpecialistVerdict"
        '- Evidence: source register, locked-source hash, and artifact observation'
        '- Evidence label: review'
    ) | Set-Content -LiteralPath (Join-Path $roundPath 'manuscript-specialist.md')
}

function Ingest-ManuscriptFinding {
    param([ValidateSet('confirmed', 'rejected')][string]$Disposition = 'confirmed', [string]$FindingId = 'F-001', [string]$SourceReference = 'MS-AXIS-SOURCE-001')
    $state = Get-ReviewState -CaseRoot $script:caseRoot
    if ($state.Status -ne 'CRITIC') { throw 'manuscript finding ingestion requires CRITIC state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    $report = Get-Content -Raw -LiteralPath (Join-Path $roundPath 'manuscript-specialist.md')
    if ($report -notmatch 'Axis: Source authority' -or $report -notmatch "Stable candidate ID: $FindingId" -or $report -notmatch 'Evidence label: review') { throw 'specialist report lost axis, stable ID, or evidence class' }
    Add-ReviewFinding -CaseRoot $script:caseRoot -FindingId $FindingId -Source 'manuscript specialist' -Axis 'source authority' -SourceFindingReference $SourceReference -Severity High -Disposition $Disposition -EvidenceLabel review
    if ($Disposition -eq 'confirmed') {
        Set-ReviewState -CaseRoot $script:caseRoot -Status REPAIR -Round $state.Round -NextAction 'direct bounded repair to Producer' -Profile manuscript -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'validated manuscript candidate finding'
    }
    else {
        Set-ReviewState -CaseRoot $script:caseRoot -Status EVALUATE -Round $state.Round -NextAction 'request fresh Evaluator' -Profile manuscript -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'rejected manuscript candidate'
    }
}

function Apply-ManuscriptRepair {
    param([bool]$InScope)
    $state = Get-ReviewState -CaseRoot $script:caseRoot
    if ($state.Status -ne 'REPAIR') { throw 'Manuscript repair requires REPAIR state' }
    if (-not $InScope) {
        Set-ReviewState -CaseRoot $script:caseRoot -Status FAIL -Round $state.Round -NextAction 'scope-changing manuscript repair rejected' -Profile manuscript -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'rejected out-of-scope Producer repair'
        return
    }
    $ids = @(Get-ConfirmedReviewFindingIds -CaseRoot $script:caseRoot)
    if ($ids.Count -eq 0) { throw 'Manuscript repair requires a confirmed finding' }
    Write-ReviewRepairEvidence -CaseRoot $script:caseRoot -Round $state.Round -FindingIds $ids -EvidenceLines @('Producer repair evidence: bounded and in-scope', 'Changed scope: existing manuscript artifact only', 'Validation: source, runtime renderer, manual visual, semantic and terminology checks', 'Evidence label: runtime', 'Evidence label: manual')
    Set-ReviewState -CaseRoot $script:caseRoot -Status EVALUATE -Round $state.Round -NextAction 'request fresh Evaluator' -Profile manuscript -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'bounded manuscript Producer repair'
}

function Write-ManuscriptEvaluator {
    param([ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$Outcome, [string]$ContextIdentity, [string]$FormatOutcome = 'PASS')
    $state = Get-State
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    $producerPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}/producer-evidence.md' -f $state.Round)
    $imageLabel = if ((Get-Content -Raw -LiteralPath $producerPath) -match 'Image axis: triggered') { 'manual' } else { 'structural' }
    $records = @(
        '# Evaluator Verdict - Round ' + ('{0:d2}' -f $state.Round)
        "Context identity: $ContextIdentity"
        "Charter revision: $($state.CharterRevision); Profile: manuscript"
        "Criterion AC-1 (reader task and structure): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: $Outcome"
        "Criterion AC-2 (source authority and factual fidelity): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: source | Outcome: $Outcome"
        "Criterion AC-3 (terminology and localization): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: review | Outcome: $Outcome"
        "Criterion AC-4 (reader fit and accessibility): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: review | Outcome: $Outcome"
        "Criterion AC-5 (safety, privacy and metadata): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: review | Outcome: $Outcome"
        "Criterion AC-6 (format, rendering and visual QA): $FormatOutcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: runtime | Outcome: $FormatOutcome"
        "Criterion AC-7 (images and figures applicability): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: $imageLabel | Outcome: $Outcome"
        "Criterion AC-8 (lifecycle, batches, gates and locked source): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: source | Outcome: $Outcome"
        "Criterion AC-9 (reproducibility and artifact evidence): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: $Outcome"
        "Criterion AC-10 (compatibility and round-trip): $FormatOutcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: runtime | Outcome: $FormatOutcome"
    )
    foreach ($id in (Get-ReviewFindingIds -CaseRoot $script:caseRoot)) {
        $repairName = "repair-evidence-$id.md"
        if (Test-Path -LiteralPath (Join-Path $roundPath $repairName)) { $records += "- [$repairName]($repairName) | Label: runtime" }
    }
    $records += @('Open blocking findings: none', "Outcome: $Outcome", "Verdict recommendation: $Outcome")
    $records | Set-Content -LiteralPath (Join-Path $roundPath 'evaluator-verdict.md')
}

function Assert-ManuscriptEvaluatorRecord {
    param(
        [Parameter(Mandatory)][string]$Text,
        [Parameter(Mandatory)][ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$OverallOutcome,
        [ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$FormatOutcome = '',
        [ValidateSet('manual', 'structural')][string]$ImageLabel = 'structural',
        [Parameter(Mandatory)][string]$Name
    )
    if ([string]::IsNullOrWhiteSpace($FormatOutcome)) { $FormatOutcome = $OverallOutcome }
    $expected = @{
        1 = @{ Outcome = $OverallOutcome; Label = 'structural' }
        2 = @{ Outcome = $OverallOutcome; Label = 'source' }
        3 = @{ Outcome = $OverallOutcome; Label = 'review' }
        4 = @{ Outcome = $OverallOutcome; Label = 'review' }
        5 = @{ Outcome = $OverallOutcome; Label = 'review' }
        6 = @{ Outcome = $FormatOutcome; Label = 'runtime' }
        7 = @{ Outcome = $OverallOutcome; Label = $ImageLabel }
        8 = @{ Outcome = $OverallOutcome; Label = 'source' }
        9 = @{ Outcome = $OverallOutcome; Label = 'structural' }
        10 = @{ Outcome = $FormatOutcome; Label = 'runtime' }
    }
    $missing = [System.Collections.Generic.List[string]]::new()
    foreach ($criterion in 1..10) {
        $line = [regex]::Match($Text, "(?m)^Criterion AC-$criterion \([^\r\n]+\): $($expected[$criterion].Outcome) - Evidence: \[producer-evidence\.md\]\(producer-evidence\.md\) \| Label: ([a-z]+) \| Outcome: $($expected[$criterion].Outcome)\r?$")
        if (-not $line.Success) {
            $missing.Add("AC-$criterion missing outcome/evidence/link")
            continue
        }
        if ($line.Groups[1].Value -ne $expected[$criterion].Label) {
            $missing.Add("AC-$criterion expected label $($expected[$criterion].Label), observed $($line.Groups[1].Value)")
        }
        if ($line.Groups[1].Value -notin @('source', 'structural', 'behavioral', 'installation', 'invocation', 'runtime', 'manual', 'review')) {
            $missing.Add("AC-$criterion uses unsupported primary label")
        }
    }
    if ($Text -notmatch "(?m)^Outcome: $OverallOutcome\r?$") { $missing.Add("overall outcome $OverallOutcome missing") }
    Assert-True ($missing.Count -eq 0) "$Name (AC-1..AC-10, links, labels, image mapping)"
}

function Evaluate-ManuscriptCase {
    param([bool]$Pass, [bool]$IndependentContext, [bool]$FormatEvidence = $true, [int]$MaximumRound = 3)
    $state = Get-ReviewState -CaseRoot $script:caseRoot
    if ($state.Status -ne 'EVALUATE') { throw 'Manuscript evaluation requires EVALUATE state' }
    if (-not $IndependentContext) {
        Write-ManuscriptEvaluator 'BLOCKED' 'unavailable independent read-only Evaluator' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'obtain independent Evaluator context' -Profile manuscript -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'independent context check' -Blocker 'independent context unavailable'
        return
    }
    $producerPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}/producer-evidence.md' -f $state.Round)
    $producer = Get-Content -Raw -LiteralPath $producerPath
    if ($producer -match 'Image axis: triggered' -and $producer -notmatch 'source/rights/placement/caption/annotation/alt-text evidence recorded') {
        Write-ManuscriptEvaluator 'BLOCKED' 'fresh independent read-only Evaluator' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'obtain required image source and visual evidence' -Profile manuscript -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'image applicability check' -Blocker 'triggered image axis evidence unavailable'
        return
    }
    if (-not $FormatEvidence) {
        Write-ManuscriptEvaluator 'BLOCKED' 'fresh independent read-only Evaluator' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'obtain required render/visual/round-trip evidence' -Profile manuscript -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'format evidence check' -Blocker 'blocking format QA unavailable'
        return
    }
    if ($Pass) {
        $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
        $registry = Join-Path $script:caseRoot '.review-loop/findings.md'
        foreach ($id in @(Get-ConfirmedReviewFindingIds -CaseRoot $script:caseRoot)) {
            $repair = Join-Path $roundPath "repair-evidence-$id.md"
            if (-not (Test-Path -LiteralPath $repair)) { throw "Missing repair evidence for $id" }
            @("Finding ${id}: Status: resolved", 'Resolution evidence: fresh independent Evaluator', "Repair evidence: rounds/round-$('{0:d2}' -f $state.Round)/repair-evidence-$id.md") | Add-Content -LiteralPath $registry
        }
        Write-ManuscriptEvaluator 'PASS' 'fresh independent read-only Evaluator' 'PASS'
        @('# Review Loop Verdict', 'Verdict: PASS', 'Issued by: review-loop Core', 'Evaluator: fresh independent read-only context', 'Specialist input: manuscript-domain source, editorial, and format evidence') | Set-Content -LiteralPath (Join-Path $script:caseRoot '.review-loop/verdict.md')
        Set-ReviewState -CaseRoot $script:caseRoot -Status PASS -Round $state.Round -NextAction 'preserve Core verdict' -Profile manuscript -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'fresh manuscript Evaluator PASS'
    }
    elseif ($Pass -eq $false -and $state.Round -lt $MaximumRound) {
        Write-ManuscriptEvaluator 'FAIL' 'fresh independent read-only Evaluator' 'PASS'
        Set-ReviewState -CaseRoot $script:caseRoot -Status FAIL -Round $state.Round -NextAction 'CRITIC (next round); bounded manuscript repair remains' -Profile manuscript -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'fresh manuscript Evaluator FAIL'
    }
    else {
        Write-ManuscriptEvaluator 'BLOCKED' 'fresh independent read-only Evaluator' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'repair limit reached' -Profile manuscript -CharterRevision $state.CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'repair limit check' -Blocker 'maximum rounds or no permitted repair'
    }
}

try {
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    $installed = Join-Path $root 'installed-review-loop'
    Copy-Item -Recurse -Force -LiteralPath $SkillRoot -Destination $installed
    Assert-True (Test-Path -LiteralPath (Join-Path $installed 'references/profiles/manuscript.md')) 'fresh install includes manuscript Profile'

    # Success: manuscript specialist evidence flows through generic repair and Core verdict.
    Start-Case 'integration'
    $acceptance = Join-Path $script:caseRoot 'acceptance.md'
    'Approved ManuscriptBrief and final deliverable revision 1' | Set-Content -LiteralPath $acceptance
    Initialize-ManuscriptCase $acceptance
    Assert-True ((Get-State).Profile -eq 'manuscript' -and (Get-State).CharterRevision -eq 'approved-manuscript-brief-r3') 'manuscript init freezes Profile and Brief revision'
    Start-ManuscriptRound | Out-Null
    Write-ManuscriptSpecialistReport -Disposition confirmed -FindingId F-001 -SpecialistVerdict PASS
    Assert-True ((Get-State).Status -eq 'CRITIC') 'specialist PASS remains evidence while Core is in CRITIC'
    Ingest-ManuscriptFinding -Disposition confirmed -FindingId F-001
    Assert-True ((Get-State).Status -eq 'REPAIR') 'manuscript finding enters generic REPAIR lifecycle'
    Apply-ManuscriptRepair $true
    Evaluate-ManuscriptCase $true $true
    $evaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    $verdict = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/verdict.md')
    Assert-ManuscriptEvaluatorRecord -Text $evaluator -OverallOutcome PASS -FormatOutcome PASS -ImageLabel structural -Name 'fresh Evaluator records non-image manuscript axes and Core owns final PASS'
    Assert-True ((Get-State).Status -eq 'PASS' -and $verdict -match 'Issued by: review-loop Core') 'Core verdict record is separate from Evaluator evidence'

    # Boundary: image axis is retained as an explicit negative applicability audit.
    $producer = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/producer-evidence.md')
    Assert-True ($producer -match 'Image axis: not applicable' -and $producer -match 'negative audit recorded') 'image axis remains explicit when no image trigger applies'

    # A triggered image/PPTX axis requires source, rights, placement, caption,
    # annotation, and alt-text evidence before the Core can PASS.
    Start-Case 'triggered-image'
    'Approved ManuscriptBrief revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-ManuscriptCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-ManuscriptRound -ImageTriggered $true -ImageEvidence $true | Out-Null
    Write-ManuscriptSpecialistReport -Disposition rejected -FindingId F-007 -SpecialistVerdict PASS
    Ingest-ManuscriptFinding -Disposition rejected -FindingId F-007
    Evaluate-ManuscriptCase $true $true
    $imageProducer = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/producer-evidence.md')
    $imageEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-ManuscriptEvaluatorRecord -Text $imageEvaluator -OverallOutcome PASS -FormatOutcome PASS -ImageLabel manual -Name 'triggered image Evaluator maps AC-7 to manual evidence'
    Assert-True ((Get-State).Status -eq 'PASS' -and $imageProducer -match 'source/rights/placement/caption/annotation/alt-text evidence recorded') 'triggered image axis passes with complete evidence'

    Start-Case 'triggered-image-missing-evidence'
    'Approved ManuscriptBrief revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-ManuscriptCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-ManuscriptRound -ImageTriggered $true -ImageEvidence $false | Out-Null
    Write-ManuscriptSpecialistReport -Disposition rejected -FindingId F-008 -SpecialistVerdict PASS
    Ingest-ManuscriptFinding -Disposition rejected -FindingId F-008
    Evaluate-ManuscriptCase $true $true
    $missingImageEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-ManuscriptEvaluatorRecord -Text $missingImageEvaluator -OverallOutcome BLOCKED -FormatOutcome BLOCKED -ImageLabel manual -Name 'triggered image Evaluator retains manual AC-7 mapping when blocked'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match 'triggered image axis evidence unavailable') 'triggered image axis blocks without complete image evidence'

    # Missing source blocks initialization without inventing a baseline.
    Start-Case 'missing-source'
    Initialize-ManuscriptCase (Join-Path $script:caseRoot 'missing-acceptance.md')
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match '(?m)^Blocker: missing approved Brief/Charter') 'missing approved manuscript source blocks init'

    # Bounded repair preserves the same finding ID and frozen Charter revision.
    Start-Case 'bounded-repair'
    'Approved ManuscriptBrief revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-ManuscriptCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-ManuscriptRound | Out-Null
    Write-ManuscriptSpecialistReport -Disposition confirmed -FindingId F-002 -SpecialistVerdict FAIL
    Ingest-ManuscriptFinding -Disposition confirmed -FindingId F-002
    Apply-ManuscriptRepair $true
    Evaluate-ManuscriptCase $false $true
    $failedEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-ManuscriptEvaluatorRecord -Text $failedEvaluator -OverallOutcome FAIL -FormatOutcome PASS -ImageLabel structural -Name 'failed manuscript Evaluator records all axes and valid labels'
    $revision = (Get-State).CharterRevision
    Assert-True ((Get-State).Status -eq 'FAIL' -and $revision -eq 'approved-manuscript-brief-r3') 'failed manuscript round retains frozen Charter and bounded next round'
    Start-NextManuscriptRound | Out-Null
    Write-ManuscriptSpecialistReport -Disposition rejected -FindingId F-002 -SpecialistVerdict PASS
    Ingest-ManuscriptFinding -Disposition rejected -FindingId F-002
    Evaluate-ManuscriptCase $true $true
    $recheckEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/evaluator-verdict.md')
    Assert-ManuscriptEvaluatorRecord -Text $recheckEvaluator -OverallOutcome PASS -FormatOutcome PASS -ImageLabel structural -Name 'rechecked manuscript Evaluator records all axes and valid labels'
    $registry = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')
    Assert-True ((Get-State).Status -eq 'PASS' -and ([regex]::Matches($registry, '(?:Finding|Re-observed) F-002')).Count -eq 2 -and $registry -match 'Disposition: rejected') 'bounded recheck preserves stable manuscript finding ID'

    # A scope-changing repair is rejected before the Producer edits.
    Start-Case 'scope-change'
    'Approved ManuscriptBrief revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-ManuscriptCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-ManuscriptRound | Out-Null
    Write-ManuscriptSpecialistReport -Disposition confirmed -FindingId F-003 -SpecialistVerdict FAIL
    Ingest-ManuscriptFinding -Disposition confirmed -FindingId F-003
    Apply-ManuscriptRepair $false
    Assert-True ((Get-State).Status -eq 'FAIL' -and (Get-State).Next -match 'scope-changing' -and -not (Test-Path -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/repair-evidence-F-003.md'))) 'scope-changing manuscript repair is rejected without Producer edit'

    # Required rendering/visual evidence is a manuscript-specific blocker.
    Start-Case 'format-evidence-block'
    'Approved ManuscriptBrief revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-ManuscriptCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-ManuscriptRound | Out-Null
    Write-ManuscriptSpecialistReport -Disposition rejected -FindingId F-004 -SpecialistVerdict PASS
    Ingest-ManuscriptFinding -Disposition rejected -FindingId F-004
    Evaluate-ManuscriptCase $true $true $false
    $blockedEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-ManuscriptEvaluatorRecord -Text $blockedEvaluator -OverallOutcome BLOCKED -FormatOutcome BLOCKED -ImageLabel structural -Name 'format-blocked manuscript Evaluator records all axes and valid labels'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match '(?m)^Blocker: blocking format QA unavailable') 'missing required render/visual evidence blocks manuscript acceptance'

    # Missing independent context blocks a specialist conclusion.
    Start-Case 'independence-block'
    'Approved ManuscriptBrief revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-ManuscriptCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-ManuscriptRound | Out-Null
    Write-ManuscriptSpecialistReport -Disposition rejected -FindingId F-005 -SpecialistVerdict PASS
    Ingest-ManuscriptFinding -Disposition rejected -FindingId F-005
    Evaluate-ManuscriptCase $true $false
    $independenceEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-ManuscriptEvaluatorRecord -Text $independenceEvaluator -OverallOutcome BLOCKED -FormatOutcome BLOCKED -ImageLabel structural -Name 'independence-blocked manuscript Evaluator records all axes and valid labels'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Next -match 'independent Evaluator') 'missing independent context blocks manuscript verdict'

    # Maximum-round stop is inherited from the generic lifecycle.
    Start-Case 'maximum-round'
    'Approved ManuscriptBrief revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-ManuscriptCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-ManuscriptRound | Out-Null
    Write-ManuscriptSpecialistReport -Disposition confirmed -FindingId F-006 -SpecialistVerdict FAIL
    Ingest-ManuscriptFinding -Disposition confirmed -FindingId F-006
    Apply-ManuscriptRepair $true
    Evaluate-ManuscriptCase $false $true $true 1
    $limitEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-ManuscriptEvaluatorRecord -Text $limitEvaluator -OverallOutcome BLOCKED -FormatOutcome BLOCKED -ImageLabel structural -Name 'maximum-round manuscript Evaluator records all axes and valid labels'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match '(?m)^Blocker: maximum rounds') 'maximum repair round returns generic BLOCKED'

    Write-Output ("MANUSCRIPT_PROFILE_BEHAVIOR_TESTS=PASS ($script:passed assertions)")
    Write-Output 'Evidence class: executable protocol runner in fresh disposable fixtures; host-model role independence remains a separate acceptance gate.'
}
finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -Recurse -Force -LiteralPath $root }
}
