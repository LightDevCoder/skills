[CmdletBinding()]
param(
    [string]$SkillRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'protocol-test-helpers.ps1')

if ([string]::IsNullOrWhiteSpace($SkillRoot)) {
    $scriptRoot = if (-not [string]::IsNullOrWhiteSpace($PSScriptRoot)) {
        $PSScriptRoot
    }
    else {
        Split-Path -Parent $MyInvocation.MyCommand.Path
    }
    $SkillRoot = Join-Path $scriptRoot '..'
}
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path

$root = Join-Path ([IO.Path]::GetTempPath()) ("review-loop-software-" + [guid]::NewGuid().ToString('N'))
$script:caseRoot = $null
$script:passed = 0

function Assert-True {
    param([bool]$Condition, [string]$Name)
    if (-not $Condition) { throw "FAIL: $Name" }
    $script:passed++
    Write-Output "PASS: $Name"
}

function Get-State {
    return Get-ReviewState -CaseRoot $script:caseRoot
}

function Set-SoftwareState {
    param(
        [ValidateSet('INIT', 'READY', 'CRITIC', 'REPAIR', 'EVALUATE', 'PASS', 'FAIL', 'BLOCKED')]
        [string]$Status,
        [int]$Round,
        [string]$NextAction,
        [string]$Blocker = 'none',
        [string]$CharterRevision = ''
    )
    $current = Get-State
    if ([string]::IsNullOrWhiteSpace($CharterRevision)) {
        $CharterRevision = $current.CharterRevision
    }
    if ([string]::IsNullOrWhiteSpace($CharterRevision)) {
        $CharterRevision = 'software-fixture-1'
    }
    Set-ReviewState -CaseRoot $script:caseRoot -Status $Status -Round $Round -NextAction $NextAction -Profile software -CharterRevision $CharterRevision -VerdictOwner 'review-loop Core' -LastCompletedAction 'executable software protocol scenario' -Blocker $Blocker
}

function Start-Case {
    param([string]$Name)
    $script:caseRoot = New-ReviewCase -Root $root -Name $Name -Profile software
}

function Initialize-SoftwareCase {
    param([string]$AcceptanceSource)
    if (-not (Test-Path -LiteralPath $AcceptanceSource -PathType Leaf)) {
        Set-SoftwareState 'BLOCKED' 0 'record missing acceptance source' 'missing acceptance source'
        return
    }
    @(
        '# Acceptance Charter'
        '- Approval state: approved'
        '- Profile: software'
        '- Charter revision: approved-software-spec-r7'
        '- Fixed point: abc1234'
        '- Acceptance source: acceptance.md'
    ) | Set-Content -LiteralPath (Join-Path $script:caseRoot '.review-loop/charter.md')
    Set-SoftwareState 'READY' 0 'collect Producer evidence' 'none' 'approved-software-spec-r7'
}

function Start-Round {
    return New-ReviewRound -CaseRoot $script:caseRoot -Profile software -NextAction 'request read-only Critic and code-review specialist' -ProducerEvidence @(
        'Scope: disposable software fixture acceptance target'
        'Profile: software'
        'Fixed point: abc1234'
        'Evidence label: behavioral'
        'Focused test: fixture assertions'
    )
}

function Start-NextRound {
    New-ReviewNextRound -CaseRoot $script:caseRoot -Profile software -NextAction 'validate existing Finding ID and request code-review recheck' -ProducerEvidence @(
        "Scope: same frozen software target; next round"
        'Evidence label: behavioral'
        'Focused test: fixture assertions after bounded repair'
    ) | Out-Null
}

