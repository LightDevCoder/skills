[CmdletBinding()]
param(
    [string]$RootsJson = '[]',
    [Parameter(Mandatory = $true)][string]$ContextJson,
    [string]$HostName = 'codex',
    [ValidateSet('next', 'workflow', 'navigate', 'validate')][string]$Mode = 'next',
    [string]$Skill = '',
    [ValidateSet('current-workflow', 'independent', 'standalone')][string]$Scope = 'current-workflow'
)

$ErrorActionPreference = 'Stop'
$python = $null
foreach ($commandName in @('python3', 'python')) {
    $candidate = Get-Command $commandName -ErrorAction SilentlyContinue
    if ($null -eq $candidate) { continue }
    try {
        & $candidate.Source -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' *> $null
        if ($LASTEXITCODE -eq 0) {
            $python = $candidate
            break
        }
    }
    catch {
        continue
    }
}
if ($null -eq $python) {
    $blocked = [ordered]@{
        mode = $Mode
        routingState = 'needs-model-judgment'
        status = 'BLOCKED'
        skill = ''
        source = ''
        reason = ''
        invocation = ''
        confidence = 'low'
        alternative = $null
        gaps = @('Python 3.9 or newer is unavailable. Follow references/discovery-contract.md manually or install the declared runtime, then rerun $ask-light.')
        reads = [ordered]@{ metadata = 0; bodies = 0; references = 0 }
        candidates = @()
        next = 'awaiting-approval'
        execution = 'recommendation phase was read-only; execution begins only after explicit user approval'
    }
    $blocked | ConvertTo-Json -Depth 4
    exit 2
}
& $python.Source (Join-Path $PSScriptRoot 'ask_light.py') --roots-json $RootsJson --context-json $ContextJson --host-name $HostName --mode $Mode --skill $Skill --scope $Scope
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
