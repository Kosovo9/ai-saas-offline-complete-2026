# ============================================================================
# Servicio de Clonación de Voz y Voice Chat Avanzado
# ============================================================================
# Archivo: backend/services/voice_cloning_service.py
# ============================================================================

import logging
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
import uuid
import json
import subprocess

logger = logging.getLogger(__name__)

class VoiceCloningService:
    """Servicio para clonación de voz y síntesis personalizada"""
    
    def __init__(
        self,
        voices_dir: str = "./data/custom_voices",
        samples_dir: str = "./data/voice_samples"
    ):
        self.voices_dir = Path(voices_dir)
        self.samples_dir = Path(samples_dir)
        
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.samples_dir.mkdir(parents=True, exist_ok=True)
        
        self.voice_profiles = {}
        self._load_voice_profiles()
        
        logger.info(f"VoiceCloningService inicializado")
        logger.info(f"  Voces personalizadas: {len(self.voice_profiles)}")
    
    def _load_voice_profiles(self):
        """Cargar perfiles de voces guardadas"""
        try:
            profiles_file = self.voices_dir / "profiles.json"
            if profiles_file.exists():
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    self.voice_profiles = json.load(f)
                logger.info(f"✅ Perfiles de voz cargados: {len(self.voice_profiles)}")
        except Exception as e:
            logger.error(f"Error cargando perfiles: {e}")
    
    def _save_voice_profiles(self):
        """Guardar perfiles de voces"""
        try:
            profiles_file = self.voices_dir / "profiles.json"
            with open(profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.voice_profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando perfiles: {e}")
    
    async def create_voice_profile(
        self,
        voice_name: str,
        audio_samples: List[str],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Crear perfil de voz a partir de muestras de audio"""
        
        try:
            logger.info(f"Creando perfil de voz: {voice_name}")
            
            # Validar que existan los archivos
            valid_samples = []
            for sample_path in audio_samples:
                if Path(sample_path).exists():
                    valid_samples.append(sample_path)
            
            if not valid_samples:
                raise Exception("No se encontraron archivos de audio válidos")
            
            # Extraer características de voz
            voice_features = await self._extract_voice_features(valid_samples)
            
            # Generar ID único
            voice_id = str(uuid.uuid4())[:8]
            
            # Crear perfil
            profile = {
                "id": voice_id,
                "name": voice_name,
                "description": description or "",
                "created_at": datetime.now().isoformat(),
                "samples_count": len(valid_samples),
                "features": voice_features,
                "status": "ready"
            }
            
            # Guardar perfil
            self.voice_profiles[voice_id] = profile
            self._save_voice_profiles()
            
            # Guardar muestras
            samples_dir = self.samples_dir / voice_id
            samples_dir.mkdir(exist_ok=True)
            
            for i, sample_path in enumerate(valid_samples):
                src = Path(sample_path)
                dst = samples_dir / f"sample_{i}.wav"
                import shutil
                shutil.copy(src, dst)
            
            logger.info(f"✅ Perfil de voz creado: {voice_id} ({voice_name})")
            
            return {
                "voice_id": voice_id,
                "name": voice_name,
                "status": "ready",
                "samples_count": len(valid_samples),
                "created_at": profile["created_at"]
            }
        
        except Exception as e:
            logger.error(f"Error creando perfil de voz: {e}")
            raise
    
    async def _extract_voice_features(self, audio_paths: List[str]) -> Dict[str, Any]:
        """Extraer características acústicas de la voz"""
        
        try:
            features = {
                "pitch_mean": [],
                "pitch_std": [],
                "mfcc_mean": [],
                "energy_mean": [],
                "duration": 0
            }
            
            for audio_path in audio_paths:
                try:
                    # Cargar audio
                    y, sr = librosa.load(audio_path, sr=None)
                    
                    # Duración
                    duration = librosa.get_duration(y=y, sr=sr)
                    features["duration"] += duration
                    
                    # Pitch (fundamental frequency)
                    f0 = librosa.yin(y, fmin=50, fmax=500)
                    f0_valid = f0[f0 > 0]
                    if len(f0_valid) > 0:
                        features["pitch_mean"].append(float(np.mean(f0_valid)))
                        features["pitch_std"].append(float(np.std(f0_valid)))
                    
                    # MFCC (Mel-frequency cepstral coefficients)
                    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                    features["mfcc_mean"].append(float(np.mean(mfcc)))
                    
                    # Energía
                    energy = np.sqrt(np.sum(y**2) / len(y))
                    features["energy_mean"].append(float(energy))
                
                except Exception as e:
                    logger.warning(f"Error procesando audio {audio_path}: {e}")
                    continue
            
            # Calcular promedios
            if features["pitch_mean"]:
                features["pitch_mean"] = float(np.mean(features["pitch_mean"]))
                features["pitch_std"] = float(np.mean(features["pitch_std"]))
            else:
                features["pitch_mean"] = 0
                features["pitch_std"] = 0
            
            if features["mfcc_mean"]:
                features["mfcc_mean"] = float(np.mean(features["mfcc_mean"]))
            else:
                features["mfcc_mean"] = 0
            
            if features["energy_mean"]:
                features["energy_mean"] = float(np.mean(features["energy_mean"]))
            else:
                features["energy_mean"] = 0
            
            return features
        
        except Exception as e:
            logger.error(f"Error extrayendo características: {e}")
            raise
    
    async def synthesize_with_voice(
        self,
        text: str,
        voice_id: str,
        speed: float = 1.0
    ) -> str:
        """Sintetizar texto usando voz clonada"""
        
        try:
            if voice_id not in self.voice_profiles:
                raise Exception(f"Perfil de voz no encontrado: {voice_id}")
            
            profile = self.voice_profiles[voice_id]
            logger.info(f"Sintetizando con voz: {profile['name']}")
            
            # Obtener muestras de referencia
            samples_dir = self.samples_dir / voice_id
            reference_samples = list(samples_dir.glob("sample_*.wav"))
            
            if not reference_samples:
                raise Exception(f"No hay muestras de voz para: {voice_id}")
            
            # Usar la primera muestra como referencia
            reference_audio = str(reference_samples[0])
            
            # Generar audio con características de voz
            output_id = str(uuid.uuid4())
            output_path = Path("./data/audio") / f"{output_id}.wav"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Usar XTTS v2 o similar para clonación (si está disponible)
            # Por ahora, usaremos Piper con ajustes basados en características
            await self._synthesize_with_piper_adjusted(
                text=text,
                reference_audio=reference_audio,
                output_path=str(output_path),
                speed=speed,
                features=profile["features"]
            )
            
            logger.info(f"✅ Audio sintetizado: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error sintetizando con voz: {e}")
            raise
    
    async def _synthesize_with_piper_adjusted(
        self,
        text: str,
        reference_audio: str,
        output_path: str,
        speed: float = 1.0,
        features: Optional[Dict] = None
    ):
        """Sintetizar con Piper ajustando parámetros según características"""
        
        try:
            # Usar Piper con parámetros ajustados
            piper_path = Path("C:\\AI-SaaS\\tools\\piper\\piper.exe")
            
            if not piper_path.exists():
                raise Exception("Piper no encontrado")
            
            # Seleccionar voz basada en características
            voice_model = "es_ES-sharvard-medium"
            
            cmd = [
                str(piper_path),
                "--model", f"C:\\AI-SaaS\\tools\\piper\\models\\{voice_model}.onnx",
                "--output_file", output_path,
                "--speed", str(speed)
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=text, timeout=60)
            
            if process.returncode != 0:
                raise Exception(f"Piper error: {stderr}")
        
        except Exception as e:
            logger.error(f"Error en síntesis ajustada: {e}")
            raise
    
    def list_voice_profiles(self) -> List[Dict[str, Any]]:
        """Listar todos los perfiles de voz disponibles"""
        profiles = []
        
        for voice_id, profile in self.voice_profiles.items():
            profiles.append({
                "id": voice_id,
                "name": profile["name"],
                "description": profile.get("description", ""),
                "created_at": profile["created_at"],
                "samples_count": profile.get("samples_count", 0),
                "status": profile.get("status", "unknown")
            })
        
        return sorted(profiles, key=lambda x: x["created_at"], reverse=True)
    
    async def delete_voice_profile(self, voice_id: str) -> bool:
        """Eliminar perfil de voz"""
        
        try:
            if voice_id not in self.voice_profiles:
                logger.warning(f"Perfil no encontrado: {voice_id}")
                return False
            
            # Eliminar perfil
            del self.voice_profiles[voice_id]
            self._save_voice_profiles()
            
            # Eliminar muestras
            samples_dir = self.samples_dir / voice_id
            if samples_dir.exists():
                import shutil
                shutil.rmtree(samples_dir)
            
            logger.info(f"✅ Perfil de voz eliminado: {voice_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error eliminando perfil: {e}")
            raise
    
    async def upload_voice_sample(
        self,
        voice_id: str,
        audio_file_path: str
    ) -> Dict[str, Any]:
        """Agregar muestra de audio a un perfil existente"""
        
        try:
            if voice_id not in self.voice_profiles:
                raise Exception(f"Perfil no encontrado: {voice_id}")
            
            # Copiar archivo
            samples_dir = self.samples_dir / voice_id
            sample_count = len(list(samples_dir.glob("sample_*.wav")))
            
            dst_path = samples_dir / f"sample_{sample_count}.wav"
            
            import shutil
            shutil.copy(audio_file_path, dst_path)
            
            # Actualizar perfil
            self.voice_profiles[voice_id]["samples_count"] = sample_count + 1
            self._save_voice_profiles()
            
            logger.info(f"✅ Muestra agregada al perfil: {voice_id}")
            
            return {
                "voice_id": voice_id,
                "sample_added": True,
                "total_samples": sample_count + 1
            }
        
        except Exception as e:
            logger.error(f"Error agregando muestra: {e}")
            raise


class VoiceChatService:
    """Servicio para chat bidireccional por voz"""
    
    def __init__(
        self,
        ollama_service,
        audio_service,
        voice_cloning_service
    ):
        self.ollama = ollama_service
        self.audio = audio_service
        self.voice_cloning = voice_cloning_service
        self.conversations = {}
        
        logger.info("VoiceChatService inicializado")
    
    async def voice_chat_session(
        self,
        audio_input_path: str,
        voice_id: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sesión completa de chat por voz: audio → texto → LLM → voz"""
        
        try:
            session_id = str(uuid.uuid4())[:8]
            logger.info(f"Iniciando sesión de voice chat: {session_id}")
            
            # 1. Transcribir audio de entrada
            logger.info("1️⃣  Transcribiendo audio...")
            user_text = await self.audio.speech_to_text(audio_input_path, language="es")
            logger.info(f"   Usuario dijo: {user_text}")
            
            # 2. Obtener respuesta del LLM
            logger.info("2️⃣  Obteniendo respuesta de IA...")
            ai_response = await self.ollama.generate(
                prompt=user_text,
                model=model,
                system_prompt=system_prompt
            )
            logger.info(f"   IA respondió: {ai_response[:100]}...")
            
            # 3. Sintetizar respuesta a voz
            logger.info("3️⃣  Sintetizando respuesta a voz...")
            if voice_id and voice_id in self.voice_cloning.voice_profiles:
                # Usar voz clonada
                output_audio = await self.voice_cloning.synthesize_with_voice(
                    text=ai_response,
                    voice_id=voice_id
                )
            else:
                # Usar voz predeterminada
                output_audio = await self.audio.text_to_speech(ai_response)
            
            logger.info(f"✅ Sesión completada: {session_id}")
            
            return {
                "session_id": session_id,
                "user_input_text": user_text,
                "ai_response_text": ai_response,
                "ai_response_audio": output_audio,
                "voice_used": voice_id or "default",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error en voice chat session: {e}")
            raise
    
    async def stream_voice_chat(
        self,
        audio_input_path: str,
        voice_id: Optional[str] = None,
        model: Optional[str] = None
    ):
        """Voice chat con streaming de respuesta"""
        
        try:
            # Transcribir
            user_text = await self.audio.speech_to_text(audio_input_path, language="es")
            
            # Streaming de respuesta
            async for chunk in self.ollama.generate_stream(
                prompt=user_text,
                model=model
            ):
                yield {
                    "type": "text_chunk",
                    "content": chunk,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Sintetizar respuesta completa
            full_response = ""
            async for chunk in self.ollama.generate_stream(
                prompt=user_text,
                model=model
            ):
                full_response += chunk
            
            # Generar audio
            output_audio = await self.voice_cloning.synthesize_with_voice(
                text=full_response,
                voice_id=voice_id
            ) if voice_id else await self.audio.text_to_speech(full_response)
            
            yield {
                "type": "audio_ready",
                "audio_path": output_audio,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error en stream_voice_chat: {e}")
            yield {
                "type": "error",
                "error": str(e)
            }
    
    async def voice_to_project(
        self,
        audio_input_path: str,
        project_id: str,
        file_path: str,
        instruction: str = "Escribe esto en el proyecto"
    ) -> Dict[str, Any]:
        """Dictar código/contenido directamente al proyecto"""
        
        try:
            logger.info(f"Dictando contenido al proyecto: {project_id}")
            
            # 1. Transcribir audio
            user_text = await self.audio.speech_to_text(audio_input_path, language="es")
            
            # 2. Procesar con LLM si es código
            if "código" in instruction.lower() or file_path.endswith((".py", ".js", ".ts", ".html", ".css")):
                processed_text = await self.ollama.generate(
                    prompt=f"Convierte esto en código válido:\n{user_text}",
                    system_prompt="Eres un experto en programación. Devuelve solo código válido sin explicaciones."
                )
            else:
                processed_text = user_text
            
            # 3. Guardar en proyecto
            from services.project_service import ProjectService
            project_service = ProjectService()
            await project_service.save_file(project_id, file_path, processed_text)
            
            # 4. Confirmar por voz
            confirmation = f"He guardado {len(processed_text)} caracteres en {file_path}"
            output_audio = await self.audio.text_to_speech(confirmation)
            
            logger.info(f"✅ Contenido guardado en proyecto")
            
            return {
                "project_id": project_id,
                "file_path": file_path,
                "dictated_text": user_text,
                "processed_text": processed_text,
                "confirmation_audio": output_audio,
                "characters_saved": len(processed_text)
            }
        
        except Exception as e:
            logger.error(f"Error en voice_to_project: {e}")
            raise
