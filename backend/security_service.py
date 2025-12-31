# ============================================================================
# Servicio de Seguridad Empresarial Completo
# ============================================================================
# Archivo: backend/services/security_service.py
# Incluye: Anti-Hacking, Anti-Copy, Antivirus, Anti-Spam, Anti-Cloning, DRM
# ============================================================================

import logging
import hashlib
import hmac
import secrets
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid
import re
import asyncio
from collections import defaultdict
import subprocess

logger = logging.getLogger(__name__)

class LicenseType(str, Enum):
    """Tipos de licencia"""
    PERPETUAL = "perpetual"      # Compra permanente
    SUBSCRIPTION = "subscription"  # Suscripción mensual/anual
    TRIAL = "trial"              # Prueba gratuita
    RENTAL = "rental"            # Alquiler temporal

class SecurityLevel(str, Enum):
    """Niveles de seguridad"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ============================================================================
# ANTI-HACKING: Detección de Intrusiones y Rate Limiting
# ============================================================================

class AntiHackingService:
    """Servicio de detección de intrusiones y protección contra ataques"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)  # IP: [timestamps]
        self.blocked_ips = {}  # IP: unblock_time
        self.suspicious_patterns = []
        self.session_tokens = {}  # token: session_data
        
        logger.info("AntiHackingService inicializado")
    
    def generate_secure_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Generar token seguro con expiración"""
        token = secrets.token_urlsafe(32)
        
        self.session_tokens[token] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=expires_in),
            "ip_addresses": set(),
            "user_agents": set()
        }
        
        logger.info(f"✅ Token seguro generado para usuario: {user_id}")
        return token
    
    def validate_token(self, token: str, ip: str, user_agent: str) -> Tuple[bool, str]:
        """Validar token y detectar anomalías"""
        
        if token not in self.session_tokens:
            return False, "Token inválido"
        
        session = self.session_tokens[token]
        
        # Verificar expiración
        if datetime.now() > session["expires_at"]:
            del self.session_tokens[token]
            return False, "Token expirado"
        
        # Detectar cambio de IP (posible hijacking)
        if session["ip_addresses"] and ip not in session["ip_addresses"]:
            logger.warning(f"⚠️  Cambio de IP detectado: {ip}")
            return False, "Cambio de IP detectado - requiere re-autenticación"
        
        # Detectar cambio de User-Agent (posible hijacking)
        if session["user_agents"] and user_agent not in session["user_agents"]:
            logger.warning(f"⚠️  Cambio de User-Agent detectado")
            return False, "Cambio de dispositivo detectado - requiere re-autenticación"
        
        # Registrar acceso
        session["ip_addresses"].add(ip)
        session["user_agents"].add(user_agent)
        
        return True, "Token válido"
    
    async def check_rate_limit(
        self,
        identifier: str,
        max_attempts: int = 5,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """Verificar rate limiting por IP/usuario"""
        
        now = datetime.now()
        
        # Limpiar intentos antiguos
        self.failed_attempts[identifier] = [
            t for t in self.failed_attempts[identifier]
            if (now - t).total_seconds() < window_seconds
        ]
        
        # Verificar si está bloqueado
        if identifier in self.blocked_ips:
            if now < self.blocked_ips[identifier]:
                remaining = (self.blocked_ips[identifier] - now).total_seconds()
                return False, int(remaining)
            else:
                del self.blocked_ips[identifier]
        
        # Verificar intentos
        attempts = len(self.failed_attempts[identifier])
        
        if attempts >= max_attempts:
            # Bloquear por 15 minutos
            self.blocked_ips[identifier] = now + timedelta(minutes=15)
            logger.warning(f"🚨 IP bloqueada por rate limiting: {identifier}")
            return False, 900  # 15 minutos
        
        return True, max_attempts - attempts
    
    async def log_failed_attempt(self, identifier: str):
        """Registrar intento fallido"""
        self.failed_attempts[identifier].append(datetime.now())
        logger.warning(f"⚠️  Intento fallido: {identifier}")
    
    async def detect_sql_injection(self, input_string: str) -> bool:
        """Detectar intentos de SQL injection"""
        
        sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bor\b.*=.*)",
            r"(\bdrop\b.*\btable\b)",
            r"(\binsert\b.*\binto\b)",
            r"(\bdelete\b.*\bfrom\b)",
            r"(;.*--)",
            r"(\bexec\b.*\()",
            r"(\bscript\b.*\>)"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                logger.warning(f"🚨 SQL Injection detectado: {input_string[:50]}")
                return True
        
        return False
    
    async def detect_xss(self, input_string: str) -> bool:
        """Detectar intentos de XSS"""
        
        xss_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe",
            r"<object",
            r"<embed"
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                logger.warning(f"🚨 XSS detectado: {input_string[:50]}")
                return True
        
        return False

# ============================================================================
# ANTI-COPY: Protección de Contenido y Watermarking
# ============================================================================

class AntiCopyService:
    """Servicio de protección contra copia y screenshot"""
    
    def __init__(self, output_dir: str = "./data/protected_content"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("AntiCopyService inicializado")
    
    async def add_watermark(
        self,
        image_path: str,
        watermark_text: str,
        user_id: str,
        opacity: float = 0.3
    ) -> str:
        """Agregar watermark personalizado a imagen"""
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            logger.info(f"Agregando watermark a imagen: {image_path}")
            
            # Cargar imagen
            image = Image.open(image_path).convert("RGBA")
            
            # Crear capa de watermark
            watermark_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(watermark_layer)
            
            # Crear texto de watermark con info de usuario
            watermark_full = f"{watermark_text}\nUsuario: {user_id}\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Calcular posición (diagonal)
            font_size = max(20, image.width // 20)
            
            # Dibujar watermark múltiples veces (diagonal)
            for y in range(0, image.height, 200):
                for x in range(0, image.width, 300):
                    draw.text(
                        (x, y),
                        watermark_full,
                        fill=(128, 128, 128, int(255 * opacity)),
                        font=None
                    )
            
            # Combinar imágenes
            watermarked = Image.alpha_composite(image, watermark_layer)
            
            # Guardar
            output_id = str(uuid.uuid4())[:8]
            output_path = self.output_dir / f"{output_id}_watermarked.png"
            watermarked.convert("RGB").save(output_path, quality=95)
            
            logger.info(f"✅ Watermark agregado: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"Error agregando watermark: {e}")
            raise
    
    async def add_digital_fingerprint(
        self,
        content_path: str,
        user_id: str
    ) -> Dict[str, str]:
        """Agregar huella digital única al contenido"""
        
        try:
            # Generar fingerprint único
            fingerprint_data = f"{user_id}:{content_path}:{datetime.now().isoformat()}"
            fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()
            
            # Guardar metadata
            metadata = {
                "fingerprint": fingerprint,
                "user_id": user_id,
                "content_path": content_path,
                "created_at": datetime.now().isoformat(),
                "access_count": 0,
                "last_accessed": None
            }
            
            metadata_path = self.output_dir / f"{fingerprint}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Fingerprint digital agregado: {fingerprint}")
            
            return {
                "fingerprint": fingerprint,
                "user_id": user_id,
                "metadata_path": str(metadata_path)
            }
        
        except Exception as e:
            logger.error(f"Error agregando fingerprint: {e}")
            raise
    
    async def detect_unauthorized_copy(
        self,
        suspected_content_path: str,
        original_fingerprint: str
    ) -> Tuple[bool, float]:
        """Detectar copia no autorizada usando fingerprint"""
        
        try:
            # Calcular hash del contenido sospechoso
            with open(suspected_content_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Comparar con fingerprint original
            similarity = self._calculate_similarity(file_hash, original_fingerprint)
            
            if similarity > 0.95:
                logger.warning(f"🚨 Copia no autorizada detectada: {suspected_content_path}")
                return True, similarity
            
            return False, similarity
        
        except Exception as e:
            logger.error(f"Error detectando copia: {e}")
            return False, 0.0
    
    def _calculate_similarity(self, hash1: str, hash2: str) -> float:
        """Calcular similitud entre dos hashes"""
        matching_chars = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        return matching_chars / len(hash1)

# ============================================================================
# ANTIVIRUS: Escaneo de Archivos y Detección de Malware
# ============================================================================

class AntivirusService:
    """Servicio de escaneo de archivos y detección de malware"""
    
    def __init__(self):
        self.quarantine_dir = Path("./data/quarantine")
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)
        
        self.threat_signatures = self._load_threat_signatures()
        self.scan_history = []
        
        logger.info("AntivirusService inicializado")
    
    def _load_threat_signatures(self) -> List[str]:
        """Cargar firmas de amenazas conocidas"""
        # En producción, estas vendrían de una base de datos actualizada
        return [
            "eicar",  # EICAR test file
            "malware",
            "trojan",
            "ransomware",
            "backdoor"
        ]
    
    async def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Escanear archivo en busca de malware"""
        
        try:
            logger.info(f"Escaneando archivo: {file_path}")
            
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise Exception(f"Archivo no encontrado: {file_path}")
            
            # Leer contenido
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Calcular hash
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Buscar firmas
            threats_found = []
            
            for signature in self.threat_signatures:
                if signature.encode() in file_content:
                    threats_found.append(signature)
            
            # Verificar extensión peligrosa
            dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js']
            if file_path.suffix.lower() in dangerous_extensions and threats_found:
                threats_found.append("dangerous_extension")
            
            # Resultado del escaneo
            is_safe = len(threats_found) == 0
            
            scan_result = {
                "file": str(file_path),
                "hash": file_hash,
                "size": file_path.stat().st_size,
                "is_safe": is_safe,
                "threats_found": threats_found,
                "scanned_at": datetime.now().isoformat()
            }
            
            # Guardar en historial
            self.scan_history.append(scan_result)
            
            # Si hay amenazas, poner en cuarentena
            if not is_safe:
                await self._quarantine_file(file_path, threats_found)
                logger.warning(f"🚨 Amenaza detectada: {threats_found}")
            else:
                logger.info(f"✅ Archivo seguro: {file_path}")
            
            return scan_result
        
        except Exception as e:
            logger.error(f"Error escaneando archivo: {e}")
            raise
    
    async def _quarantine_file(self, file_path: Path, threats: List[str]):
        """Poner archivo en cuarentena"""
        
        try:
            import shutil
            
            quarantine_file = self.quarantine_dir / f"{uuid.uuid4().hex}_{file_path.name}"
            shutil.move(str(file_path), str(quarantine_file))
            
            # Guardar info de cuarentena
            quarantine_info = {
                "original_path": str(file_path),
                "quarantine_path": str(quarantine_file),
                "threats": threats,
                "quarantined_at": datetime.now().isoformat()
            }
            
            info_file = quarantine_file.with_suffix('.json')
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(quarantine_info, f, indent=2)
            
            logger.warning(f"📦 Archivo puesto en cuarentena: {quarantine_file}")
        
        except Exception as e:
            logger.error(f"Error poniendo en cuarentena: {e}")

