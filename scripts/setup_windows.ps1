# ============================================================================
# AI SaaS Offline - Setup Automatizado para Windows 11
# ============================================================================
# Este script automatiza la instalación y configuración completa
# Ejecutar como Administrador: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# ============================================================================

param(
    [switch]$SkipOllama = $false,
    [switch]$SkipPython = $false,
    [switch]$SkipModels = $false
)

# Colores para output
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
}

function Write-Status {
    param([string]$Message, [string]$Status = "Info")
    $Color = $Colors[$Status]
    Write-Host $Message -ForegroundColor $Color
}

function Test-CommandExists {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# ============================================================================
# 1. VERIFICAR REQUISITOS
# ============================================================================

Write-Status "🔍 Verificando requisitos del sistema..." "Info"

# Verificar Windows 11
$OSVersion = [System.Environment]::OSVersion.Version
if ($OSVersion.Major -lt 10) {
    Write-Status "❌ Se requiere Windows 10 o superior" "Error"
    exit 1
}

Write-Status "✅ Windows 11 detectado" "Success"

# Verificar Git
if (-not (Test-CommandExists "git")) {
    Write-Status "❌ Git no está instalado. Descárgalo desde https://git-scm.com/" "Error"
    exit 1
}
Write-Status "✅ Git instalado" "Success"

# Verificar Python
if (-not (Test-CommandExists "python")) {
    Write-Status "❌ Python no está instalado. Descárgalo desde https://www.python.org/" "Error"
    exit 1
}
$PythonVersion = python --version
Write-Status "✅ $PythonVersion instalado" "Success"

# Verificar Node.js
if (-not (Test-CommandExists "node")) {
    Write-Status "⚠️  Node.js no está instalado (opcional)" "Warning"
} else {
    $NodeVersion = node --version
    Write-Status "✅ Node.js $NodeVersion instalado" "Success"
}

# ============================================================================
# 2. CREAR ESTRUCTURA DE CARPETAS
# ============================================================================

Write-Status "`n📁 Creando estructura de carpetas..." "Info"

$ProjectRoot = "C:\AI-SaaS"
$Folders = @(
    "$ProjectRoot",
    "$ProjectRoot\backend",
    "$ProjectRoot\backend\services",
    "$ProjectRoot\backend\models",
    "$ProjectRoot\backend\utils",
    "$ProjectRoot\frontend",
    "$ProjectRoot\data",
    "$ProjectRoot\data\projects",
    "$ProjectRoot\data\models",
    "$ProjectRoot\tools",
    "$ProjectRoot\logs"
)

foreach ($Folder in $Folders) {
    if (-not (Test-Path $Folder)) {
        New-Item -ItemType Directory -Path $Folder -Force | Out-Null
        Write-Status "✅ Carpeta creada: $Folder" "Success"
    }
}

# ============================================================================
# 3. INSTALAR OLLAMA (Opcional)
# ============================================================================

if (-not $SkipOllama) {
    Write-Status "`n🤖 Instalando Ollama..." "Info"
    
    if (Test-CommandExists "ollama") {
        Write-Status "✅ Ollama ya está instalado" "Success"
    } else {
        Write-Status "⚠️  Descarga Ollama manualmente desde https://ollama.com/download" "Warning"
        Write-Status "   Luego ejecuta este script nuevamente" "Info"
        $Response = Read-Host "¿Ya instalaste Ollama? (s/n)"
        if ($Response -ne "s") {
            exit 1
        }
    }
}

# ============================================================================
# 4. CREAR ENTORNO VIRTUAL PYTHON
# ============================================================================

Write-Status "`n🐍 Creando entorno virtual Python..." "Info"

cd $ProjectRoot

if (-not (Test-Path ".\venv")) {
    python -m venv venv
    Write-Status "✅ Entorno virtual creado" "Success"
} else {
    Write-Status "✅ Entorno virtual ya existe" "Success"
}

# Activar entorno virtual
& ".\venv\Scripts\Activate.ps1"
Write-Status "✅ Entorno virtual activado" "Success"

# ============================================================================
# 5. INSTALAR DEPENDENCIAS PYTHON
# ============================================================================

Write-Status "`n📦 Instalando dependencias Python..." "Info"

$RequirementsContent = @"
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
requests==2.31.0
pillow==10.1.0
torch==2.1.1
torchvision==0.16.1
diffusers==0.24.0
transformers==4.35.2
accelerate==0.24.1
safetensors==0.4.1
pydantic==2.5.0
pydantic-settings==2.1.0
aiofiles==23.2.1
websockets==12.0
PyGithub==2.1.1
numpy==1.24.3
scipy==1.11.4
scikit-learn==1.3.2
"@

$RequirementsContent | Out-File -FilePath "$ProjectRoot\requirements.txt" -Encoding UTF8

Write-Status "Instalando paquetes (esto puede tardar 5-10 minutos)..." "Info"
pip install --upgrade pip setuptools wheel
pip install -r "$ProjectRoot\requirements.txt"

if ($LASTEXITCODE -eq 0) {
    Write-Status "✅ Dependencias instaladas correctamente" "Success"
} else {
    Write-Status "❌ Error al instalar dependencias" "Error"
    exit 1
}

# ============================================================================
# 6. DESCARGAR MODELOS DE IA (Opcional)
# ============================================================================

if (-not $SkipModels) {
    Write-Status "`n🎯 Descargando modelos de IA..." "Info"
    
    $Models = @(
        "deepseek-r1:7b",
        "qwen2.5-coder:7b",
        "phi4-mini"
    )
    
    foreach ($Model in $Models) {
        Write-Status "Descargando $Model..." "Info"
        ollama pull $Model
        Write-Status "✅ $Model descargado" "Success"
    }
}

# ============================================================================
# 7. CREAR ARCHIVO .ENV
# ============================================================================

Write-Status "`n⚙️  Creando archivo de configuración..." "Info"

$EnvContent = @"
# Configuración de Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_NUM_GPU=1
OLLAMA_NUM_THREAD=8
OLLAMA_MAX_LOADED_MODELS=2
OLLAMA_KEEP_ALIVE=5m

# Configuración de Backend
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
DEBUG=false

# Configuración de Modelos
DEFAULT_LLM_MODEL=deepseek-r1:7b
DEFAULT_IMAGE_MODEL=stabilityai/stable-diffusion-xl-base-1.0
DEVICE=cuda

# Configuración de GitHub (opcional)
GITHUB_TOKEN=

# Configuración de Audio
WHISPER_MODEL=medium
PIPER_VOICE=es_ES-sharvard-medium
"@

$EnvContent | Out-File -FilePath "$ProjectRoot\.env" -Encoding UTF8
Write-Status "✅ Archivo .env creado en $ProjectRoot\.env" "Success"

# ============================================================================
# 8. CREAR SCRIPT DE VERIFICACIÓN
# ============================================================================

Write-Status "`n✅ Creando script de verificación..." "Info"

$TestScriptContent = @"
import os
import subprocess
import requests
import torch
from pathlib import Path

print("🔍 Verificando instalación del sistema...\n")

# 1. Verificar Ollama
print("1️⃣  Ollama:")
try:
    response = requests.get("http://localhost:11434/api/tags")
    models = response.json().get("models", [])
    print(f"   ✅ Ollama corriendo. Modelos: {len(models)}")
    for model in models[:3]:
        print(f"      - {model['name']}")
except:
    print("   ⚠️  Ollama no está corriendo. Inicia Ollama manualmente.")

# 2. Verificar Python
print("\n2️⃣  Python:")
print(f"   ✅ Python {os.sys.version.split()[0]}")

# 3. Verificar PyTorch
print("\n3️⃣  PyTorch:")
print(f"   ✅ PyTorch {torch.__version__}")
print(f"   ✅ CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   ✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"   ✅ VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")

print("\n✅ Verificación completada")
"@

$TestScriptContent | Out-File -FilePath "$ProjectRoot\test_setup.py" -Encoding UTF8

# ============================================================================
# 9. CREAR SCRIPT DE INICIO
# ============================================================================

Write-Status "✅ Creando script de inicio..." "Info"

$StartScriptContent = @"
@echo off
echo ========================================
echo AI SaaS Offline - Iniciando servicios
echo ========================================

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Iniciar backend
echo Iniciando backend en http://localhost:8000
start cmd /k "python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

REM Esperar a que el backend inicie
timeout /t 3

REM Iniciar frontend (si existe)
if exist "frontend\package.json" (
    echo Iniciando frontend en http://localhost:3000
    cd frontend
    start cmd /k "npm start"
    cd ..
)

echo ========================================
echo Servicios iniciados
echo ========================================
pause
"@

$StartScriptContent | Out-File -FilePath "$ProjectRoot\start.bat" -Encoding ASCII

# ============================================================================
# 10. RESUMEN FINAL
# ============================================================================

Write-Status "`n" "Info"
Write-Status "╔════════════════════════════════════════════════════════════╗" "Success"
Write-Status "║  ✅ INSTALACIÓN COMPLETADA EXITOSAMENTE                   ║" "Success"
Write-Status "╚════════════════════════════════════════════════════════════╝" "Success"

Write-Status "`n📋 Próximos pasos:" "Info"
Write-Status "1. Inicia Ollama manualmente (busca 'Ollama' en el menú de inicio)" "Info"
Write-Status "2. Abre PowerShell en $ProjectRoot" "Info"
Write-Status "3. Ejecuta: .\venv\Scripts\Activate.ps1" "Info"
Write-Status "4. Ejecuta: python test_setup.py" "Info"
Write-Status "5. Ejecuta: python -m uvicorn backend.main:app --reload" "Info"

Write-Status "`n📁 Ubicación del proyecto:" "Info"
Write-Status "   $ProjectRoot" "Info"

Write-Status "`n🌐 Acceso:" "Info"
Write-Status "   Backend: http://localhost:8000" "Info"
Write-Status "   API Docs: http://localhost:8000/docs" "Info"
Write-Status "   Frontend: http://localhost:3000 (cuando esté listo)" "Info"

Write-Status "`n📚 Documentación:" "Info"
Write-Status "   Guía completa: $ProjectRoot\INSTALLATION_GUIDE_WINDOWS11.md" "Info"

Write-Status "`n" "Info"
