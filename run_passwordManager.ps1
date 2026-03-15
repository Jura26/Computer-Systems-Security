#  .\run_passwordManager.ps1 init mAsterPasswrd
#  .\run_passwordManager.ps1 put mAsterPasswrd www.fer.hr neprobojnAsifrA
#  .\run_passwordManager.ps1 get mAsterPasswrd www.fer.hr
#  .\run_passwordManager.ps1 get wrongPasswrd www.fer.hr

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    $ForwardedArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

function Invoke-BasePython {
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$PyArgs
    )

    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 @PyArgs
        if ($LASTEXITCODE -eq 0) { return }
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python @PyArgs
        if ($LASTEXITCODE -eq 0) { return }
    }

    throw "Python 3 was not found. Install Python and add it to PATH."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvDir = Join-Path $scriptDir ".venv"
$venvPython = Join-Path $scriptDir ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating virtual environment in $venvDir ..."
    Invoke-BasePython -PyArgs @("-m", "venv", $venvDir)
}

$python = $venvPython

& $python -c "import Crypto.Cipher" 1>$null 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing dependency: pycryptodome ..."
    & $python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { Write-Error "pip upgrade failed"; exit $LASTEXITCODE }

    & $python -m pip install pycryptodome
    if ($LASTEXITCODE -ne 0) { Write-Error "Failed to install pycryptodome"; exit $LASTEXITCODE }
}

& $python -m py_compile (Join-Path $scriptDir "passwordManager.py")
if ($LASTEXITCODE -ne 0) { Write-Error "Compilation failed"; exit $LASTEXITCODE }

& $python (Join-Path $scriptDir "passwordManager.py") @ForwardedArgs
exit $LASTEXITCODE
