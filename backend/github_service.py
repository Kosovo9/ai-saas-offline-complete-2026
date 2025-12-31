# ============================================================================
# Servicio de Integración con GitHub\n# ============================================================================
# Archivo: backend/services/github_service.py
# ============================================================================

import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class GitHubService:
    """Servicio para sincronización y gestión de repositorios GitHub"""
    
    def __init__(self, token: str = "", base_path: str = "./data/projects"):
        self.token = token
        self.base_path = Path(base_path)
        self.git_available = self._check_git()
        
        logger.info(f"GitHubService inicializado")
        logger.info(f"  Git disponible: {'✅' if self.git_available else '❌'}")
        logger.info(f"  GitHub token: {'✅' if token else '❌ (opcional)'}")
    
    def _check_git(self) -> bool:
        """Verificar si Git está instalado"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"Git no disponible: {e}")
            return False
    
    async def init_repo(self, project_id: str, repo_name: Optional[str] = None) -> Dict[str, Any]:
        """Inicializar repositorio Git local"""
        
        if not self.git_available:
            raise RuntimeError("Git no está instalado")
        
        try:
            project_path = self.base_path / project_id
            
            if not project_path.exists():
                raise Exception(f"Proyecto no encontrado: {project_id}")
            
            # Inicializar repositorio
            result = subprocess.run(
                ["git", "init"],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Error inicializando repo: {result.stderr}")
            
            # Configurar usuario (si no está configurado)
            subprocess.run(
                ["git", "config", "user.email", "ai-saas@offline.local"],
                cwd=str(project_path),
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "AI SaaS Offline"],
                cwd=str(project_path),
                capture_output=True
            )
            
            # Crear .gitignore
            gitignore_path = project_path / ".gitignore"
            gitignore_content = """# AI SaaS Generated
