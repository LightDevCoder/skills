[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RootsJson,
    [Parameter(Mandatory = $true)][string]$ContextJson,
    [string]$HostName = 'codex',
    [ValidateRange(1, 10)][int]$ShortlistLimit = 3
)

$ErrorActionPreference = 'Stop'

function ConvertTo-Scalar {
    param([string]$Value)
    if ($null -eq $Value) { return '' }
    $trimmed = $Value.Trim()
    if (($trimmed.StartsWith('"') -and $trimmed.EndsWith('"')) -or ($trimmed.StartsWith("'") -and $trimmed.EndsWith("'"))) {
        return $trimmed.Substring(1, $trimmed.Length - 2)
    }
    return $trimmed
}

function Read-Frontmatter {
    param([string]$Path)
    $result = [ordered]@{ name = ''; description = ''; status = 'unavailable'; error = '' }
    try {
        $reader = [System.IO.StreamReader]::new($Path, $true)
        try {
            $first = $reader.ReadLine()
            if ($first -ne '---') { $result.error = 'SKILL.md has no YAML frontmatter'; return [pscustomobject]$result }
            while (($line = $reader.ReadLine()) -ne $null) {
                if ($line -eq '---') { $result.status = 'ok'; break }
                if ($line -match '^name:\s*(.+)$') { $result.name = ConvertTo-Scalar $Matches[1] }
                elseif ($line -match '^description:\s*(.+)$') { $result.description = ConvertTo-Scalar $Matches[1] }
            }
            if ($result.status -ne 'ok') { $result.error = 'frontmatter has no closing delimiter' }
            elseif ([string]::IsNullOrWhiteSpace($result.name) -or [string]::IsNullOrWhiteSpace($result.description)) {
                $result.status = 'unavailable'; $result.error = 'name and description are required'
            }
        } finally { $reader.Dispose() }
    } catch { $result.error = $_.Exception.Message }
    return [pscustomobject]$result
}

function Read-AgentMetadata {
    param([string]$Path)
    $result = [ordered]@{ displayName = ''; shortDescription = ''; defaultPrompt = ''; allowImplicitInvocation = $null; hosts = @(); status = 'missing'; error = '' }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return [pscustomobject]$result }
    try {
        $yaml = Get-Content -Raw -LiteralPath $Path
        foreach ($field in @('display_name','short_description','default_prompt')) {
            if ($yaml -match "(?m)^\s*${field}:\s*(.+)$") {
                $value = ConvertTo-Scalar $Matches[1]
                $key = switch ($field) { 'display_name' { 'displayName' } 'short_description' { 'shortDescription' } default { 'defaultPrompt' } }
                $result[$key] = $value
            }
        }
        if ($yaml -match '(?m)^\s*allow_implicit_invocation:\s*(true|false)\s*$') { $result.allowImplicitInvocation = [bool]::Parse($Matches[1]) }
        $yamlLines = $yaml -split '\r?\n'
        for ($lineIndex = 0; $lineIndex -lt $yamlLines.Count; $lineIndex++) {
            if ($yamlLines[$lineIndex] -match '^\s*hosts:\s*\[([^\]]*)\]') {
                $inlineHosts = @($Matches[1] -split ',' | ForEach-Object { ConvertTo-Scalar $_ } | Where-Object { $_ })
                foreach ($hostValue in $inlineHosts) { $result.hosts += $hostValue }
            } elseif ($yamlLines[$lineIndex] -match '^\s*hosts:\s*$') {
                for ($hostIndex = $lineIndex + 1; $hostIndex -lt $yamlLines.Count; $hostIndex++) {
                    if ([string]::IsNullOrWhiteSpace($yamlLines[$hostIndex])) { continue }
                    if ($yamlLines[$hostIndex] -match '^\s*-\s*(.+)$') { $result.hosts += ConvertTo-Scalar $Matches[1] }
                    else { break }
                }
            }
        }
        $missing = [System.Collections.Generic.List[string]]::new()
        foreach ($field in @('displayName','shortDescription','defaultPrompt')) { if ([string]::IsNullOrWhiteSpace([string]$result[$field])) { $missing.Add($field) } }
        if ($null -eq $result.allowImplicitInvocation) { $missing.Add('allow_implicit_invocation') }
        if ($missing.Count -gt 0) { $result.status = 'unavailable'; $result.error = 'metadata fields missing: ' + ($missing -join ', ') }
        else { $result.status = 'ok' }
    } catch { $result.status = 'unavailable'; $result.error = $_.Exception.Message }
    return [pscustomobject]$result
}

