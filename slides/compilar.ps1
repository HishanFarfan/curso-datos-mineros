# Compila todos los decks Beamer del curso (dos pasadas cada uno).
# Uso:  pwsh ./compilar.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$decks = Get-ChildItem -Filter "0?_*.tex" | Sort-Object Name
foreach ($d in $decks) {
    Write-Host "==> $($d.Name)"
    pdflatex -interaction=nonstopmode -halt-on-error $d.Name | Out-Null
    pdflatex -interaction=nonstopmode -halt-on-error $d.Name | Out-Null
}

# Limpieza de auxiliares
Get-ChildItem -Include *.aux,*.log,*.nav,*.snm,*.toc,*.out,*.vrb -Recurse |
    Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "`nPDFs generados:"
Get-ChildItem -Filter "0?_*.pdf" | Select-Object Name, Length