function Write-CodeReviewReport {
    param(
        [ValidateSet('confirmed', 'rejected')][string]$Disposition = 'confirmed',
        [string]$StandardsFindingId = 'F-001',
        [string]$SpecFindingId = 'F-002',
        [ValidateSet('Critical', 'High', 'Medium', 'Low')][string]$StandardsSeverity = 'High',
        [ValidateSet('Critical', 'High', 'Medium', 'Low')][string]$SpecSeverity = 'Medium',
        [string]$StandardsSourceFindingReference = 'CR-STD-001',
        [string]$SpecSourceFindingReference = 'CR-SPEC-001',
        [string]$SpecialistVerdict = 'PASS'
    )
    $state = Get-State
    if ($state.Status -ne 'CRITIC') { throw 'code-review report requires CRITIC state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    @(
        '# code-review Standards report'
        '- Fixed point: abc1234'
        '- Axis: Standards'
        "- Source finding reference: $StandardsSourceFindingReference"
        "- Stable candidate ID: $StandardsFindingId"
        "- Severity: $StandardsSeverity"
        "- Disposition candidate: $Disposition"
        "- Specialist verdict: $SpecialistVerdict"
        '- Evidence label: review'
    ) | Set-Content -LiteralPath (Join-Path $roundPath 'code-review-standards.md')
    @(
        '# code-review Spec report'
        '- Fixed point: abc1234'
        '- Axis: Spec'
        "- Source finding reference: $SpecSourceFindingReference"
        "- Stable candidate ID: $SpecFindingId"
        "- Severity: $SpecSeverity"
        "- Disposition candidate: $Disposition"
        "- Specialist verdict: $SpecialistVerdict"
        '- Evidence label: review'
    ) | Set-Content -LiteralPath (Join-Path $roundPath 'code-review-spec.md')
}