# ============================================================================
# ANTI-SPAM: Filtrado Inteligente
# ============================================================================

class AntiSpamService:
    """Servicio de detección y filtrado de spam"""
    
    def __init__(self):
        self.spam_patterns = [
            r"(?i)(viagra|cialis|casino|lottery|winner|click here|buy now)",
            r"(?i)(free money|make money|work from home|easy cash)",
            r"(?i)(limited time|act now|urgent|hurry|don't miss)",
            r"(?i)(congratulations|you won|claim your|verify account)"
        ]
        
        self.blocked_domains = set()
        self.spam_history = []
        
        logger.info("AntiSpamService inicializado")
    
    async def check_spam(self, text: str) -> Tuple[bool, float, str]:
        """Verificar si texto es spam"""
        
        spam_score = 0.0
        reasons = []
        
        # Verificar patrones
        for pattern in self.spam_patterns:
            if re.search(pattern, text):
                spam_score += 0.2
                reasons.append(f"Patrón detectado: {pattern[:30]}")
        
        # Verificar URLs sospechosas
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        for url in urls:
            domain = url.split('/')[2]
            if domain in self.blocked_domains:
                spam_score += 0.3
                reasons.append(f"Dominio bloqueado: {domain}")
        
        # Verificar mayúsculas excesivas
        if len(text) > 10:
            uppercase_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if uppercase_ratio > 0.5:
                spam_score += 0.1
                reasons.append("Mayúsculas excesivas")
        
        # Verificar caracteres especiales excesivos
        special_chars = sum(1 for c in text if not c.isalnum() and c != ' ')
        if special_chars / len(text) > 0.3:
            spam_score += 0.1
            reasons.append("Caracteres especiales excesivos")
        
        is_spam = spam_score > 0.5
        
        if is_spam:
            logger.warning(f"🚨 Spam detectado (score: {spam_score:.2f}): {text[:50]}")
        
        return is_spam, spam_score, " | ".join(reasons)

