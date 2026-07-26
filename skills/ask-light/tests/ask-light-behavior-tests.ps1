param([string]$SkillRoot = '')

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($SkillRoot)) { $SkillRoot = Split-Path -Parent $PSScriptRoot }
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path
$script:failures = [System.Collections.Generic.List[string]]::new()
$script:assertions = 0
function Assert-True { param([bool]$Condition, [string]$Name); $script:assertions++; if (-not $Condition) { $script:failures.Add($Name) } }

$scanner = Join-Path $SkillRoot 'scripts/ask-light.ps1'
$fixture = Join-Path ([IO.Path]::GetTempPath()) ('ask-light-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $fixture | Out-Null

function New-Skill {
    param(
        [string]$Root,
        [string]$Name,
        [string]$Description,
        [switch]$AllowImplicit,
        [switch]$Malformed,
        [string]$Body = '',
        [string]$Hosts = '',
        [switch]$BlockHosts
    )
    $path = Join-Path $Root $Name
    New-Item -ItemType Directory -Force -Path (Join-Path $path 'agents') | Out-Null
    if ($Malformed) {
        Set-Content -LiteralPath (Join-Path $path 'SKILL.md') -Value "# no metadata"
    } else {
        Set-Content -LiteralPath (Join-Path $path 'SKILL.md') -Value @("---", "name: $Name", "description: $Description", "---", '', $Body)
    }
    $yaml = [System.Collections.Generic.List[string]]::new()
    foreach ($line in @("interface:", "  display_name: `"$Name`"", "  short_description: `"$Description`"", "  default_prompt: `"Use `$$Name`"", '', 'policy:', "  allow_implicit_invocation: $($AllowImplicit.ToString().ToLowerInvariant())")) { $yaml.Add($line) }
    if (-not [string]::IsNullOrWhiteSpace($Hosts)) {
        if ($BlockHosts) { $yaml.Add('hosts:'); foreach ($hostNameValue in ($Hosts -split ',')) { $yaml.Add("  - $($hostNameValue.Trim())") } }
        else { $yaml.Add("hosts: [$Hosts]") }
    }
    Set-Content -LiteralPath (Join-Path $path 'agents/openai.yaml') -Value $yaml
    return $path
}

try {
    $roots = @()
    foreach ($category in @('project','global','first-party','upstream','modified-third-party','other')) {
        $categoryRoot = Join-Path $fixture $category
        New-Item -ItemType Directory -Force -Path $categoryRoot | Out-Null
        $roots += [ordered]@{ category = $category; path = $categoryRoot }
    }

    # Every supported source category is visible in one metadata-first catalog.
    New-Skill (Join-Path $fixture 'project') 'local-helper' 'A generic local project helper.' | Out-Null
    New-Skill (Join-Path $fixture 'global') 'global-helper' 'A generic global helper.' -AllowImplicit | Out-Null
    New-Skill (Join-Path $fixture 'first-party') 'manuscript-review' 'Review manuscript documents and source evidence.' | Out-Null
    New-Skill (Join-Path $fixture 'upstream') 'research' 'Research primary sources and synthesize evidence.' -AllowImplicit | Out-Null
    New-Skill (Join-Path $fixture 'modified-third-party') 'data-adapter' 'Analyze data and repair compatibility issues.' | Out-Null
    New-Skill (Join-Path $fixture 'other') 'knowledge-notes' 'Organize knowledge notes and links.' | Out-Null

    # Same name at two sources remains two candidate identities.
    New-Skill (Join-Path $fixture 'project') 'shared' 'A shared project Skill.' | Out-Null
    New-Skill (Join-Path $fixture 'upstream') 'shared' 'A shared upstream Skill.' | Out-Null

    # Unavailable metadata stays a remediation gap and cannot be selected.
    New-Skill (Join-Path $fixture 'other') 'broken-metadata' 'ignored' -Malformed | Out-Null
    $incompletePath = Join-Path $fixture 'other/incomplete-metadata'
    New-Item -ItemType Directory -Force -Path (Join-Path $incompletePath 'agents') | Out-Null
    Set-Content -LiteralPath (Join-Path $incompletePath 'SKILL.md') -Value @('---', 'name: incomplete-metadata', 'description: Incomplete metadata fixture.', '---', '', 'Body')
    Set-Content -LiteralPath (Join-Path $incompletePath 'agents/openai.yaml') -Value @('interface:', 'policy:', '  allow_implicit_invocation: false')

    # Large catalog: bodies are only loaded for the bounded shortlist.
    for ($i = 1; $i -le 25; $i++) {
        New-Skill (Join-Path $fixture 'other') ("catalog-$i") 'A catalog entry with no matching task.' -Body "SENTINEL-BODY-$i" | Out-Null
    }
    $rootsJson = ConvertTo-Json -InputObject ([array]$roots) -Compress
    $softwareContext = [ordered]@{ goal = 'review software source changes'; artifacts = @('src/parser.ts'); blockers = ''; projectType = 'software'; taskKind = 'review'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $result = & $scanner -RootsJson $rootsJson -ContextJson $softwareContext | ConvertFrom-Json

    Assert-True ($result.status -eq 'RECOMMEND') 'available catalog returns recommendation'
    Assert-True ($result.skill -eq 'manuscript-review') 'context selects the best manuscript review fit'
    Assert-True ($result.source -match '^first-party:') 'first-party source is retained in recommendation'
    Assert-True ($result.invocation -eq '$manuscript-review') 'Codex invocation is explicit and host-appropriate'
    Assert-True ($result.execution -match 'nothing was invoked or installed') 'recommendation does not execute or install'
    Assert-True ($result.reads.metadata -ge 30 -and $result.reads.bodies -le 3) 'large catalog uses metadata-first bounded body reads'
    Assert-True ((@($result.candidates | Where-Object sourceCategory -eq 'project')).Count -gt 0) 'project source discovered'
    Assert-True ((@($result.candidates | Where-Object sourceCategory -eq 'global')).Count -gt 0) 'global source discovered'
    Assert-True ((@($result.candidates | Where-Object sourceCategory -eq 'first-party')).Count -gt 0) 'first-party source discovered'
    Assert-True ((@($result.candidates | Where-Object sourceCategory -eq 'upstream')).Count -gt 0) 'upstream source discovered'
    Assert-True ((@($result.candidates | Where-Object sourceCategory -eq 'modified-third-party')).Count -gt 0) 'modified third-party source discovered'
    Assert-True ((@($result.candidates | Where-Object sourceCategory -eq 'other')).Count -gt 0) 'other readable source discovered'
    Assert-True ((@($result.candidates | Where-Object name -eq 'shared')).Count -eq 2) 'duplicate names remain distinct records'
    Assert-True ((@($result.gaps | Where-Object { $_ -match 'broken-metadata' })).Count -eq 1) 'unavailable metadata is reported as a gap'
    Assert-True ((@($result.candidates | Where-Object { $_.name -eq 'broken-metadata' -and $_.metadataStatus -eq 'unavailable' -and $_.packagePath -match 'other' })).Count -eq 1) 'malformed metadata candidate is retained with source and path'
    Assert-True ((@($result.candidates | Where-Object { $_.name -eq 'incomplete-metadata' -and $_.metadataStatus -eq 'unavailable' -and $_.metadataError -match 'displayName|shortDescription|defaultPrompt' })).Count -eq 1) 'incomplete metadata fields are explicitly unavailable'

    # A catalog with two equal, materially different review paths gets one alternative.
    $ambRoot = Join-Path $fixture 'ambiguous'; New-Item -ItemType Directory -Force -Path $ambRoot | Out-Null
    New-Skill $ambRoot 'review-code' 'Review changes and verify acceptance.' | Out-Null
    New-Skill $ambRoot 'review-spec' 'Review specification requirements and verify acceptance.' | Out-Null
    $ambRoots = ConvertTo-Json -InputObject ([array]@([ordered]@{ category = 'project'; path = $ambRoot })) -Compress
    $ambContext = [ordered]@{ goal = 'review and verify acceptance'; artifacts = @('artifact.md'); blockers = ''; projectType = 'generic'; taskKind = 'review'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $ambiguous = & $scanner -RootsJson $ambRoots -ContextJson $ambContext | ConvertFrom-Json
    Assert-True ($ambiguous.status -eq 'RECOMMEND' -and $null -ne $ambiguous.alternative) 'genuine tie returns exactly one alternative'

    # Equivalent duplicate actions do not manufacture an alternative.
    $equivRoot = Join-Path $fixture 'equivalent'; New-Item -ItemType Directory -Force -Path $equivRoot | Out-Null
    New-Skill $equivRoot 'review-one' 'Review artifacts and verify acceptance.' | Out-Null
    New-Skill $equivRoot 'review-two' 'Review artifacts and verify acceptance.' | Out-Null
    $equivRoots = ConvertTo-Json -InputObject ([array]@([ordered]@{ category = 'project'; path = $equivRoot })) -Compress
    $equiv = & $scanner -RootsJson $equivRoots -ContextJson $ambContext | ConvertFrom-Json
    Assert-True ($equiv.status -eq 'RECOMMEND' -and $null -eq $equiv.alternative) 'equivalent tied actions suppress alternative'

    # A host-incompatible Skill is filtered even when its description is a strong fit.
    $hostRoot = Join-Path $fixture 'host-filter'; New-Item -ItemType Directory -Force -Path $hostRoot | Out-Null
    New-Skill $hostRoot 'claude-review' 'Review software changes and verify acceptance.' -Hosts 'claude' | Out-Null
    New-Skill $hostRoot 'claude-block' 'Review software changes and verify acceptance.' -Hosts 'claude' -BlockHosts | Out-Null
    New-Skill $hostRoot 'codex-review' 'Review software changes.' -Hosts 'codex' | Out-Null
    $hostRoots = ConvertTo-Json -InputObject ([array]@([ordered]@{ category = 'project'; path = $hostRoot })) -Compress
    $hostAvailability = [ordered]@{ host = 'codex'; readablePaths = @($hostRoot); unavailableSkills = @() } | ConvertTo-Json -Compress
    $hostContext = [ordered]@{ goal = 'review software changes'; artifacts = @('src/parser.ts'); blockers = ''; projectType = 'software'; taskKind = 'review'; availability = ($hostAvailability | ConvertFrom-Json); invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $hostResult = & $scanner -HostName codex -RootsJson $hostRoots -ContextJson $hostContext | ConvertFrom-Json
    Assert-True ($hostResult.status -eq 'RECOMMEND' -and $hostResult.skill -eq 'codex-review') 'host availability selects compatible Skill'
    Assert-True ((@($hostResult.candidates | Where-Object { $_.name -eq 'claude-review' -and $_.availabilityStatus -eq 'unavailable' })).Count -eq 1) 'host-incompatible Skill is not eligible'
    Assert-True ((@($hostResult.candidates | Where-Object { $_.name -eq 'claude-block' -and $_.availabilityStatus -eq 'unavailable' })).Count -eq 1) 'block-list host incompatibility is not eligible'
    Assert-True (($hostResult.gaps -join ' ') -match "host 'codex' is not declared") 'host incompatibility has actionable gap'

    # A shortlisted body with a missing linked reference is ineligible, not recommendable from metadata.
    $readFailRoot = Join-Path $fixture 'read-failure'; New-Item -ItemType Directory -Force -Path $readFailRoot | Out-Null
    New-Skill $readFailRoot 'broken-body' 'Review software changes.' -Body '[missing](references/missing.md)' | Out-Null
    $readFailRoots = ConvertTo-Json -InputObject ([array]@([ordered]@{ category = 'project'; path = $readFailRoot })) -Compress
    $readFail = & $scanner -RootsJson $readFailRoots -ContextJson $ambContext | ConvertFrom-Json
    Assert-True ($readFail.status -eq 'BLOCKED') 'unreadable shortlisted reference blocks recommendation'
    Assert-True ((@($readFail.candidates | Where-Object { $_.name -eq 'broken-body' -and $_.readStatus -eq 'unavailable' })).Count -eq 1) 'unreadable shortlisted candidate is marked ineligible'
    Assert-True (($readFail.gaps -join ' ') -match 'body/reference unreadable|restore') 'unreadable body/reference has actionable gap'

    # A clear winner suppresses alternatives.
    $clearContext = [ordered]@{ goal = 'review software parser implementation'; artifacts = @('src/parser.ts'); blockers = ''; projectType = 'software'; taskKind = 'implementation'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $clear = & $scanner -RootsJson $rootsJson -ContextJson $clearContext | ConvertFrom-Json
    Assert-True ($null -eq $clear.alternative) 'clear winner has no alternative'

    # No usable package yields actionable installation/readability guidance.
    $missingRoot = Join-Path $fixture 'missing'; New-Item -ItemType Directory -Force -Path $missingRoot | Out-Null
    New-Skill $missingRoot 'unreadable' 'not usable' -Malformed | Out-Null
    $missingRoots = ConvertTo-Json -InputObject ([array]@([ordered]@{ category = 'global'; path = $missingRoot })) -Compress
    $missingContext = [ordered]@{ goal = 'something'; artifacts = @(); blockers = ''; projectType = 'generic'; taskKind = 'implementation'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $missing = & $scanner -RootsJson $missingRoots -ContextJson $missingContext | ConvertFrom-Json
    Assert-True ($missing.status -eq 'BLOCKED' -and ($missing.gaps -join ' ') -match 'Install or restore|unreadable') 'missing Skill gives actionable guidance'

    $inputContext = [ordered]@{ goal = ''; artifacts = @(); blockers = ''; projectType = 'generic'; taskKind = ''; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $input = & $scanner -RootsJson $rootsJson -ContextJson $inputContext | ConvertFrom-Json
    Assert-True ($input.status -eq 'NEED-INPUT' -and ($input.gaps -join ' ') -match 'goal and taskKind') 'unknown context asks for input instead of guessing'

    # Workflow mode returns a recipe with real package availability and never executes a step.
    $workflowRoot = Join-Path $fixture 'workflow'; New-Item -ItemType Directory -Force -Path $workflowRoot | Out-Null
    $wfFirst = Join-Path $workflowRoot 'first-party'; $wfUpstream = Join-Path $workflowRoot 'upstream'; $wfThird = Join-Path $workflowRoot 'modified-third-party'
    New-Item -ItemType Directory -Force -Path $wfFirst,$wfUpstream,$wfThird | Out-Null
    foreach ($name in @('review-loop','ask-light','project-init','learn-anything','manuscript-ops')) { New-Skill $wfFirst $name "First-party $name capability." | Out-Null }
    foreach ($name in @('to-spec','to-tickets','implement','code-review','handoff','diagnosing-bugs','grill-me','wayfinder','writing-great-skills')) { New-Skill $wfUpstream $name "Upstream $name capability." -AllowImplicit | Out-Null }
    New-Skill $wfThird 'code-review' 'Modified third-party code review capability.' -AllowImplicit | Out-Null
    $wfRoots = ConvertTo-Json -InputObject ([array]@(
        [ordered]@{ category = 'first-party'; path = $wfFirst },
        [ordered]@{ category = 'upstream'; path = $wfUpstream },
        [ordered]@{ category = 'modified-third-party'; path = $wfThird }
    )) -Compress
    $featureContext = [ordered]@{ goal = 'build a software feature with acceptance criteria'; artifacts = @('brief.md'); blockers = ''; projectType = 'software'; taskKind = 'feature'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $featureWorkflow = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $featureContext | ConvertFrom-Json
    Assert-True ($featureWorkflow.status -eq 'RECOMMEND' -and $featureWorkflow.workflow -eq 'software-feature') 'software feature workflow is recommended'
    Assert-True (@($featureWorkflow.steps).Count -eq 7) 'software feature workflow exposes all handoff steps'
    Assert-True ((@($featureWorkflow.steps | Where-Object { $_.skill -eq 'review-loop' })).Count -eq 2) 'software feature workflow retains both review-loop boundaries'
    Assert-True (($featureWorkflow.finalAuthority -eq 'review-loop') -and ($featureWorkflow.stoppingBoundary -match 'PASS|FAIL|BLOCKED')) 'workflow reports final authority and stopping boundary'
    Assert-True ($featureWorkflow.execution -match 'nothing was invoked|orchestrated') 'workflow recommendation does not execute or orchestrate'
    Assert-True ((@($featureWorkflow.steps | Where-Object { $_.skill -eq 'to-spec' -and $_.sourceCategory -eq 'upstream' })).Count -eq 1) 'workflow preserves third-party source category'
    Assert-True ((@($featureWorkflow.steps | Where-Object { $_.skill -eq 'code-review' -and $_.sourceCategory -eq 'upstream' -and $_.availability -eq 'available' })).Count -eq 1) 'workflow selects the declared source category when duplicate Skill names exist'
    Assert-True ($featureWorkflow.reads.metadata -eq 15 -and $featureWorkflow.reads.bodies -eq 0 -and $featureWorkflow.reads.references -eq 0) 'workflow exposes bounded metadata-only read counts'

    $bugContext = [ordered]@{ goal = 'diagnose a software regression and repair the error'; artifacts = @('failing-test.txt'); blockers = ''; projectType = 'software'; taskKind = 'bug'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $bugWorkflow = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $bugContext | ConvertFrom-Json
    Assert-True ($bugWorkflow.workflow -eq 'bug-diagnosis' -and @($bugWorkflow.steps | Where-Object skill -eq 'diagnosing-bugs').Count -eq 1) 'bug diagnosis workflow selects diagnosing-bugs'

    $manuscriptContext = [ordered]@{ goal = 'start a manuscript project with explicit handoffs'; artifacts = @('brief.md'); blockers = ''; projectType = 'manuscript'; taskKind = 'initialization'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $manuscriptWorkflow = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $manuscriptContext | ConvertFrom-Json
    Assert-True ($manuscriptWorkflow.status -eq 'RECOMMEND' -and $manuscriptWorkflow.workflow -eq 'manuscript-project') 'manuscript workflow is recommended'
    Assert-True (($manuscriptWorkflow.stoppingBoundary -match 'handoff') -and (@($manuscriptWorkflow.steps | Where-Object { $_.skill -eq 'project-init' -and $_.invocationType -eq 'user-invoked' })).Count -eq 1) 'manuscript workflow preserves explicit handoff and invocation boundary'

    $mismatchedWorkflowContext = [ordered]@{ goal = 'write a manuscript and plan chapters'; artifacts = @('brief.md'); blockers = ''; projectType = 'generic'; taskKind = 'maintenance'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $mismatchedWorkflow = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $mismatchedWorkflowContext | ConvertFrom-Json
    Assert-True ($mismatchedWorkflow.status -eq 'NEED-INPUT' -and $mismatchedWorkflow.workflow -eq '') 'mismatched project type and task kind do not select a manuscript recipe'

    $missingProjectTypeContext = [ordered]@{ goal = 'build a software feature'; artifacts = @('brief.md'); blockers = ''; projectType = ''; taskKind = 'feature'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $missingProjectType = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $missingProjectTypeContext | ConvertFrom-Json
    Assert-True ($missingProjectType.status -eq 'NEED-INPUT' -and ($missingProjectType.gaps -join ' ') -match 'projectType') 'workflow requires project type before matching a recipe'

    $incompleteWorkflowContext = [ordered]@{ goal = 'build a software feature'; projectType = 'software'; taskKind = 'feature' } | ConvertTo-Json -Compress
    $incompleteWorkflow = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $incompleteWorkflowContext | ConvertFrom-Json
    Assert-True ($incompleteWorkflow.status -eq 'NEED-INPUT' -and ($incompleteWorkflow.gaps -join ' ') -match 'artifacts.*blockers.*availability.*invocationControl') 'workflow requires the remaining context fields instead of assuming them'

    $invalidAvailabilityContext = [ordered]@{ goal = 'build a software feature'; artifacts = @('brief.md'); blockers = ''; projectType = 'software'; taskKind = 'feature'; availability = [ordered]@{}; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $invalidAvailability = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $invalidAvailabilityContext | ConvertFrom-Json
    Assert-True ($invalidAvailability.status -eq 'NEED-INPUT' -and ($invalidAvailability.gaps -join ' ') -match 'availability') 'empty availability context is not treated as reliable'

    $invalidInvocationContext = [ordered]@{ goal = 'build a software feature'; artifacts = @('brief.md'); blockers = ''; projectType = 'software'; taskKind = 'feature'; availability = 'codex'; invocationControl = 'automatic' } | ConvertTo-Json -Compress
    $invalidInvocation = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $invalidInvocationContext | ConvertFrom-Json
    Assert-True ($invalidInvocation.status -eq 'NEED-INPUT' -and ($invalidInvocation.gaps -join ' ') -match 'invocationControl') 'unknown invocation control is not accepted as reliable context'

    $sourceContext = [ordered]@{ goal = 'learn a reusable Skill method from source material'; artifacts = @('transcript.md'); blockers = ''; projectType = 'skill-development'; taskKind = 'skill-development'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $sourceWorkflow = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $sourceContext | ConvertFrom-Json
    $learnStep = @($sourceWorkflow.steps | Where-Object skill -eq 'learn-anything')[0]
    Assert-True ($sourceWorkflow.workflow -eq 'source-to-skill' -and $learnStep.availability -eq 'available') 'source-to-skill workflow recommends learn-anything'
    Assert-True ($learnStep.invocationType -eq 'user-invoked' -and $sourceWorkflow.execution -match 'nothing was invoked') 'explicit-only mode does not exclude learn-anything and remains non-executing'

    $newProjectContext = [ordered]@{ goal = 'initialize a new project'; artifacts = @(); blockers = ''; projectType = 'generic'; taskKind = 'initialization'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $newProjectWorkflow = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $newProjectContext | ConvertFrom-Json
    Assert-True ($newProjectWorkflow.workflow -eq 'new-project-initialization') 'new project initialization workflow is recommended'

    $finalContext = [ordered]@{ goal = 'perform the final acceptance review and issue a verdict'; artifacts = @('evidence.md'); blockers = ''; projectType = 'generic'; taskKind = 'final-review'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $finalWorkflow = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $finalContext | ConvertFrom-Json
    Assert-True ($finalWorkflow.workflow -eq 'final-review' -and @($finalWorkflow.steps).Count -eq 1 -and $finalWorkflow.finalAuthority -eq 'review-loop') 'final review workflow delegates final authority to review-loop'

    # A private third-party package that is not visible is an accurate BLOCKED gap, not a fabricated recommendation.
    $privateRoot = Join-Path $fixture 'private-third-party'; New-Item -ItemType Directory -Force -Path $privateRoot | Out-Null
    New-Skill $privateRoot 'review-loop' 'First-party final acceptance.' | Out-Null
    $privateRoots = ConvertTo-Json -InputObject ([array]@([ordered]@{ category = 'first-party'; path = $privateRoot })) -Compress
    $privateContext = [ordered]@{ goal = 'resolve a private third-party dependency'; artifacts = @(); blockers = ''; projectType = 'generic'; taskKind = 'dependency'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $privateWorkflow = & $scanner -Mode workflow -RootsJson $privateRoots -ContextJson $privateContext | ConvertFrom-Json
    Assert-True ($privateWorkflow.status -eq 'BLOCKED' -and ($privateWorkflow.gaps -join ' ') -match 'private skills-3rdParty') 'missing private third-party dependency is BLOCKED with an availability gap'
    Assert-True ((@($privateWorkflow.steps | Where-Object { $_.skill -eq 'code-review' -and $_.availability -eq 'unavailable' })).Count -eq 1) 'missing private dependency step is explicitly unavailable'

    # Missing metadata is not silently treated as availability.
    $learnMissingRoot = Join-Path $fixture 'learn-missing'; New-Item -ItemType Directory -Force -Path (Join-Path $learnMissingRoot 'learn-anything/agents') | Out-Null
    Set-Content -LiteralPath (Join-Path $learnMissingRoot 'learn-anything/SKILL.md') -Value @('---','name: learn-anything','description: Learn from source.','---','', 'Body')
    Set-Content -LiteralPath (Join-Path $learnMissingRoot 'learn-anything/agents/openai.yaml') -Value @('interface:','policy:','  allow_implicit_invocation: false')
    $learnMissingRoots = ConvertTo-Json -InputObject ([array]@([ordered]@{ category = 'first-party'; path = $learnMissingRoot })) -Compress
    $learnMissing = & $scanner -RootsJson $learnMissingRoots -ContextJson $sourceContext | ConvertFrom-Json
    Assert-True ($learnMissing.status -eq 'BLOCKED' -and ($learnMissing.gaps -join ' ') -match 'learn-anything') 'missing learn-anything metadata blocks a workflow recommendation'

    $ambiguousContext = [ordered]@{ goal = 'unclear work with no reliable route'; artifacts = @(); blockers = ''; projectType = 'generic'; taskKind = 'maintenance'; availability = 'codex'; invocationControl = 'explicit-only' } | ConvertTo-Json -Compress
    $ambiguousWorkflow = & $scanner -Mode workflow -RootsJson $wfRoots -ContextJson $ambiguousContext | ConvertFrom-Json
    Assert-True ($ambiguousWorkflow.status -eq 'NEED-INPUT' -and ($ambiguousWorkflow.gaps -join ' ') -match 'No reliable workflow recipe') 'ambiguous workflow requests input instead of guessing'
} finally {
    Remove-Item -LiteralPath $fixture -Recurse -Force -ErrorAction SilentlyContinue
}

if ($script:failures.Count -gt 0) { throw "ask-light behavior failed: $($script:failures -join '; ')" }
Write-Output "ASK_LIGHT_BEHAVIOR_ASSERTIONS=$($script:assertions)"
Write-Output 'PASS - ask-light behavior (sources, duplicates, bounded reads, ranking, workflow recipes, guidance, non-execution)'
