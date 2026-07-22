[CmdletBinding()]
param(
    [string]$SkillRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'protocol-test-helpers.ps1')

if ([string]::IsNullOrWhiteSpace($SkillRoot)) { $SkillRoot = Split-Path -Parent $PSScriptRoot }
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path

$root = Join-Path ([IO.Path]::GetTempPath()) ("review-loop-agent-skill-" + [guid]::NewGuid().ToString('N'))
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
    $script:caseRoot = New-ReviewCase -Root $root -Name $Name -Profile 'agent-skill'
}

function Initialize-AgentSkillCase {
    param(
        [string]$AcceptanceSource,
        [ValidateSet('user-invoked', 'model-invoked')][string]$InvocationType = 'model-invoked'
    )
    if (-not (Test-Path -LiteralPath $AcceptanceSource -PathType Leaf)) {
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round 0 -NextAction 'record missing acceptance source' -Profile 'agent-skill' -CharterRevision agent-skill-fixture-1 -LastCompletedAction 'agent-skill source check' -Blocker 'missing approved package acceptance source'
        return
    }
    $packageRoot = Join-Path $script:caseRoot 'package'
    New-Item -ItemType Directory -Force -Path (Join-Path $packageRoot 'agents') | Out-Null
    @(
        '---'
        'name: fixture-skill'
        'description: Reusable fixture method for Agent-Skill Profile acceptance.'
        '---'
        '# Fixture Skill'
        'Use this package only for the frozen fixture acceptance target.'
    ) | Set-Content -LiteralPath (Join-Path $packageRoot 'SKILL.md')
    @(
        'interface:'
        '  display_name: "Fixture Skill"'
        '  short_description: "Reusable fixture method"'
        '  default_prompt: "Use the fixture skill for the approved case."'
        'policy:'
        '  allow_implicit_invocation: true'
    ) | Set-Content -LiteralPath (Join-Path $packageRoot 'agents/openai.yaml')
    @(
        '# Acceptance Charter'
        '- Approval state: approved'
        '- Profile: agent-skill'
        '- Charter revision: approved-agent-skill-r2'
        '- Package revision: fixture-skill-1'
        "- Invocation type: $InvocationType"
        '- Discovery target: clean installed package'
        '- Acceptance source: acceptance.md'
    ) | Set-Content -LiteralPath (Join-Path $script:caseRoot '.review-loop/charter.md')
    Set-ReviewState -CaseRoot $script:caseRoot -Status READY -Round 0 -NextAction 'collect Producer evidence' -Profile 'agent-skill' -CharterRevision approved-agent-skill-r2 -LastCompletedAction 'agent-skill Charter freeze'
}