# ============================================================================
# ANTI-CLONING: Detección de Duplicación
# ============================================================================

class AntiCloningService:
    """Servicio de detección de clonación de contenido"""
    
    def __init__(self):
        self.content_registry = {}  # hash: metadata
        self.clone_attempts = []
        
        logger.info("AntiCloningService inicializado")
    
    async def register_content(
        self,
        content_path: str,
        owner_id: str,
        license_type: str
    ) -> str:
        """Registrar contenido en el sistema anti-cloning"""
        
        try:
            # Calcular hash del contenido
            with open(content_path, 'rb') as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Registrar
            self.content_registry[content_hash] = {
                "owner_id": owner_id,
                "content_path": content_path,
                "license_type": license_type,
                "registered_at": datetime.now().isoformat(),
                "access_count": 0,
                "clone_attempts": 0
            }
            
            logger.info(f"✅ Contenido registrado: {content_hash[:8]}")
            return content_hash
        
        except Exception as e:
            logger.error(f"Error registrando contenido: {e}")
            raise
    
    async def detect_clone(
        self,
        suspected_content_path: str
    ) -> Tuple[bool, Optional[str], float]:
        """Detectar si contenido es clon no autorizado"""
        
        try:
            # Calcular hash
            with open(suspected_content_path, 'rb') as f:
                suspected_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Buscar en registro
            for registered_hash, metadata in self.content_registry.items():
                similarity = self._calculate_hash_similarity(suspected_hash, registered_hash)
                
                if similarity > 0.95:
                    # Clon detectado
                    metadata["clone_attempts"] += 1
                    
                    self.clone_attempts.append({
                        "original_hash": registered_hash,
                        "suspected_hash": suspected_hash,
                        "owner_id": metadata["owner_id"],
                        "detected_at": datetime.now().isoformat(),
                        "similarity": similarity
                    })
                    
                    logger.warning(f"🚨 Clon detectado: {similarity:.2%} similar a contenido de {metadata['owner_id']}")
                    
                    return True, metadata["owner_id"], similarity
            
            return False, None, 0.0
        
        except Exception as e:
            logger.error(f"Error detectando clon: {e}")
            return False, None, 0.0
    
    def _calculate_hash_similarity(self, hash1: str, hash2: str) -> float:
        """Calcular similitud entre hashes"""
        matching = sum(c1 == c2 for c1, c2 in zip(hash1, hash2))
        return matching / len(hash1)

