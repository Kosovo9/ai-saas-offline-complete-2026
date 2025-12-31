# ============================================================================
# Servicio de Gestión de Proyectos
# ============================================================================
# Archivo: backend/services/project_service.py\n# ============================================================================

import json
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class ProjectService:
    """Servicio para gestionar proyectos locales"""
    
    def __init__(self, base_path: str = "./data/projects"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"ProjectService inicializado en: {self.base_path}")
    
    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        template: Optional[str] = None
    ) -> Dict[str, Any]:
        """Crear nuevo proyecto"""
        try:
            # Generar ID único
            project_id = str(uuid.uuid4())[:8]
            project_path = self.base_path / project_id
            
            # Crear estructura de carpetas
            project_path.mkdir(parents=True, exist_ok=True)
            (project_path / "src").mkdir(exist_ok=True)
            (project_path / "assets").mkdir(exist_ok=True)
            (project_path / "docs").mkdir(exist_ok=True)
            
            # Crear metadata del proyecto
            metadata = {
                "id": project_id,
                "name": name,
                "description": description or "",
                "template": template or "blank",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "files": [],
                "github_repo": None,
                "tags": []
            }
            
            # Guardar metadata
            metadata_path = project_path / "project.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Crear archivo README
            readme_path = project_path / "README.md"
            readme_content = f"""# {name}

{description or ""}

## Estructura del Proyecto

- `src/` - Código fuente
- `assets/` - Recursos (imágenes, estilos, etc.)
- `docs/` - Documentación

## Creado con AI SaaS Offline

Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            logger.info(f"✅ Proyecto creado: {project_id} ({name})")
            
            return {
                "id": project_id,
                "name": name,
                "description": description,
                "path": str(project_path),
                "created_at": metadata["created_at"]
            }
        
        except Exception as e:
            logger.error(f"Error creando proyecto: {e}")
            raise
    
    async def list_all(self) -> List[Dict[str, Any]]:
        """Listar todos los proyectos"""
        try:
            projects = []
            
            for project_dir in self.base_path.iterdir():
                if project_dir.is_dir():
                    metadata_path = project_dir / "project.json"
                    
                    if metadata_path.exists():
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        projects.append({
                            "id": metadata["id"],
                            "name": metadata["name"],
                            "description": metadata["description"],
                            "template": metadata["template"],
                            "created_at": metadata["created_at"],
                            "updated_at": metadata["updated_at"],
                            "path": str(project_dir)
                        })
            
            logger.info(f"Listados {len(projects)} proyectos")
            return sorted(projects, key=lambda x: x["updated_at"], reverse=True)
        
        except Exception as e:
            logger.error(f"Error listando proyectos: {e}")
            raise
    
    async def get(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Obtener detalles de un proyecto"""
        try:
            project_path = self.base_path / project_id
            metadata_path = project_path / "project.json"
            
            if not metadata_path.exists():
                logger.warning(f"Proyecto no encontrado: {project_id}")
                return None
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Listar archivos
            files = []
            for file_path in project_path.rglob("*"):
                if file_path.is_file() and file_path.name != "project.json":
                    rel_path = file_path.relative_to(project_path)
                    files.append({
                        "name": file_path.name,
                        "path": str(rel_path),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            metadata["files"] = files
            metadata["path"] = str(project_path)
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error obteniendo proyecto: {e}")
            raise
    
    async def update(
        self,
        project_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        files: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Actualizar proyecto"""
        try:
            project_path = self.base_path / project_id
            metadata_path = project_path / "project.json"
            
            if not metadata_path.exists():
                raise Exception(f"Proyecto no encontrado: {project_id}")
            
            # Leer metadata actual
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Actualizar campos
            if name:
                metadata["name"] = name
            if description:
                metadata["description"] = description
            
            metadata["updated_at"] = datetime.now().isoformat()
            
            # Guardar metadata
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Guardar archivos si se proporcionan
            if files:
                for file_path, content in files.items():
                    full_path = project_path / file_path
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    logger.info(f"✅ Archivo guardado: {file_path}")
            
            logger.info(f"✅ Proyecto actualizado: {project_id}")
            
            return await self.get(project_id)
        
        except Exception as e:
            logger.error(f"Error actualizando proyecto: {e}")
            raise
    
    async def delete(self, project_id: str) -> bool:
        """Eliminar proyecto"""
        try:
            project_path = self.base_path / project_id
            
            if not project_path.exists():
                logger.warning(f"Proyecto no encontrado: {project_id}")
                return False
            
            # Eliminar carpeta completa
            shutil.rmtree(project_path)
            
            logger.info(f"✅ Proyecto eliminado: {project_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error eliminando proyecto: {e}")
            raise
    
    async def export_project(self, project_id: str, export_format: str = "zip") -> str:
        """Exportar proyecto"""
        try:
            project_path = self.base_path / project_id
            
            if not project_path.exists():
                raise Exception(f"Proyecto no encontrado: {project_id}")
            
            if export_format == "zip":
                export_path = self.base_path / f"{project_id}_export.zip"
                shutil.make_archive(str(export_path.with_suffix('')), 'zip', project_path)
                logger.info(f"✅ Proyecto exportado: {export_path}")
                return str(export_path)
            
            elif export_format == "tar":
                export_path = self.base_path / f"{project_id}_export.tar.gz"
                shutil.make_archive(str(export_path.with_suffix('')), 'gztar', project_path)
                logger.info(f"✅ Proyecto exportado: {export_path}")
                return str(export_path)
            
            else:
                raise Exception(f"Formato de exportación no soportado: {export_format}")
        
        except Exception as e:
            logger.error(f"Error exportando proyecto: {e}")
            raise
    
    async def import_project(self, import_path: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Importar proyecto desde archivo"""
        try:
            import_file = Path(import_path)
            
            if not import_file.exists():
                raise Exception(f"Archivo no encontrado: {import_path}")
            
            # Generar ID único
            project_id = str(uuid.uuid4())[:8]
            project_path = self.base_path / project_id
            
            # Extraer archivo
            if import_file.suffix == ".zip":
                shutil.unpack_archive(import_path, project_path, 'zip')
            elif import_file.suffix == ".gz":
                shutil.unpack_archive(import_path, project_path, 'gztar')
            else:
                raise Exception(f"Formato no soportado: {import_file.suffix}")
            
            # Crear metadata
            metadata = {
                "id": project_id,
                "name": name or import_file.stem,
                "description": "Proyecto importado",
                "template": "imported",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "files": [],
                "github_repo": None,
                "tags": ["imported"]
            }
            
            metadata_path = project_path / "project.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Proyecto importado: {project_id}")
            
            return {
                "id": project_id,
                "name": metadata["name"],
                "path": str(project_path)
            }
        
        except Exception as e:
            logger.error(f"Error importando proyecto: {e}")
            raise
    
    async def get_file(self, project_id: str, file_path: str) -> str:
        """Obtener contenido de archivo"""
        try:
            full_path = self.base_path / project_id / file_path
            
            if not full_path.exists():
                raise Exception(f"Archivo no encontrado: {file_path}")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
        
        except Exception as e:
            logger.error(f"Error obteniendo archivo: {e}")
            raise
    
    async def save_file(self, project_id: str, file_path: str, content: str) -> bool:
        """Guardar archivo en proyecto"""
        try:
            full_path = self.base_path / project_id / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"✅ Archivo guardado: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error guardando archivo: {e}")
            raise
    
    async def delete_file(self, project_id: str, file_path: str) -> bool:
        """Eliminar archivo del proyecto"""
        try:
            full_path = self.base_path / project_id / file_path
            
            if not full_path.exists():
                logger.warning(f"Archivo no encontrado: {file_path}")
                return False
            
            full_path.unlink()
            logger.info(f"✅ Archivo eliminado: {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error eliminando archivo: {e}")
            raise