function Ingest-CodeReviewFindings {
    param(
        [ValidateSet('confirmed', 'rejected')][string]$StandardsDisposition = 'confirmed',
        [ValidateSet('confirmed', 'rejected')][string]$SpecDisposition = 'confirmed',
        [string]$StandardsFindingId = 'F-001',
        [string]$SpecFindingId = 'F-002',
        [string]$StandardsSeverity = '',
        [string]$SpecSeverity = '',
        [string]$StandardsSourceFindingReference = 'CR-STD-001',
        [string]$SpecSourceFindingReference = 'CR-SPEC-001'
    )
    $state = Get-State
    if ($state.Status -ne 'CRITIC') { throw 'Finding ingestion requires CRITIC state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    $standardsReport = Get-Content -Raw -LiteralPath (Join-Path $roundPath 'code-review-standards.md')
    $specReport = Get-Content -Raw -LiteralPath (Join-Path $roundPath 'code-review-spec.md')
    if ($standardsReport -notmatch 'Axis: Standards' -or $specReport -notmatch 'Axis: Spec') {
        throw 'code-review must retain separate Standards and Spec reports'
    }
    $parsedStandardsSeverity = [regex]::Match($standardsReport, '(?m)^- Severity: (Critical|High|Medium|Low)').Groups[1].Value
    $parsedSpecSeverity = [regex]::Match($specReport, '(?m)^- Severity: (Critical|High|Medium|Low)').Groups[1].Value
    if ([string]::IsNullOrWhiteSpace($parsedStandardsSeverity) -or [string]::IsNullOrWhiteSpace($parsedSpecSeverity)) {
        throw 'code-review reports must retain severity metadata'
    }
    if ((-not [string]::IsNullOrWhiteSpace($StandardsSeverity) -and $StandardsSeverity -ne $parsedStandardsSeverity) -or (-not [string]::IsNullOrWhiteSpace($SpecSeverity) -and $SpecSeverity -ne $parsedSpecSeverity)) {
        throw 'provided severity expectations do not match code-review reports'
    }
    if ($standardsReport -notmatch "Stable candidate ID: $StandardsFindingId" -or $specReport -notmatch "Stable candidate ID: $SpecFindingId" -or $standardsReport -notmatch "Source finding reference: $StandardsSourceFindingReference" -or $specReport -notmatch "Source finding reference: $SpecSourceFindingReference") {
        throw 'code-review reports must retain stable candidate IDs'
    }
    $registry = Join-Path $script:caseRoot '.review-loop/findings.md'
    if (Test-Path -LiteralPath $registry) {
        @(
            "Re-observed $StandardsFindingId in round $($state.Round)"
            'Source: code-review; Axis: Standards; Source finding reference: ' + $StandardsSourceFindingReference
            'Severity: ' + $parsedStandardsSeverity
            "Disposition: $StandardsDisposition"
            "Re-observed $SpecFindingId in round $($state.Round)"
            'Source: code-review; Axis: Spec; Source finding reference: ' + $SpecSourceFindingReference
            'Severity: ' + $parsedSpecSeverity
            "Disposition: $SpecDisposition"
            'Evidence label: review'
        ) | Add-Content -LiteralPath $registry
    }
    else {
        @(
            '# Finding Registry'
            "Finding $StandardsFindingId"
            'Source: code-review; Axis: Standards; Source finding reference: ' + $StandardsSourceFindingReference
            'Severity: ' + $parsedStandardsSeverity
            "Disposition: $StandardsDisposition"
            "Finding $SpecFindingId"
            'Source: code-review; Axis: Spec; Source finding reference: ' + $SpecSourceFindingReference
            'Severity: ' + $parsedSpecSeverity
            "Disposition: $SpecDisposition"
            'Evidence label: review'
            'Resolution evidence: pending fresh Evaluator'
        ) | Set-Content -LiteralPath $registry
    }
    if ($StandardsDisposition -eq 'confirmed' -or $SpecDisposition -eq 'confirmed') {
        Set-SoftwareState 'REPAIR' $state.Round 'direct bounded repair to Producer'
    }
    else {
        Set-SoftwareState 'EVALUATE' $state.Round 'request fresh Evaluator'
    }
}

function Get-AllFindingIds {
    $registryPath = Join-Path $script:caseRoot '.review-loop/findings.md'
    if (-not (Test-Path -LiteralPath $registryPath)) { return @() }
    $order = [System.Collections.Generic.List[string]]::new()
    foreach ($line in (Get-Content -LiteralPath $registryPath)) {
        $findingMatch = [regex]::Match($line, '^(?:Finding|Re-observed) (F-\d{3})(?:\s|$)')
        if ($findingMatch.Success -and -not $order.Contains($findingMatch.Groups[1].Value)) {
            $order.Add($findingMatch.Groups[1].Value)
        }
    }
    return @($order)
}

function Get-ConfirmedFindingIds {
    $registryPath = Join-Path $script:caseRoot '.review-loop/findings.md'
    if (-not (Test-Path -LiteralPath $registryPath)) { return @() }
    $currentId = ''
    $currentDisposition = ''
    $order = [System.Collections.Generic.List[string]]::new()
    $latestDisposition = @{}
    foreach ($line in (Get-Content -LiteralPath $registryPath)) {
        $findingMatch = [regex]::Match($line, '^(?:Finding|Re-observed) (F-\d{3})(?:\s|$)')
        if ($findingMatch.Success) {
            if (-not [string]::IsNullOrWhiteSpace($currentId)) {
                $latestDisposition[$currentId] = $currentDisposition
            }
            $currentId = $findingMatch.Groups[1].Value
            $currentDisposition = ''
            if (-not $order.Contains($currentId)) { $order.Add($currentId) }
            continue
        }
        $dispositionMatch = [regex]::Match($line, '^Disposition: (confirmed|rejected)')
        if ($dispositionMatch.Success) {
            $currentDisposition = $dispositionMatch.Groups[1].Value
        }
    }
    if (-not [string]::IsNullOrWhiteSpace($currentId)) {
        $latestDisposition[$currentId] = $currentDisposition
    }
    return @($order | Where-Object { $latestDisposition[$_] -eq 'confirmed' })
}

function Apply-Repair {
    param([bool]$InScope)
    $state = Get-State
    if ($state.Status -ne 'REPAIR') { throw 'Repair requires REPAIR state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    if (-not $InScope) {
        Set-SoftwareState 'FAIL' $state.Round 'scope-changing repair rejected'
        return
    }
    $findingIds = @(Get-ConfirmedFindingIds)
    if ($findingIds.Count -eq 0) { throw 'Repair requires at least one confirmed finding' }
    foreach ($findingId in $findingIds) {
        @(
            "Finding: $findingId"
            "Stable finding ID: $findingId"
            'Producer repair evidence: bounded and in-scope'
            'Changed scope: existing implementation only'
            'Validation: focused behavioral and negative fixture scenarios'
            'Evidence label: behavioral'
        ) | Set-Content -LiteralPath (Join-Path $roundPath "repair-evidence-$findingId.md")
    }
    Set-SoftwareState 'EVALUATE' $state.Round 'request fresh Evaluator'
}

function Write-SoftwareEvaluatorVerdict {
    param(
        [Parameter(Mandatory)][string]$Outcome,
        [Parameter(Mandatory)][string]$ContextIdentity,
        [Parameter(Mandatory)][string]$StandardsOutcome,
        [Parameter(Mandatory)][string]$SpecOutcome,
        [Parameter(Mandatory)][string]$BehaviorOutcome,
        [Parameter(Mandatory)][string]$SafetyOutcome,
        [Parameter(Mandatory)][string]$BlockingFindings
    )
    $state = Get-State
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
    $records = @(
        '# Evaluator Verdict - Round ' + ('{0:d2}' -f $state.Round)
        "Context identity: $ContextIdentity"
        "Charter revision: $($state.CharterRevision); Profile: software"
        "Criterion AC-1 (Standards): $StandardsOutcome - Evidence: [code-review-standards.md](code-review-standards.md) | Label: review | Outcome: $StandardsOutcome"
        "Criterion AC-2 (Spec fidelity): $SpecOutcome - Evidence: [code-review-spec.md](code-review-spec.md) | Label: review | Outcome: $SpecOutcome"
        "Criterion AC-3 (behavioral correctness): $BehaviorOutcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: behavioral | Outcome: $BehaviorOutcome"
        "Criterion AC-4 (operational safety): $SafetyOutcome - Evidence: [producer-evidence.md](producer-evidence.md) | Label: behavioral | Outcome: $SafetyOutcome"
        'Evidence links and labels:'
        '- [code-review-standards.md](code-review-standards.md) | Label: review'
        '- [code-review-spec.md](code-review-spec.md) | Label: review'
        '- [producer-evidence.md](producer-evidence.md) | Label: behavioral'
    )
    foreach ($findingId in (Get-AllFindingIds)) {
        $repairName = "repair-evidence-$findingId.md"
        $repairPath = Join-Path $roundPath $repairName
        if (Test-Path -LiteralPath $repairPath) {
            $records += "- [$repairName]($repairName) | Label: behavioral"
        }
    }
    $records += @(
        "Open blocking findings: $BlockingFindings"
        "Outcome: $Outcome"
        "Verdict recommendation: $Outcome"
    )
    $path = Join-Path $roundPath 'evaluator-verdict.md'
    $records | Set-Content -LiteralPath $path
    return $path
}

function Assert-EvaluatorRecord {
    param(
        [Parameter(Mandatory)][string]$Text,
        [Parameter(Mandatory)][ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$OverallOutcome,
        [Parameter(Mandatory)][ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$StandardsOutcome,
        [Parameter(Mandatory)][ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$SpecOutcome,
        [Parameter(Mandatory)][ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$BehaviorOutcome,
        [Parameter(Mandatory)][ValidateSet('PASS', 'FAIL', 'BLOCKED')][string]$SafetyOutcome,
        [Parameter(Mandatory)][string]$Name
    )
    $patterns = @(
        "(?m)^Criterion AC-1 .*Evidence: \[code-review-standards\.md\]\(code-review-standards\.md\) \| Label: review \| Outcome: $StandardsOutcome\r?$"
        "(?m)^Criterion AC-2 .*Evidence: \[code-review-spec\.md\]\(code-review-spec\.md\) \| Label: review \| Outcome: $SpecOutcome\r?$"
        "(?m)^Criterion AC-3 .*Evidence: \[producer-evidence\.md\]\(producer-evidence\.md\) \| Label: behavioral \| Outcome: $BehaviorOutcome\r?$"
        "(?m)^Criterion AC-4 .*Evidence: \[producer-evidence\.md\]\(producer-evidence\.md\) \| Label: behavioral \| Outcome: $SafetyOutcome\r?$"
        "(?m)^Outcome: $OverallOutcome\r?$"
    )
    $allMatch = @($patterns | Where-Object { $Text -notmatch $_ }).Count -eq 0
    Assert-True $allMatch $Name
}

function Evaluate-Case {
    param(
        [bool]$Pass,
        [bool]$IndependentContext,
        [bool]$RepairAvailable,
        [int]$MaximumRound = 3
    )
    $state = Get-State
    if ($state.Status -ne 'EVALUATE') { throw 'Evaluation requires EVALUATE state' }
    if (-not $IndependentContext) {
        Write-SoftwareEvaluatorVerdict -Outcome BLOCKED -ContextIdentity 'unavailable independent read-only Evaluator' -StandardsOutcome BLOCKED -SpecOutcome BLOCKED -BehaviorOutcome BLOCKED -SafetyOutcome BLOCKED -BlockingFindings 'independent context unavailable' | Out-Null
        Set-SoftwareState 'BLOCKED' $state.Round 'obtain independent Evaluator context' 'independent context unavailable'
        return
    }
    if ($Pass) {
        $findingIds = Get-ConfirmedFindingIds
        $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
        $findingPath = Join-Path $script:caseRoot '.review-loop/findings.md'
        foreach ($findingId in $findingIds) {
            $repairName = "repair-evidence-$findingId.md"
            if (-not (Test-Path -LiteralPath (Join-Path $roundPath $repairName))) {
                throw "Missing per-finding repair evidence: $repairName"
            }
            @(
                "Finding ${findingId}: Status: resolved"
                'Resolution evidence: fresh independent Evaluator'
                "Repair evidence: rounds/round-$('{0:d2}' -f $state.Round)/$repairName"
            ) | Add-Content -LiteralPath $findingPath
        }
        Write-SoftwareEvaluatorVerdict -Outcome PASS -ContextIdentity 'fresh independent read-only Evaluator' -StandardsOutcome PASS -SpecOutcome PASS -BehaviorOutcome PASS -SafetyOutcome PASS -BlockingFindings 'none' | Out-Null
        $evaluatorVerdict = Get-Content -Raw -LiteralPath (Join-Path $roundPath 'evaluator-verdict.md')
        if ($evaluatorVerdict -notmatch 'Criterion AC-1 \(Standards\): PASS' -or $evaluatorVerdict -notmatch 'Criterion AC-2 \(Spec fidelity\): PASS' -or $evaluatorVerdict -notmatch 'Criterion AC-3 \(behavioral correctness\): PASS' -or $evaluatorVerdict -notmatch 'Criterion AC-4 \(operational safety\): PASS') {
            throw 'Evaluator verdict must record criterion-by-criterion software judgments before Core PASS'
        }
        @(
            '# Review Loop Verdict'
            'Verdict: PASS'
            'Issued by: review-loop Core'
            'Evaluator: fresh independent read-only context'
            'Specialist input: code-review Standards + Spec findings'
        ) | Set-Content -LiteralPath (Join-Path $script:caseRoot '.review-loop/verdict.md')
        Set-SoftwareState 'PASS' $state.Round 'preserve Core verdict'
        return
    }
    if ($RepairAvailable -and $state.Round -lt $MaximumRound) {
        Write-SoftwareEvaluatorVerdict -Outcome FAIL -ContextIdentity 'fresh independent read-only Evaluator' -StandardsOutcome FAIL -SpecOutcome FAIL -BehaviorOutcome PASS -SafetyOutcome PASS -BlockingFindings 'confirmed code-review findings' | Out-Null
        Set-SoftwareState 'FAIL' $state.Round 'CRITIC (next round); bounded repair remains'
    }
    else {
        Write-SoftwareEvaluatorVerdict -Outcome BLOCKED -ContextIdentity 'fresh independent read-only Evaluator' -StandardsOutcome BLOCKED -SpecOutcome BLOCKED -BehaviorOutcome BLOCKED -SafetyOutcome BLOCKED -BlockingFindings 'repair limit reached' | Out-Null
        Set-SoftwareState 'BLOCKED' $state.Round 'repair limit reached' 'maximum rounds or no permitted repair'
    }
}

try {
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    $installedRoot = Join-Path $root 'installed-review-loop'
    Copy-Item -Recurse -Force -LiteralPath $SkillRoot -Destination $installedRoot
    Assert-True (Test-Path -LiteralPath (Join-Path $installedRoot 'references/profiles/software.md')) 'fresh install includes software Profile'

    # Integration and verdict ownership: specialist output is evidence, not a verdict.
    Start-Case 'integration'
    $acceptance = Join-Path $script:caseRoot 'acceptance.md'
    'Approved software Spec revision 1' | Set-Content -LiteralPath $acceptance
    Initialize-SoftwareCase $acceptance
    Assert-True ((Get-State).CharterRevision -eq 'approved-software-spec-r7') 'software init freezes approved Charter revision'
    Start-Round | Out-Null
    Write-CodeReviewReport -Disposition confirmed -StandardsFindingId 'F-001' -SpecFindingId 'F-002' -SpecialistVerdict PASS
    Assert-True ((Get-State).Status -eq 'CRITIC') 'code-review specialist PASS does not set final state'
    Ingest-CodeReviewFindings -StandardsDisposition confirmed -SpecDisposition confirmed -StandardsFindingId 'F-001' -SpecFindingId 'F-002'
    Assert-True ((Get-State).Status -eq 'REPAIR') 'code-review findings enter generic REPAIR lifecycle'
    $registry = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')
    $standardsReport = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/code-review-standards.md')
    $specReport = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/code-review-spec.md')
    Assert-True ($standardsReport -match 'Axis: Standards' -and $standardsReport -match 'Source finding reference: CR-STD-001' -and $standardsReport -match 'Stable candidate ID: F-001' -and $standardsReport -match 'Severity: High' -and $specReport -match 'Axis: Spec' -and $specReport -match 'Source finding reference: CR-SPEC-001' -and $specReport -match 'Stable candidate ID: F-002' -and $specReport -match 'Severity: Medium') 'separate specialist reports retain axis, source reference, severity, and stable ID'
    Assert-True ($registry -match 'Axis: Standards' -and $registry -match 'CR-STD-001' -and $registry -match 'Axis: Spec' -and $registry -match 'CR-SPEC-001' -and $registry -match 'Severity: High' -and $registry -match 'Severity: Medium' -and $registry -match 'Evidence label: review') 'specialist metadata enters generic finding registry'
    Apply-Repair $true
    Evaluate-Case $true $true $true
    $evaluatorVerdict = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    $verdict = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/verdict.md')
    Assert-EvaluatorRecord -Text $evaluatorVerdict -OverallOutcome PASS -StandardsOutcome PASS -SpecOutcome PASS -BehaviorOutcome PASS -SafetyOutcome PASS -Name 'fresh Evaluator records every criterion with linked evidence, labels, and PASS outcome'
    Assert-True ((Get-State).Status -eq 'PASS' -and $verdict -match 'Issued by: review-loop Core' -and $verdict -notmatch 'Issued by: code-review') 'Core owns final PASS verdict'

    # Bounded repair preserves FAIL and reuses the same stable finding ID.
    Start-Case 'bounded-repair'
    'Approved software Spec revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SoftwareCase (Join-Path $script:caseRoot 'acceptance.md')
    Assert-True ((Get-State).CharterRevision -eq 'approved-software-spec-r7') 'bounded repair starts from approved Charter revision'
    Start-Round | Out-Null
    Write-CodeReviewReport -Disposition confirmed -StandardsFindingId 'F-001' -SpecFindingId 'F-002' -SpecialistVerdict FAIL
    Ingest-CodeReviewFindings -StandardsDisposition confirmed -SpecDisposition confirmed -StandardsFindingId 'F-001' -SpecFindingId 'F-002'
    Apply-Repair $true
    Evaluate-Case $false $true $true
    $charterRevision = (Get-State).CharterRevision
    Assert-True ($charterRevision -eq 'approved-software-spec-r7') 'failed round retains exact approved Charter revision'
    Assert-True ((Get-State).Status -eq 'FAIL' -and (Get-State).Next -match 'next round') 'failed evaluation preserves bounded next-round path'
    Start-NextRound
    Assert-True ((Get-State).CharterRevision -eq $charterRevision -and (Get-State).CharterRevision -eq 'approved-software-spec-r7') 'next round preserves exact frozen Charter revision'
    Write-CodeReviewReport -Disposition confirmed -StandardsFindingId 'F-001' -SpecFindingId 'F-002' -SpecialistVerdict PASS
    Ingest-CodeReviewFindings -StandardsDisposition confirmed -SpecDisposition confirmed -StandardsFindingId 'F-001' -SpecFindingId 'F-002'
    Apply-Repair $true
    Evaluate-Case $true $true $true
    $registry = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')
    $repairEvidenceStandards = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/repair-evidence-F-001.md')
    $repairEvidenceSpec = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/repair-evidence-F-002.md')
    $evaluatorVerdict = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/evaluator-verdict.md')
    $firstRoundEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-EvaluatorRecord -Text $firstRoundEvaluator -OverallOutcome FAIL -StandardsOutcome FAIL -SpecOutcome FAIL -BehaviorOutcome PASS -SafetyOutcome PASS -Name 'failed Evaluator record includes every criterion with linked evidence, labels, and FAIL outcome'
    Assert-True ((Get-State).Status -eq 'PASS' -and ([regex]::Matches($registry, '(?m)^Finding F-001\r?$')).Count -eq 1 -and ([regex]::Matches($registry, '(?m)^Finding F-002\r?$')).Count -eq 1 -and ([regex]::Matches($registry, 'CR-STD-001')).Count -eq 2 -and ([regex]::Matches($registry, 'CR-SPEC-001')).Count -eq 2 -and $registry -match 'Re-observed F-001' -and $registry -match 'Re-observed F-002' -and $registry -match 'Finding F-001: Status: resolved' -and $registry -match 'Finding F-002: Status: resolved' -and $registry -match 'Resolution evidence: fresh independent Evaluator' -and $repairEvidenceStandards -match 'Finding: F-001' -and $repairEvidenceSpec -match 'Finding: F-002' -and $evaluatorVerdict -match '\]\(repair-evidence-F-001\.md\)' -and $evaluatorVerdict -match '\]\(repair-evidence-F-002\.md\)') 'bounded repair resolves every specialist ID with per-ID evidence and final evaluation'
    Assert-EvaluatorRecord -Text $evaluatorVerdict -OverallOutcome PASS -StandardsOutcome PASS -SpecOutcome PASS -BehaviorOutcome PASS -SafetyOutcome PASS -Name 'bounded repair final Evaluator record includes every criterion with linked evidence, labels, and PASS outcome'

    # A repair that changes frozen scope is rejected before Producer edits.
    Start-Case 'scope-changing-repair'
    'Approved software Spec revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SoftwareCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-Round | Out-Null
    Write-CodeReviewReport -Disposition confirmed -StandardsFindingId 'F-003' -SpecFindingId 'F-004' -SpecialistVerdict FAIL
    Ingest-CodeReviewFindings -StandardsDisposition confirmed -SpecDisposition confirmed -StandardsFindingId 'F-003' -SpecFindingId 'F-004'
    Apply-Repair $false
    Assert-True ((Get-State).Status -eq 'FAIL' -and (Get-State).Next -match 'scope-changing' -and -not (Test-Path -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/repair-evidence.md'))) 'scope-changing repair is rejected without Producer edit'

    # Missing independent context blocks even a specialist PASS.
    Start-Case 'independence-block'
    'Approved software Spec revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SoftwareCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-Round | Out-Null
    Write-CodeReviewReport -Disposition rejected -StandardsFindingId 'F-005' -SpecFindingId 'F-006' -SpecialistVerdict PASS
    Ingest-CodeReviewFindings -StandardsDisposition rejected -SpecDisposition rejected -StandardsFindingId 'F-005' -SpecFindingId 'F-006'
    Evaluate-Case $true $false $false
    $blockedEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Next -match 'independent Evaluator') 'missing independent context blocks specialist conclusion'
    Assert-EvaluatorRecord -Text $blockedEvaluator -OverallOutcome BLOCKED -StandardsOutcome BLOCKED -SpecOutcome BLOCKED -BehaviorOutcome BLOCKED -SafetyOutcome BLOCKED -Name 'independence BLOCKED Evaluator record includes every criterion with linked evidence, labels, and BLOCKED outcome'

    # A later rejected recheck supersedes an earlier confirmed disposition.
    Start-Case 'rejected-recheck'
    'Approved software Spec revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SoftwareCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-Round | Out-Null
    Write-CodeReviewReport -Disposition confirmed -StandardsFindingId 'F-009' -SpecFindingId 'F-010' -StandardsSeverity Critical -SpecSeverity Low -SpecialistVerdict FAIL
    Ingest-CodeReviewFindings -StandardsDisposition confirmed -SpecDisposition confirmed -StandardsFindingId 'F-009' -SpecFindingId 'F-010' -StandardsSeverity Critical -SpecSeverity Low
    $initialRegistry = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')
    Assert-True ($initialRegistry -match 'Finding F-009' -and $initialRegistry -match 'Severity: Critical' -and $initialRegistry -match 'Finding F-010' -and $initialRegistry -match 'Severity: Low') 'specialist Critical and Low severities enter registry exactly'
    Apply-Repair $true
    Evaluate-Case $false $true $true
    Start-NextRound
    Write-CodeReviewReport -Disposition rejected -StandardsFindingId 'F-009' -SpecFindingId 'F-010' -StandardsSeverity Critical -SpecSeverity Low -SpecialistVerdict PASS
    Ingest-CodeReviewFindings -StandardsDisposition rejected -SpecDisposition rejected -StandardsFindingId 'F-009' -SpecFindingId 'F-010' -StandardsSeverity Critical -SpecSeverity Low
    Assert-True (@(Get-ConfirmedFindingIds).Count -eq 0) 'rejected recheck removes IDs from confirmed repair set'
    Evaluate-Case $true $true $false
    $recheckRegistry = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')
    $recheckEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/evaluator-verdict.md')
    Assert-True ((Get-State).Status -eq 'PASS' -and $recheckRegistry -match 'Re-observed F-009' -and $recheckRegistry -match 'Re-observed F-010' -and $recheckRegistry -match 'Disposition: rejected' -and ([regex]::Matches($recheckRegistry, 'Severity: Critical')).Count -eq 2 -and ([regex]::Matches($recheckRegistry, 'Severity: Low')).Count -eq 2 -and -not (Test-Path -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/repair-evidence-F-009.md')) -and -not (Test-Path -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/repair-evidence-F-010.md'))) 'rejected recheck reaches PASS without stale repair evidence'
    Assert-EvaluatorRecord -Text $recheckEvaluator -OverallOutcome PASS -StandardsOutcome PASS -SpecOutcome PASS -BehaviorOutcome PASS -SafetyOutcome PASS -Name 'rejected recheck PASS Evaluator record includes every criterion with linked evidence, labels, and PASS outcome'

    # Maximum-round BLOCKED records retain every criterion and evidence link.
    Start-Case 'maximum-round'
    'Approved software Spec revision 1' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-SoftwareCase (Join-Path $script:caseRoot 'acceptance.md')
    Start-Round | Out-Null
    Write-CodeReviewReport -Disposition confirmed -StandardsFindingId 'F-007' -SpecFindingId 'F-008' -SpecialistVerdict FAIL
    Ingest-CodeReviewFindings -StandardsDisposition confirmed -SpecDisposition confirmed -StandardsFindingId 'F-007' -SpecFindingId 'F-008'
    Apply-Repair $true
    Evaluate-Case $false $true $true 1
    $limitEvaluator = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/evaluator-verdict.md')
    Assert-True ((Get-State).Status -eq 'BLOCKED') 'maximum-round stop returns BLOCKED'
    Assert-EvaluatorRecord -Text $limitEvaluator -OverallOutcome BLOCKED -StandardsOutcome BLOCKED -SpecOutcome BLOCKED -BehaviorOutcome BLOCKED -SafetyOutcome BLOCKED -Name 'maximum-round BLOCKED Evaluator record includes every criterion with linked evidence, labels, and BLOCKED outcome'

    Write-Output ("SOFTWARE_PROFILE_BEHAVIOR_TESTS=PASS ($script:passed assertions)")
    Write-Output 'Evidence class: executable protocol runner in fresh disposable fixtures; host-model role independence remains a separate acceptance gate.'
}
finally {
    if (Test-Path -LiteralPath $root) {
        Remove-Item -Recurse -Force -LiteralPath $root
    }
}
