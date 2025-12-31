# ============================================================================
# Rutas API para Gestión de Super Prompts
# ============================================================================
# Archivo: backend/routes/prompt_routes.py
# ============================================================================

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/prompts", tags=["prompts"])

# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class GeneratePromptRequest(BaseModel):
    task_description: str
    category: str  # coding, writing, analysis, creative, business, etc.
    tone: str  # professional, casual, academic, creative, technical, friendly, formal
    context: Optional[Dict] = None

class FillTemplateRequest(BaseModel):
    template_name: str
    values: Dict[str, str]

class UpdateEffectivenessRequest(BaseModel):
    prompt_id: str
    score: float  # 0-10

# ============================================================================
# RUTAS: GENERACIÓN DE PROMPTS
# ============================================================================

@router.post("/generate")
async def generate_super_prompt(request: GeneratePromptRequest):
    """Generar un super prompt optimizado"""
    try:
        from services.prompt_engineering_service import PromptEngineeringService, PromptCategory, PromptTone
        from services.ollama_service import OllamaService
        
        prompt_service = PromptEngineeringService()
        ollama_service = OllamaService()
        
        # Validar categoría y tono
        try:
            category = PromptCategory(request.category)
            tone = PromptTone(request.tone)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Categoría o tono inválido: {e}")
        
        # Generar prompt
        result = await prompt_service.generate_super_prompt(
            task_description=request.task_description,
            category=category,
            tone=tone,
            context=request.context,
            ollama_service=ollama_service
        )
        
        return {
            "success": True,
            "prompt": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generando prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: TEMPLATES
# ============================================================================

@router.get("/templates")
async def list_templates():
    """Listar todos los templates disponibles"""
    try:
        from services.prompt_engineering_service import PromptEngineeringService
        
        prompt_service = PromptEngineeringService()
        templates = prompt_service.list_templates()
        
        return {
            "success": True,
            "templates": templates,
            "count": len(templates)
        }
    except Exception as e:
        logger.error(f"Error listando templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_name}")
async def get_template(template_name: str):
    """Obtener template específico"""
    try:
        from services.prompt_engineering_service import PromptEngineeringService
        
        prompt_service = PromptEngineeringService()
        template = prompt_service.get_template(template_name)
        
        if not template:
            raise HTTPException(status_code=404, detail="Template no encontrado")
        
        return {
            "success": True,
            "template": template
        }
    except Exception as e:
        logger.error(f"Error obteniendo template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/templates/fill")
async def fill_template(request: FillTemplateRequest):
    """Rellenar template con valores"""
    try:
        from services.prompt_engineering_service import PromptEngineeringService
        
        prompt_service = PromptEngineeringService()
        filled_prompt = prompt_service.fill_template(
            template_name=request.template_name,
            values=request.values
        )
        
        return {
            "success": True,
            "prompt": filled_prompt,
            "template_name": request.template_name
        }
    except Exception as e:
        logger.error(f"Error rellenando template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: BIBLIOTECA DE PROMPTS
# ============================================================================

@router.get("/library")
async def get_library():
    """Obtener biblioteca de prompts guardados"""
    try:
        from services.prompt_engineering_service import PromptEngineeringService
        
        prompt_service = PromptEngineeringService()
        library = prompt_service.get_library()
        
        return {
            "success": True,
            "prompts": library,
            "count": len(library)
        }
    except Exception as e:
        logger.error(f"Error obteniendo biblioteca: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/library/{prompt_id}")
async def get_prompt(prompt_id: str):
    """Obtener prompt específico de la biblioteca"""
    try:
        from services.prompt_engineering_service import PromptEngineeringService
        
        prompt_service = PromptEngineeringService()
        prompt = prompt_service.get_prompt(prompt_id)
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt no encontrado")
        
        return {
            "success": True,
            "prompt": prompt
        }
    except Exception as e:
        logger.error(f"Error obteniendo prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/library/{prompt_id}")
async def delete_prompt(prompt_id: str):
    """Eliminar prompt de la biblioteca"""
    try:
        from services.prompt_engineering_service import PromptEngineeringService
        
        prompt_service = PromptEngineeringService()
        success = prompt_service.delete_prompt(prompt_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Prompt no encontrado")
        
        return {
            "success": True,
            "message": "Prompt eliminado",
            "prompt_id": prompt_id
        }
    except Exception as e:
        logger.error(f"Error eliminando prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: EFECTIVIDAD Y ANALYTICS
# ============================================================================

@router.post("/effectiveness")
async def update_effectiveness(request: UpdateEffectivenessRequest):
    """Actualizar puntuación de efectividad de un prompt"""
    try:
        from services.prompt_engineering_service import PromptEngineeringService
        
        # Validar score
        if not 0 <= request.score <= 10:
            raise HTTPException(status_code=400, detail="Score debe estar entre 0 y 10")
        
        prompt_service = PromptEngineeringService()
        success = prompt_service.update_effectiveness(
            prompt_id=request.prompt_id,
            score=request.score
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Prompt no encontrado")
        
        return {
            "success": True,
            "message": "Efectividad actualizada",
            "prompt_id": request.prompt_id,
            "score": request.score
        }
    except Exception as e:
        logger.error(f"Error actualizando efectividad: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics")
async def get_analytics():
    """Obtener analytics de prompts"""
    try:
        from services.prompt_engineering_service import PromptEngineeringService
        
        prompt_service = PromptEngineeringService()
        library = prompt_service.get_library()
        
        # Calcular estadísticas
        total_prompts = len(library)
        total_usage = sum(p.get("usage_count", 0) for p in library)
        avg_effectiveness = sum(p.get("effectiveness_score", 0) for p in library) / total_prompts if total_prompts > 0 else 0
        
        # Top prompts
        top_prompts = sorted(library, key=lambda x: x.get("effectiveness_score", 0), reverse=True)[:5]
        
        # Por categoría
        by_category = {}
        for prompt in library:
            cat = prompt.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += 1
        
        return {
            "success": True,
            "analytics": {
                "total_prompts": total_prompts,
                "total_usage": total_usage,
                "average_effectiveness": round(avg_effectiveness, 2),
                "top_prompts": top_prompts,
                "by_category": by_category
            }
        }
    except Exception as e:
        logger.error(f"Error obteniendo analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: EXPORT
# ============================================================================

@router.get("/export/{format}")
async def export_library(format: str = "json"):
    """Exportar biblioteca de prompts"""
    try:
        from services.prompt_engineering_service import PromptEngineeringService
        from fastapi.responses import FileResponse
        
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Formato debe ser 'json' o 'csv'")
        
        prompt_service = PromptEngineeringService()
        export_path = prompt_service.export_library(format=format)
        
        return FileResponse(
            export_path,
            media_type="application/json" if format == "json" else "text/csv",
            filename=f"prompts_library.{format}"
        )
    except Exception as e:
        logger.error(f"Error exportando biblioteca: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUTAS: CATEGORÍAS Y TONOS
# ============================================================================

@router.get("/categories")
async def get_categories():
    """Obtener categorías disponibles"""
    from services.prompt_engineering_service import PromptCategory
    
    categories = [cat.value for cat in PromptCategory]
    
    return {
        "success": True,
        "categories": categories
    }

@router.get("/tones")
async def get_tones():
    """Obtener tonos disponibles"""
    from services.prompt_engineering_service import PromptTone
    
    tones = [tone.value for tone in PromptTone]
    
    return {
        "success": True,
        "tones": tones
    }

# ============================================================================
# Agregar router al main.py
# ============================================================================
# En backend/main.py, agregar:
# from routes.prompt_routes import router as prompt_router
# app.include_router(prompt_router)
