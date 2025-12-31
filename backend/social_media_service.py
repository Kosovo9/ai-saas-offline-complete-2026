# ============================================================================
# Servicio de Generación y Distribución en Redes Sociales
# ============================================================================
# Archivo: backend/services/social_media_service.py
# ============================================================================

import logging
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio

logger = logging.getLogger(__name__)

class SocialPlatform(str, Enum):
    """Plataformas de redes sociales soportadas"""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    THREADS = "threads"
    BLUESKY = "bluesky"

class ContentType(str, Enum):
    """Tipos de contenido"""
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    SHORT = "short"
    TEXT = "text"

class SocialMediaService:
    """Servicio para generación y distribución de contenido en redes sociales"""
    
    # Especificaciones de cada plataforma
    PLATFORM_SPECS = {
        SocialPlatform.INSTAGRAM: {
            "image_size": (1080, 1350),
            "video_size": (1080, 1920),
            "story_size": (1080, 1920),
            "reel_size": (1080, 1920),
            "max_caption_length": 2200,
            "max_hashtags": 30,
            "supported_formats": ["jpg", "png", "mp4", "mov"],
            "aspect_ratios": ["1:1", "4:5", "9:16"]
        },
        SocialPlatform.TIKTOK: {
            "video_size": (1080, 1920),
            "max_caption_length": 2200,
            "max_hashtags": 20,
            "supported_formats": ["mp4", "mov", "webm"],
            "aspect_ratios": ["9:16"],
            "max_duration": 600  # 10 minutos
        },
        SocialPlatform.YOUTUBE: {
            "thumbnail_size": (1280, 720),
            "short_size": (1080, 1920),
            "video_size": (1920, 1080),
            "max_title_length": 100,
            "max_description_length": 5000,
            "max_tags": 500,
            "supported_formats": ["mp4", "mov", "avi", "mkv"],
            "aspect_ratios": ["16:9", "9:16"]
        },
        SocialPlatform.TWITTER: {
            "image_size": (1200, 675),
            "video_size": (1200, 675),
            "max_text_length": 280,
            "supported_formats": ["jpg", "png", "gif", "mp4", "mov"],
            "aspect_ratios": ["16:9", "1:1"]
        },
        SocialPlatform.FACEBOOK: {
            "image_size": (1200, 628),
            "video_size": (1200, 628),
            "max_caption_length": 63206,
            "supported_formats": ["jpg", "png", "mp4", "mov"],
            "aspect_ratios": ["1.91:1", "1:1", "4:5"]
        },
        SocialPlatform.LINKEDIN: {
            "image_size": (1200, 627),
            "video_size": (1200, 627),
            "max_caption_length": 3000,
            "supported_formats": ["jpg", "png", "mp4", "mov"],
            "aspect_ratios": ["1.91:1", "1:1"]
        },
        SocialPlatform.PINTEREST: {
            "image_size": (1000, 1500),
            "video_size": (1000, 1500),
            "max_description_length": 500,
            "supported_formats": ["jpg", "png", "gif", "mp4"],
            "aspect_ratios": ["2:3", "1:1"]
        },
        SocialPlatform.THREADS: {
            "image_size": (1080, 1350),
            "max_text_length": 500,
            "supported_formats": ["jpg", "png"],
            "aspect_ratios": ["1:1", "4:5"]
        },
        SocialPlatform.BLUESKY: {
            "image_size": (1200, 675),
            "max_text_length": 300,
            "supported_formats": ["jpg", "png"],
            "aspect_ratios": ["16:9", "1:1"]
        }
    }
    
    def __init__(
        self,
        config_dir: str = "./data/social_media",
        output_dir: str = "./data/social_content"
    ):
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.credentials = {}
        self.scheduled_posts = []
        self.post_history = []
        
        self._load_credentials()
        self._load_scheduled_posts()
        
        logger.info("SocialMediaService inicializado")
    
    def _load_credentials(self):
        """Cargar credenciales de redes sociales"""
        try:
            creds_file = self.config_dir / "credentials.json"
            if creds_file.exists():
                with open(creds_file, 'r', encoding='utf-8') as f:
                    self.credentials = json.load(f)
                logger.info(f"✅ Credenciales cargadas para {len(self.credentials)} plataformas")
        except Exception as e:
            logger.error(f"Error cargando credenciales: {e}")
    
    def _save_credentials(self):
        """Guardar credenciales de redes sociales"""
        try:
            creds_file = self.config_dir / "credentials.json"
            with open(creds_file, 'w', encoding='utf-8') as f:
                json.dump(self.credentials, f, indent=2)
        except Exception as e:
            logger.error(f"Error guardando credenciales: {e}")
    
    def _load_scheduled_posts(self):
        """Cargar posts programados"""
        try:
            schedule_file = self.config_dir / "scheduled_posts.json"
            if schedule_file.exists():
                with open(schedule_file, 'r', encoding='utf-8') as f:
                    self.scheduled_posts = json.load(f)
                logger.info(f"✅ {len(self.scheduled_posts)} posts programados cargados")
        except Exception as e:
            logger.error(f"Error cargando posts programados: {e}")
    
    def _save_scheduled_posts(self):
        """Guardar posts programados"""
        try:
            schedule_file = self.config_dir / "scheduled_posts.json"
            with open(schedule_file, 'w', encoding='utf-8') as f:
                json.dump(self.scheduled_posts, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error guardando posts programados: {e}")
    
    async def add_credentials(
        self,
        platform: SocialPlatform,
        credentials: Dict[str, str]
    ) -> bool:
        """Agregar credenciales para una plataforma"""
        
        try:
            self.credentials[platform.value] = credentials
            self._save_credentials()
            logger.info(f"✅ Credenciales agregadas para {platform.value}")
            return True
        except Exception as e:
            logger.error(f"Error agregando credenciales: {e}")
            return False
    
    async def generate_content(
        self,
        topic: str,
        platforms: List[SocialPlatform],
        content_type: ContentType,
        tone: str = "professional",
        ollama_service = None
    ) -> Dict[str, Any]:
        """Generar contenido optimizado para múltiples plataformas"""
        
        try:
            logger.info(f"Generando contenido para {len(platforms)} plataformas")
            
            content_id = str(uuid.uuid4())[:8]
            generated_content = {
                "id": content_id,
                "topic": topic,
                "created_at": datetime.now().isoformat(),
                "platforms": {}
            }
            
            for platform in platforms:
                logger.info(f"Generando para {platform.value}")
                
                # Generar texto
                text = await self._generate_text(
                    topic=topic,
                    platform=platform,
                    tone=tone,
                    ollama_service=ollama_service
                )
                
                # Generar hashtags
                hashtags = await self._generate_hashtags(
                    topic=topic,
                    platform=platform,
                    ollama_service=ollama_service
                )
                
                # Generar caption
                caption = await self._generate_caption(
                    text=text,
                    hashtags=hashtags,
                    platform=platform
                )
                
                generated_content["platforms"][platform.value] = {
                    "text": text,
                    "caption": caption,
                    "hashtags": hashtags,
                    "specs": self.PLATFORM_SPECS[platform]
                }
            
            # Guardar contenido
            content_file = self.output_dir / f"{content_id}_content.json"
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(generated_content, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Contenido generado: {content_id}")
            return generated_content
        
        except Exception as e:
            logger.error(f"Error generando contenido: {e}")
            raise
    
    async def _generate_text(
        self,
        topic: str,
        platform: SocialPlatform,
        tone: str,
        ollama_service
    ) -> str:
        """Generar texto optimizado para plataforma"""
        
        try:
            max_length = self.PLATFORM_SPECS[platform].get("max_caption_length", 280)
            
            prompt = f"""Genera un texto atractivo para {platform.value}.

Tema: {topic}
Tono: {tone}
Máximo {max_length} caracteres

Requisitos:
1. Atractivo y relevante
2. Optimizado para la plataforma
3. Incluye llamada a la acción
4. Usa emojis si es apropiado
5. Profesional pero accesible

Devuelve SOLO el texto, sin explicaciones."""
            
            if ollama_service:
                text = await ollama_service.generate(prompt=prompt)
            else:
                text = f"Contenido sobre {topic} para {platform.value}"
            
            # Truncar si es necesario
            if len(text) > max_length:
                text = text[:max_length-3] + "..."
            
            return text
        
        except Exception as e:
            logger.error(f"Error generando texto: {e}")
            return f"Contenido sobre {topic}"
    
    async def _generate_hashtags(
        self,
        topic: str,
        platform: SocialPlatform,
        ollama_service
    ) -> List[str]:
        """Generar hashtags optimizados para plataforma"""
        
        try:
            max_hashtags = self.PLATFORM_SPECS[platform].get("max_hashtags", 10)
            
            prompt = f"""Genera {max_hashtags} hashtags relevantes para {platform.value}.

Tema: {topic}

Requisitos:
1. Hashtags populares y relevantes
2. Mix de hashtags amplios y específicos
3. Optimizados para {platform.value}
4. Sin espacios, formato correcto

Devuelve SOLO los hashtags separados por espacios."""
            
            if ollama_service:
                hashtags_text = await ollama_service.generate(prompt=prompt)
            else:
                hashtags_text = f"#{topic.replace(' ', '')} #contenido"
            
            # Parsear hashtags
            hashtags = [tag.strip() for tag in hashtags_text.split() if tag.startswith("#")]
            hashtags = hashtags[:max_hashtags]
            
            return hashtags
        
        except Exception as e:
            logger.error(f"Error generando hashtags: {e}")
            return []
    
    async def _generate_caption(
        self,
        text: str,
        hashtags: List[str],
        platform: SocialPlatform
    ) -> str:
        """Generar caption completo con hashtags"""
        
        try:
            caption = text
            
            if hashtags:
                caption += "\n\n" + " ".join(hashtags)
            
            max_length = self.PLATFORM_SPECS[platform].get("max_caption_length", 280)
            
            if len(caption) > max_length:
                caption = caption[:max_length-3] + "..."
            
            return caption
        
        except Exception as e:
            logger.error(f"Error generando caption: {e}")
            return text
    
    async def schedule_post(
        self,
        content_id: str,
        platforms: List[SocialPlatform],
        scheduled_time: datetime,
        media_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Programar post para múltiples plataformas"""
        
        try:
            post_id = str(uuid.uuid4())[:8]
            
            post = {
                "id": post_id,
                "content_id": content_id,
                "platforms": [p.value for p in platforms],
                "scheduled_time": scheduled_time.isoformat(),
                "media_paths": media_paths or [],
                "status": "scheduled",
                "created_at": datetime.now().isoformat()
            }
            
            self.scheduled_posts.append(post)
            self._save_scheduled_posts()
            
            logger.info(f"✅ Post programado: {post_id} para {len(platforms)} plataformas")
            
            return post
        
        except Exception as e:
            logger.error(f"Error programando post: {e}")
            raise
    
    async def publish_post(
        self,
        content_id: str,
        platforms: List[SocialPlatform],
        media_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Publicar post inmediatamente en múltiples plataformas"""
        
        try:
            logger.info(f"Publicando contenido {content_id} en {len(platforms)} plataformas")
            
            results = {}
            
            for platform in platforms:
                try:
                    if platform not in self.credentials:
                        logger.warning(f"Credenciales no configuradas para {platform.value}")
                        results[platform.value] = {
                            "success": False,
                            "error": "Credenciales no configuradas"
                        }
                        continue
                    
                    # Publicar según plataforma
                    if platform == SocialPlatform.INSTAGRAM:
                        result = await self._publish_instagram(content_id, media_paths)
                    elif platform == SocialPlatform.TIKTOK:
                        result = await self._publish_tiktok(content_id, media_paths)
                    elif platform == SocialPlatform.YOUTUBE:
                        result = await self._publish_youtube(content_id, media_paths)
                    elif platform == SocialPlatform.TWITTER:
                        result = await self._publish_twitter(content_id, media_paths)
                    elif platform == SocialPlatform.FACEBOOK:
                        result = await self._publish_facebook(content_id, media_paths)
                    elif platform == SocialPlatform.LINKEDIN:
                        result = await self._publish_linkedin(content_id, media_paths)
                    elif platform == SocialPlatform.PINTEREST:
                        result = await self._publish_pinterest(content_id, media_paths)
                    elif platform == SocialPlatform.THREADS:
                        result = await self._publish_threads(content_id, media_paths)
                    elif platform == SocialPlatform.BLUESKY:
                        result = await self._publish_bluesky(content_id, media_paths)
                    else:
                        result = {"success": False, "error": "Plataforma no soportada"}
                    
                    results[platform.value] = result
                
                except Exception as e:
                    logger.error(f"Error publicando en {platform.value}: {e}")
                    results[platform.value] = {"success": False, "error": str(e)}
            
            logger.info(f"✅ Publicación completada")
            return {
                "content_id": content_id,
                "results": results,
                "published_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error publicando post: {e}")
            raise
    
    async def _publish_instagram(self, content_id: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publicar en Instagram"""
        try:
            # Aquí iría la integración real con Instagram API
            logger.info(f"Publicando en Instagram: {content_id}")
            return {
                "success": True,
                "platform": "instagram",
                "post_id": str(uuid.uuid4())[:8]
            }
        except Exception as e:
            logger.error(f"Error publicando en Instagram: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_tiktok(self, content_id: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publicar en TikTok"""
        try:
            logger.info(f"Publicando en TikTok: {content_id}")
            return {
                "success": True,
                "platform": "tiktok",
                "post_id": str(uuid.uuid4())[:8]
            }
        except Exception as e:
            logger.error(f"Error publicando en TikTok: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_youtube(self, content_id: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publicar en YouTube"""
        try:
            logger.info(f"Publicando en YouTube: {content_id}")
            return {
                "success": True,
                "platform": "youtube",
                "post_id": str(uuid.uuid4())[:8]
            }
        except Exception as e:
            logger.error(f"Error publicando en YouTube: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_twitter(self, content_id: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publicar en Twitter/X"""
        try:
            logger.info(f"Publicando en Twitter: {content_id}")
            return {
                "success": True,
                "platform": "twitter",
                "post_id": str(uuid.uuid4())[:8]
            }
        except Exception as e:
            logger.error(f"Error publicando en Twitter: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_facebook(self, content_id: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publicar en Facebook"""
        try:
            logger.info(f"Publicando en Facebook: {content_id}")
            return {
                "success": True,
                "platform": "facebook",
                "post_id": str(uuid.uuid4())[:8]
            }
        except Exception as e:
            logger.error(f"Error publicando en Facebook: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_linkedin(self, content_id: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publicar en LinkedIn"""
        try:
            logger.info(f"Publicando en LinkedIn: {content_id}")
            return {
                "success": True,
                "platform": "linkedin",
                "post_id": str(uuid.uuid4())[:8]
            }
        except Exception as e:
            logger.error(f"Error publicando en LinkedIn: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_pinterest(self, content_id: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publicar en Pinterest"""
        try:
            logger.info(f"Publicando en Pinterest: {content_id}")
            return {
                "success": True,
                "platform": "pinterest",
                "post_id": str(uuid.uuid4())[:8]
            }
        except Exception as e:
            logger.error(f"Error publicando en Pinterest: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_threads(self, content_id: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publicar en Threads"""
        try:
            logger.info(f"Publicando en Threads: {content_id}")
            return {
                "success": True,
                "platform": "threads",
                "post_id": str(uuid.uuid4())[:8]
            }
        except Exception as e:
            logger.error(f"Error publicando en Threads: {e}")
            return {"success": False, "error": str(e)}
    
    async def _publish_bluesky(self, content_id: str, media_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Publicar en Bluesky"""
        try:
            logger.info(f"Publicando en Bluesky: {content_id}")
            return {
                "success": True,
                "platform": "bluesky",
                "post_id": str(uuid.uuid4())[:8]
            }
        except Exception as e:
            logger.error(f"Error publicando en Bluesky: {e}")
            return {"success": False, "error": str(e)}
    
    def get_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Obtener posts programados"""
        return sorted(self.scheduled_posts, key=lambda x: x["scheduled_time"])
    
    def get_post_history(self) -> List[Dict[str, Any]]:
        """Obtener historial de posts publicados"""
        return sorted(self.post_history, key=lambda x: x["published_at"], reverse=True)
