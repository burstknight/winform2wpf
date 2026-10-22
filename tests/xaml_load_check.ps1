# Parse a XAML file with the real WPF parser.
#
# Exit codes:
#   0 - the XAML loaded successfully
#   1 - the XAML failed to load (the parser message is printed to stdout)
#   2 - the environment cannot run the check (no WPF assemblies)
#
# The script is intentionally ASCII-only: Windows PowerShell 5.1 reads files
# without a BOM as ANSI, so any non-ASCII byte would be mangled.

param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$ErrorActionPreference = 'Stop'

try {
    Add-Type -AssemblyName PresentationFramework
    Add-Type -AssemblyName PresentationCore
    Add-Type -AssemblyName WindowsBase
    Add-Type -AssemblyName System.Xaml
} catch {
    Write-Output 'SKIP: WPF assemblies are not available'
    exit 2
}

if (-not (Test-Path -LiteralPath $Path)) {
    Write-Output ("FAIL: file not found: " + $Path)
    exit 1
}

$text = [System.IO.File]::ReadAllText($Path)

try {
    $null = [System.Windows.Markup.XamlReader]::Parse($text)
} catch {
    Write-Output ('FAIL: ' + $_.Exception.GetBaseException().Message)
    exit 1
}

Write-Output 'OK'
exit 0
