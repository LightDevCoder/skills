[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RootsJson,
    [Parameter(Mandatory = $true)][string]$ContextJson,
    [string]$HostName = 'codex',
    [ValidateRange(1, 10)][int]$ShortlistLimit = 3,
    [ValidateSet('next', 'workflow')][string]$Mode = 'next'
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

function Normalize-Identity {
    param([string]$Value)
    return (ConvertTo-Scalar $Value).Trim().ToLowerInvariant()
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
                if ($line -match '^name:\s*(.+)$') { $result.name = Normalize-Identity $Matches[1] }
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

function Test-WorkflowAvailabilityValue {
    param($Value)
    if ($null -eq $Value) { return $false }
    if ($Value -is [string]) { return -not [string]::IsNullOrWhiteSpace([string]$Value) }
    foreach ($field in @('host', 'availableSkills', 'available', 'unavailableSkills', 'unavailable', 'readablePaths')) {
        $property = @($Value.PSObject.Properties | Where-Object Name -eq $field | Select-Object -First 1)
        if ($property.Count -eq 0 -or $null -eq $property[0].Value) { continue }
        $fieldValue = $property[0].Value
        if ($fieldValue -is [string]) {
            if (-not [string]::IsNullOrWhiteSpace([string]$fieldValue)) { return $true }
        } elseif ($fieldValue -is [System.Collections.IEnumerable]) {
            if (@($fieldValue).Count -gt 0) { return $true }
        } elseif (-not [string]::IsNullOrWhiteSpace([string]$fieldValue)) {
            return $true
        }
    }
    return $false
}

function Test-WorkflowInvocationControlValue {
    param($Value)
    return @('explicit-only', 'model-callable', 'either') -contains (Normalize-Identity ([string]$Value))
}

function Test-PathUnder {
    param([string]$Path, [string]$Root)
    try {
        $sep = [IO.Path]::DirectorySeparatorChar
        $resolvedPath = [IO.Path]::GetFullPath($Path).TrimEnd($sep)
        $resolvedRoot = [IO.Path]::GetFullPath($Root).TrimEnd($sep)
        return $resolvedPath.Equals($resolvedRoot, [StringComparison]::OrdinalIgnoreCase) -or $resolvedPath.StartsWith($resolvedRoot + $sep, [StringComparison]::OrdinalIgnoreCase)
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

function Get-WorkflowRecipes {
    return @(
        [ordered]@{
            id = 'software-feature'; title = 'Software feature';
            entryCondition = 'A software goal has a defined feature or implementation outcome.'
            projectTypes = @('software'); taskKinds = @('feature', 'implementation', 'specification')
            keywords = @('feature', 'software', 'acceptance', 'implementation')
            stoppingBoundary = 'Stop after each handoff; review-loop owns the final PASS, FAIL, or BLOCKED verdict.'
            finalAuthority = 'review-loop'
            steps = @(
                [ordered]@{ skill = 'to-spec'; sourceCategory = 'upstream'; fallbackInvocation = 'user-invoked'; expectedInput = 'goal, constraints, and conversation'; expectedOutput = 'traceable specification'; handoffArtifact = 'specification'; stopCondition = 'Specification is explicit enough for a specification review.'; optional = $false },
                [ordered]@{ skill = 'review-loop'; sourceCategory = 'first-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'frozen specification and acceptance source'; expectedOutput = 'specification findings or verdict'; handoffArtifact = 'review evidence'; stopCondition = 'Specification review returns a durable finding set or verdict.'; optional = $false },
                [ordered]@{ skill = 'to-tickets'; sourceCategory = 'upstream'; fallbackInvocation = 'user-invoked'; expectedInput = 'approved specification'; expectedOutput = 'dependency-ordered tracer tickets'; handoffArtifact = 'ticket graph'; stopCondition = 'Tickets are published; do not auto-start implementation.'; optional = $false },
                [ordered]@{ skill = 'implement'; sourceCategory = 'upstream'; fallbackInvocation = 'user-invoked'; expectedInput = 'one unblocked ticket'; expectedOutput = 'bounded implementation and test evidence'; handoffArtifact = 'implementation commit'; stopCondition = 'One ticket is implemented and handed to review.'; optional = $false },
                [ordered]@{ skill = 'code-review'; sourceCategory = 'upstream'; fallbackInvocation = 'model-invoked'; expectedInput = 'fixed implementation diff'; expectedOutput = 'Standards and Spec findings'; handoffArtifact = 'specialist review'; stopCondition = 'Findings are supplied to the acceptance loop.'; optional = $false },
                [ordered]@{ skill = 'review-loop'; sourceCategory = 'first-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'implementation, tests, and specialist findings'; expectedOutput = 'final PASS, FAIL, or BLOCKED verdict'; handoffArtifact = 'review-loop verdict'; stopCondition = 'Preserve the final verdict; do not unlock work from tests alone.'; optional = $false },
                [ordered]@{ skill = 'handoff'; sourceCategory = 'upstream'; fallbackInvocation = 'user-invoked'; expectedInput = 'accepted result or blocked state'; expectedOutput = 'resume/closeout record'; handoffArtifact = 'handoff document'; stopCondition = 'Close or explicitly resume from the handoff record.'; optional = $false }
            )
        },
        [ordered]@{
            id = 'bug-diagnosis'; title = 'Bug diagnosis';
            entryCondition = 'A reproducible bug, regression, error, or performance problem is reported.'
            projectTypes = @('software'); taskKinds = @('bug', 'debugging', 'diagnosis')
            keywords = @('bug', 'debug', 'diagnos', 'regression', 'error', 'performance')
            stoppingBoundary = 'Diagnose and hand off one bounded repair; do not turn the recipe into an automatic loop.'
            finalAuthority = 'review-loop'
            steps = @(
                [ordered]@{ skill = 'diagnosing-bugs'; sourceCategory = 'upstream'; fallbackInvocation = 'user-invoked'; expectedInput = 'reported failure and a tight failing reproduction'; expectedOutput = 'root-cause evidence and regression test'; handoffArtifact = 'diagnosis record'; stopCondition = 'The bug is reproduced or the smallest BLOCKED evidence gap is recorded.'; optional = $false },
                [ordered]@{ skill = 'implement'; sourceCategory = 'upstream'; fallbackInvocation = 'user-invoked'; expectedInput = 'bounded repair ticket'; expectedOutput = 'repair and focused tests'; handoffArtifact = 'repair diff'; stopCondition = 'Repair is ready for specialist review.'; optional = $false },
                [ordered]@{ skill = 'code-review'; sourceCategory = 'upstream'; fallbackInvocation = 'model-invoked'; expectedInput = 'repair diff'; expectedOutput = 'review findings'; handoffArtifact = 'code review'; stopCondition = 'Findings are handed to review-loop.'; optional = $false },
                [ordered]@{ skill = 'review-loop'; sourceCategory = 'first-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'diagnosis, repair, tests, and findings'; expectedOutput = 'final PASS, FAIL, or BLOCKED verdict'; handoffArtifact = 'review-loop verdict'; stopCondition = 'Preserve verdict and stop.'; optional = $false }
            )
        },
        [ordered]@{
            id = 'manuscript-project'; title = 'Manuscript project';
            entryCondition = 'The goal is a governed manuscript, manual, book, or multilingual document project.'
            projectTypes = @('manuscript'); taskKinds = @('initialization', 'production', 'review', 'manuscript')
            keywords = @('manuscript', 'book', 'manual', 'document', 'writing', 'multilingual')
            stoppingBoundary = 'Preserve explicit handoff and resume boundaries; manuscript-ops and review-loop do not silently call user-invoked Skills.'
            finalAuthority = 'review-loop'
            steps = @(
                [ordered]@{ skill = 'manuscript-ops'; sourceCategory = 'first-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'manuscript scope and current project state'; expectedOutput = 'routing and state assessment'; handoffArtifact = 'manuscript project state'; stopCondition = 'Routing is explicit before any next user-invoked Skill.'; optional = $false },
                [ordered]@{ skill = 'grill-me'; sourceCategory = 'upstream'; fallbackInvocation = 'user-invoked'; expectedInput = 'unresolved decisions'; expectedOutput = 'confirmed understanding'; handoffArtifact = 'decision record'; stopCondition = 'Stop when the user confirms shared understanding.'; optional = $true },
                [ordered]@{ skill = 'wayfinder'; sourceCategory = 'upstream'; fallbackInvocation = 'user-invoked'; expectedInput = 'multi-session uncertainty'; expectedOutput = 'investigation map and decisions'; handoffArtifact = 'wayfinder map'; stopCondition = 'Stop when the route is clear; do not implement from the map.'; optional = $true },
                [ordered]@{ skill = 'project-init'; sourceCategory = 'first-party'; fallbackInvocation = 'user-invoked'; expectedInput = 'confirmed manuscript preset'; expectedOutput = 'minimal project initialization'; handoffArtifact = 'project guidance'; stopCondition = 'Initialization ends before discovery, specification, implementation, or review.'; optional = $false },
                [ordered]@{ skill = 'review-loop'; sourceCategory = 'first-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'frozen manuscript acceptance source'; expectedOutput = 'review findings or verdict'; handoffArtifact = 'review evidence'; stopCondition = 'Do not lock or publish without the final verdict.'; optional = $false },
                [ordered]@{ skill = 'manuscript-ops'; sourceCategory = 'first-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'accepted manuscript plan and evidence'; expectedOutput = 'production and format QA handoff'; handoffArtifact = 'production record'; stopCondition = 'Respect the user-controlled lock and resume boundary.'; optional = $false },
                [ordered]@{ skill = 'review-loop'; sourceCategory = 'first-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'production artifacts and QA evidence'; expectedOutput = 'final PASS, FAIL, or BLOCKED verdict'; handoffArtifact = 'final manuscript verdict'; stopCondition = 'Stop at the final verdict.'; optional = $false }
            )
        },
        [ordered]@{
            id = 'source-to-skill'; title = 'Source to reusable Skill';
            entryCondition = 'Sufficient source material may contain a reusable method.'
            projectTypes = @('skill-development'); taskKinds = @('skill-development', 'research', 'authoring')
            keywords = @('learn', 'source', 'reusable', 'skill', 'distill', 'method')
            stoppingBoundary = 'learn-anything stops at its Method Contract or bounded package handoff; it does not implicitly invoke authoring or review Skills.'
            finalAuthority = 'review-loop'
            steps = @(
                [ordered]@{ skill = 'learn-anything'; sourceCategory = 'first-party'; fallbackInvocation = 'user-invoked'; expectedInput = 'source material and provenance'; expectedOutput = 'Method Contract or precise source gaps'; handoffArtifact = 'method contract'; stopCondition = 'Stop if evidence is insufficient; do not invent a Skill.'; optional = $false },
                [ordered]@{ skill = 'writing-great-skills'; sourceCategory = 'upstream'; fallbackInvocation = 'model-invoked'; expectedInput = 'approved method contract'; expectedOutput = 'authoring guidance'; handoffArtifact = 'authoring notes'; stopCondition = 'This is optional knowledge, never an implicit learn-anything runtime dependency.'; optional = $true },
                [ordered]@{ skill = 'review-loop'; sourceCategory = 'first-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'deterministic Skill package and acceptance source'; expectedOutput = 'agent-skill review verdict'; handoffArtifact = 'admission evidence'; stopCondition = 'Admission requires the final review-loop verdict.'; optional = $false }
            )
        },
        [ordered]@{
            id = 'new-project-initialization'; title = 'New project initialization';
            entryCondition = 'A new project needs only a minimal confirmed starting point.'
            projectTypes = @('software', 'manuscript', 'research', 'knowledge-base', 'data-analysis', 'skill-development', 'generic')
            taskKinds = @('initialization', 'discovery', 'setup')
            keywords = @('new project', 'initialize', 'initialization', 'setup', 'start')
            stoppingBoundary = 'Initialization is not discovery, specification, implementation, or final review; ask-light stops after recommending the next explicit choice.'
            finalAuthority = 'user chooses the next Skill'
            steps = @(
                [ordered]@{ skill = 'ask-light'; sourceCategory = 'first-party'; fallbackInvocation = 'user-invoked'; expectedInput = 'goal, project type, artifacts, blockers, and availability'; expectedOutput = 'one next Skill recommendation'; handoffArtifact = 'recommendation JSON'; stopCondition = 'Stop after recommendation; user explicitly selects the next Skill.'; optional = $false },
                [ordered]@{ skill = 'project-init'; sourceCategory = 'first-party'; fallbackInvocation = 'user-invoked'; expectedInput = 'user-confirmed preset'; expectedOutput = 'minimal initialization'; handoffArtifact = 'initialization report'; stopCondition = 'Stop after validation and report; no implicit workflow chain.'; optional = $false }
            )
        },
        [ordered]@{
            id = 'final-review'; title = 'Final review';
            entryCondition = 'Target, acceptance source, and evidence boundary are already frozen.'
            projectTypes = @('software', 'manuscript', 'skill-development', 'generic')
            taskKinds = @('review', 'final-review', 'acceptance')
            keywords = @('final review', 'acceptance', 'verdict', 'pass', 'blocked')
            stoppingBoundary = 'review-loop owns the verdict and stops at PASS, FAIL, or BLOCKED.'
            finalAuthority = 'review-loop'
            steps = @(
                [ordered]@{ skill = 'review-loop'; sourceCategory = 'first-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'frozen target, acceptance source, and admissible evidence'; expectedOutput = 'PASS, FAIL, or BLOCKED'; handoffArtifact = 'verdict and durable state'; stopCondition = 'Stop at the final verdict; do not publish from specialist findings alone.'; optional = $false }
            )
        },
        [ordered]@{
            id = 'private-third-party-dependency'; title = 'Private third-party dependency';
            entryCondition = 'A requested workflow explicitly depends on a private or modified third-party Skill.'
            projectTypes = @('software', 'skill-development', 'generic'); taskKinds = @('maintenance', 'review', 'dependency')
            keywords = @('private third-party', 'third-party dependency', 'modified third-party')
            stoppingBoundary = 'Report the availability gap; do not install or reveal private content from ask-light.'
            finalAuthority = 'user resolves availability, then review-loop if acceptance is required'
            steps = @(
                [ordered]@{ skill = 'code-review'; sourceCategory = 'modified-third-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'available third-party package and fixed diff'; expectedOutput = 'specialist findings'; handoffArtifact = 'review findings'; stopCondition = 'Stop with an accurate availability gap when the private package is not visible.'; optional = $false },
                [ordered]@{ skill = 'review-loop'; sourceCategory = 'first-party'; fallbackInvocation = 'model-invoked'; expectedInput = 'package evidence and review findings'; expectedOutput = 'final verdict'; handoffArtifact = 'review-loop verdict'; stopCondition = 'Do not proceed while the required private dependency is unavailable.'; optional = $false }
            )
        }
    )
}

function Get-WorkflowMatches {
    param($Context)
    $contextProjectType = Normalize-Identity $Context.projectType
    $contextTaskKind = Normalize-Identity $Context.taskKind
    $keywordParts = @($Context.goal, $Context.blockers)
    if ($Context.artifacts -is [System.Collections.IEnumerable] -and -not ($Context.artifacts -is [string])) { $keywordParts += @($Context.artifacts) } else { $keywordParts += $Context.artifacts }
    $text = (($keywordParts | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) }) -join ' ').ToLowerInvariant()
    $results = [System.Collections.Generic.List[object]]::new()
    foreach ($recipe in (Get-WorkflowRecipes)) {
        if (-not [string]::IsNullOrWhiteSpace($contextProjectType) -and -not (@($recipe.projectTypes | ForEach-Object { Normalize-Identity $_ }) -contains $contextProjectType)) { continue }
        if (-not [string]::IsNullOrWhiteSpace($contextTaskKind) -and -not (@($recipe.taskKinds | ForEach-Object { Normalize-Identity $_ }) -contains $contextTaskKind)) { continue }
        $score = 0
        $keywordHits = 0
        if (@($recipe.projectTypes | ForEach-Object { Normalize-Identity $_ }) -contains $contextProjectType) {
            $score += 8
            if (@($recipe.projectTypes).Count -eq 1) { $score += 2 }
        }
        if (@($recipe.taskKinds | ForEach-Object { Normalize-Identity $_ }) -contains $contextTaskKind) { $score += 6 }
        foreach ($keyword in @($recipe.keywords)) {
            if ($text -match [regex]::Escape($keyword.ToLowerInvariant())) { $score += 2; $keywordHits++ }
        }
        $results.Add([pscustomobject]@{ recipe = $recipe; score = $score; keywordHits = $keywordHits })
    }
    return @($results | Where-Object { $_.score -gt 0 -and $_.keywordHits -gt 0 } | Sort-Object @{ Expression = 'score'; Descending = $true }, @{ Expression = { $_.recipe.id }; Descending = $false })
}

function Get-WorkflowRecommendation {
    param($Recipe, $Records, $Context, $Policy, [int]$MetadataReads)
    $steps = [System.Collections.Generic.List[object]]::new()
    $gaps = [System.Collections.Generic.List[string]]::new()
    $order = 0
    foreach ($step in @($Recipe.steps)) {
        $order++
        $candidate = @($Records | Where-Object { (Normalize-Identity $_.name) -eq (Normalize-Identity $step.skill) -and (Normalize-Identity $_.sourceCategory) -eq (Normalize-Identity $step.sourceCategory) } | Sort-Object -Property packagePath)
        $available = $false; $source = "$($step.sourceCategory): not visible in active roots"; $missing = ''
        $invocation = $step.fallbackInvocation; $metadataStatus = 'unavailable'; $packagePath = ''
        if ($candidate.Count -gt 0) {
            $candidate = $candidate[0]
            $packagePath = $candidate.packagePath
            $source = "$($candidate.sourceCategory): $($candidate.packagePath)"
            $metadataStatus = [string]$candidate.metadataStatus
            if ($candidate.availabilityStatus -eq 'available' -and $candidate.metadataReadable) {
                $available = $true
                $invocation = if ($candidate.allowImplicitInvocation -eq $true) { 'model-invoked' } else { 'user-invoked' }
            } else {
                $missing = if (-not [string]::IsNullOrWhiteSpace([string]$candidate.availabilityError)) { [string]$candidate.availabilityError } else { 'Skill metadata or package is unavailable' }
            }
        } else {
            $missing = switch ($step.sourceCategory) {
                'modified-third-party' { 'private skills-3rdParty dependency is not visible to the active host' }
                'upstream' { 'upstream third-party Skill is not visible to the active host' }
                default { 'first-party Skill is not installed or readable' }
            }
        }
        if (-not $available -and -not $step.optional) { $gaps.Add("step $order $($step.skill): $missing") }
        $steps.Add([ordered]@{
            order = $order; skill = $step.skill; source = $source; sourceCategory = $step.sourceCategory
            invocationType = $invocation; invocationControl = [string]$Context.invocationControl
            availability = if ($available) { 'available' } else { 'unavailable' }
            metadataStatus = $metadataStatus; packagePath = $packagePath
            expectedInput = $step.expectedInput; expectedOutput = $step.expectedOutput
            handoffArtifact = $step.handoffArtifact; stopCondition = $step.stopCondition
            missingDependency = $missing; optional = [bool]$step.optional
        })
    }
    $status = if ($gaps.Count -gt 0) { 'BLOCKED' } else { 'RECOMMEND' }
    [ordered]@{
        status = $status; mode = 'workflow'; workflow = $Recipe.id; title = $Recipe.title
        reason = $Recipe.entryCondition; entryCondition = $Recipe.entryCondition
        stoppingBoundary = $Recipe.stoppingBoundary; finalAuthority = $Recipe.finalAuthority
        steps = @($steps); gaps = @($gaps)
        execution = 'recommendation only; nothing was invoked, installed, or orchestrated'
        reads = [ordered]@{ metadata = $MetadataReads; bodies = 0; references = 0 }
        availability = [ordered]@{ host = $Policy.host; known = $Policy.known }
    }
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
        $record = [ordered]@{ name = (Normalize-Identity $front.name); description = $front.description; sourceCategory = (Normalize-Identity $category); packagePath = $package; metadataStatus = $front.status; metadataError = $front.error; metadataReadable = $false; displayName = $agent.displayName; shortDescription = $agent.shortDescription; defaultPrompt = $agent.defaultPrompt; allowImplicitInvocation = $agent.allowImplicitInvocation; hosts = @($agent.hosts); availabilityStatus = 'unavailable'; availabilityError = ''; readStatus = 'pending'; readError = ''; bodyRead = $false; referencesRead = 0; actionFingerprint = ''; score = -999; evidence = @() }
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
$workflowMissingFields = [System.Collections.Generic.List[string]]::new()
foreach ($field in @('goal', 'projectType', 'taskKind', 'artifacts', 'blockers', 'availability', 'invocationControl')) {
    $property = @($context.PSObject.Properties | Where-Object Name -eq $field | Select-Object -First 1)
    if ($property.Count -eq 0 -or $null -eq $property[0].Value) {
        $workflowMissingFields.Add($field)
        continue
    }
    if (@('goal', 'projectType', 'taskKind', 'invocationControl') -contains $field -and [string]::IsNullOrWhiteSpace([string]$property[0].Value)) {
        $workflowMissingFields.Add($field)
        continue
    }
    if ($field -eq 'availability' -and -not (Test-WorkflowAvailabilityValue $property[0].Value)) {
        $workflowMissingFields.Add($field)
        continue
    }
    if ($field -eq 'invocationControl' -and -not (Test-WorkflowInvocationControlValue $property[0].Value)) {
        $workflowMissingFields.Add($field)
    }
}
$workflowContextMissing = $workflowMissingFields.Count -gt 0
if ($Mode -eq 'workflow') {
    $workflowOutput = [ordered]@{
        status = ''; mode = 'workflow'; workflow = ''; title = ''; reason = ''
        entryCondition = ''; stoppingBoundary = ''; finalAuthority = ''
        steps = @(); gaps = @(); alternatives = @()
        execution = 'recommendation only; nothing was invoked, installed, or orchestrated'
        reads = [ordered]@{ metadata = $metadataReads; bodies = 0; references = 0 }
        availability = [ordered]@{ host = $availabilityPolicy.host; known = $availabilityPolicy.known }
    }
    if ($workflowContextMissing) {
        $workflowOutput.status = 'NEED-INPUT'
        $workflowOutput.gaps = @('Provide these workflow context fields before selecting a recipe: ' + ($workflowMissingFields -join ', ') + '.')
    } else {
        $matches = @(Get-WorkflowMatches $context)
        if ($matches.Count -eq 0) {
            $workflowOutput.status = 'NEED-INPUT'
            $workflowOutput.gaps = @('No reliable workflow recipe matches the current goal, projectType, and taskKind; provide a narrower workflow intent or use next mode.')
        } elseif ($matches.Count -gt 1 -and $matches[0].score -eq $matches[1].score) {
            $workflowOutput.status = 'NEED-INPUT'
            $workflowOutput.gaps = @('Workflow intent is ambiguous; choose one recipe before invoking any Skill.')
            $workflowOutput.alternatives = @($matches | Select-Object -First 3 | ForEach-Object { [ordered]@{ workflow = $_.recipe.id; title = $_.recipe.title; score = $_.score; entryCondition = $_.recipe.entryCondition } })
        } else {
            $workflowOutput = Get-WorkflowRecommendation $matches[0].recipe $records $context $availabilityPolicy $metadataReads
        }
    }
    $workflowOutput | ConvertTo-Json -Depth 12
    exit 0
}
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
