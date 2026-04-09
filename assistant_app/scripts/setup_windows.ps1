$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "No encontré el lanzador 'py'. Instala Python 3.11+ desde python.org."
}

py -3.12 -m venv .venv

$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Pip = Join-Path $Root ".venv\Scripts\pip.exe"

& $Python -m pip install --upgrade pip wheel setuptools

$packages = @(
    "PySide6>=6.7",
    "python-dotenv>=1.0",
    "httpx>=0.27",
    "requests>=2.32",
    "numpy>=1.26",
    "sounddevice>=0.4",
    "faster-whisper>=1.0",
    "opencv-python>=4.10",
    "Pillow>=10.4",
    "pytest>=8.3",
    "pytest-qt>=4.4"
)

& $Pip install @packages

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"

    $envText = Get-Content ".env" -Raw
    $envText = $envText -replace "FULLSCREEN=true", "FULLSCREEN=false"
    $envText = $envText -replace "VOICE_ALWAYS_ON=true", "VOICE_ALWAYS_ON=false"
    $envText = $envText -replace "TTS_ENABLED=true", "TTS_ENABLED=false"
    $envText = $envText -replace "FACE_RECOGNITION_ENABLED=true", "FACE_RECOGNITION_ENABLED=false"
    Set-Content ".env" $envText -Encoding UTF8
}

New-Item -ItemType Directory -Force -Path "data\known_faces","data\unknown_faces","data\conversation_cache" | Out-Null

Write-Host "Entorno Windows listo."
Write-Host "Configuración inicial segura aplicada en .env:"
Write-Host "  FULLSCREEN=false"
Write-Host "  VOICE_ALWAYS_ON=false"
Write-Host "  TTS_ENABLED=false"
Write-Host "  FACE_RECOGNITION_ENABLED=false"
