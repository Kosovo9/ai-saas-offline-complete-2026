# ============================================================================
# Motor de Sincronización Automática - Offline-First con Sync Online
# ============================================================================
# Archivo: backend/services/sync_engine_service.py
# Sincroniza automáticamente cuando hay conexión a internet
# ============================================================================

import logging
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
from collections import defaultdict
import aiohttp

logger = logging.getLogger(__name__)

class SyncStatus(str, Enum):
    """Estados de sincronización"""
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"
    FAILED = "failed"

class ChangeType(str, Enum):
    """Tipos de cambios"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

class SyncEngineService:
    """Motor de sincronización offline-first con auto-sync online"""
    
    def __init__(
        self,
        local_db_dir: str = "./data/local_db",
        sync_dir: str = "./data/sync_queue",
        cloud_endpoint: str = "https://api.ai-saas.cloud"
    ):
        self.local_db_dir = Path(local_db_dir)
        self.sync_dir = Path(sync_dir)
        self.cloud_endpoint = cloud_endpoint
        
        self.local_db_dir.mkdir(parents=True, exist_ok=True)
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        
        # Cola de cambios pendientes
        self.sync_queue = defaultdict(list)
        
        # Historial de sincronización
        self.sync_history = []
        
        # Conflictos detectados
        self.conflicts = []
        
        # Estado de conexión
        self.is_online = False
        self.last_sync = None
        
        # Cargar cola pendiente
        self._load_sync_queue()
        
        # Iniciar monitor de conexión
        asyncio.create_task(self._monitor_connection())
        
        logger.info("SyncEngineService inicializado (Offline-First)")
    
    # ========================================================================
    # OPERACIONES LOCALES (OFFLINE)
    # ========================================================================
    
    async def save_local(
        self,
        entity_type: str,
        entity_id: str,
        data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Guardar datos localmente (funciona offline)"""
        
        try:
            # Generar cambio
            change = {
                "id": str(uuid.uuid4())[:8],
                "entity_type": entity_type,
                "entity_id": entity_id,
                "change_type": ChangeType.CREATE.value if not self._entity_exists_local(entity_type, entity_id) else ChangeType.UPDATE.value,
                "data": data,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "status": SyncStatus.PENDING.value,
                "hash": self._calculate_hash(data),
                "synced": False
            }
            
            # Guardar localmente
            local_path = self.local_db_dir / entity_type / f"{entity_id}.json"
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(local_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Agregar a cola de sincronización
            self.sync_queue[entity_type].append(change)
            self._save_sync_queue()
            
            logger.info(f"✅ Datos guardados localmente: {entity_type}/{entity_id}")
            
            # Si está online, sincronizar inmediatamente
            if self.is_online:
                asyncio.create_task(self._sync_change(change))
            
            return {
                "success": True,
                "entity_id": entity_id,
                "status": "saved_locally",
                "will_sync": self.is_online,
                "change_id": change["id"]
            }
        
        except Exception as e:
            logger.error(f"Error guardando localmente: {e}")
            raise
    
    async def load_local(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """Cargar datos localmente (funciona offline)"""
        
        try:
            local_path = self.local_db_dir / entity_type / f"{entity_id}.json"
            
            if not local_path.exists():
                return None
            
            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
        
        except Exception as e:
            logger.error(f"Error cargando localmente: {e}")
            return None
    
    async def list_local(self, entity_type: str) -> List[Dict[str, Any]]:
        """Listar todos los datos locales de un tipo"""
        
        try:
            entity_dir = self.local_db_dir / entity_type
            
            if not entity_dir.exists():
                return []
            
            items = []
            for file_path in entity_dir.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    items.append({
                        "id": file_path.stem,
                        "data": data
                    })
            
            return items
        
        except Exception as e:
            logger.error(f"Error listando localmente: {e}")
            return []
    
    async def delete_local(
        self,
        entity_type: str,
        entity_id: str,
        user_id: str
    ) -> bool:
        """Eliminar datos localmente"""
        
        try:
            local_path = self.local_db_dir / entity_type / f"{entity_id}.json"
            
            if not local_path.exists():
                return False
            
            # Crear cambio de eliminación
            change = {
                "id": str(uuid.uuid4())[:8],
                "entity_type": entity_type,
                "entity_id": entity_id,
                "change_type": ChangeType.DELETE.value,
                "data": None,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "status": SyncStatus.PENDING.value,
                "synced": False
            }
            
            # Eliminar localmente
            local_path.unlink()
            
            # Agregar a cola de sincronización
            self.sync_queue[entity_type].append(change)
            self._save_sync_queue()
            
            logger.info(f"✅ Datos eliminados localmente: {entity_type}/{entity_id}")
            
            # Si está online, sincronizar
            if self.is_online:
                asyncio.create_task(self._sync_change(change))
            
            return True
        
        except Exception as e:
            logger.error(f"Error eliminando localmente: {e}")
            return False
    
    # ========================================================================
    # SINCRONIZACIÓN (ONLINE)
    # ========================================================================
    
    async def _monitor_connection(self):
        """Monitorear conexión a internet continuamente"""
        
        while True:
            try:
                # Intentar conectar con servidor
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(
                            f"{self.cloud_endpoint}/health",
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as resp:
                            was_offline = not self.is_online
                            self.is_online = resp.status == 200
                            
                            if was_offline and self.is_online:
                                logger.info("🌐 Conexión restaurada - Iniciando sincronización")
                                await self._sync_all()
                            elif not self.is_online:
                                logger.warning("📡 Sin conexión - Trabajando offline")
                    
                    except Exception:
                        self.is_online = False
                
                # Verificar cada 30 segundos
                await asyncio.sleep(30)
            
            except Exception as e:
                logger.error(f"Error monitoreando conexión: {e}")
                await asyncio.sleep(30)
    
    async def _sync_all(self):
        """Sincronizar todos los cambios pendientes"""
        
        try:
            logger.info("🔄 Iniciando sincronización completa")
            
            total_changes = sum(len(changes) for changes in self.sync_queue.values())
            synced_count = 0
            failed_count = 0
            
            for entity_type, changes in self.sync_queue.items():
                for change in changes[:]:  # Copiar lista para iterar
                    try:
                        success = await self._sync_change(change)
                        
                        if success:
                            synced_count += 1
                            changes.remove(change)
                        else:
                            failed_count += 1
                    
                    except Exception as e:
                        logger.error(f"Error sincronizando cambio: {e}")
                        failed_count += 1
            
            # Guardar cola actualizada
            self._save_sync_queue()
            
            self.last_sync = datetime.now()
            
            logger.info(f"✅ Sincronización completada: {synced_count} sincronizados, {failed_count} fallidos")
            
            return {
                "total": total_changes,
                "synced": synced_count,
                "failed": failed_count,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error en sincronización completa: {e}")
            raise
    
    async def _sync_change(self, change: Dict[str, Any]) -> bool:
        """Sincronizar un cambio individual"""
        
        try:
            change["status"] = SyncStatus.SYNCING.value
            
            async with aiohttp.ClientSession() as session:
                # Determinar endpoint según tipo de cambio
                if change["change_type"] == ChangeType.CREATE.value:
                    method = "POST"
                    url = f"{self.cloud_endpoint}/api/{change['entity_type']}"
                elif change["change_type"] == ChangeType.UPDATE.value:
                    method = "PUT"
                    url = f"{self.cloud_endpoint}/api/{change['entity_type']}/{change['entity_id']}"
                elif change["change_type"] == ChangeType.DELETE.value:
                    method = "DELETE"
                    url = f"{self.cloud_endpoint}/api/{change['entity_type']}/{change['entity_id']}"
                
                # Enviar cambio
                async with session.request(
                    method,
                    url,
                    json={
                        "data": change["data"],
                        "user_id": change["user_id"],
                        "timestamp": change["timestamp"],
                        "hash": change["hash"]
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status in [200, 201, 204]:
                        change["status"] = SyncStatus.SYNCED.value
                        change["synced"] = True
                        change["synced_at"] = datetime.now().isoformat()
                        
                        logger.info(f"✅ Cambio sincronizado: {change['id']}")
                        return True
                    
                    elif resp.status == 409:
                        # Conflicto detectado
                        await self._handle_conflict(change, await resp.json())
                        return False
                    
                    else:
                        change["status"] = SyncStatus.FAILED.value
                        logger.error(f"Error sincronizando: {resp.status}")
                        return False
        
        except Exception as e:
            logger.error(f"Error en sync_change: {e}")
            change["status"] = SyncStatus.FAILED.value
            return False
    
    # ========================================================================
    # RESOLUCIÓN DE CONFLICTOS
    # ========================================================================
    
    async def _handle_conflict(
        self,
        local_change: Dict[str, Any],
        remote_data: Dict[str, Any]
    ):
        """Manejar conflictos de sincronización"""
        
        try:
            logger.warning(f"⚠️  Conflicto detectado: {local_change['entity_id']}")
            
            conflict = {
                "id": str(uuid.uuid4())[:8],
                "entity_type": local_change["entity_type"],
                "entity_id": local_change["entity_id"],
                "local_change": local_change,
                "remote_data": remote_data,
                "detected_at": datetime.now().isoformat(),
                "resolution": None
            }
            
            self.conflicts.append(conflict)
            
            # Estrategia de resolución automática
            resolution = await self._resolve_conflict_auto(conflict)
            
            if resolution:
                conflict["resolution"] = resolution
                logger.info(f"✅ Conflicto resuelto automáticamente: {resolution}")
            else:
                logger.warning(f"⚠️  Conflicto requiere resolución manual: {conflict['id']}")
        
        except Exception as e:
            logger.error(f"Error manejando conflicto: {e}")
    
    async def _resolve_conflict_auto(self, conflict: Dict[str, Any]) -> Optional[str]:
        """Resolver conflicto automáticamente"""
        
        try:
            local_time = datetime.fromisoformat(conflict["local_change"]["timestamp"])
            remote_time = datetime.fromisoformat(conflict["remote_data"].get("updated_at", ""))
            
            # Estrategia: Last-Write-Wins (LWW)
            if local_time > remote_time:
                # Local es más reciente, usar local
                return "local_wins"
            else:
                # Remote es más reciente, usar remote
                return "remote_wins"
        
        except Exception as e:
            logger.error(f"Error resolviendo conflicto: {e}")
            return None
    
    async def resolve_conflict_manual(
        self,
        conflict_id: str,
        resolution: str  # "local_wins" o "remote_wins"
    ) -> bool:
        """Resolver conflicto manualmente"""
        
        try:
            conflict = next((c for c in self.conflicts if c["id"] == conflict_id), None)
            
            if not conflict:
                return False
            
            conflict["resolution"] = resolution
            conflict["resolved_at"] = datetime.now().isoformat()
            
            # Si local gana, re-sincronizar
            if resolution == "local_wins":
                await self._sync_change(conflict["local_change"])
            
            logger.info(f"✅ Conflicto resuelto manualmente: {conflict_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error resolviendo conflicto manualmente: {e}")
            return False
    
    # ========================================================================
    # BACKUP Y VERSIONADO
    # ========================================================================
    
    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Crear backup local de todos los datos"""
        
        try:
            backup_name = backup_name or datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.sync_dir / f"backup_{backup_name}"
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Copiar todos los datos locales
            import shutil
            for entity_dir in self.local_db_dir.iterdir():
                if entity_dir.is_dir():
                    dest = backup_path / entity_dir.name
                    shutil.copytree(entity_dir, dest)
            
            logger.info(f"✅ Backup creado: {backup_path}")
            return str(backup_path)
        
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            raise
    
    async def restore_backup(self, backup_path: str) -> bool:
        """Restaurar datos desde backup"""
        
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                logger.error(f"Backup no encontrado: {backup_path}")
                return False
            
            # Restaurar datos
            import shutil
            for entity_dir in backup_path.iterdir():
                if entity_dir.is_dir():
                    dest = self.local_db_dir / entity_dir.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(entity_dir, dest)
            
            logger.info(f"✅ Datos restaurados desde: {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            return False
    
    async def get_version_history(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[Dict[str, Any]]:
        """Obtener historial de versiones de una entidad"""
        
        try:
            history = []
            
            # Buscar en cambios sincronizados
            for changes in self.sync_queue.values():
                for change in changes:
                    if change["entity_type"] == entity_type and change["entity_id"] == entity_id:
                        history.append({
                            "timestamp": change["timestamp"],
                            "change_type": change["change_type"],
                            "user_id": change["user_id"],
                            "synced": change.get("synced", False)
                        })
            
            return sorted(history, key=lambda x: x["timestamp"], reverse=True)
        
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []
    
    # ========================================================================
    # UTILIDADES
    # ========================================================================
    
    def _save_sync_queue(self):
        """Guardar cola de sincronización"""
        try:
            queue_file = self.sync_dir / "sync_queue.json"
            
            # Convertir defaultdict a dict normal
            queue_data = {k: v for k, v in self.sync_queue.items()}
            
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error guardando cola: {e}")
    
    def _load_sync_queue(self):
        """Cargar cola de sincronización"""
        try:
            queue_file = self.sync_dir / "sync_queue.json"
            
            if queue_file.exists():
                with open(queue_file, 'r', encoding='utf-8') as f:
                    queue_data = json.load(f)
                    self.sync_queue = defaultdict(list, queue_data)
                logger.info(f"✅ Cola de sincronización cargada")
        except Exception as e:
            logger.error(f"Error cargando cola: {e}")
    
    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calcular hash de datos para detección de cambios"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _entity_exists_local(self, entity_type: str, entity_id: str) -> bool:
        """Verificar si entidad existe localmente"""
        local_path = self.local_db_dir / entity_type / f"{entity_id}.json"
        return local_path.exists()
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """Obtener estado de sincronización"""
        
        total_pending = sum(len(changes) for changes in self.sync_queue.values())
        total_conflicts = len(self.conflicts)
        
        return {
            "is_online": self.is_online,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "pending_changes": total_pending,
            "conflicts": total_conflicts,
            "queue": {k: len(v) for k, v in self.sync_queue.items()},
            "sync_history_count": len(self.sync_history)
        }
