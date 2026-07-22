# Shared disposable-fixture and state-machine helpers for protocol runners.
# Dot-source this file from a behavior test; it deliberately has no test cases.

function Get-ReviewState {
    param([Parameter(Mandatory)][string]$CaseRoot)

    $path = Join-Path $CaseRoot '.review-loop/state.md'
    $raw = Get-Content -Raw -LiteralPath $path
    $status = [regex]::Match($raw, '(?m)^Status: ([^\r\n]+)').Groups[1].Value.Trim()
    $round = [int][regex]::Match($raw, '(?m)^Round: (\d+)').Groups[1].Value
    $next = [regex]::Match($raw, '(?m)^Next action: ([^\r\n]+)').Groups[1].Value.Trim()
    $charterRevision = [regex]::Match($raw, '(?m)^Charter revision: ([^\r\n]+)').Groups[1].Value.Trim()
    $profile = [regex]::Match($raw, '(?m)^Profile: ([^\r\n]+)').Groups[1].Value.Trim()
    $owner = [regex]::Match($raw, '(?m)^Verdict owner: ([^\r\n]+)').Groups[1].Value.Trim()
    [pscustomobject]@{
        Status = $status
        Round = $round
        Next = $next
        CharterRevision = $charterRevision
        Profile = $profile
        Owner = $owner
        Raw = $raw
    }
}

function Set-ReviewState {
    param(
        [Parameter(Mandatory)][string]$CaseRoot,
        [Parameter(Mandatory)][ValidateSet('INIT', 'READY', 'CRITIC', 'REPAIR', 'EVALUATE', 'PASS', 'FAIL', 'BLOCKED')][string]$Status,
        [Parameter(Mandatory)][int]$Round,
        [Parameter(Mandatory)][string]$NextAction,
        [string]$Profile = 'generic',
        [string]$CharterRevision = 'fixture-1',
        [string]$VerdictOwner = '',
        [string]$LastCompletedAction = 'protocol transition',
        [string]$Blocker = 'none'
    )

    $current = Get-ReviewState -CaseRoot $CaseRoot
    $allowed = @{
        INIT     = @('READY', 'BLOCKED')
        READY    = @('CRITIC', 'BLOCKED')
        CRITIC   = @('REPAIR', 'EVALUATE', 'BLOCKED')
        REPAIR   = @('EVALUATE', 'FAIL', 'BLOCKED')
        EVALUATE = @('PASS', 'FAIL', 'BLOCKED')
        FAIL     = @('CRITIC', 'BLOCKED')
        BLOCKED  = @('READY', 'CRITIC')
        PASS     = @()
    }
    if (-not ($allowed[$current.Status] -contains $Status)) {
        throw "Invalid transition $($current.Status) -> $Status"
    }
    if ($Status -eq 'CRITIC' -and $Round -lt $current.Round) {
        throw 'Round cannot move backwards'
    }
    $records = @(
        "Status: $Status"
        "Round: $Round"
        "Next action: $NextAction"
        "Charter revision: $CharterRevision"
        "Profile: $Profile"
        'Maximum rounds: 3'
        'Independence declaration: fresh read-only Evaluator required'
    )
    if (-not [string]::IsNullOrWhiteSpace($VerdictOwner)) {
        $records += "Verdict owner: $VerdictOwner"
    }
    $records += @(
        "Last completed action: $LastCompletedAction"
        "Blocker: $Blocker"
        'Evidence label: executable protocol scenario'
    )
    $records | Set-Content -LiteralPath (Join-Path $CaseRoot '.review-loop/state.md')
}

function New-ReviewCase {
    param(
        [Parameter(Mandatory)][string]$Root,
        [Parameter(Mandatory)][string]$Name,
        [string]$Profile = 'generic'
    )

    $caseRoot = Join-Path $Root $Name
    New-Item -ItemType Directory -Force -Path (Join-Path $caseRoot '.review-loop') | Out-Null
    @(
        'Status: INIT'
        'Round: 0'
        'Next action: resolve acceptance source'
        "Profile: $Profile"
    ) | Set-Content -LiteralPath (Join-Path $caseRoot '.review-loop/state.md')
    return $caseRoot
}

function New-ReviewRound {
    param(
        [Parameter(Mandatory)][string]$CaseRoot,
        [Parameter(Mandatory)][string]$Profile,
        [Parameter(Mandatory)][string]$NextAction,
        [Parameter(Mandatory)][string[]]$ProducerEvidence
    )

    $state = Get-ReviewState -CaseRoot $CaseRoot
    if ($state.Status -ne 'READY') { throw 'Review round requires READY state' }
    if ([string]::IsNullOrWhiteSpace($state.CharterRevision)) { throw 'Review round requires a frozen Charter revision' }
    $nextRound = [Math]::Max(1, $state.Round)
    Set-ReviewState -CaseRoot $CaseRoot -Status CRITIC -Round $nextRound -NextAction $NextAction -Profile $Profile -CharterRevision $state.CharterRevision -VerdictOwner $(if ($Profile -in @('software', 'manuscript')) { 'review-loop Core' } else { '' }) -LastCompletedAction 'executable protocol scenario'
    $roundPath = Join-Path $CaseRoot ('.review-loop/rounds/round-{0:d2}' -f $nextRound)
    New-Item -ItemType Directory -Force -Path $roundPath | Out-Null
    $ProducerEvidence | Set-Content -LiteralPath (Join-Path $roundPath 'producer-evidence.md')
    return $roundPath
}

