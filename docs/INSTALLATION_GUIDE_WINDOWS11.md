# Guía de Instalación: AI SaaS Offline para Windows 11

**Optimizado para**: Windows 11, 40GB RAM, GPU 6GB (RTX 2060/2070 Super)

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación de Componentes Base](#instalación-de-componentes-base)
3. [Configuración de Ollama](#configuración-de-ollama)
4. [Instalación de Modelos de IA](#instalación-de-modelos-de-ia)
5. [Setup del Backend Python](#setup-del-backend-python)
6. [Configuración de Stable Diffusion](#configuración-de-stable-diffusion)
7. [Instalación de Herramientas de Audio](#instalación-de-herramientas-de-audio)
8. [Verificación del Sistema](#verificación-del-sistema)
9. [Troubleshooting](#troubleshooting)

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Windows 11** (versión 22H2 o superior)
- **Git** (descargable desde https://git-scm.com/)
- **Python 3.11+** (descargable desde https://www.python.org/)
- **Node.js 20+** (descargable desde https://nodejs.org/)
- **Visual C++ Redistributable** (necesario para algunos componentes)
- **CUDA Toolkit 12.1** (para GPU NVIDIA - descargable desde https://developer.nvidia.com/cuda-toolkit)

### Verificar Instalaciones

Abre PowerShell y ejecuta:

```powershell
python --version
node --version
git --version
```

---

## Instalación de Componentes Base

### Paso 1: Crear Carpeta de Proyecto

```powershell
mkdir C:\AI-SaaS
cd C:\AI-SaaS
```

### Paso 2: Descargar e Instalar Ollama

1. Ve a https://ollama.com/download
2. Descarga el instalador para Windows
3. Ejecuta el instalador y sigue las instrucciones
4. Ollama se instalará en `C:\Users\[TuUsuario]\AppData\Local\Programs\Ollama`

**Verificar instalación:**

```powershell
ollama --version
```

### Paso 3: Descargar e Instalar Git LFS (para modelos grandes)

```powershell
# Descargar desde https://git-lfs.com/
# O usar Chocolatey si está instalado:
choco install git-lfs
```

---

## Configuración de Ollama

### Paso 1: Iniciar Servicio de Ollama

Ollama se ejecuta como servicio en Windows. Para verificar que está corriendo:

```powershell
# Verificar que el servicio está activo
Get-Service | Where-Object {$_.Name -like "*ollama*"}
```

Si no está corriendo, inicia Ollama manualmente desde el menú de inicio.

### Paso 2: Configurar Variables de Entorno (Opcional)

Para optimizar el uso de GPU, crea un archivo `.env` en `C:\AI-SaaS`:

```
OLLAMA_NUM_GPU=1
OLLAMA_NUM_THREAD=8
OLLAMA_MAX_LOADED_MODELS=2
OLLAMA_KEEP_ALIVE=5m
```

---

## Instalación de Modelos de IA

### Modelos Recomendados para tu GPU (6GB)

Abre PowerShell y ejecuta estos comandos uno por uno:

```powershell
# DeepSeek-R1 7B (4.7GB) - Excelente para razonamiento
ollama pull deepseek-r1:7b

# Qwen 2.5 Coder 7B (4.3GB) - Perfecto para código
ollama pull qwen2.5-coder:7b

# Llama 2 7B (3.8GB) - Alternativa ligera
ollama pull llama2:7b

# Phi 4 Mini (2.5GB) - Muy rápido, bueno para chat
ollama pull phi4-mini
```

**Nota**: Estos comandos descargarán los modelos automáticamente. Asegúrate de tener al menos 100GB de espacio libre en tu disco.

### Verificar Modelos Instalados

```powershell
ollama list
```

---

## Setup del Backend Python

### Paso 1: Crear Entorno Virtual

```powershell
cd C:\AI-SaaS
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Paso 2: Instalar Dependencias

Crea un archivo `requirements.txt`:

```
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
```

Instala las dependencias:

```powershell
pip install -r requirements.txt
```

**Nota**: La instalación de `torch` con CUDA puede tardar varios minutos.

### Paso 3: Crear Estructura de Carpetas

```powershell
mkdir backend
mkdir backend\services
mkdir backend\models
mkdir backend\utils
mkdir frontend
mkdir data
mkdir data\projects
mkdir data\models
```

---

## Configuración de Stable Diffusion

### Paso 1: Descargar Modelos

Dentro del entorno virtual de Python:

```powershell
python -c "
from diffusers import StableDiffusionXLPipeline
import torch

# Descargar modelo (primera vez toma tiempo)
pipe = StableDiffusionXLPipeline.from_pretrained(
    'stabilityai/stable-diffusion-xl-base-1.0',
    torch_dtype=torch.float16,
    use_safetensors=True
)
print('Modelo descargado exitosamente')
"
```

**Nota**: Este modelo ocupa ~7GB. Asegúrate de tener espacio suficiente.

---

## Instalación de Herramientas de Audio

### Paso 1: Instalar Whisper (Speech-to-Text)

```powershell
pip install openai-whisper
```

Descargar modelo:

```powershell
python -m whisper --model medium --language es --output_format txt "test.wav"
```

### Paso 2: Instalar Piper (Text-to-Speech)

Descarga desde: https://github.com/rhasspy/piper/releases

1. Descarga `piper_amd64.zip` para Windows
2. Extrae en `C:\AI-SaaS\tools\piper`
3. Descarga voces en español:

```powershell
cd C:\AI-SaaS\tools\piper
# Descargar voz en español
Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES-sharvard-medium.onnx" -OutFile "models\es_ES-sharvard-medium.onnx"
```

---

## Verificación del Sistema

Crea un script de prueba `test_setup.py`:

```python
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
    print("   ❌ Ollama no está corriendo. Inicia Ollama manualmente.")

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

# 4. Verificar Whisper
print("\n4️⃣  Whisper:")
try:
    result = subprocess.run(["whisper", "--version"], capture_output=True, text=True)
    print(f"   ✅ Whisper instalado")
except:
    print("   ❌ Whisper no encontrado")

# 5. Verificar Piper
print("\n5️⃣  Piper:")
piper_path = Path("C:\\AI-SaaS\\tools\\piper\\piper.exe")
if piper_path.exists():
    print(f"   ✅ Piper encontrado")
else:
    print(f"   ❌ Piper no encontrado en {piper_path}")

print("\n✅ Verificación completada")
```

Ejecuta:

```powershell
python test_setup.py
```

---

## Troubleshooting

### Problema: Ollama no inicia

**Solución:**
1. Reinicia Windows
2. Abre PowerShell como administrador
3. Ejecuta: `net start Ollama`

### Problema: GPU no se detecta

**Solución:**
1. Verifica que CUDA Toolkit 12.1 esté instalado
2. Actualiza drivers NVIDIA: https://www.nvidia.com/Download/driverDetails.aspx
3. Ejecuta: `nvidia-smi` en PowerShell para verificar

### Problema: Falta memoria (OOM)

**Solución:**
1. Reduce el tamaño del modelo (usa versiones 1B o 3B)
2. Habilita `use_8bit=True` en Stable Diffusion
3. Reduce batch size en generación de imágenes

### Problema: Whisper muy lento

**Solución:**
1. Usa modelo `small` en lugar de `medium`
2. Especifica idioma: `--language es`

---

## Próximos Pasos

Una vez completada la instalación:

1. Inicia Ollama
2. Ejecuta `test_setup.py` para verificar
3. Procede con la instalación del Backend Python
4. Luego instala el Frontend React

**Tiempo estimado de instalación**: 2-3 horas (dependiendo de velocidad de internet)

---

**Versión**: 1.0
**Última actualización**: 30 de diciembre de 2025
**Autor**: Manus AI
