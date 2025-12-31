# ============================================================================
# Rutas API para Gestión de Redes Sociales
# ============================================================================
# Archivo: backend/routes/social_media_routes.py
# ============================================================================

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/social", tags=["social_media"])

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class AddCredentialsRequest(BaseModel):
    platform: str
    credentials: Dict[str, str]

class GenerateContentRequest(BaseModel):
    topic: str
    platforms: List[str]
    content_type: str
    tone: Optional[str] = "professional"

class SchedulePostRequest(BaseModel):
    content_id: str
    platforms: List[str]
    scheduled_time: str  # ISO format
    media_paths: Optional[List[str]] = None

class PublishPostRequest(BaseModel):
    content_id: str
    platforms: List[str]
    media_paths: Optional[List[str]] = None

# ============================================================================
# RUTAS: CREDENCIALES
# ============================================================================

@router.post("/credentials/add")
async def add_credentials(request: AddCredentialsRequest):
    """Agregar credenciales para una plataforma"""
    try:
        from services.social_media_service import SocialMediaService, SocialPlatform
        
        social_service = SocialMediaService()
        
        # Validar plataforma
        try:
            platform = SocialPlatform(request.platform)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Plataforma no soportada: {request.platform}")
        
        # Agregar credenciales
        success = await social_service.add_credentials(platform, request.credentials)
        
        if not success:
            raise HTTPException(status_code=500, detail="Error agregando credenciales")
        
        return {
            "success": True,
            "platform": request.platform,
            "message": "Credenciales agregadas correctamente"
        }
    except Exception as e:
        logger.error(f"Error agregando credenciales: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/credentials/platforms")
async def get_supported_platforms():
    """Obtener plataformas soportadas"""
    from services.social_media_service import SocialPlatform
    
    platforms = [p.value for p in SocialPlatform]
    
    return {
        "success": True,
        "platforms": platforms,
        "count": len(platforms)
    }

# ============================================================================
# RUTAS: GENERACIÓN DE CONTENIDO
# ============================================================================