function Get-Packages {
    param([string]$Root)
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return @() }
    $direct = Join-Path $Root 'SKILL.md'
    if (Test-Path -LiteralPath $direct -PathType Leaf) { return @((Resolve-Path -LiteralPath $Root).Path) }
    $packages = Get-ChildItem -LiteralPath $Root -Directory -Recurse -ErrorAction SilentlyContinue |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') } |
        Select-Object -ExpandProperty FullName
    return @($packages)
}

function Get-SourceRank {
    param([string]$Category)
    switch ($Category.ToLowerInvariant()) {
        'project' { return 6 }; 'global' { return 5 }; 'first-party' { return 4 }
        'modified-third-party' { return 3 }; 'upstream' { return 2 }; default { return 1 }
    }
}

function Get-ContextText {
    param($Context)
    $parts = @($Context.goal, $Context.projectType, $Context.taskKind, $Context.blockers)
    if ($Context.artifacts -is [System.Collections.IEnumerable] -and -not ($Context.artifacts -is [string])) { $parts += @($Context.artifacts) } else { $parts += $Context.artifacts }
    return (($parts | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) }) -join ' ').ToLowerInvariant()
}

function Get-AvailabilityPolicy {
    param($Context, [string]$DefaultHost)
    $policy = [ordered]@{ known = $false; host = $DefaultHost; availableSkills = @(); unavailableSkills = @(); readablePaths = @() }
    $availability = $Context.availability
    if ($null -eq $availability) { return [pscustomobject]$policy }
    if ($availability -is [string]) {
        if (-not [string]::IsNullOrWhiteSpace($availability)) { $policy.known = $true; $policy.host = [string]$availability }
        return [pscustomobject]$policy
    }
    $policy.known = $true
    if (-not [string]::IsNullOrWhiteSpace([string]$availability.host)) { $policy.host = [string]$availability.host }
    foreach ($field in @('availableSkills','available')) {
        if ($null -ne $availability.$field) { $policy.availableSkills = @($availability.$field); break }
    }
    foreach ($field in @('unavailableSkills','unavailable')) {
        if ($null -ne $availability.$field) { $policy.unavailableSkills = @($availability.$field); break }
    }
    if ($null -ne $availability.readablePaths) { $policy.readablePaths = @($availability.readablePaths) }
    return [pscustomobject]$policy
}

