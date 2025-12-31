# ============================================================================
# Servicio de Generación de Imágenes - Stable Diffusion
# ============================================================================
# Archivo: backend/services/image_service.py
# ============================================================================

import torch
import logging
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import uuid
from PIL import Image

try:
    from diffusers import StableDiffusionXLPipeline, StableDiffusionPipeline
    from diffusers import DPMSolverMultistepScheduler
except ImportError:
    raise ImportError("Instala diffusers: pip install diffusers")

logger = logging.getLogger(__name__)

class ImageGenerationService:
    """Servicio para generar imágenes usando Stable Diffusion"""
    
    def __init__(
        self,
        model_name: str = "stabilityai/stable-diffusion-xl-base-1.0",
        device: str = "cuda",
        output_dir: str = "./data/generated_images"
    ):
        self.model_name = model_name
        self.device = device if torch.cuda.is_available() else "cpu"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.pipe = None
        self.is_xl = "xl" in model_name.lower()
        
        logger.info(f"ImageGenerationService inicializado con device: {self.device}")
        logger.info(f"Modelo: {model_name}")
    
    def check_gpu_available(self) -> dict:
        """Verificar disponibilidad de GPU"""
        return {
            "cuda_available": torch.cuda.is_available(),
            "device": self.device,
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
            "vram_gb": torch.cuda.get_device_properties(0).total_memory / 1e9 if torch.cuda.is_available() else 0
        }
    
    def _load_model(self):
        """Cargar modelo (lazy loading)"""
        if self.pipe is None:
            logger.info(f"Cargando modelo: {self.model_name}")
            
            try:
                if self.is_xl:
                    self.pipe = StableDiffusionXLPipeline.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                        use_safetensors=True,
                        variant="fp16" if self.device == "cuda" else None
                    )
                else:
                    self.pipe = StableDiffusionPipeline.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                        use_safetensors=True,
                        variant="fp16" if self.device == "cuda" else None
                    )
                
                # Optimizaciones para GPU de 6GB
                if self.device == "cuda":
                    # Usar scheduler más eficiente
                    self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                        self.pipe.scheduler.config
                    )
                    
                    # Memory optimizations
                    self.pipe.enable_attention_slicing()
                    self.pipe.enable_sequential_cpu_offload()
                
                self.pipe = self.pipe.to(self.device)
                logger.info("✅ Modelo cargado exitosamente")
            
            except Exception as e:
                logger.error(f"Error al cargar modelo: {e}")
                raise
    
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "blurry, low quality, distorted",
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        height: int = 768,
        width: int = 768,
        seed: Optional[int] = None
    ) -> str:
        """Generar imagen a partir de prompt"""
        try:
            # Cargar modelo si es necesario
            self._load_model()
            
            logger.info(f"Generando imagen: {prompt[:50]}...")
            
            # Configurar seed para reproducibilidad
            if seed is None:
                seed = int(datetime.now().timestamp())
            
            generator = torch.Generator(device=self.device).manual_seed(seed)
            
            # Generar imagen
            with torch.no_grad():
                result = self.pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    height=height,
                    width=width,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator
                )
            
            image = result.images[0]
            
            # Guardar imagen
            image_id = str(uuid.uuid4())
            image_path = self.output_dir / f"{image_id}.png"
            image.save(image_path)
            
            logger.info(f"✅ Imagen guardada: {image_path}")
            
            return str(image_path)
        
        except Exception as e:
            logger.error(f"Error al generar imagen: {e}")
            raise
    
    async def generate_batch(
        self,
        prompts: list,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        height: int = 768,
        width: int = 768
    ) -> list:
        """Generar múltiples imágenes"""
        results = []
        
        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"Generando imagen {i+1}/{len(prompts)}")
                image_path = await self.generate(
                    prompt=prompt,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    height=height,
                    width=width
                )
                results.append({
                    "prompt": prompt,
                    "image_path": image_path,
                    "success": True
                })
            except Exception as e:
                logger.error(f"Error generando imagen para prompt '{prompt}': {e}")
                results.append({
                    "prompt": prompt,
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    async def upscale_image(
        self,
        image_path: str,
        scale_factor: int = 2
    ) -> str:
        """Aumentar resolución de imagen (requiere modelo adicional)"""
        try:
            from diffusers import StableDiffusionUpscalePipeline
            
            image = Image.open(image_path)
            
            upscaler = StableDiffusionUpscalePipeline.from_pretrained(
                "stabilityai/stable-diffusion-x4-upscaler",
                torch_dtype=torch.float16,
                variant="fp16"
            )
            upscaler = upscaler.to(self.device)
            
            with torch.no_grad():
                upscaled = upscaler(
                    prompt="",
                    image=image,
                    num_inference_steps=20,
                    guidance_scale=0
                )
            
            upscaled_image = upscaled.images[0]
            
            # Guardar imagen upscaleada
            image_id = str(uuid.uuid4())
            output_path = self.output_dir / f"{image_id}_upscaled.png"
            upscaled_image.save(output_path)
            
            logger.info(f"✅ Imagen upscaleada: {output_path}")
            
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error al upscalear imagen: {e}")
            raise
    
    async def modify_image(
        self,
        image_path: str,
        prompt: str,
        strength: float = 0.8,
        num_inference_steps: int = 30
    ) -> str:
        """Modificar imagen existente (img2img)"""
        try:
            from diffusers import StableDiffusionImg2ImgPipeline
            
            self._load_model()
            
            image = Image.open(image_path).convert("RGB")
            
            img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            img2img_pipe = img2img_pipe.to(self.device)
            
            with torch.no_grad():
                result = img2img_pipe(
                    prompt=prompt,
                    image=image,
                    strength=strength,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=7.5
                )
            
            modified_image = result.images[0]
            
            # Guardar imagen modificada
            image_id = str(uuid.uuid4())
            output_path = self.output_dir / f"{image_id}_modified.png"
            modified_image.save(output_path)
            
            logger.info(f"✅ Imagen modificada: {output_path}")
            
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error al modificar imagen: {e}")
            raise
    
    def list_generated_images(self) -> list:
        """Listar todas las imágenes generadas"""
        images = []
        
        for image_file in self.output_dir.glob("*.png"):
            images.append({
                "filename": image_file.name,
                "path": str(image_file),
                "size": image_file.stat().st_size,
                "created": datetime.fromtimestamp(image_file.stat().st_ctime).isoformat()
            })
        
        return sorted(images, key=lambda x: x["created"], reverse=True)
    
    def delete_image(self, image_id: str) -> bool:
        """Eliminar imagen generada"""
        try:
            image_path = self.output_dir / f"{image_id}.png"
            if image_path.exists():
                image_path.unlink()
                logger.info(f"✅ Imagen eliminada: {image_id}")
                return True
            else:
                logger.warning(f"Imagen no encontrada: {image_id}")
                return False
        except Exception as e:
            logger.error(f"Error al eliminar imagen: {e}")
            return False
    
    def unload_model(self):
        """Descargar modelo de memoria"""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            logger.info("✅ Modelo descargado de memoria")
