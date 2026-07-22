param([string]$SkillRoot = '')

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($SkillRoot)) { $SkillRoot = Split-Path -Parent $PSScriptRoot }
$SkillRoot = (Resolve-Path -LiteralPath $SkillRoot).Path
$script:failures = [System.Collections.Generic.List[string]]::new()
function Assert-True { param([bool]$Condition, [string]$Name); if (-not $Condition) { $script:failures.Add($Name) } }

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
} finally {
    Remove-Item -LiteralPath $fixture -Recurse -Force -ErrorAction SilentlyContinue
}

if ($script:failures.Count -gt 0) { throw "ask-light behavior failed: $($script:failures -join '; ')" }
Write-Output 'PASS - ask-light behavior (sources, duplicates, bounded reads, ranking, ambiguity, guidance, non-execution)'
