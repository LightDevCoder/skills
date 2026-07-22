[CmdletBinding()]
param(
    [string]$SkillRoot = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'protocol-test-helpers.ps1')

if ([string]::IsNullOrWhiteSpace($SkillRoot)) {
    $scriptRoot = $PSScriptRoot
    if ([string]::IsNullOrWhiteSpace($scriptRoot)) {
        $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    }
    $SkillRoot = Join-Path $scriptRoot '..'
}
$SkillRoot = (Resolve-Path $SkillRoot).Path

$root = Join-Path ([IO.Path]::GetTempPath()) ("review-loop-behavior-" + [guid]::NewGuid().ToString('N'))
$installRoot = Join-Path $root 'installed-review-loop'
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

function Set-ProtocolState {
    param([string]$Target, [int]$Round, [string]$NextAction, [string]$CharterRevision = '')
    $current = Get-State
    if ([string]::IsNullOrWhiteSpace($CharterRevision)) {
        $CharterRevision = $current.CharterRevision
    }
    if ([string]::IsNullOrWhiteSpace($CharterRevision)) {
        $CharterRevision = 'fixture-1'
    }
    Set-ReviewState -CaseRoot $script:caseRoot -Status $Target -Round $Round -NextAction $NextAction -Profile generic -CharterRevision $CharterRevision -LastCompletedAction 'protocol transition' -Blocker $(if ($Target -eq 'BLOCKED') { $NextAction } else { 'none' })
}

function Start-Case {
    param([string]$Name)
    $script:caseRoot = New-ReviewCase -Root $root -Name $Name -Profile generic
}

function Initialize-Case {
    param([string]$AcceptanceSource)
    if (-not (Test-Path -LiteralPath $AcceptanceSource)) {
        Set-ProtocolState 'BLOCKED' 0 'record missing acceptance source'
        return
    }
    Set-ProtocolState 'READY' 0 'collect Producer evidence'
}

function Resume-SourceBlocked {
    $state = Get-State
    if ($state.Status -ne 'BLOCKED') { throw 'Resume-Blocked requires BLOCKED state' }
    if ($state.Next -notmatch 'missing acceptance source') { throw 'Resume-SourceBlocked requires a source blocker' }
    Set-ProtocolState 'READY' $state.Round 'collect Producer evidence'
}

function Start-Round {
    return New-ReviewRound -CaseRoot $script:caseRoot -Profile generic -NextAction 'request read-only Critic' -ProducerEvidence @(
        'Scope: disposable fixture acceptance target'
        'Evidence class: executable protocol scenario'
        'Inputs: approved acceptance source and fixture artifact'
    )
}

function Record-Candidate {
    param([string]$Id, [ValidateSet('confirmed', 'rejected')][string]$Disposition)
    if ((Get-State).Status -ne 'CRITIC') { throw 'Candidates require CRITIC state' }
    if ($Id -notmatch '^F-\d{3}$') { throw "Invalid finding ID: $Id" }
    $path = Join-Path $script:caseRoot '.review-loop/findings.md'
    if (Test-Path -LiteralPath $path) {
        $existing = Get-Content -Raw -LiteralPath $path
        if ($existing -match "Finding $Id") {
            @("Re-observed $Id in round $((Get-State).Round)", "Disposition: $Disposition", 'Evidence: executable protocol scenario') |
                Add-Content -LiteralPath $path
        } else {
            @("Finding $Id", "Disposition: $Disposition", 'Evidence: executable protocol scenario') |
                Add-Content -LiteralPath $path
        }
    } else {
        @("Finding $Id", "Disposition: $Disposition", 'Evidence: executable protocol scenario') |
            Set-Content -LiteralPath $path
    }
    if ($Disposition -eq 'confirmed') {
        Set-ProtocolState 'REPAIR' (Get-State).Round 'direct bounded repair to Producer'
    } else {
        Set-ProtocolState 'EVALUATE' (Get-State).Round 'fresh Evaluator'
    }
}