function New-ReviewNextRound {
    param(
        [Parameter(Mandatory)][string]$CaseRoot,
        [Parameter(Mandatory)][string]$Profile,
        [Parameter(Mandatory)][string]$NextAction,
        [Parameter(Mandatory)][string[]]$ProducerEvidence
    )

    $state = Get-ReviewState -CaseRoot $CaseRoot
    if ($state.Status -ne 'FAIL') { throw 'Next round requires FAIL state' }
    if ([string]::IsNullOrWhiteSpace($state.CharterRevision)) { throw 'Next round requires the existing Charter revision' }
    $round = $state.Round + 1
    Set-ReviewState -CaseRoot $CaseRoot -Status CRITIC -Round $round -NextAction $NextAction -Profile $Profile -CharterRevision $state.CharterRevision -VerdictOwner $(if ($Profile -in @('software', 'manuscript')) { 'review-loop Core' } else { '' }) -LastCompletedAction 'executable protocol scenario'
    $roundPath = Join-Path $CaseRoot ('.review-loop/rounds/round-{0:d2}' -f $round)
    New-Item -ItemType Directory -Force -Path $roundPath | Out-Null
    $ProducerEvidence | Set-Content -LiteralPath (Join-Path $roundPath 'producer-evidence.md')
    return $roundPath
}

function Get-ReviewFindingIds {
    param([Parameter(Mandatory)][string]$CaseRoot)

    $path = Join-Path $CaseRoot '.review-loop/findings.md'
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return @() }
    $ids = [System.Collections.Generic.List[string]]::new()
    foreach ($line in Get-Content -LiteralPath $path) {
        $match = [regex]::Match($line, '^(?:Finding|Re-observed) (F-\d{3})(?:\s|$)')
        if ($match.Success -and -not $ids.Contains($match.Groups[1].Value)) {
            $ids.Add($match.Groups[1].Value)
        }
    }
    return @($ids)
}

function Get-ConfirmedReviewFindingIds {
    param([Parameter(Mandatory)][string]$CaseRoot)

    $path = Join-Path $CaseRoot '.review-loop/findings.md'
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { return @() }
    $latest = @{}
    $current = ''
    $disposition = ''
    foreach ($line in Get-Content -LiteralPath $path) {
        $match = [regex]::Match($line, '^(?:Finding|Re-observed) (F-\d{3})(?:\s|$)')
        if ($match.Success) {
            if ($current) { $latest[$current] = $disposition }
            $current = $match.Groups[1].Value
            $disposition = ''
            continue
        }
        $disp = [regex]::Match($line, '^Disposition: (confirmed|rejected)')
        if ($disp.Success) { $disposition = $disp.Groups[1].Value }
    }
    if ($current) { $latest[$current] = $disposition }
    return @(Get-ReviewFindingIds -CaseRoot $CaseRoot | Where-Object { $latest[$_] -eq 'confirmed' })
}

function Add-ReviewFinding {
    param(
        [Parameter(Mandatory)][string]$CaseRoot,
        [Parameter(Mandatory)][string]$FindingId,
        [Parameter(Mandatory)][string]$Source,
        [Parameter(Mandatory)][string]$Axis,
        [Parameter(Mandatory)][string]$SourceFindingReference,
        [Parameter(Mandatory)][ValidateSet('Critical', 'High', 'Medium', 'Low')][string]$Severity,
        [Parameter(Mandatory)][ValidateSet('confirmed', 'rejected', 'duplicate', 'out-of-scope')][string]$Disposition,
        [string]$EvidenceLabel = 'review'
    )

    $path = Join-Path $CaseRoot '.review-loop/findings.md'
    $prefix = if (Test-Path -LiteralPath $path -PathType Leaf) { 'Re-observed' } else { 'Finding' }
    $records = @(
        "$prefix $FindingId"
        "Source: $Source; Axis: $Axis; Source finding reference: $SourceFindingReference"
        "Severity: $Severity"
        "Disposition: $Disposition"
        "Evidence label: $EvidenceLabel"
    )
    if ($prefix -eq 'Finding') {
        $records = @('# Finding Registry') + $records + @('Resolution evidence: pending fresh Evaluator')
        $records | Set-Content -LiteralPath $path
    }
    else {
        $records | Add-Content -LiteralPath $path
    }
}

function Write-ReviewRepairEvidence {
    param(
        [Parameter(Mandatory)][string]$CaseRoot,
        [Parameter(Mandatory)][int]$Round,
        [Parameter(Mandatory)][string[]]$FindingIds,
        [Parameter(Mandatory)][string[]]$EvidenceLines
    )

    $roundPath = Join-Path $CaseRoot ('.review-loop/rounds/round-{0:d2}' -f $Round)
    foreach ($findingId in $FindingIds) {
        @("Finding: $findingId", "Stable finding ID: $findingId") + $EvidenceLines | Set-Content -LiteralPath (Join-Path $roundPath "repair-evidence-$findingId.md")
    }
}
