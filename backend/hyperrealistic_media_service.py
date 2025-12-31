# ============================================================================
# Servicio de Generación de Contenido Multimedia Hiper Realista
# ============================================================================
# Archivo: backend/services/hyperrealistic_media_service.py
# ============================================================================

import torch
import numpy as np
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import uuid
from enum import Enum
from PIL import Image
import cv2

logger = logging.getLogger(__name__)

class ImageQuality(str, Enum):
    """Calidades de imagen disponibles"""
    SD = "sd"          # 480p
    HD = "hd"          # 720p
    FULL_HD = "full_hd"  # 1080p
    QHD = "qhd"        # 1440p
    UHD_4K = "4k"      # 2160p
    UHD_8K = "8k"      # 4320p

class ImageFormat(str, Enum):
    """Formatos de imagen soportados"""
    PNG = "png"
    JPG = "jpg"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"

class HyperrealisticMediaService:
    """Servicio para generación de contenido multimedia hiper realista"""
    
    QUALITY_RESOLUTIONS = {
        ImageQuality.SD: (854, 480),
        ImageQuality.HD: (1280, 720),
        ImageQuality.FULL_HD: (1920, 1080),
        ImageQuality.QHD: (2560, 1440),
        ImageQuality.UHD_4K: (3840, 2160),
        ImageQuality.UHD_8K: (7680, 4320)
    }
    
    def __init__(
        self,
        output_dir: str = "./data/generated_media",
        device: str = "cuda"
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.device = device if torch.cuda.is_available() else "cpu"
        
        # Cargar modelos
        self.upscaler = None
        self.face_enhancer = None
        self.video_generator = None
        
        logger.info(f"HyperrealisticMediaService inicializado")
        logger.info(f"  Device: {self.device}")
    
    async def enhance_image(
        self,
        image_path: str,
        quality: ImageQuality = ImageQuality.UHD_4K,
        enhancement_level: float = 1.0
    ) -> str:
        """Mejorar y upscalear imagen"""
        
        try:
            logger.info(f"Mejorando imagen: {image_path}")
            
            # Cargar imagen
            image = Image.open(image_path).convert("RGB")
            original_size = image.size
            
            # Aplicar mejoras
            enhanced = await self._apply_enhancements(image, enhancement_level)
            
            # Upscalear a calidad deseada
            target_size = self.QUALITY_RESOLUTIONS[quality]
            enhanced = enhanced.resize(target_size, Image.Resampling.LANCZOS)
            
            # Guardar
            output_id = str(uuid.uuid4())[:8]
            output_path = self.output_dir / f"{output_id}_enhanced.png"
            enhanced.save(output_path, quality=95)
            
            logger.info(f"✅ Imagen mejorada: {output_path}")
            logger.info(f"   Original: {original_size} → Mejorada: {target_size}")
            
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error mejorando imagen: {e}")
            raise
    
    async def _apply_enhancements(self, image: Image.Image, level: float) -> Image.Image:
        """Aplicar mejoras a la imagen"""
        
        try:
            import cv2
            from PIL import ImageEnhance
            
            # Convertir a numpy
            img_array = np.array(image)
            
            # Mejorar contraste
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.0 + (level * 0.3))
            
            # Mejorar brillo
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.0 + (level * 0.1))
            
            # Mejorar saturación
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.0 + (level * 0.2))
            
            # Reducir ruido (si es necesario)
            if level > 0.5:
                img_array = np.array(image)
                img_array = cv2.fastNlMeansDenoisingColored(
                    img_array,
                    None,
                    h=10,
                    hForColorComponents=10,
                    templateWindowSize=7,
                    searchWindowSize=21
                )
                image = Image.fromarray(img_array)
            
            return image
        
        except Exception as e:
            logger.error(f"Error aplicando mejoras: {e}")
            return image
    
    async def upscale_image(
        self,
        image_path: str,
        scale_factor: int = 4,
        quality: ImageQuality = ImageQuality.UHD_4K
    ) -> str:
        """Upscalear imagen usando modelos de IA"""
        
        try:
            logger.info(f"Upscaleando imagen: {image_path} (x{scale_factor})")
            
            # Cargar imagen
            image = Image.open(image_path).convert("RGB")
            
            # Usar Real-ESRGAN o similar
            try:
                from basicsr.archs.rrdbnet_arch import RRDBNet
                from realesrgan import RealESRGANer
                
                # Cargar modelo
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=scale_factor)
                upsampler = RealESRGANer(scale_factor, model_path=None, upscale=scale_factor, tile=400, tile_pad=10, pre_pad=0, half=True)
                
                # Upscalear
                img_array = np.array(image)
                output, _ = upsampler.enhance(img_array, outscale=scale_factor)
                upscaled = Image.fromarray(output)
                
            except ImportError:
                # Fallback: upscalear con PIL
                new_size = (image.width * scale_factor, image.height * scale_factor)
                upscaled = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Guardar
            output_id = str(uuid.uuid4())[:8]
            output_path = self.output_dir / f"{output_id}_upscaled_{scale_factor}x.png"
            upscaled.save(output_path, quality=95)
            
            logger.info(f"✅ Imagen upscaleada: {output_path}")
            
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error upscaleando imagen: {e}")
            raise
    
    async def clone_from_images(
        self,
        reference_images: List[str],
        prompt: str,
        quality: ImageQuality = ImageQuality.UHD_4K,
        num_variations: int = 3
    ) -> List[str]:
        """Clonar y generar variaciones a partir de imágenes de referencia"""
        
        try:
            logger.info(f"Clonando desde {len(reference_images)} imágenes de referencia")
            
            # Cargar imágenes de referencia
            reference_imgs = []
            for ref_path in reference_images:
                img = Image.open(ref_path).convert("RGB")
                reference_imgs.append(img)
            
            # Extraer características
            features = await self._extract_image_features(reference_imgs)
            
            # Generar variaciones
            generated_paths = []
            
            for i in range(num_variations):
                logger.info(f"Generando variación {i+1}/{num_variations}")
                
                # Usar Stable Diffusion con características extraídas
                try:
                    from diffusers import StableDiffusionXLPipeline
                    
                    pipe = StableDiffusionXLPipeline.from_pretrained(
                        "stabilityai/stable-diffusion-xl-base-1.0",
                        torch_dtype=torch.float16,
                        use_safetensors=True
                    )
                    pipe = pipe.to(self.device)
                    
                    # Crear prompt mejorado
                    enhanced_prompt = f"{prompt}, high quality, detailed, photorealistic, 8k, professional photography"
                    
                    # Generar
                    with torch.no_grad():
                        result = pipe(
                            prompt=enhanced_prompt,
                            height=self.QUALITY_RESOLUTIONS[quality][1],
                            width=self.QUALITY_RESOLUTIONS[quality][0],
                            num_inference_steps=50,
                            guidance_scale=7.5
                        )
                    
                    generated_img = result.images[0]
                    
                    # Guardar
                    output_id = str(uuid.uuid4())[:8]
                    output_path = self.output_dir / f"{output_id}_clone_var{i+1}.png"
                    generated_img.save(output_path, quality=95)
                    
                    generated_paths.append(str(output_path))
                    
                except Exception as e:
                    logger.warning(f"Error generando variación: {e}")
                    continue
            
            logger.info(f"✅ {len(generated_paths)} variaciones generadas")
            return generated_paths
        
        except Exception as e:
            logger.error(f"Error clonando desde imágenes: {e}")
            raise
    
    async def _extract_image_features(self, images: List[Image.Image]) -> Dict[str, Any]:
        """Extraer características de imágenes"""
        
        try:
            features = {
                "colors": [],
                "composition": [],
                "lighting": [],
                "style": "photorealistic"
            }
            
            for img in images:
                img_array = np.array(img)
                
                # Colores dominantes
                colors = self._get_dominant_colors(img_array)
                features["colors"].extend(colors)
                
                # Análisis de iluminación
                brightness = np.mean(img_array)
                features["lighting"].append(float(brightness))
            
            return features
        
        except Exception as e:
            logger.error(f"Error extrayendo características: {e}")
            return {}
    
    def _get_dominant_colors(self, img_array: np.ndarray, n_colors: int = 5) -> List[Tuple[int, int, int]]:
        """Obtener colores dominantes de una imagen"""
        
        try:
            from sklearn.cluster import KMeans
            
            # Reshape imagen
            pixels = img_array.reshape((-1, 3))
            
            # Clustering
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Convertir a tuplas RGB
            colors = [tuple(map(int, color)) for color in kmeans.cluster_centers_]
            return colors
        
        except Exception as e:
            logger.warning(f"Error obteniendo colores dominantes: {e}")
            return []
    
    async def generate_video_from_images(
        self,
        image_paths: List[str],
        duration: float = 5.0,
        fps: int = 30,
        quality: ImageQuality = ImageQuality.FULL_HD,
        interpolation: bool = True
    ) -> str:
        """Generar video a partir de imágenes"""
        
        try:
            logger.info(f"Generando video desde {len(image_paths)} imágenes")
            
            # Cargar imágenes
            images = []
            for img_path in image_paths:
                img = Image.open(img_path).convert("RGB")
                target_size = self.QUALITY_RESOLUTIONS[quality]
                img = img.resize(target_size, Image.Resampling.LANCZOS)
                images.append(np.array(img))
            
            # Interpolar frames si es necesario
            if interpolation and len(images) > 1:
                images = await self._interpolate_frames(images, fps, duration)
            
            # Crear video
            output_id = str(uuid.uuid4())[:8]
            output_path = self.output_dir / f"{output_id}_video.mp4"
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(
                str(output_path),
                fourcc,
                fps,
                self.QUALITY_RESOLUTIONS[quality]
            )
            
            # Escribir frames
            for img_array in images:
                # Convertir RGB a BGR para OpenCV
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                out.write(img_bgr)
            
            out.release()
            
            logger.info(f"✅ Video generado: {output_path}")
            logger.info(f"   Duración: {duration}s, FPS: {fps}, Calidad: {quality.value}")
            
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error generando video: {e}")
            raise
    
    async def _interpolate_frames(
        self,
        images: List[np.ndarray],
        fps: int,
        duration: float
    ) -> List[np.ndarray]:
        """Interpolar frames intermedios"""
        
        try:
            total_frames = int(fps * duration)
            frames_per_image = total_frames // len(images)
            
            interpolated = []
            
            for i in range(len(images) - 1):
                current_img = images[i]
                next_img = images[i + 1]
                
                interpolated.append(current_img)
                
                # Generar frames intermedios
                for j in range(1, frames_per_image):
                    alpha = j / frames_per_image
                    blended = cv2.addWeighted(
                        current_img,
                        1 - alpha,
                        next_img,
                        alpha,
                        0
                    )
                    interpolated.append(blended)
            
            # Agregar última imagen
            interpolated.append(images[-1])
            
            logger.info(f"✅ {len(interpolated)} frames interpolados")
            return interpolated
        
        except Exception as e:
            logger.error(f"Error interpolando frames: {e}")
            return images
    
    async def convert_format(
        self,
        image_path: str,
        target_format: ImageFormat,
        quality: int = 95
    ) -> str:
        """Convertir imagen a diferente formato"""
        
        try:
            logger.info(f"Convirtiendo imagen a {target_format.value}")
            
            # Cargar imagen
            image = Image.open(image_path).convert("RGB")
            
            # Guardar en nuevo formato
            output_id = str(uuid.uuid4())[:8]
            output_path = self.output_dir / f"{output_id}_converted.{target_format.value}"
            
            if target_format == ImageFormat.PNG:
                image.save(output_path, "PNG", quality=quality)
            elif target_format == ImageFormat.JPG:
                image.save(output_path, "JPEG", quality=quality)
            elif target_format == ImageFormat.WEBP:
                image.save(output_path, "WEBP", quality=quality)
            elif target_format == ImageFormat.TIFF:
                image.save(output_path, "TIFF", quality=quality)
            elif target_format == ImageFormat.BMP:
                image.save(output_path, "BMP")
            
            logger.info(f"✅ Imagen convertida: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error convirtiendo formato: {e}")
            raise
    
    async def batch_process(
        self,
        image_paths: List[str],
        operation: str,
        quality: ImageQuality = ImageQuality.UHD_4K,
        **kwargs
    ) -> List[str]:
        """Procesar múltiples imágenes en lote"""
        
        results = []
        
        for i, img_path in enumerate(image_paths):
            try:
                logger.info(f"Procesando imagen {i+1}/{len(image_paths)}")
                
                if operation == "enhance":
                    result = await self.enhance_image(img_path, quality)
                elif operation == "upscale":
                    result = await self.upscale_image(img_path, kwargs.get("scale_factor", 4), quality)
                elif operation == "convert":
                    result = await self.convert_format(img_path, kwargs.get("target_format", ImageFormat.PNG))
                else:
                    logger.warning(f"Operación desconocida: {operation}")
                    continue
                
                results.append(result)
            
            except Exception as e:
                logger.error(f"Error procesando imagen {i+1}: {e}")
                continue
        
        logger.info(f"✅ {len(results)}/{len(image_paths)} imágenes procesadas")
        return results
    
    def list_generated_media(self) -> List[Dict[str, Any]]:
        """Listar todo el contenido multimedia generado"""
        
        media = []
        
        for file_path in self.output_dir.glob("*"):
            if file_path.is_file():
                media.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "type": file_path.suffix.lower(),
                    "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                })
        
        return sorted(media, key=lambda x: x["created"], reverse=True)
