param([string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path)

$ErrorActionPreference = "Stop"
$script:assertions = 0
$script:failures = @()
function Assert-Quick { param([bool]$Condition, [string]$Message); $script:assertions++; if (-not $Condition) { $script:failures += $Message } }
$en = Get-Content -LiteralPath (Join-Path $Root "examples/quick-start/README.md") -Raw
$zh = Get-Content -LiteralPath (Join-Path $Root "examples/quick-start/README.zh-CN.md") -Raw
$brief = Get-Content -LiteralPath (Join-Path $Root "examples/quick-start/brief.md") -Raw
$agents = Get-Content -LiteralPath (Join-Path $Root "examples/quick-start/AGENTS.md") -Raw
foreach ($path in @("examples/quick-start/README.md", "examples/quick-start/README.zh-CN.md", "examples/quick-start/brief.md", "examples/quick-start/AGENTS.md")) { Assert-Quick (Test-Path -LiteralPath (Join-Path $Root $path) -PathType Leaf) "Quick Start file is missing: $path" }
Assert-Quick ($en -match 'npx skills add LightDevCoder/skills#v0\.1\.1' -and $en -match '\$ask-light next' -and $en -match '\$project-init' -and $en -match '\$review-loop') "English Quick Start is missing a required command."
Assert-Quick ($en -match 'illustrative' -and $en -match 'nothing was invoked, installed, or orchestrated') "English Quick Start must label output and preserve non-execution boundary."
Assert-Quick ($zh.Contains('README.md') -and $zh.Contains('Illustrative output')) "Chinese Quick Start is missing pairing or illustrative output."
Assert-Quick ($brief -match 'Goal' -and $brief -match 'Boundary' -and $agents -match 'Stop at each handoff') "Quick Start fixture lacks a minimal brief or explicit stop rule."
if ($script:failures.Count -gt 0) { $script:failures | ForEach-Object { "FAIL: $_" }; throw "QUICK_START=FAIL ($($script:failures.Count) failures, $($script:assertions) assertions)" }
"QUICK_START_ASSERTIONS=$($script:assertions)"
"QUICK_START=PASS"