@router.post("/content/generate")
async def generate_content(request: GenerateContentRequest):
    """Generar contenido optimizado para múltiples plataformas"""
    try:
        from services.social_media_service import SocialMediaService, SocialPlatform, ContentType
        from services.ollama_service import OllamaService
        
        social_service = SocialMediaService()
        ollama_service = OllamaService()
        
        # Validar plataformas
        platforms = []
        for p in request.platforms:
            try:
                platforms.append(SocialPlatform(p))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Plataforma no válida: {p}")
        
        # Validar tipo de contenido
        try:
            content_type = ContentType(request.content_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Tipo de contenido no válido: {request.content_type}")
        
        # Generar contenido
        content = await social_service.generate_content(
            topic=request.topic,
            platforms=platforms,
            content_type=content_type,
            tone=request.tone,
            ollama_service=ollama_service
        )
        
        return {
            "success": True,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generando contenido: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/types")
async def get_content_types():
    """Obtener tipos de contenido disponibles"""
    from services.social_media_service import ContentType
    
    types = [t.value for t in ContentType]
    
    return {
        "success": True,
        "content_types": types
    }

# ============================================================================
# RUTAS: PROGRAMACIÓN DE POSTS
# ============================================================================

@router.post("/posts/schedule")
async def schedule_post(request: SchedulePostRequest):
    """Programar post para múltiples plataformas"""
    try:
        from services.social_media_service import SocialMediaService, SocialPlatform
        
        social_service = SocialMediaService()
        
        # Validar plataformas
        platforms = []
        for p in request.platforms:
            try:
                platforms.append(SocialPlatform(p))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Plataforma no válida: {p}")
        
        # Parsear fecha
        try:
            scheduled_time = datetime.fromisoformat(request.scheduled_time)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido (usar ISO format)")
        
        # Programar post
        post = await social_service.schedule_post(
            content_id=request.content_id,
            platforms=platforms,
            scheduled_time=scheduled_time,
            media_paths=request.media_paths
        )
        
        return {
            "success": True,
            "post": post,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error programando post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/scheduled")
async def get_scheduled_posts():
    """Obtener posts programados"""
    try:
        from services.social_media_service import SocialMediaService
        
        social_service = SocialMediaService()
        posts = social_service.get_scheduled_posts()
        
        return {
            "success": True,
            "posts": posts,
            "count": len(posts)
        }
    except Exception as e:
        logger.error(f"Error obteniendo posts programados: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: PUBLICACIÓN DE POSTS
# ============================================================================

@router.post("/posts/publish")
async def publish_post(request: PublishPostRequest):
    """Publicar post inmediatamente en múltiples plataformas"""
    try:
        from services.social_media_service import SocialMediaService, SocialPlatform
        
        social_service = SocialMediaService()
        
        # Validar plataformas
        platforms = []
        for p in request.platforms:
            try:
                platforms.append(SocialPlatform(p))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Plataforma no válida: {p}")
        
        # Publicar post
        result = await social_service.publish_post(
            content_id=request.content_id,
            platforms=platforms,
            media_paths=request.media_paths
        )
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error publicando post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/posts/history")
async def get_post_history():
    """Obtener historial de posts publicados"""
    try:
        from services.social_media_service import SocialMediaService
        
        social_service = SocialMediaService()
        posts = social_service.get_post_history()
        
        return {
            "success": True,
            "posts": posts,
            "count": len(posts)
        }
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: ESPECIFICACIONES DE PLATAFORMAS
# ============================================================================

@router.get("/platforms/specs")
async def get_platform_specs():
    """Obtener especificaciones de todas las plataformas"""
    try:
        from services.social_media_service import SocialMediaService
        
        specs = SocialMediaService.PLATFORM_SPECS
        
        return {
            "success": True,
            "specs": {k.value: v for k, v in specs.items()},
            "platforms_count": len(specs)
        }
    except Exception as e:
        logger.error(f"Error obteniendo especificaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/{platform}/specs")
async def get_platform_spec(platform: str):
    """Obtener especificaciones de una plataforma específica"""
    try:
        from services.social_media_service import SocialMediaService, SocialPlatform
        
        try:
            plat = SocialPlatform(platform)
        except ValueError:
            raise HTTPException(status_code=404, detail=f"Plataforma no encontrada: {platform}")
        
        specs = SocialMediaService.PLATFORM_SPECS.get(plat)
        
        if not specs:
            raise HTTPException(status_code=404, detail=f"Especificaciones no encontradas para {platform}")
        
        return {
            "success": True,
            "platform": platform,
            "specs": specs
        }
    except Exception as e:
        logger.error(f"Error obteniendo especificaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: ADAPTACIÓN DE CONTENIDO
# ============================================================================

@router.post("/content/adapt")
async def adapt_content_for_platform(
    platform: str,
    text: str,
    file: Optional[UploadFile] = File(None)
):
    """Adaptar contenido para una plataforma específica"""
    try:
        from services.social_media_service import SocialMediaService, SocialPlatform
        from PIL import Image
        import io
        
        try:
            plat = SocialPlatform(platform)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Plataforma no válida: {platform}")
        
        social_service = SocialMediaService()
        specs = SocialMediaService.PLATFORM_SPECS[plat]
        
        # Adaptar texto
        max_length = specs.get("max_caption_length", 280)
        adapted_text = text[:max_length] if len(text) > max_length else text
        
        # Adaptar imagen si se proporciona
        adapted_image_path = None
        if file:
            # Leer imagen
            content = await file.read()
            image = Image.open(io.BytesIO(content))
            
            # Redimensionar
            target_size = specs.get("image_size", (1080, 1080))
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Guardar
            import uuid
            from pathlib import Path
            output_dir = Path("./data/adapted_content")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            adapted_image_path = output_dir / f"{uuid.uuid4().hex[:8]}_adapted.png"
            image.save(adapted_image_path)
        
        return {
            "success": True,
            "platform": platform,
            "adapted_text": adapted_text,
            "adapted_image": str(adapted_image_path) if adapted_image_path else None,
            "specs": specs
        }
    except Exception as e:
        logger.error(f"Error adaptando contenido: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Agregar router al main.py
# ============================================================================
# En backend/main.py, agregar:
# from routes.social_media_routes import router as social_router
# app.include_router(social_router)