function Start-AgentSkillRound {
    param(
        [bool]$Executable = $true,
        [bool]$ExecutableEvidence = $true,
        [bool]$DependencyAvailable = $true,
        [ValidateSet('user-invoked', 'model-invoked')][string]$InvocationType = 'model-invoked',
        [bool]$TriggerObserved = $true
    )
    $evidence = @(
        'Scope: frozen installable Agent Skill package and acceptance source'
        'Profile: agent-skill'
        'Package revision: fixture-skill-1'
        'Structure: SKILL.md, agents/openai.yaml, and declared references inspected'
        'Clean install: copied to an empty install root and discovered by metadata'
        'Evidence label: structural'
        'Evidence label: installation'
        "Invocation: $InvocationType; trigger observed: $TriggerObserved; downstream user-invoked Skills are recommended, not executed"
        'Evidence label: invocation'
        'Success path: fixture method returns expected reusable output'
        'Boundary path: non-trigger request returns no-op recommendation without execution'
        'Evidence label: behavioral'
        'Interaction seam: explicit input, output, authority owner, and stop condition preserved'
        'Dependency: fixture host requirement checked'
        'Evidence label: runtime'
    )
    if ($Executable) {
        if ($ExecutableEvidence) {
            $evidence += 'Executable script: focused assertion-bearing tests (12 assertions), negative/adversarial fixture, and code-review Standards/Spec reports retained'
            $evidence += 'Evidence label: review'
        }
        else {
            $evidence += 'Executable script: focused or adversarial/code-review evidence missing'
            $evidence += 'Evidence label: structural'
        }
    }
    else {
        $evidence += 'Executable axis: not applicable; package has no scripts or executable resources'
        $evidence += 'Evidence label: structural'
    }
    if (-not $DependencyAvailable) { $evidence += 'Missing dependency: required host capability unavailable; smallest unblock is to install the declared dependency' }
    $roundPath = New-ReviewRound -CaseRoot $script:caseRoot -Profile 'agent-skill' -NextAction 'request read-only package and invocation specialists' -ProducerEvidence $evidence
    if ($Executable -and $ExecutableEvidence) {
        @(
            '# Focused executable Skill tests'
            '- Assertions: 12'
            '- Success, boundary, and failure scenarios: PASS'
            '- Negative/adversarial fixture: PASS'
            '- Evidence label: behavioral'
        ) | Set-Content -LiteralPath (Join-Path $roundPath 'focused-script-tests.md')
        @(
            '# code-review Standards report'
            '- Fixed package revision: fixture-skill-1'
            '- Axis: Standards'
            '- Evidence label: review'
            '- Specialist verdict: PASS'
        ) | Set-Content -LiteralPath (Join-Path $roundPath 'code-review-standards.md')
        @(
            '# code-review Spec report'
            '- Fixed package revision: fixture-skill-1'
            '- Axis: Spec'
            '- Evidence label: review'
            '- Specialist verdict: PASS'
        ) | Set-Content -LiteralPath (Join-Path $roundPath 'code-review-spec.md')
    }
    return $roundPath
}

function Write-AgentSkillSpecialistReport {
    param(
        [ValidateSet('confirmed', 'rejected')][string]$Disposition = 'rejected',
        [string]$FindingId = 'F-001',
        [ValidateSet('Critical', 'High', 'Medium', 'Low')][string]$Severity = 'High',
        [string]$Axis = 'invocation contract',
        [string]$SourceReference = 'AS-AXIS-001',
        [string]$SpecialistVerdict = 'PASS'
    )
    $state = Get-State
    if ($state.Status -ne 'CRITIC') { throw 'Agent-Skill specialist report requires CRITIC state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    @(
        '# Agent-Skill Specialist Report'
        '- Package: package/SKILL.md'
        '- Profile: agent-skill'
        "- Axis: $Axis"
        "- Source finding reference: $SourceReference"
        "- Stable candidate ID: $FindingId"
        "- Severity: $Severity"
        "- Disposition candidate: $Disposition"
        "- Specialist verdict: $SpecialistVerdict"
        '- Evidence: clean installation, trigger boundary, method fixture, and interaction record'
        '- Evidence label: review'
    ) | Set-Content -LiteralPath (Join-Path $roundPath 'agent-skill-specialist.md')
}

