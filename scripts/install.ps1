# Install life-pattern-reading into a DSH skills directory.
#
# Usage (Windows PowerShell):
#   powershell -File .\scripts\install.ps1                 # user scope: ~/.dsh/skills
#   powershell -File .\scripts\install.ps1 -Scope project  # <current dir>/.dsh/skills
#   powershell -File .\scripts\install.ps1 -Force          # replace an existing copy
#
# PowerShell 7+ users can run the same commands with `pwsh`.
#
# The script only copies files; it does not run them, install dependencies, or
# modify the registry.

param(
    [ValidateSet("user", "project")]
    [string]$Scope = "user",
    [string]$ProjectPath = (Get-Location).Path,
    [string]$TargetRoot = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$source = Split-Path -Parent $PSScriptRoot
$skillFile = Join-Path $source "SKILL.md"
if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) {
    throw "SKILL.md not found under $source. Run this script from the repository's scripts/ directory."
}

if ($TargetRoot) {
    $destRoot = $TargetRoot
} elseif ($Scope -eq "project") {
    $destRoot = Join-Path $ProjectPath ".dsh\skills"
} else {
    $homePath = if ($env:USERPROFILE) { $env:USERPROFILE } else { $HOME }
    $destRoot = Join-Path $homePath ".dsh\skills"
}

$dest = Join-Path $destRoot "life-pattern-reading"
$resolvedParent = [System.IO.Path]::GetFullPath($destRoot)
$resolvedDest = [System.IO.Path]::GetFullPath($dest)

if ($resolvedDest -eq $resolvedParent) {
    throw "Refusing to install over the skills root itself."
}

if (Test-Path -LiteralPath $dest) {
    if (-not $Force) {
        throw "Destination already exists: $dest`nRe-run with -Force to replace it."
    }
    Remove-Item -LiteralPath $dest -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $dest | Out-Null

$items = @(
    "SKILL.md",
    "README.md",
    "README.en.md",
    "LICENSE",
    "CHANGELOG.md",
    "references",
    "assets",
    "scripts",
    "examples"
)

foreach ($item in $items) {
    $path = Join-Path $source $item
    if (Test-Path -LiteralPath $path) {
        Copy-Item -LiteralPath $path -Destination $dest -Recurse -Force
    }
}

Write-Host "Installed: $dest"
Write-Host "Next: start a new DSH session (or wait for the skill watcher to refresh) and invoke /life-pattern-reading, or ask for a life-pattern reading."
