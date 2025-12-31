# Prompt Master para DeepSeek / Kimi (Generación de Código)

**Rol:** Eres un Arquitecto de Software Senior especializado en React, Python (FastAPI) y Arquitecturas Híbridas (Cloud/Edge).

**Contexto del Proyecto:**
Estamos construyendo "AI SaaS Offline Complete", una plataforma que funciona tanto 100% Offline (Localhost) como Online (Cloud).
Actualmente tengo el Backend base estructurado, pero necesito:
1.  El **Frontend completo** (React + Vite + Tailwind).
2.  Una adaptación en el Backend para usar **Hugging Face Inference API** cuando estemos en modo "Online", para evitar requerir GPUs costosas en el despliegue.

**Token de Hugging Face a usar:** `[TU_TOKEN_HUGGING_FACE_AQUI]`

---

## TAREA 1: GENERAR EL FRONTEND (Carpeta `/frontend`)

Necesito que generes una aplicación **React con Vite y TypeScript**.
**Estilo:** "Futurista, Dark Mode, estilo Cyberpunk limpio pero profesional".

**Instrucciones Técnicas:**
1.  **Tech Stack:** React, TypeScript, TailwindCSS, Lucide-React (iconos), Framer Motion (animaciones), React-Router-Dom.
2.  **Estructura de Carpetas:**
    - `src/components`: Componentes UI reutilizables (Button, Card, Input).
    - `src/layouts`: DashboardLayout (Sidebar fija, Header).
    - `src/pages`: Home, Chat, ImageGenerator, VoiceStudio, Settings.
    - `src/api`: Cliente Axios configurado para apuntar a `import.meta.env.VITE_API_URL`.
3.  **Componentes Clave a Generar:**
    - **Sidebar:** Navegación entre módulos. Debe mostrar el estado "🟢 ONLINE: Hugging Face" o "🟠 OFFLINE: Local".
    - **ChatInterface:** Clon de ChatGPT. Debe soportar Streaming de texto.
    - **ImageGenerator:** Input de texto, slider de settings, y galería de resultados.
    - **Settings:** Toggle para cambiar entre modo "Cloud API" y "Local Ollama" (esto enviará un flag al backend).

## TAREA 2: ADAPTADOR DE BACKEND "CLOUD MODE"

Necesito modificar el backend para que soporte el modo híbrido.

**Instrucciones Técnicas:**
1.  Crea un nuevo servicio `backend/services/cloud_inference_service.py`.
    - Usa `huggingface_hub.InferenceClient`.
    - Implementa métodos equivalentes a `ollama_service` pero usando la API de HF.
    - **Modelos a usar en Cloud:**
        - Texto: `mistralai/Mixtral-8x7B-Instruct-v0.1` o `HuggingFaceH4/zephyr-7b-beta`.
        - Imagen: `stabilityai/stable-diffusion-xl-base-1.0`.
2.  Modifica `backend/backend_main.py`:
    - Agrega una variable de entorno `AI_MODE` (valores: `LOCAL`, `CLOUD`).
    - Si `AI_MODE == "CLOUD"`, inyecta `CloudInferenceService` en lugar de `OllamaService`.

**Salida Esperada:**
Dame el código completo de los archivos clave modificados y los nuevos archivos del frontend.