function Ingest-AgentSkillFinding {
    param([ValidateSet('confirmed', 'rejected')][string]$Disposition = 'rejected', [string]$FindingId = 'F-001', [string]$SourceReference = 'AS-AXIS-001')
    $state = Get-State
    if ($state.Status -ne 'CRITIC') { throw 'Agent-Skill finding ingestion requires CRITIC state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    $report = Get-Content -Raw -LiteralPath (Join-Path $roundPath 'agent-skill-specialist.md')
    if ($report -notmatch "Stable candidate ID: $FindingId" -or $report -notmatch 'Evidence label: review') { throw 'specialist report lost stable ID or evidence class' }
    Add-ReviewFinding -CaseRoot $script:caseRoot -FindingId $FindingId -Source 'agent-skill specialist' -Axis 'agent-skill package' -SourceFindingReference $SourceReference -Severity High -Disposition $Disposition -EvidenceLabel review
    if ($Disposition -eq 'confirmed') {
        Set-ReviewState -CaseRoot $script:caseRoot -Status REPAIR -Round $state.Round -NextAction 'direct bounded package repair to Producer' -Profile 'agent-skill' -CharterRevision $state.CharterRevision -LastCompletedAction 'validated Agent-Skill candidate finding'
    }
    else {
        Set-ReviewState -CaseRoot $script:caseRoot -Status EVALUATE -Round $state.Round -NextAction 'request fresh Evaluator' -Profile 'agent-skill' -CharterRevision $state.CharterRevision -LastCompletedAction 'rejected Agent-Skill candidate'
    }
}

function Apply-AgentSkillRepair {
    param([bool]$InScope)
    $state = Get-State
    if ($state.Status -ne 'REPAIR') { throw 'Agent-Skill repair requires REPAIR state' }
    if (-not $InScope) {
        Set-ReviewState -CaseRoot $script:caseRoot -Status FAIL -Round $state.Round -NextAction 'scope-changing package repair rejected' -Profile 'agent-skill' -CharterRevision $state.CharterRevision -LastCompletedAction 'rejected out-of-scope Producer repair'
        return
    }
    $ids = @(Get-ConfirmedReviewFindingIds -CaseRoot $script:caseRoot)
    if ($ids.Count -eq 0) { throw 'Agent-Skill repair requires a confirmed finding' }
    Write-ReviewRepairEvidence -CaseRoot $script:caseRoot -Round $state.Round -FindingIds $ids -EvidenceLines @('Producer repair evidence: bounded and in-scope', 'Changed scope: existing Skill package only', 'Validation: focused success, boundary, failure and installation scenarios', 'Evidence label: behavioral', 'Evidence label: installation')
    Set-ReviewState -CaseRoot $script:caseRoot -Status EVALUATE -Round $state.Round -NextAction 'request fresh Evaluator' -Profile 'agent-skill' -CharterRevision $state.CharterRevision -LastCompletedAction 'bounded Agent-Skill Producer repair'
}

function Write-AgentSkillEvaluator {
    param([ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$Outcome, [string]$ContextIdentity, [ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$ExecutableOutcome = 'PASS')
    $state = Get-State
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    $producerPath = Join-Path $roundPath 'producer-evidence.md'
    $producer = Get-Content -Raw -LiteralPath $producerPath
    $execLabel = if ($producer -match 'Executable axis: not applicable') { 'structural' } else { 'review' }
    @(
        '# Evaluator Verdict - Round ' + ('{0:d2}' -f $state.Round)
        "Context identity: $ContextIdentity"
        "Charter revision: $($state.CharterRevision); Profile: agent-skill"
        "Criterion AC-1 (package structure and discoverability): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: structural | Outcome: $Outcome"
        "Criterion AC-2 (installation and fresh discovery): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: installation | Outcome: $Outcome"
        "Criterion AC-3 (invocation contract and boundaries): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: invocation | Outcome: $Outcome"
        "Criterion AC-4 (reusable behavior and method fidelity): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: behavioral | Outcome: $Outcome"
        "Criterion AC-5 (interaction and composition seams): $Outcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: behavioral | Outcome: $Outcome"
        "Criterion AC-6 (executable artifact quality): $ExecutableOutcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: $execLabel | Outcome: $ExecutableOutcome"
        'Open blocking findings: none'
        "Outcome: $Outcome"
        "Verdict recommendation: $Outcome"
    ) | Set-Content -LiteralPath (Join-Path $roundPath 'evaluator-verdict.md')
}

function Assert-AgentSkillEvaluatorRecord {
    param([Parameter(Mandatory)][string]$Text, [Parameter(Mandatory)][ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$OverallOutcome, [ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$ExecutableOutcome = 'PASS', [Parameter(Mandatory)][string]$Name)
    $expected = @{
        1 = @{ Outcome = $OverallOutcome; Label = 'structural' }
        2 = @{ Outcome = $OverallOutcome; Label = 'installation' }
        3 = @{ Outcome = $OverallOutcome; Label = 'invocation' }
        4 = @{ Outcome = $OverallOutcome; Label = 'behavioral' }
        5 = @{ Outcome = $OverallOutcome; Label = 'behavioral' }
        6 = @{ Outcome = $ExecutableOutcome; Label = if ($Text -match 'Executable axis: not applicable') { 'structural' } else { 'review' } }
    }
    $missing = [System.Collections.Generic.List[string]]::new()
    foreach ($criterion in 1..6) {
        $value = $expected[$criterion]
        $line = [regex]::Match($Text, "(?m)^Criterion AC-$criterion \([^\r\n]+\): $($value.Outcome) - Evidence: \[producer-evidence\.md\]\(producer-evidence\.md\) \| Label: ([a-z]+) \| Outcome: $($value.Outcome)\r?$")
        if (-not $line.Success) { $missing.Add("AC-$criterion missing outcome/evidence/link"); continue }
        if ($line.Groups[1].Value -ne $value.Label) { $missing.Add("AC-$criterion expected label $($value.Label), observed $($line.Groups[1].Value)") }
    }
    if ($Text -notmatch "(?m)^Outcome: $OverallOutcome\r?$") { $missing.Add("overall outcome $OverallOutcome missing") }
    Assert-True ($missing.Count -eq 0) "$Name (AC-1..AC-6, links, labels)"
}

function Evaluate-AgentSkillCase {
    param([bool]$Pass, [bool]$IndependentContext, [bool]$DependencyAvailable = $true, [bool]$ExecutableEvidence = $true, [int]$MaximumRound = 3)
    $state = Get-State
    if ($state.Status -ne 'EVALUATE') { throw 'Agent-Skill evaluation requires EVALUATE state' }
    if (-not $IndependentContext) {
        Write-AgentSkillEvaluator 'BLOCKED' 'unavailable independent read-only Evaluator' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'obtain independent Evaluator context' -Profile 'agent-skill' -CharterRevision $state.CharterRevision -LastCompletedAction 'independent context check' -Blocker 'independent context unavailable'
        return
    }
    if (-not $DependencyAvailable) {
        Write-AgentSkillEvaluator 'BLOCKED' 'fresh independent read-only Evaluator' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'install declared host dependency' -Profile 'agent-skill' -CharterRevision $state.CharterRevision -LastCompletedAction 'dependency check' -Blocker 'required host dependency unavailable'
        return
    }
    if (-not $ExecutableEvidence) {
        Write-AgentSkillEvaluator 'BLOCKED' 'fresh independent read-only Evaluator' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'obtain executable focused, adversarial, and code-review evidence' -Profile 'agent-skill' -CharterRevision $state.CharterRevision -LastCompletedAction 'executable evidence check' -Blocker 'required executable evidence unavailable'
        return
    }
    if ($Pass) {
        $registry = Join-Path $script:caseRoot '.review-loop/findings.md'
        foreach ($id in @(Get-ConfirmedReviewFindingIds -CaseRoot $script:caseRoot)) {
            $repair = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}/repair-evidence-{1}.md' -f $state.Round, $id)
            if (-not (Test-Path -LiteralPath $repair)) { throw "Missing repair evidence for $id" }
            @("Finding ${id}: Status: resolved", 'Resolution evidence: fresh independent Evaluator', "Repair evidence: rounds/round-$('{0:d2}' -f $state.Round)/repair-evidence-$id.md") | Add-Content -LiteralPath $registry
        }
        Write-AgentSkillEvaluator 'PASS' 'fresh independent read-only Evaluator' 'PASS'
        @('# Review Loop Verdict', 'Verdict: PASS', 'Issued by: review-loop Core', 'Evaluator: fresh independent read-only context', 'Specialist input: package, installation, invocation, behavior, and interaction evidence') | Set-Content -LiteralPath (Join-Path $script:caseRoot '.review-loop/verdict.md')
        Set-ReviewState -CaseRoot $script:caseRoot -Status PASS -Round $state.Round -NextAction 'preserve Core verdict' -Profile 'agent-skill' -CharterRevision $state.CharterRevision -LastCompletedAction 'fresh Agent-Skill Evaluator PASS'
    }
    elseif ($state.Round -lt $MaximumRound) {
        Write-AgentSkillEvaluator 'FAIL' 'fresh independent read-only Evaluator' 'PASS'
        Set-ReviewState -CaseRoot $script:caseRoot -Status FAIL -Round $state.Round -NextAction 'CRITIC (next round); bounded package repair remains' -Profile 'agent-skill' -CharterRevision $state.CharterRevision -LastCompletedAction 'fresh Agent-Skill Evaluator FAIL'
    }
    else {
        Write-AgentSkillEvaluator 'BLOCKED' 'fresh independent read-only Evaluator' 'BLOCKED'
        Set-ReviewState -CaseRoot $script:caseRoot -Status BLOCKED -Round $state.Round -NextAction 'repair limit reached' -Profile 'agent-skill' -CharterRevision $state.CharterRevision -LastCompletedAction 'repair limit check' -Blocker 'maximum rounds or no permitted repair'
    }
}

try {
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    $installed = Join-Path $root 'installed-review-loop'
    Copy-Item -Recurse -Force -LiteralPath $SkillRoot -Destination $installed
    Assert-True (Test-Path -LiteralPath (Join-Path $installed 'references/profiles/agent-skill.md')) 'fresh install includes Agent-Skill Profile'
    Assert-True (Test-Path -LiteralPath (Join-Path $installed 'SKILL.md')) 'fresh install is discoverable through SKILL.md'

    # Success: package evidence enters the generic finding and Core verdict flow.
    Start-Case 'integration'
    $acceptance = Join-Path $script:caseRoot 'acceptance.md'
    'Approved fixture Skill package revision 1' | Set-Content -LiteralPath $acceptance
    Initialize-AgentSkillCase $acceptance 'model-invoked'
    Assert-True ((Get-State).Profile -eq 'agent-skill' -and (Get-State).CharterRevision -eq 'approved-agent-skill-r2') 'init freezes Agent-Skill Profile and package revision'
    $integrationRound = Start-AgentSkillRound
    Assert-True ((Test-Path -LiteralPath (Join-Path $integrationRound 'focused-script-tests.md')) -and (Test-Path -LiteralPath (Join-Path $integrationRound 'code-review-standards.md')) -and (Test-Path -LiteralPath (Join-Path $integrationRound 'code-review-spec.md'))) 'executable Skill evidence retains focused tests and separate code-review axes'
    Write-AgentSkillSpecialistReport -Disposition rejected -FindingId F-001 -SpecialistVerdict PASS
    Assert-True ((Get-State).Status -eq 'CRITIC') 'specialist PASS remains evidence while Core is in CRITIC'
    Ingest-AgentSkillFinding -Disposition rejected -FindingId F-001
    Assert-True ((Get-State).Status -eq 'EVALUATE') 'rejected package candidate proceeds to fresh Evaluator'
    Evaluate-AgentSkillCase $true $true
    $evaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    $verdict = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/verdict.md')
    Assert-AgentSkillEvaluatorRecord -Text $evaluator -OverallOutcome PASS -Name 'fresh Evaluator records Agent-Skill axes and Core owns final PASS'
    Assert-True ((Get-State).Status -eq 'PASS' -and $verdict -match 'Issued by: review-loop Core') 'Core verdict record is separate from specialist evidence'

    # Boundary: a non-trigger recommends another user-invoked Skill and does not execute it.
    Start-Case 'invocation-boundary'
    'Approved fixture Skill package revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-AgentSkillCase (Join-Path $script:caseRoot 'acceptance.md') 'user-invoked'
    Start-AgentSkillRound -InvocationType 'user-invoked' -TriggerObserved $false | Out-Null
    Write-AgentSkillSpecialistReport -Disposition rejected -FindingId F-002 -Axis 'invocation contract and boundaries' -SpecialistVerdict PASS
    Ingest-AgentSkillFinding -Disposition rejected -FindingId F-002
    Evaluate-AgentSkillCase $true $true
    $boundaryProducer = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/producer-evidence.md')
    Assert-True ((Get-State).Status -eq 'PASS' -and $boundaryProducer -match 'non-trigger request returns no-op recommendation' -and $boundaryProducer -match 'recommended, not executed') 'non-trigger boundary recommends without invoking another user Skill'

    # Missing acceptance source blocks initialization without inventing a baseline.
    Start-Case 'missing-source'
    Initialize-AgentSkillCase (Join-Path $script:caseRoot 'missing-acceptance.md')
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match 'missing approved package acceptance source') 'missing acceptance source blocks Agent-Skill init'

    # Missing host dependency blocks acceptance and records a smallest safe unblock.
    Start-Case 'missing-dependency'
    'Approved fixture Skill package revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-AgentSkillCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-AgentSkillRound -DependencyAvailable $false | Out-Null
    Write-AgentSkillSpecialistReport -Disposition rejected -FindingId F-003
    Ingest-AgentSkillFinding -Disposition rejected -FindingId F-003
    Evaluate-AgentSkillCase $true $true $false
    $dependencyEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-AgentSkillEvaluatorRecord -Text $dependencyEvaluator -OverallOutcome BLOCKED -ExecutableOutcome BLOCKED -Name 'missing dependency Evaluator records all axes and BLOCKED'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match 'required host dependency unavailable') 'missing dependency returns Core BLOCKED with unblock'

    # Executable packages cannot pass without focused, adversarial and code-review evidence.
    Start-Case 'executable-evidence-block'
    'Approved fixture Skill package revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-AgentSkillCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-AgentSkillRound -ExecutableEvidence $false | Out-Null
    Write-AgentSkillSpecialistReport -Disposition rejected -FindingId F-004
    Ingest-AgentSkillFinding -Disposition rejected -FindingId F-004
    Evaluate-AgentSkillCase $true $true $true $false
    $execEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-AgentSkillEvaluatorRecord -Text $execEvaluator -OverallOutcome BLOCKED -ExecutableOutcome BLOCKED -Name 'missing executable evidence blocks with valid labels'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match 'executable evidence unavailable') 'missing executable evidence returns Core BLOCKED'

    # Bounded repair preserves stable finding identity and the frozen revision.
    Start-Case 'bounded-repair'
    'Approved fixture Skill package revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-AgentSkillCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-AgentSkillRound | Out-Null
    Write-AgentSkillSpecialistReport -Disposition confirmed -FindingId F-005 -SpecialistVerdict FAIL
    Ingest-AgentSkillFinding -Disposition confirmed -FindingId F-005
    Apply-AgentSkillRepair $true
    Evaluate-AgentSkillCase $false $true
    $failedEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-AgentSkillEvaluatorRecord -Text $failedEvaluator -OverallOutcome FAIL -Name 'failed Agent-Skill round records all axes and valid labels'
    $revision = (Get-State).CharterRevision
    Assert-True ((Get-State).Status -eq 'FAIL' -and $revision -eq 'approved-agent-skill-r2') 'failed round retains frozen package revision and bounded next action'
    New-ReviewNextRound -CaseRoot $script:caseRoot -Profile 'agent-skill' -NextAction 'recheck stable Agent-Skill finding' -ProducerEvidence @('Scope: same frozen Skill package; next round', 'Evidence label: behavioral', 'Evidence label: installation') | Out-Null
    Write-AgentSkillSpecialistReport -Disposition rejected -FindingId F-005 -SpecialistVerdict PASS
    Ingest-AgentSkillFinding -Disposition rejected -FindingId F-005
    Evaluate-AgentSkillCase $true $true
    $recheckEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/evaluator-verdict.md')
    Assert-AgentSkillEvaluatorRecord -Text $recheckEvaluator -OverallOutcome PASS -Name 'rechecked Agent-Skill round records all axes and valid labels'
    $registry = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')
    Assert-True ((Get-State).Status -eq 'PASS' -and ([regex]::Matches($registry, '(?:Finding|Re-observed) F-005')).Count -eq 2 -and $registry -match 'Disposition: rejected') 'bounded recheck preserves stable Agent-Skill finding ID'

    # A scope-changing repair is rejected before the Producer edits.
    Start-Case 'scope-change'
    'Approved fixture Skill package revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-AgentSkillCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-AgentSkillRound | Out-Null
    Write-AgentSkillSpecialistReport -Disposition confirmed -FindingId F-006 -SpecialistVerdict FAIL
    Ingest-AgentSkillFinding -Disposition confirmed -FindingId F-006
    Apply-AgentSkillRepair $false
    Assert-True ((Get-State).Status -eq 'FAIL' -and (Get-State).Next -match 'scope-changing' -and -not (Test-Path -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/repair-evidence-F-006.md'))) 'scope-changing Agent-Skill repair is rejected without Producer edit'

    # Missing independent context is inherited as a Core blocker.
    Start-Case 'independence-block'
    'Approved fixture Skill package revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-AgentSkillCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-AgentSkillRound | Out-Null
    Write-AgentSkillSpecialistReport -Disposition rejected -FindingId F-007
    Ingest-AgentSkillFinding -Disposition rejected -FindingId F-007
    Evaluate-AgentSkillCase $true $false
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Next -match 'independent Evaluator') 'missing independent Evaluator context blocks Agent-Skill verdict'

    # Non-executable Skills explicitly record applicability and can pass.
    Start-Case 'no-executable-axis'
    'Approved fixture Skill package revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-AgentSkillCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-AgentSkillRound -Executable $false | Out-Null
    Write-AgentSkillSpecialistReport -Disposition rejected -FindingId F-008
    Ingest-AgentSkillFinding -Disposition rejected -FindingId F-008
    Evaluate-AgentSkillCase $true $true
    $noExecProducer = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/producer-evidence.md')
    Assert-True ((Get-State).Status -eq 'PASS' -and $noExecProducer -match 'Executable axis: not applicable') 'non-executable Skill records explicit executable-axis applicability'

    # Maximum-round stop remains owned by generic Core.
    Start-Case 'maximum-round'
    'Approved fixture Skill package revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-AgentSkillCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-AgentSkillRound | Out-Null
    Write-AgentSkillSpecialistReport -Disposition rejected -FindingId F-009
    Ingest-AgentSkillFinding -Disposition rejected -FindingId F-009
    Evaluate-AgentSkillCase $false $true $true $true 1
    $limitEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-AgentSkillEvaluatorRecord -Text $limitEvaluator -OverallOutcome BLOCKED -ExecutableOutcome BLOCKED -Name 'maximum-round Agent-Skill Evaluator records all axes and valid labels'
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Raw -match 'maximum rounds') 'maximum repair round returns generic Core BLOCKED'

    Write-Output ("AGENT_SKILL_PROFILE_BEHAVIOR_TESTS=PASS ($script:passed assertions)")
    Write-Output 'Evidence class: executable protocol runner in fresh disposable fixtures; host-model role independence remains a separate acceptance gate.'
}
finally {
    if (Test-Path -LiteralPath $root) { Remove-Item -Recurse -Force -LiteralPath $root }
}