__pycache__/
*.pyc
.DS_Store
node_modules/
.env.local
*.log
.cache/
venv/
.venv/
"""
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            
            # Primer commit
            subprocess.run(
                ["git", "add", "."],
                cwd=str(project_path),
                capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=str(project_path),
                capture_output=True
            )
            
            logger.info(f"✅ Repositorio inicializado: {project_id}")
            
            return {
                "project_id": project_id,
                "status": "initialized",
                "path": str(project_path)
            }
        
        except Exception as e:
            logger.error(f"Error inicializando repo: {e}")
            raise
    
    async def add_remote(
        self,
        project_id: str,
        remote_url: str,
        remote_name: str = "origin"
    ) -> Dict[str, Any]:
        """Agregar repositorio remoto"""
        
        if not self.git_available:
            raise RuntimeError("Git no está instalado")
        
        try:
            project_path = self.base_path / project_id
            
            # Agregar remote
            result = subprocess.run(
                ["git", "remote", "add", remote_name, remote_url],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Si ya existe, actualizar
                subprocess.run(
                    ["git", "remote", "set-url", remote_name, remote_url],
                    cwd=str(project_path),
                    capture_output=True
                )
            
            logger.info(f"✅ Remote agregado: {remote_name} -> {remote_url}")
            
            return {
                "project_id": project_id,
                "remote_name": remote_name,
                "remote_url": remote_url,
                "status": "added"
            }
        
        except Exception as e:
            logger.error(f"Error agregando remote: {e}")
            raise
    
    async def commit(
        self,
        project_id: str,
        message: str,
        files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Hacer commit de cambios"""
        
        if not self.git_available:
            raise RuntimeError("Git no está instalado")
        
        try:
            project_path = self.base_path / project_id
            
            # Agregar archivos
            if files:
                for file in files:
                    subprocess.run(
                        ["git", "add", file],
                        cwd=str(project_path),
                        capture_output=True
                    )
            else:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=str(project_path),
                    capture_output=True
                )
            
            # Hacer commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning(f"Commit sin cambios o error: {result.stderr}")
                return {
                    "project_id": project_id,
                    "status": "no_changes",
                    "message": message
                }
            
            logger.info(f"✅ Commit realizado: {message}")
            
            return {
                "project_id": project_id,
                "status": "committed",
                "message": message,
                "output": result.stdout
            }
        
        except Exception as e:
            logger.error(f"Error en commit: {e}")
            raise
    
    async def push(
        self,
        project_id: str,
        remote_name: str = "origin",
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Hacer push a repositorio remoto"""
        
        if not self.git_available:
            raise RuntimeError("Git no está instalado")
        
        try:
            project_path = self.base_path / project_id
            
            # Hacer push
            result = subprocess.run(
                ["git", "push", "-u", remote_name, branch],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"Error en push: {result.stderr}")
                raise Exception(f"Push error: {result.stderr}")
            
            logger.info(f"✅ Push completado: {remote_name}/{branch}")
            
            return {
                "project_id": project_id,
                "status": "pushed",
                "remote": remote_name,
                "branch": branch,
                "output": result.stdout
            }
        
        except subprocess.TimeoutExpired:
            logger.error("Timeout en push")
            raise Exception("Push timeout")
        except Exception as e:
            logger.error(f"Error en push: {e}")
            raise
    
    async def pull(
        self,
        project_id: str,
        remote_name: str = "origin",
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Hacer pull desde repositorio remoto"""
        
        if not self.git_available:
            raise RuntimeError("Git no está instalado")
        
        try:
            project_path = self.base_path / project_id
            
            # Hacer pull
            result = subprocess.run(
                ["git", "pull", remote_name, branch],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"Error en pull: {result.stderr}")
                raise Exception(f"Pull error: {result.stderr}")
            
            logger.info(f"✅ Pull completado: {remote_name}/{branch}")
            
            return {
                "project_id": project_id,
                "status": "pulled",
                "remote": remote_name,
                "branch": branch,
                "output": result.stdout
            }
        
        except subprocess.TimeoutExpired:
            logger.error("Timeout en pull")
            raise Exception("Pull timeout")
        except Exception as e:
            logger.error(f"Error en pull: {e}")
            raise
    
    async def get_status(self, project_id: str) -> Dict[str, Any]:
        """Obtener estado del repositorio"""
        
        if not self.git_available:
            raise RuntimeError("Git no está instalado")
        
        try:
            project_path = self.base_path / project_id
            
            # Obtener estado
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Error obteniendo status: {result.stderr}")
            
            # Parsear cambios
            changes = {
                "modified": [],
                "added": [],
                "deleted": [],
                "untracked": []
            }
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                status = line[:2]
                file = line[3:]
                
                if status == "M ":
                    changes["modified"].append(file)
                elif status == "A ":
                    changes["added"].append(file)
                elif status == "D ":
                    changes["deleted"].append(file)
                elif status == "??":
                    changes["untracked"].append(file)
            
            return {
                "project_id": project_id,
                "changes": changes,
                "has_changes": any(changes.values())
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo status: {e}")
            raise
    
    async def get_log(self, project_id: str, max_commits: int = 10) -> List[Dict[str, Any]]:
        """Obtener historial de commits"""
        
        if not self.git_available:
            raise RuntimeError("Git no está instalado")
        
        try:
            project_path = self.base_path / project_id
            
            # Obtener log
            result = subprocess.run(
                ["git", "log", f"-{max_commits}", "--pretty=format:%H|%an|%ae|%ad|%s"],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning(f"No hay commits disponibles")
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })
            
            return commits
        
        except Exception as e:
            logger.error(f"Error obteniendo log: {e}")
            raise
    
    async def sync_project(self, project_id: str) -> Dict[str, Any]:
        """Sincronizar proyecto (pull + push)"""
        
        try:
            # Primero hacer pull
            pull_result = await self.pull(project_id)
            
            # Luego hacer push
            push_result = await self.push(project_id)
            
            return {
                "project_id": project_id,
                "status": "synced",
                "pull": pull_result,
                "push": push_result
            }
        
        except Exception as e:
            logger.error(f"Error sincronizando proyecto: {e}")
            raise
    
    async def create_branch(self, project_id: str, branch_name: str) -> Dict[str, Any]:
        """Crear nueva rama"""
        
        if not self.git_available:
            raise RuntimeError("Git no está instalado")
        
        try:
            project_path = self.base_path / project_id
            
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Error creando rama: {result.stderr}")
            
            logger.info(f"✅ Rama creada: {branch_name}")
            
            return {
                "project_id": project_id,
                "branch": branch_name,
                "status": "created"
            }
        
        except Exception as e:
            logger.error(f"Error creando rama: {e}")
            raise
    
    async def switch_branch(self, project_id: str, branch_name: str) -> Dict[str, Any]:
        """Cambiar a otra rama"""
        
        if not self.git_available:
            raise RuntimeError("Git no está instalado")
        
        try:
            project_path = self.base_path / project_id
            
            result = subprocess.run(
                ["git", "checkout", branch_name],
                cwd=str(project_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Error cambiando rama: {result.stderr}")
            
            logger.info(f"✅ Rama cambiada: {branch_name}")
            
            return {
                "project_id": project_id,
                "branch": branch_name,
                "status": "switched"
            }
        
        except Exception as e:
            logger.error(f"Error cambiando rama: {e}")
            raise
