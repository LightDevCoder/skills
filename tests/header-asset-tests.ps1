param([string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path)

$ErrorActionPreference = "Stop"
$script:assertions = 0
$script:failures = @()
function Assert-Header { param([bool]$Condition, [string]$Message); $script:assertions++; if (-not $Condition) { $script:failures += $Message } }
function Read-UInt32BE { param([byte[]]$Bytes, [int]$Offset); return ([uint32]$Bytes[$Offset] -shl 24) -bor ([uint32]$Bytes[$Offset + 1] -shl 16) -bor ([uint32]$Bytes[$Offset + 2] -shl 8) -bor [uint32]$Bytes[$Offset + 3] }

$svgPath = Join-Path $Root "skills/docs/assets/skills-header.svg"
$pngPath = Join-Path $Root "skills/docs/assets/skills-header.png"
$manifestPath = Join-Path $Root "skills/docs/assets/skills-header.json"
Assert-Header (Test-Path -LiteralPath $svgPath -PathType Leaf) "Editable SVG is missing."
Assert-Header (Test-Path -LiteralPath $pngPath -PathType Leaf) "PNG header is missing."
Assert-Header (Test-Path -LiteralPath $manifestPath -PathType Leaf) "Header asset manifest is missing."
if (Test-Path -LiteralPath $manifestPath -PathType Leaf) {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    Assert-Header ($manifest.source_svg -eq 'skills-header.svg' -and $manifest.rendered_png -eq 'skills-header.png' -and $manifest.width -eq 1536 -and $manifest.height -eq 1024) "Header asset manifest does not describe the current 1536x1024 PNG."
}
if (Test-Path -LiteralPath $svgPath -PathType Leaf) {
    $svg = Get-Content -LiteralPath $svgPath -Raw
    Assert-Header ($svg -match '<svg\b' -and $svg -match 'width="1600"' -and $svg -match 'height="480"' -and $svg -match 'viewBox="0 0 1600 480"') "SVG dimensions/viewBox are not 1600x480."
    Assert-Header ($svg -match 'LightDevCoder' -and $svg -match '/skills' -and $svg -match 'Personal Skills Collection') "SVG does not contain the requested wordmark and slogan."
    Assert-Header ($svg -match 'fill="#72a0a3"' -and $svg -match 'translate\(6 8\)') "SVG does not contain the flat under-layer typography."
}
if (Test-Path -LiteralPath $pngPath -PathType Leaf) {
    $png = [IO.File]::ReadAllBytes($pngPath)
    Assert-Header ($png.Length -gt 100 -and $png[0] -eq 137 -and $png[1] -eq 80 -and $png[2] -eq 78 -and $png[3] -eq 71) "PNG signature is invalid."
    if ($png.Length -ge 24) {
        Assert-Header ((Read-UInt32BE $png 16) -eq $manifest.width -and (Read-UInt32BE $png 20) -eq $manifest.height) "PNG IHDR dimensions do not match the header asset manifest."
    }
}
if ((Test-Path -LiteralPath $manifestPath -PathType Leaf) -and (Test-Path -LiteralPath $svgPath -PathType Leaf) -and (Test-Path -LiteralPath $pngPath -PathType Leaf)) {
    Assert-Header ((Get-FileHash -Algorithm SHA256 -LiteralPath $svgPath).Hash.ToLowerInvariant() -eq $manifest.svg_sha256) "SVG does not match the checked-in header asset manifest."
    Assert-Header ((Get-FileHash -Algorithm SHA256 -LiteralPath $pngPath).Hash.ToLowerInvariant() -eq $manifest.png_sha256) "PNG does not match the checked-in header asset manifest."
}
if ($script:failures.Count -gt 0) { $script:failures | ForEach-Object { "FAIL: $_" }; throw "HEADER_ASSETS=FAIL ($($script:failures.Count) failures, $($script:assertions) assertions)" }
"HEADER_ASSET_ASSERTIONS=$($script:assertions)"
"HEADER_ASSETS=PASS"
