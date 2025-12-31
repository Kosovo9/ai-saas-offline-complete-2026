# ============================================================================
# Servicio de Ollama - Integración con LLMs Locales
# ============================================================================
# Archivo: backend/services/ollama_service.py
# ============================================================================

import asyncio
import httpx
import json
from typing import Optional, List, AsyncGenerator, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OllamaService:
    """Servicio para interactuar con Ollama y modelos LLM locales"""
    
    def __init__(self, host: str = "http://localhost:11434", default_model: str = "deepseek-r1:7b"):
        self.host = host
        self.default_model = default_model
        self.client = httpx.AsyncClient(timeout=None)
        self.conversation_history = {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar si Ollama está disponible"""
        try:
            response = await self.client.get(f"{self.host}/api/tags")
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "models_count": len(response.json().get("models", []))
                }
            else:
                return {"status": "unhealthy", "error": "API no responde"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Listar todos los modelos disponibles"""
        try:
            response = await self.client.get(f"{self.host}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [
                    {
                        "name": model.get("name"),
                        "size": model.get("size"),
                        "digest": model.get("digest"),
                        "modified_at": model.get("modified_at")
                    }
                    for model in models
                ]
            else:
                logger.error(f"Error al listar modelos: {response.text}")
                return []
        except Exception as e:
            logger.error(f"Excepción al listar modelos: {e}")
            return []
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40
    ) -> str:
        """Generar respuesta completa del modelo"""
        model = model or self.default_model
        
        try:
            # Construir mensajes
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            if context:
                messages.extend(context)
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Hacer request a Ollama
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.host}/api/chat",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                logger.error(f"Error de Ollama: {response.text}")
                raise Exception(f"Ollama error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Excepción en generate: {e}")
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Generar respuesta con streaming (token por token)"""
        model = model or self.default_model
        
        try:
            # Construir mensajes
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            if context:
                messages.extend(context)
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Hacer request con streaming
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": True
            }
            
            async with self.client.stream(
                "POST",
                f"{self.host}/api/chat",
                json=payload
            ) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                content = data.get("message", {}).get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
                else:
                    logger.error(f"Error de Ollama: {response.text}")
                    raise Exception(f"Ollama error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Excepción en generate_stream: {e}")
            raise
    
    async def pull_model(self, model_name: str) -> bool:
        """Descargar un modelo (si no está disponible)"""
        try:
            logger.info(f"Descargando modelo: {model_name}")
            
            payload = {"name": model_name}
            
            async with self.client.stream(
                "POST",
                f"{self.host}/api/pull",
                json=payload
            ) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line:
                            data = json.loads(line)
                            status = data.get("status", "")
                            logger.info(f"  {status}")
                    
                    logger.info(f"✅ Modelo {model_name} descargado")
                    return True
                else:
                    logger.error(f"Error al descargar modelo: {response.text}")
                    return False
        
        except Exception as e:
            logger.error(f"Excepción en pull_model: {e}")
            return False
    
    async def delete_model(self, model_name: str) -> bool:
        """Eliminar un modelo"""
        try:
            payload = {"name": model_name}
            response = await self.client.delete(
                f"{self.host}/api/delete",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Modelo {model_name} eliminado")
                return True
            else:
                logger.error(f"Error al eliminar modelo: {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Excepción en delete_model: {e}")
            return False
    
    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un modelo específico"""
        try:
            payload = {"name": model_name}
            response = await self.client.post(
                f"{self.host}/api/show",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error al obtener info del modelo: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Excepción en get_model_info: {e}")
            return None
    
    async def generate_embedding(self, text: str, model: str = "nomic-embed-text") -> Optional[List[float]]:
        """Generar embedding de texto (útil para búsqueda semántica)"""
        try:
            payload = {
                "model": model,
                "prompt": text
            }
            
            response = await self.client.post(
                f"{self.host}/api/embeddings",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("embedding")
            else:
                logger.error(f"Error al generar embedding: {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Excepción en generate_embedding: {e}")
            return None
    
    def save_conversation(self, conversation_id: str, messages: List[Dict[str, str]]):
        """Guardar conversación en memoria"""
        self.conversation_history[conversation_id] = {
            "messages": messages,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def get_conversation(self, conversation_id: str) -> Optional[List[Dict[str, str]]]:
        """Recuperar conversación guardada"""
        if conversation_id in self.conversation_history:
            return self.conversation_history[conversation_id]["messages"]
        return None
    
    def clear_conversation(self, conversation_id: str):
        """Limpiar conversación"""
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]
    
    async def close(self):
        """Cerrar cliente HTTP"""
        await self.client.aclose()
    
    def __del__(self):
        """Cleanup al destruir objeto"""
        try:
            asyncio.run(self.close())
        except:
            pass