function Test-PathUnder {
    param([string]$Path, [string]$Root)
    try {
        $resolvedPath = [IO.Path]::GetFullPath($Path).TrimEnd('\')
        $resolvedRoot = [IO.Path]::GetFullPath($Root).TrimEnd('\')
        return $resolvedPath.Equals($resolvedRoot, [StringComparison]::OrdinalIgnoreCase) -or $resolvedPath.StartsWith($resolvedRoot + '\', [StringComparison]::OrdinalIgnoreCase)
    } catch { return $false }
}

function Test-CandidateAvailability {
    param($Candidate, $Policy)
    $reasons = [System.Collections.Generic.List[string]]::new()
    if (@($Policy.unavailableSkills) -contains $Candidate.name) { $reasons.Add('Skill is listed as unavailable by the active host') }
    if (@($Policy.availableSkills).Count -gt 0 -and @($Policy.availableSkills) -notcontains $Candidate.name) { $reasons.Add('Skill is not in the host available-skill set') }
    if (@($Policy.readablePaths).Count -gt 0 -and -not (@($Policy.readablePaths | Where-Object { Test-PathUnder $Candidate.packagePath ([string]$_) }).Count -gt 0)) { $reasons.Add('package path is outside host readable paths') }
    if ($Policy.known -and @($Candidate.hosts).Count -gt 0 -and @($Candidate.hosts) -notcontains $Policy.host) { $reasons.Add("host '$($Policy.host)' is not declared by the Skill") }
    return [pscustomobject]@{ available = ($reasons.Count -eq 0); reason = ($reasons -join '; ') }
}

function Get-ActionFingerprint {
    param($Candidate, [string]$Body = '')
    $text = (([string]$Candidate.name) + ' ' + ([string]$Candidate.description) + ' ' + $Body).ToLowerInvariant()
    $families = [ordered]@{
        debugging = @('debug','diagnos','bug','error'); implementation = @('implement','build','code','develop')
        review = @('review','accept','verify','quality'); initialization = @('init','initialize','setup')
        research = @('research','source','evidence'); 'skill-development' = @('skill','learn','author')
        manuscript = @('manuscript','document','editor'); 'knowledge-base' = @('obsidian','note','knowledge')
        'data-analysis' = @('data','spreadsheet','analysis','dashboard'); specification = @('spec','brief','requirement')
    }
    $matched = [System.Collections.Generic.List[string]]::new()
    foreach ($family in $families.Keys) { foreach ($term in $families[$family]) { if ($text -match $term) { $matched.Add($family); break } } }
    if ($matched.Count -eq 0) { return 'other' }
    return (($matched | Sort-Object -Unique) -join '+')
}

function Get-Fit {
    param($Candidate, $Context)
    $text = Get-ContextText $Context
    $name = ([string]$Candidate.name).ToLowerInvariant()
    $desc = ([string]$Candidate.description).ToLowerInvariant()
    $tokens = [regex]::Matches($text, '[a-z0-9][a-z0-9-]{2,}') | ForEach-Object Value | Select-Object -Unique
    $score = 0; $evidence = [System.Collections.Generic.List[string]]::new()
    foreach ($token in $tokens) {
        if ($name -match [regex]::Escape($token)) { $score += 4; $evidence.Add("name matches '$token'") }
        elseif ($desc -match [regex]::Escape($token)) { $score += 2; $evidence.Add("description matches '$token'") }
    }
    $hints = @{
        'debugging' = @('diagnos','debug','bug','error'); 'implementation' = @('implement','build','code','develop')
        'review' = @('review','accept','verify','quality'); 'initialization' = @('init','project','setup')
        'research' = @('research','source','evidence'); 'skill-development' = @('skill','learn','author')
        'manuscript' = @('manuscript','document','editor'); 'knowledge-base' = @('obsidian','note','knowledge')
        'data-analysis' = @('data','spreadsheet','analysis','dashboard'); 'specification' = @('spec','brief','requirement')
    }
    $kind = [string]$Context.taskKind
    if ($hints.ContainsKey($kind.ToLowerInvariant())) {
        foreach ($hint in $hints[$kind.ToLowerInvariant()]) { if (($name + ' ' + $desc) -match $hint) { $score += 3; $evidence.Add("task kind '$kind' matches") ; break } }
    }
    if ($Candidate.availabilityStatus -eq 'available') { $score += 2; $evidence.Add('availability verified') }
    if ($Context.invocationControl -eq 'explicit-only' -and $Candidate.allowImplicitInvocation -eq $false) { $score += 2; $evidence.Add('explicit invocation policy matches') }
    elseif ($Context.invocationControl -eq 'model-callable' -and $Candidate.allowImplicitInvocation -eq $true) { $score += 2; $evidence.Add('model-callable policy matches') }
    elseif ($Context.invocationControl -eq 'explicit-only' -and $Candidate.allowImplicitInvocation -eq $true) { $score -= 1 }
    $Candidate.score = $score
    $Candidate.evidence = @($evidence)
    return $Candidate
}

function Get-Invocation {
    param($Candidate, [string]$HostLabel)
    if ($HostLabel.ToLowerInvariant() -eq 'codex') { return '$' + $Candidate.name }
    if (-not [string]::IsNullOrWhiteSpace($Candidate.defaultPrompt)) { return "Use the host Skill picker for '$($Candidate.name)' (default prompt: $($Candidate.defaultPrompt))" }
    return "Select '$($Candidate.name)' in the host Skill picker"
}

$roots = @(ConvertFrom-Json -InputObject $RootsJson | ForEach-Object { $_ })
$context = ConvertFrom-Json -InputObject $ContextJson
$availabilityPolicy = Get-AvailabilityPolicy $context $HostName
$records = [System.Collections.Generic.List[object]]::new(); $gaps = [System.Collections.Generic.List[string]]::new()
$metadataReads = 0
foreach ($root in $roots) {
    $category = [string]$root.category; $rootPath = [string]$root.path
    if (-not (Test-Path -LiteralPath $rootPath -PathType Container)) { $gaps.Add("$category root unavailable: $rootPath"); continue }
    foreach ($package in (Get-Packages $rootPath)) {
        $metadataReads++
        $front = Read-Frontmatter (Join-Path $package 'SKILL.md')
        $agent = Read-AgentMetadata (Join-Path $package 'agents/openai.yaml')
        $record = [ordered]@{ name = $front.name; description = $front.description; sourceCategory = $category; packagePath = $package; metadataStatus = $front.status; metadataError = $front.error; metadataReadable = $false; displayName = $agent.displayName; shortDescription = $agent.shortDescription; defaultPrompt = $agent.defaultPrompt; allowImplicitInvocation = $agent.allowImplicitInvocation; hosts = @($agent.hosts); availabilityStatus = 'unavailable'; availabilityError = ''; readStatus = 'pending'; readError = ''; bodyRead = $false; referencesRead = 0; actionFingerprint = ''; score = -999; evidence = @() }
        $metadataErrors = [System.Collections.Generic.List[string]]::new()
        if ($front.status -ne 'ok') { $metadataErrors.Add("SKILL.md: $($front.error)") }
        if ($agent.status -ne 'ok') { $metadataErrors.Add("agents/openai.yaml: $($agent.error)") }
        if ($metadataErrors.Count -gt 0) {
            if ([string]::IsNullOrWhiteSpace($record.name)) { $record.name = Split-Path $package -Leaf }
            $record.metadataStatus = 'unavailable'; $record.metadataReadable = $false; $record.metadataError = ($metadataErrors -join '; ')
            $gaps.Add("$category/$($record.name): metadata unavailable at $package; $($record.metadataError)")
            $records.Add([pscustomobject]$record)
        } else {
            $record.metadataReadable = $true
            $availability = Test-CandidateAvailability ([pscustomobject]$record) $availabilityPolicy
            if ($availability.available) { $record.availabilityStatus = 'available' }
            else { $record.availabilityError = $availability.reason; $gaps.Add("$category/$($record.name): unavailable - $($availability.reason)") }
            $records.Add([pscustomobject]$record)
        }
    }
}
$contextMissing = [string]::IsNullOrWhiteSpace([string]$context.goal) -or [string]::IsNullOrWhiteSpace([string]$context.taskKind)
$eligible = @($records | Where-Object { $_.availabilityStatus -eq 'available' } | ForEach-Object { Get-Fit $_ $context } | Where-Object { $_.score -gt 0 } | Sort-Object @{Expression='score';Descending=$true},@{Expression={ Get-SourceRank $_.sourceCategory };Descending=$true},@{Expression='packagePath';Descending=$false})
$shortlist = @($eligible | Select-Object -First $ShortlistLimit)
$bodyReads = 0; $referenceReads = 0
foreach ($candidate in $shortlist) {
    try {
        $body = Get-Content -Raw -LiteralPath (Join-Path $candidate.packagePath 'SKILL.md')
        $candidate.bodyRead = $true; $bodyReads++
        $links = [regex]::Matches($body, '\]\(([^)]+\.md)\)') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique
        foreach ($link in $links) { $path = Join-Path $candidate.packagePath $link; if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "reference not readable: $path" }; Get-Content -Raw -LiteralPath $path | Out-Null; $referenceReads++; $candidate.referencesRead++ }
        $candidate.actionFingerprint = Get-ActionFingerprint $candidate $body
        $candidate.readStatus = 'ok'
    } catch {
        $candidate.readStatus = 'unavailable'; $candidate.readError = $_.Exception.Message
        $gaps.Add("$($candidate.name): body/reference unreadable; restore a readable SKILL.md and linked reference: $($_.Exception.Message)")
    }
}
$readableShortlist = @($shortlist | Where-Object { $_.readStatus -eq 'ok' })
$output = [ordered]@{ status = ''; skill = ''; source = ''; reason = ''; invocation = ''; confidence = 'low'; alternative = $null; gaps = @($gaps); reads = [ordered]@{ metadata = $metadataReads; bodies = $bodyReads; references = $referenceReads }; execution = 'recommendation only; nothing was invoked or installed'; candidates = @($records | Select-Object name,sourceCategory,packagePath,metadataStatus,metadataReadable,metadataError,availabilityStatus,availabilityError,readStatus,readError,bodyRead,score) }
if ($contextMissing) { $output.status = 'NEED-INPUT'; $output.gaps += 'Provide goal and taskKind before ranking.' }
elseif ($shortlist.Count -eq 0) { $output.status = 'BLOCKED'; $output.gaps += 'Install or restore a readable Skill with SKILL.md frontmatter and declared invocation metadata, refresh the host, then rerun $ask-light.' }
elseif ($readableShortlist.Count -eq 0) { $output.status = 'BLOCKED'; $output.gaps += 'Shortlisted Skill bodies or references were unreadable; restore the package and linked files, refresh the host, then rerun $ask-light.' }
else {
    $best = $readableShortlist[0]; $output.status = 'RECOMMEND'; $output.skill = $best.name; $output.source = "$($best.sourceCategory): $($best.packagePath)"; $output.reason = (($best.evidence | Select-Object -First 3) -join '; '); if ([string]::IsNullOrWhiteSpace($output.reason)) { $output.reason = 'best available contextual fit after metadata and availability checks' }; $output.invocation = Get-Invocation $best $HostName; $output.confidence = if ($best.score -ge 8) { 'high' } elseif ($best.score -ge 3) { 'medium' } else { 'low' }
    if ($readableShortlist.Count -gt 1 -and [math]::Abs($best.score - $readableShortlist[1].score) -le 1 -and $best.name -ne $readableShortlist[1].name -and $best.actionFingerprint -ne $readableShortlist[1].actionFingerprint) { $output.alternative = [ordered]@{ skill = $readableShortlist[1].name; source = "$($readableShortlist[1].sourceCategory): $($readableShortlist[1].packagePath)"; reason = 'materially tied with a different next action after narrow body/reference read'; invocation = Get-Invocation $readableShortlist[1] $HostName } }
}
$output | ConvertTo-Json -Depth 8