function Apply-Repair {
    param([bool]$InScope)
    if ((Get-State).Status -ne 'REPAIR') { throw 'Repairs require REPAIR state' }
    $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f (Get-State).Round)
    if (-not $InScope) {
        Set-ProtocolState 'FAIL' (Get-State).Round 'scope-changing repair rejected'
        return
    }
    $findingId = [regex]::Match((Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')), 'Finding (F-\d{3})').Groups[1].Value
    @(
        "Finding: $findingId"
        'Producer repair evidence: bounded and in-scope'
        'Validation: focused executable protocol scenario'
    ) | Set-Content -LiteralPath (Join-Path $roundPath 'repair-evidence.md')
    Set-ProtocolState 'EVALUATE' (Get-State).Round 'request fresh Evaluator'
}

function Evaluate-Case {
    param([bool]$Pass, [bool]$IndependentContext, [bool]$RepairAvailable, [int]$MaximumRound)
    if ((Get-State).Status -ne 'EVALUATE') { throw 'Evaluation requires EVALUATE state' }
    $state = Get-State
    if (-not $IndependentContext) {
        Set-ProtocolState 'BLOCKED' $state.Round 'obtain independent Evaluator context'
        return
    }
    if ($Pass) {
        $path = Join-Path $script:caseRoot '.review-loop/findings.md'
        if (Test-Path $path) {
            'Status: resolved; Resolution evidence: fresh Evaluator' |
                Add-Content -LiteralPath $path
        }
        $roundPath = Join-Path $script:caseRoot ('.review-loop/rounds/round-{0:d2}' -f $state.Round)
        @(
            '# Evaluator Verdict - Round ' + ('{0:d2}' -f $state.Round)
            'Context: fresh independent read-only Evaluator'
            'Criterion AC-1 (frozen acceptance source): PASS - source and fixture evidence retained'
            'Criterion AC-2 (generic lifecycle): PASS - findings and bounded repair evidence retained'
            'Open blocking findings: none'
            'Verdict recommendation: PASS'
        ) | Set-Content -LiteralPath (Join-Path $roundPath 'evaluator-verdict.md')
        Set-ProtocolState 'PASS' $state.Round 'preserve verdict'
        return
    }
    if ($RepairAvailable -and $state.Round -lt $MaximumRound) {
        Set-ProtocolState 'FAIL' $state.Round 'CRITIC (next round); bounded repair remains'
    } else {
        Set-ProtocolState 'BLOCKED' $state.Round 'repair limit reached'
    }
}

function Resume-NextRound {
    New-ReviewNextRound -CaseRoot $script:caseRoot -Profile generic -NextAction 'validate existing Finding ID' -ProducerEvidence @(
        'Scope: disposable fixture acceptance target; next round'
        'Evidence class: executable protocol scenario'
    ) | Out-Null
}

try {
    New-Item -ItemType Directory -Force -Path $root | Out-Null
    Copy-Item -Recurse -Force -LiteralPath $SkillRoot -Destination $installRoot
    $installedSkill = Join-Path $installRoot 'SKILL.md'
    Assert-True (Test-Path $installedSkill) 'fresh-install discovers SKILL.md'
    Assert-True (Test-Path (Join-Path $installRoot 'agents/openai.yaml')) 'fresh-install discovers metadata'
    $skillText = Get-Content -Raw -LiteralPath $installedSkill
    $stoppingText = Get-Content -Raw -LiteralPath (Join-Path $installRoot 'references/stopping-rules.md')
    Assert-True ($skillText -match '(?i)model-invoked and may also be manually invoked') 'invocation contract is model/manual'
    $stateSection = $stoppingText.Split('Record the Charter')[0]
    Assert-True ($stoppingText -match '(?s)FAIL.*CRITIC \(next round\)' -and $stateSection -notmatch 'SKIPPED') 'state machine documents bounded next round'

    Start-Case 'missing-source'
    $missing = Join-Path $script:caseRoot 'acceptance.md'
    Initialize-Case $missing
    Assert-True ((Get-State).Status -eq 'BLOCKED') 'missing acceptance source blocks init'
    'Approved acceptance source' | Set-Content -LiteralPath $missing
    Resume-SourceBlocked
    Assert-True ((Get-State).Status -eq 'READY') 'resume after source unblock reaches READY'

    Start-Case 'bounded-repair'
    $acceptance = Join-Path $script:caseRoot 'acceptance.md'
    'Approved acceptance source' | Set-Content -LiteralPath $acceptance
    Initialize-Case $acceptance
    Start-Round | Out-Null
    Record-Candidate 'F-001' 'confirmed'
    Apply-Repair $true
    Evaluate-Case $false $true $true 3
    Assert-True ((Get-State).Status -eq 'FAIL' -and (Get-State).Next -match 'next round') 'failed round preserves bounded repair path'
    Resume-NextRound
    Record-Candidate 'F-001' 'confirmed'
    Apply-Repair $true
    Evaluate-Case $true $true $true 3
    $finding = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/findings.md')
    $repairEvidence = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/repair-evidence.md')
    $producerEvidence = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-01/producer-evidence.md')
    $evaluatorVerdict = Get-Content -Raw -LiteralPath (Join-Path $script:caseRoot '.review-loop/rounds/round-02/evaluator-verdict.md')
    Assert-True ((Get-State).Status -eq 'PASS' -and $finding -match 'F-001' -and $finding -match 'Status: resolved' -and $repairEvidence -match 'Finding: F-001' -and $repairEvidence -match 'Validation:' -and $producerEvidence -match 'Evidence class:' -and $evaluatorVerdict -match 'Criterion AC-1.*PASS') 'bounded repair reaches PASS with stable resolved ID'

    Start-Case 'rejected-candidate'
    'Approved acceptance source' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-Case (Join-Path $script:caseRoot 'acceptance.md')
    Start-Round | Out-Null
    Record-Candidate 'F-002' 'rejected'
    Evaluate-Case $true $true $false 3
    Assert-True ((Get-State).Status -eq 'PASS' -and -not (Test-Path (Join-Path $script:caseRoot '.review-loop/rounds/round-01/repair-evidence.md'))) 'rejected candidate bypasses Producer repair'

    Start-Case 'scope-change'
    'Approved acceptance source' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-Case (Join-Path $script:caseRoot 'acceptance.md')
    Start-Round | Out-Null
    Record-Candidate 'F-003' 'confirmed'
    Apply-Repair $false
    Assert-True ((Get-State).Status -eq 'FAIL' -and (Get-State).Next -match 'scope-changing') 'scope-changing repair returns FAIL'

    Start-Case 'missing-context'
    'Approved acceptance source' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-Case (Join-Path $script:caseRoot 'acceptance.md')
    Start-Round | Out-Null
    Record-Candidate 'F-004' 'rejected'
    Evaluate-Case $false $false $false 3
    Assert-True ((Get-State).Status -eq 'BLOCKED') 'missing independent context returns BLOCKED'

    Start-Case 'maximum-round'
    'Approved acceptance source' | Set-Content -LiteralPath (Join-Path $script:caseRoot 'acceptance.md')
    Initialize-Case (Join-Path $script:caseRoot 'acceptance.md')
    Start-Round | Out-Null
    Record-Candidate 'F-005' 'confirmed'
    Apply-Repair $true
    Evaluate-Case $false $true $true 1
    Assert-True ((Get-State).Status -eq 'BLOCKED' -and (Get-State).Next -match 'repair limit') 'maximum-round stop returns BLOCKED'

    Write-Output ("GENERIC_PROFILE_BEHAVIOR_TESTS=PASS ($script:passed assertions)")
    Write-Output 'Evidence class: executable protocol runner in fresh disposable fixtures; host-model role independence remains a separate acceptance gate.'
}
finally {
    if (Test-Path $root) { Remove-Item -Recurse -Force -LiteralPath $root }
}
