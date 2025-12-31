# ============================================================================
# Servicio de Audio - Speech-to-Text y Text-to-Speech
# ============================================================================
# Archivo: backend/services/audio_service.py
# ============================================================================

import subprocess
import logging
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import uuid
import json

logger = logging.getLogger(__name__)

class AudioService:
    """Servicio para transcripción de audio y síntesis de voz"""
    
    def __init__(
        self,
        whisper_model: str = "medium",
        piper_voice: str = "es_ES-sharvard-medium",
        piper_path: str = "C:\\AI-SaaS\\tools\\piper",
        output_dir: str = "./data/audio"
    ):
        self.whisper_model = whisper_model
        self.piper_voice = piper_voice
        self.piper_path = Path(piper_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.whisper_available = self._check_whisper()
        self.piper_available = self._check_piper()
        
        logger.info(f"AudioService inicializado")
        logger.info(f"  Whisper: {'✅' if self.whisper_available else '❌'}")
        logger.info(f"  Piper: {'✅' if self.piper_available else '❌'}")
    
    def _check_whisper(self) -> bool:
        """Verificar si Whisper está disponible"""
        try:
            result = subprocess.run(
                ["whisper", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Whisper no disponible: {e}")
            return False
    
    def _check_piper(self) -> bool:
        """Verificar si Piper está disponible"""
        try:
            piper_exe = self.piper_path / "piper.exe"
            return piper_exe.exists()
        except Exception as e:
            logger.warning(f"Piper no disponible: {e}")
            return False
    
    def check_available(self) -> dict:
        """Verificar disponibilidad de servicios de audio"""
        return {
            "whisper": self.whisper_available,
            "piper": self.piper_available,
            "whisper_model": self.whisper_model if self.whisper_available else None,
            "piper_voice": self.piper_voice if self.piper_available else None
        }
    
    async def speech_to_text(
        self,
        audio_path: str,
        language: str = "es",
        task: str = "transcribe"
    ) -> str:
        """Convertir audio a texto usando Whisper"""
        
        if not self.whisper_available:
            raise RuntimeError("Whisper no está disponible. Instala con: pip install openai-whisper")
        
        try:
            logger.info(f"Transcribiendo audio: {audio_path}")
            
            # Comando de Whisper
            cmd = [
                "whisper",
                audio_path,
                "--model", self.whisper_model,
                "--language", language,
                "--task", task,
                "--output_format", "json",
                "--output_dir", str(self.output_dir)
            ]
            
            # Ejecutar Whisper
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos máximo
            )
            
            if result.returncode == 0:
                # Leer resultado JSON
                base_name = Path(audio_path).stem
                json_path = self.output_dir / f"{base_name}.json"
                
                if json_path.exists():
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        text = data.get("text", "")
                    
                    logger.info(f"✅ Transcripción completada: {len(text)} caracteres")
                    return text
                else:
                    raise Exception("No se generó archivo JSON de salida")
            else:
                logger.error(f"Error en Whisper: {result.stderr}")
                raise Exception(f"Whisper error: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error("Timeout en transcripción de audio")
            raise Exception("Transcripción cancelada por timeout")
        except Exception as e:
            logger.error(f"Error en speech_to_text: {e}")
            raise
    
    async def text_to_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0
    ) -> str:
        """Convertir texto a audio usando Piper"""
        
        if not self.piper_available:
            raise RuntimeError("Piper no está disponible. Descárgalo desde: https://github.com/rhasspy/piper/releases")
        
        try:
            voice = voice or self.piper_voice
            logger.info(f"Sintetizando voz: {text[:50]}...")
            
            # Generar ID único para el archivo
            audio_id = str(uuid.uuid4())
            output_path = self.output_dir / f"{audio_id}.wav"
            
            # Ruta del modelo de voz
            model_path = self.piper_path / "models" / f"{voice}.onnx"
            
            if not model_path.exists():
                logger.error(f"Modelo de voz no encontrado: {model_path}")
                raise Exception(f"Modelo de voz no disponible: {voice}")
            
            # Comando de Piper
            piper_exe = self.piper_path / "piper.exe"
            
            cmd = [
                str(piper_exe),
                "--model", str(model_path),
                "--output_file", str(output_path),
                "--speed", str(speed)
            ]
            
            # Ejecutar Piper
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=text, timeout=60)
            
            if process.returncode == 0:
                if output_path.exists():
                    logger.info(f"✅ Audio sintetizado: {output_path}")
                    return str(output_path)
                else:
                    raise Exception("No se generó archivo de audio")
            else:
                logger.error(f"Error en Piper: {stderr}")
                raise Exception(f"Piper error: {stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error("Timeout en síntesis de voz")
            raise Exception("Síntesis de voz cancelada por timeout")
        except Exception as e:
            logger.error(f"Error en text_to_speech: {e}")
            raise
    
    async def batch_text_to_speech(
        self,
        texts: list,
        voice: Optional[str] = None
    ) -> list:
        """Convertir múltiples textos a audio"""
        results = []
        
        for i, text in enumerate(texts):
            try:
                logger.info(f"Sintetizando {i+1}/{len(texts)}")
                audio_path = await self.text_to_speech(text, voice)
                results.append({
                    "text": text,
                    "audio_path": audio_path,
                    "success": True
                })
            except Exception as e:
                logger.error(f"Error sintetizando texto {i+1}: {e}")
                results.append({
                    "text": text,
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    async def transcribe_with_timestamps(
        self,
        audio_path: str,
        language: str = "es"
    ) -> dict:
        """Transcribir con timestamps de cada palabra"""
        
        if not self.whisper_available:
            raise RuntimeError("Whisper no está disponible")
        
        try:
            logger.info(f"Transcribiendo con timestamps: {audio_path}")
            
            cmd = [
                "whisper",
                audio_path,
                "--model", self.whisper_model,
                "--language", language,
                "--output_format", "json",
                "--output_dir", str(self.output_dir),
                "--verbose", "False"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                base_name = Path(audio_path).stem
                json_path = self.output_dir / f"{base_name}.json"
                
                if json_path.exists():
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    logger.info(f"✅ Transcripción con timestamps completada")
                    return data
                else:
                    raise Exception("No se generó archivo JSON")
            else:
                raise Exception(f"Whisper error: {result.stderr}")
        
        except Exception as e:
            logger.error(f"Error en transcribe_with_timestamps: {e}")
            raise
    
    def list_generated_audio(self) -> list:
        """Listar todos los audios generados"""
        audios = []
        
        for audio_file in self.output_dir.glob("*.wav"):
            audios.append({
                "filename": audio_file.name,
                "path": str(audio_file),
                "size": audio_file.stat().st_size,
                "created": datetime.fromtimestamp(audio_file.stat().st_ctime).isoformat()
            })
        
        return sorted(audios, key=lambda x: x["created"], reverse=True)
    
    def delete_audio(self, audio_id: str) -> bool:
        """Eliminar archivo de audio"""
        try:
            audio_path = self.output_dir / f"{audio_id}.wav"
            if audio_path.exists():
                audio_path.unlink()
                logger.info(f"✅ Audio eliminado: {audio_id}")
                return True
            else:
                logger.warning(f"Audio no encontrado: {audio_id}")
                return False
        except Exception as e:
            logger.error(f"Error al eliminar audio: {e}")
            return False
    
    async def get_available_voices(self) -> list:
        """Listar voces disponibles de Piper"""
        voices = []
        
        try:
            models_dir = self.piper_path / "models"
            
            if models_dir.exists():
                for model_file in models_dir.glob("*.onnx"):
                    voice_name = model_file.stem
                    voices.append({
                        "name": voice_name,
                        "path": str(model_file),
                        "size": model_file.stat().st_size
                    })
            
            logger.info(f"Voces disponibles: {len(voices)}")
            return voices
        
        except Exception as e:
            logger.error(f"Error listando voces: {e}")
            return []
    
    async def download_voice(self, voice_name: str) -> bool:
        """Descargar modelo de voz (requiere conexión a internet)"""
        try:
            logger.info(f"Descargando voz: {voice_name}")
            
            # URL base de Hugging Face
            base_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
            
            # Construir URL
            url = f"{base_url}/{voice_name}.onnx"
            
            # Descargar
            import requests
            response = requests.get(url, stream=True, timeout=300)
            
            if response.status_code == 200:
                models_dir = self.piper_path / "models"
                models_dir.mkdir(parents=True, exist_ok=True)
                
                output_path = models_dir / f"{voice_name}.onnx"
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                logger.info(f"✅ Voz descargada: {voice_name}")
                return True
            else:
                logger.error(f"Error descargando voz: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Error en download_voice: {e}")
            return False