# ============================================================================
# SISTEMA DE LICENCIAMIENTO Y DRM
# ============================================================================

class LicensingService:
    """Servicio de licenciamiento, venta y renta con DRM"""
    
    def __init__(self, licenses_dir: str = "./data/licenses"):
        self.licenses_dir = Path(licenses_dir)
        self.licenses_dir.mkdir(parents=True, exist_ok=True)
        
        self.licenses = {}
        self.transactions = []
        
        self._load_licenses()
        
        logger.info("LicensingService inicializado")
    
    def _load_licenses(self):
        """Cargar licencias guardadas"""
        try:
            licenses_file = self.licenses_dir / "licenses.json"
            if licenses_file.exists():
                with open(licenses_file, 'r', encoding='utf-8') as f:
                    self.licenses = json.load(f)
                logger.info(f"✅ {len(self.licenses)} licencias cargadas")
        except Exception as e:
            logger.error(f"Error cargando licencias: {e}")
    
    def _save_licenses(self):
        """Guardar licencias"""
        try:
            licenses_file = self.licenses_dir / "licenses.json"
            with open(licenses_file, 'w', encoding='utf-8') as f:
                json.dump(self.licenses, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error guardando licencias: {e}")
    
    async def create_license(
        self,
        product_id: str,
        user_id: str,
        license_type: LicenseType,
        price: float,
        duration_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Crear nueva licencia (venta o renta)"""
        
        try:
            license_id = str(uuid.uuid4())[:12]
            
            now = datetime.now()
            expires_at = None
            
            if license_type == LicenseType.SUBSCRIPTION:
                expires_at = (now + timedelta(days=30)).isoformat()
            elif license_type == LicenseType.RENTAL:
                if not duration_days:
                    duration_days = 7
                expires_at = (now + timedelta(days=duration_days)).isoformat()
            elif license_type == LicenseType.TRIAL:
                expires_at = (now + timedelta(days=14)).isoformat()
            
            # Generar clave de licencia
            license_key = self._generate_license_key(license_id, user_id, product_id)
            
            license_data = {
                "id": license_id,
                "key": license_key,
                "product_id": product_id,
                "user_id": user_id,
                "type": license_type.value,
                "price": price,
                "created_at": now.isoformat(),
                "expires_at": expires_at,
                "status": "active",
                "activation_count": 0,
                "max_activations": 5 if license_type != LicenseType.PERPETUAL else None,
                "devices": [],
                "last_verified": None
            }
            
            self.licenses[license_id] = license_data
            self._save_licenses()
            
            # Registrar transacción
            self.transactions.append({
                "license_id": license_id,
                "user_id": user_id,
                "product_id": product_id,
                "type": "purchase" if license_type == LicenseType.PERPETUAL else "rental",
                "price": price,
                "timestamp": now.isoformat()
            })
            
            logger.info(f"✅ Licencia creada: {license_id} ({license_type.value})")
            
            return license_data
        
        except Exception as e:
            logger.error(f"Error creando licencia: {e}")
            raise
    
    def _generate_license_key(self, license_id: str, user_id: str, product_id: str) -> str:
        """Generar clave de licencia segura"""
        
        key_data = f"{license_id}:{user_id}:{product_id}:{secrets.token_hex(16)}"
        key_hash = hashlib.sha256(key_data.encode()).hexdigest()
        
        # Formato: XXXX-XXXX-XXXX-XXXX
        key = "-".join([key_hash[i:i+4].upper() for i in range(0, 16, 4)])
        
        return key
    
    async def activate_license(
        self,
        license_key: str,
        device_id: str,
        device_info: Dict[str, str]
    ) -> Tuple[bool, str]:
        """Activar licencia en dispositivo"""
        
        try:
            # Buscar licencia por clave
            license_data = None
            license_id = None
            
            for lid, ld in self.licenses.items():
                if ld["key"] == license_key:
                    license_data = ld
                    license_id = lid
                    break
            
            if not license_data:
                logger.warning(f"⚠️  Clave de licencia no válida: {license_key}")
                return False, "Clave de licencia no válida"
            
            # Verificar expiración
            if license_data["expires_at"]:
                if datetime.fromisoformat(license_data["expires_at"]) < datetime.now():
                    logger.warning(f"⚠️  Licencia expirada: {license_id}")
                    return False, "Licencia expirada"
            
            # Verificar límite de activaciones
            if license_data["max_activations"]:
                if license_data["activation_count"] >= license_data["max_activations"]:
                    logger.warning(f"🚨 Límite de activaciones alcanzado: {license_id}")
                    return False, "Límite de activaciones alcanzado"
            
            # Agregar dispositivo
            license_data["devices"].append({
                "device_id": device_id,
                "device_info": device_info,
                "activated_at": datetime.now().isoformat()
            })
            
            license_data["activation_count"] += 1
            license_data["last_verified"] = datetime.now().isoformat()
            
            self._save_licenses()
            
            logger.info(f"✅ Licencia activada: {license_id} en dispositivo {device_id}")
            
            return True, f"Licencia activada exitosamente. Activaciones: {license_data['activation_count']}/{license_data['max_activations'] or 'Ilimitadas'}"
        
        except Exception as e:
            logger.error(f"Error activando licencia: {e}")
            return False, f"Error: {str(e)}"
    
    async def verify_license(self, license_key: str) -> Tuple[bool, Dict[str, Any]]:
        """Verificar validez de licencia"""
        
        try:
            # Buscar licencia
            for license_id, license_data in self.licenses.items():
                if license_data["key"] == license_key:
                    # Verificar expiración
                    if license_data["expires_at"]:
                        expires = datetime.fromisoformat(license_data["expires_at"])
                        if expires < datetime.now():
                            return False, {"error": "Licencia expirada"}
                    
                    # Verificar estado
                    if license_data["status"] != "active":
                        return False, {"error": "Licencia inactiva"}
                    
                    return True, {
                        "valid": True,
                        "license_id": license_id,
                        "type": license_data["type"],
                        "expires_at": license_data["expires_at"],
                        "activations": license_data["activation_count"],
                        "max_activations": license_data["max_activations"]
                    }
            
            return False, {"error": "Licencia no encontrada"}
        
        except Exception as e:
            logger.error(f"Error verificando licencia: {e}")
            return False, {"error": str(e)}
    
    async def revoke_license(self, license_id: str, reason: str) -> bool:
        """Revocar licencia (por fraude, etc.)"""
        
        try:
            if license_id not in self.licenses:
                return False
            
            self.licenses[license_id]["status"] = "revoked"
            self.licenses[license_id]["revoked_at"] = datetime.now().isoformat()
            self.licenses[license_id]["revoke_reason"] = reason
            
            self._save_licenses()
            
            logger.warning(f"🚨 Licencia revocada: {license_id} - Razón: {reason}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error revocando licencia: {e}")
            return False
    
    def get_license_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de licencias"""
        
        total_licenses = len(self.licenses)
        active_licenses = sum(1 for l in self.licenses.values() if l["status"] == "active")
        expired_licenses = sum(1 for l in self.licenses.values() if l["expires_at"] and datetime.fromisoformat(l["expires_at"]) < datetime.now())
        
        total_revenue = sum(t["price"] for t in self.transactions)
        
        return {
            "total_licenses": total_licenses,
            "active_licenses": active_licenses,
            "expired_licenses": expired_licenses,
            "total_transactions": len(self.transactions),
            "total_revenue": total_revenue,
            "average_price": total_revenue / len(self.transactions) if self.transactions else 0
        }
