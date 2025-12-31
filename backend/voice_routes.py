# ============================================================================
# Rutas API para Voice Chat y Clonación de Voz
# ============================================================================
# Archivo: backend/routes/voice_routes.py
# Agregar estas rutas al archivo main.py
# ============================================================================

from fastapi import APIRouter, UploadFile, File, WebSocket, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class VoiceProfileCreate(BaseModel):
    voice_name: str
    description: Optional[str] = None

class VoiceChatRequest(BaseModel):
    audio_file_path: str
    voice_id: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None

class VoiceToProjectRequest(BaseModel):
    audio_file_path: str
    project_id: str
    file_path: str
    instruction: Optional[str] = None

# ============================================================================
# RUTAS: CLONACIÓN DE VOZ
# ============================================================================

@router.post("/clone/create-profile")
async def create_voice_profile(
    voice_name: str,
    description: Optional[str] = None,
    files: List[UploadFile] = File(...)
):
    """Crear perfil de voz a partir de muestras de audio"""
    try:
        from services.voice_cloning_service import VoiceCloningService
        
        voice_service = VoiceCloningService()
        
        # Guardar archivos temporales
        temp_paths = []
        for file in files:
            temp_path = f"./data/temp/{file.filename}"
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            temp_paths.append(temp_path)
        
        # Crear perfil
        result = await voice_service.create_voice_profile(
            voice_name=voice_name,
            audio_samples=temp_paths,
            description=description
        )
        
        # Limpiar temporales
        import os
        for path in temp_paths:
            try:
                os.remove(path)
            except:
                pass
        
        return {
            "success": True,
            "profile": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creando perfil de voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clone/profiles")
async def list_voice_profiles():
    """Listar todos los perfiles de voz disponibles"""
    try:
        from services.voice_cloning_service import VoiceCloningService
        
        voice_service = VoiceCloningService()
        profiles = voice_service.list_voice_profiles()
        
        return {
            "success": True,
            "profiles": profiles,
            "count": len(profiles)
        }
    except Exception as e:
        logger.error(f"Error listando perfiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clone/profiles/{voice_id}")
async def delete_voice_profile(voice_id: str):
    """Eliminar perfil de voz"""
    try:
        from services.voice_cloning_service import VoiceCloningService
        
        voice_service = VoiceCloningService()
        success = await voice_service.delete_voice_profile(voice_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Perfil no encontrado")
        
        return {
            "success": True,
            "message": "Perfil eliminado",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error eliminando perfil: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clone/add-sample/{voice_id}")
async def add_voice_sample(voice_id: str, file: UploadFile = File(...)):
    """Agregar muestra de audio a un perfil existente"""
    try:
        from services.voice_cloning_service import VoiceCloningService
        
        voice_service = VoiceCloningService()
        
        # Guardar archivo temporal
        temp_path = f"./data/temp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Agregar muestra
        result = await voice_service.upload_voice_sample(voice_id, temp_path)
        
        # Limpiar temporal
        import os
        try:
            os.remove(temp_path)
        except:
            pass
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error agregando muestra: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: VOICE CHAT
# ============================================================================

@router.post("/chat/session")
async def voice_chat_session(request: VoiceChatRequest):
    """Sesión completa de voice chat: audio → texto → IA → voz"""
    try:
        from services.voice_cloning_service import VoiceChatService
        from services.ollama_service import OllamaService
        from services.audio_service import AudioService
        from services.voice_cloning_service import VoiceCloningService
        
        # Inicializar servicios
        ollama = OllamaService()
        audio = AudioService()
        voice_cloning = VoiceCloningService()
        voice_chat = VoiceChatService(ollama, audio, voice_cloning)
        
        # Ejecutar sesión
        result = await voice_chat.voice_chat_session(
            audio_input_path=request.audio_file_path,
            voice_id=request.voice_id,
            model=request.model,
            system_prompt=request.system_prompt
        )
        
        return {
            "success": True,
            "session": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error en voice chat session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/chat/stream")
async def websocket_voice_chat(websocket: WebSocket):
    """Voice chat con streaming en tiempo real"""
    await websocket.accept()
    
    try:
        from services.voice_cloning_service import VoiceChatService
        from services.ollama_service import OllamaService
        from services.audio_service import AudioService
        from services.voice_cloning_service import VoiceCloningService
        
        # Inicializar servicios
        ollama = OllamaService()
        audio = AudioService()
        voice_cloning = VoiceCloningService()
        voice_chat = VoiceChatService(ollama, audio, voice_cloning)
        
        while True:
            # Recibir datos
            data = await websocket.receive_json()
            audio_file_path = data.get("audio_file_path")
            voice_id = data.get("voice_id")
            model = data.get("model")
            
            # Procesar stream
            async for chunk in voice_chat.stream_voice_chat(
                audio_input_path=audio_file_path,
                voice_id=voice_id,
                model=model
            ):
                await websocket.send_json(chunk)
    
    except Exception as e:
        logger.error(f"Error en websocket voice chat: {e}")
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })
    finally:
        await websocket.close()

@router.post("/chat/to-project")
async def voice_to_project(request: VoiceToProjectRequest):
    """Dictar contenido directamente al proyecto"""
    try:
        from services.voice_cloning_service import VoiceChatService
        from services.ollama_service import OllamaService
        from services.audio_service import AudioService
        from services.voice_cloning_service import VoiceCloningService
        
        # Inicializar servicios
        ollama = OllamaService()
        audio = AudioService()
        voice_cloning = VoiceCloningService()
        voice_chat = VoiceChatService(ollama, audio, voice_cloning)
        
        # Dictar al proyecto
        result = await voice_chat.voice_to_project(
            audio_input_path=request.audio_file_path,
            project_id=request.project_id,
            file_path=request.file_path,
            instruction=request.instruction or "Escribe esto en el proyecto"
        )
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error en voice_to_project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: DESCARGA DE AUDIO
# ============================================================================

@router.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """Descargar archivo de audio generado"""
    try:
        from pathlib import Path
        
        audio_path = Path(f"./data/audio/{audio_id}.wav")
        
        if not audio_path.exists():
            raise HTTPException(status_code=404, detail="Audio no encontrado")
        
        return FileResponse(
            audio_path,
            media_type="audio/wav",
            filename=f"{audio_id}.wav"
        )
    except Exception as e:
        logger.error(f"Error descargando audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: UPLOAD DE AUDIO
# ============================================================================

@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """Subir archivo de audio para procesamiento"""
    try:
        from pathlib import Path
        import uuid
        
        # Generar nombre único
        file_id = str(uuid.uuid4())[:8]
        file_ext = Path(file.filename).suffix or ".wav"
        
        # Guardar archivo
        upload_dir = Path("./data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / f"{file_id}{file_ext}"
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"✅ Audio subido: {file_id}")
        
        return {
            "success": True,
            "file_id": file_id,
            "file_path": str(file_path),
            "filename": file.filename,
            "size": len(content),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error subiendo audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: INFORMACIÓN DE SERVICIOS
# ============================================================================

@router.get("/status")
async def voice_services_status():
    """Obtener estado de servicios de audio"""
    try:
        from services.audio_service import AudioService
        from services.voice_cloning_service import VoiceCloningService
        
        audio = AudioService()
        voice_cloning = VoiceCloningService()
        
        return {
            "success": True,
            "audio_services": audio.check_available(),
            "voice_profiles": len(voice_cloning.voice_profiles),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error obteniendo status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Agregar router al main.py
# ============================================================================
# En backend/main.py, agregar:
# from routes.voice_routes import router as voice_router
# app.include_router(voice_router)
