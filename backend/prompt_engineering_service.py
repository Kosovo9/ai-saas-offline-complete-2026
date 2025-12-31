# ============================================================================
# Servicio de Ingeniería de Prompts - Super Prompts de Alta Gama
# ============================================================================
# Archivo: backend/services/prompt_engineering_service.py
# ============================================================================

import json
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid
from enum import Enum

logger = logging.getLogger(__name__)

class PromptCategory(str, Enum):
    """Categorías de prompts"""
    CODING = "coding"
    WRITING = "writing"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    BUSINESS = "business"
    EDUCATION = "education"
    RESEARCH = "research"
    MARKETING = "marketing"
    DESIGN = "design"
    CUSTOM = "custom"

class PromptTone(str, Enum):
    """Tonos de prompts"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ACADEMIC = "academic"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"
    FORMAL = "formal"

class PromptEngineeringService:
    """Servicio para generación y gestión de prompts de alta calidad"""
    
    def __init__(self, prompts_dir: str = "./data/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        self.prompts_library = {}
        self.prompt_templates = {}
        self.prompt_history = []
        
        self._load_library()
        self._initialize_templates()
        
        logger.info(f"PromptEngineeringService inicializado")
        logger.info(f"  Prompts en biblioteca: {len(self.prompts_library)}")
    
    def _load_library(self):
        """Cargar biblioteca de prompts guardados"""
        try:
            library_file = self.prompts_dir / "library.json"
            if library_file.exists():
                with open(library_file, 'r', encoding='utf-8') as f:
                    self.prompts_library = json.load(f)
                logger.info(f"✅ Biblioteca de prompts cargada")
        except Exception as e:
            logger.error(f"Error cargando biblioteca: {e}")
    
    def _save_library(self):
        """Guardar biblioteca de prompts"""
        try:
            library_file = self.prompts_dir / "library.json"
            with open(library_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompts_library, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando biblioteca: {e}")
    
    def _initialize_templates(self):
        """Inicializar templates de prompts predefinidos"""
        
        self.prompt_templates = {
            "code_generator": {
                "name": "Generador de Código",
                "category": PromptCategory.CODING,
                "template": """Eres un experto programador en {language}. 

Requisitos:
- Lenguaje: {language}
- Framework: {framework}
- Estilo de código: {style}
- Documentación: {documentation}

Tarea: {task}

Genera código limpio, eficiente y bien documentado. Incluye:
1. Código principal
2. Comentarios explicativos
3. Manejo de errores
4. Ejemplos de uso
5. Tests unitarios si es aplicable

Responde SOLO con código válido.""",
                "variables": ["language", "framework", "style", "documentation", "task"]
            },
            
            "content_writer": {
                "name": "Escritor de Contenido",
                "category": PromptCategory.WRITING,
                "template": """Eres un escritor profesional especializado en {niche}.

Contexto:
- Audiencia: {audience}
- Tono: {tone}
- Longitud: {length} palabras
- Propósito: {purpose}
- Idioma: {language}

Tema: {topic}

Genera contenido:
1. Atractivo y relevante
2. Optimizado para SEO
3. Con estructura clara
4. Llamadas a la acción
5. Datos y estadísticas si aplica

Asegúrate de que sea original y de alta calidad.""",
                "variables": ["niche", "audience", "tone", "length", "purpose", "language", "topic"]
            },
            
            "data_analyst": {
                "name": "Analista de Datos",
                "category": PromptCategory.ANALYSIS,
                "template": """Eres un analista de datos experto.

Datos a analizar:
{data}

Contexto:
- Objetivo: {objective}
- Industria: {industry}
- Período: {period}
- Métrica clave: {metric}

Proporciona:
1. Resumen ejecutivo
2. Patrones identificados
3. Anomalías detectadas
4. Recomendaciones accionables
5. Visualizaciones sugeridas
6. Próximos pasos

Sé específico y basado en datos.""",
                "variables": ["data", "objective", "industry", "period", "metric"]
            },
            
            "creative_brainstorm": {
                "name": "Brainstorm Creativo",
                "category": PromptCategory.CREATIVE,
                "template": """Eres un especialista en creatividad e innovación.

Proyecto: {project}
Restricciones: {constraints}
Público objetivo: {target_audience}
Presupuesto: {budget}
Plazo: {timeline}

Genera:
1. 10 ideas innovadoras
2. Concepto único para cada una
3. Ventajas competitivas
4. Riesgos potenciales
5. Recursos necesarios
6. Métricas de éxito

Sé audaz pero realista. Piensa fuera de la caja.""",
                "variables": ["project", "constraints", "target_audience", "budget", "timeline"]
            },
            
            "business_strategy": {
                "name": "Estrategia Empresarial",
                "category": PromptCategory.BUSINESS,
                "template": """Eres un consultor estratégico de negocios.

Empresa: {company}
Industria: {industry}
Situación actual: {current_situation}
Objetivo: {objective}
Horizonte: {timeframe}

Desarrolla una estrategia que incluya:
1. Análisis FODA
2. Oportunidades de mercado
3. Ventajas competitivas
4. Plan de acción (90 días)
5. KPIs y métricas
6. Riesgos y mitigación
7. Presupuesto estimado

Sé práctico y orientado a resultados.""",
                "variables": ["company", "industry", "current_situation", "objective", "timeframe"]
            },
            
            "research_paper": {
                "name": "Investigación Académica",
                "category": PromptCategory.RESEARCH,
                "template": """Eres un investigador académico experto en {field}.

Tema de investigación: {topic}
Nivel: {level}
Extensión: {length} palabras
Enfoque: {approach}
Audiencia: {audience}

Estructura la investigación:
1. Introducción con contexto
2. Estado del arte
3. Metodología
4. Hallazgos principales
5. Análisis crítico
6. Conclusiones
7. Referencias (mínimo 10)

Usa lenguaje académico riguroso y citas apropiadas.""",
                "variables": ["field", "topic", "level", "length", "approach", "audience"]
            },
            
            "marketing_campaign": {
                "name": "Campaña de Marketing",
                "category": PromptCategory.MARKETING,
                "template": """Eres un estratega de marketing digital.

Producto/Servicio: {product}
Mercado objetivo: {target_market}
Presupuesto: {budget}
Canales: {channels}
Duración: {duration}
Objetivo: {goal}

Diseña una campaña completa:
1. Propuesta de valor única
2. Mensajes clave
3. Estrategia por canal
4. Calendario de ejecución
5. Contenido específico
6. Métricas de éxito
7. Presupuesto desglosado
8. Contingencias

Sé creativo pero data-driven.""",
                "variables": ["product", "target_market", "budget", "channels", "duration", "goal"]
            },
            
            "design_brief": {
                "name": "Brief de Diseño",
                "category": PromptCategory.DESIGN,
                "template": """Eres un director creativo de diseño.

Proyecto: {project}
Tipo: {design_type}
Audiencia: {audience}
Estilo: {style}
Restricciones: {constraints}

Crea un brief que incluya:
1. Visión del proyecto
2. Elementos visuales clave
3. Paleta de colores (con códigos hex)
4. Tipografía recomendada
5. Composición y layout
6. Iconografía
7. Animaciones (si aplica)
8. Especificaciones técnicas

Proporciona referencias visuales sugeridas.""",
                "variables": ["project", "design_type", "audience", "style", "constraints"]
            }
        }
    
    async def generate_super_prompt(
        self,
        task_description: str,
        category: PromptCategory,
        tone: PromptTone,
        context: Optional[Dict[str, Any]] = None,
        ollama_service = None
    ) -> Dict[str, Any]:
        """Generar un super prompt optimizado usando IA"""
        
        try:
            logger.info(f"Generando super prompt: {category}")
            
            # Construir prompt para generar el super prompt
            generation_prompt = f"""Eres un experto en ingeniería de prompts. Tu tarea es crear un prompt de alta calidad.

Requisitos:
- Categoría: {category.value}
- Tono: {tone.value}
- Descripción de tarea: {task_description}
- Contexto adicional: {json.dumps(context or {})}

Genera un super prompt que:
1. Sea específico y detallado
2. Incluya instrucciones claras
3. Defina el rol del asistente
4. Especifique el formato de salida
5. Incluya ejemplos si es necesario
6. Tenga restricciones y límites claros
7. Sea optimizado para obtener mejores resultados

Formato de respuesta (JSON):
{{
    "prompt": "El prompt completo aquí",
    "variables": ["lista", "de", "variables"],
    "tips": ["tip1", "tip2", "tip3"],
    "expected_output": "Descripción del output esperado"
}}"""
            
            # Generar usando LLM
            if ollama_service:
                response_text = await ollama_service.generate(
                    prompt=generation_prompt,
                    system_prompt="Eres un experto en ingeniería de prompts. Devuelve SOLO JSON válido."
                )
            else:
                # Respuesta de ejemplo si no hay LLM
                response_text = self._generate_example_prompt(task_description, category, tone)
            
            # Parsear respuesta
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Intentar extraer JSON de la respuesta
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {
                        "prompt": response_text,
                        "variables": [],
                        "tips": [],
                        "expected_output": "Respuesta del modelo"
                    }
            
            # Guardar en biblioteca
            prompt_id = str(uuid.uuid4())[:8]
            prompt_entry = {
                "id": prompt_id,
                "task_description": task_description,
                "category": category.value,
                "tone": tone.value,
                "prompt": result.get("prompt", ""),
                "variables": result.get("variables", []),
                "tips": result.get("tips", []),
                "expected_output": result.get("expected_output", ""),
                "created_at": datetime.now().isoformat(),
                "usage_count": 0,
                "effectiveness_score": 0
            }
            
            self.prompts_library[prompt_id] = prompt_entry
            self._save_library()
            
            logger.info(f"✅ Super prompt generado: {prompt_id}")
            
            return {
                "prompt_id": prompt_id,
                "prompt": result.get("prompt", ""),
                "variables": result.get("variables", []),
                "tips": result.get("tips", []),
                "expected_output": result.get("expected_output", ""),
                "category": category.value,
                "tone": tone.value
            }
        
        except Exception as e:
            logger.error(f"Error generando super prompt: {e}")
            raise
    
    def _generate_example_prompt(
        self,
        task_description: str,
        category: PromptCategory,
        tone: PromptTone
    ) -> str:
        """Generar prompt de ejemplo (sin LLM)"""
        
        tone_descriptions = {
            PromptTone.PROFESSIONAL: "profesional y formal",
            PromptTone.CASUAL: "casual y amigable",
            PromptTone.ACADEMIC: "académico y riguroso",
            PromptTone.CREATIVE: "creativo e innovador",
            PromptTone.TECHNICAL: "técnico y detallado",
            PromptTone.FRIENDLY: "amigable y accesible",
            PromptTone.FORMAL: "formal y corporativo"
        }
        
        prompt = f"""Eres un experto en {category.value}.

Tu tarea: {task_description}

Tono: {tone_descriptions.get(tone, 'neutral')}

Por favor:
1. Analiza la solicitud cuidadosamente
2. Proporciona una respuesta completa y bien estructurada
3. Incluye ejemplos cuando sea relevante
4. Asegúrate de que la calidad sea alta
5. Sigue las mejores prácticas de la industria

Responde de manera clara y concisa."""
        
        return json.dumps({
            "prompt": prompt,
            "variables": ["task_description", "category", "tone"],
            "tips": [
                "Sé específico en tus solicitudes",
                "Proporciona contexto adicional si es necesario",
                "Define claramente el formato de salida esperado"
            ],
            "expected_output": "Respuesta de alta calidad según la tarea"
        })
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Obtener template predefinido"""
        return self.prompt_templates.get(template_name)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """Listar todos los templates disponibles"""
        templates = []
        
        for name, template in self.prompt_templates.items():
            templates.append({
                "name": template.get("name"),
                "category": template.get("category"),
                "variables": template.get("variables", [])
            })
        
        return templates
    
    def fill_template(self, template_name: str, values: Dict[str, str]) -> str:
        """Rellenar template con valores"""
        
        template = self.prompt_templates.get(template_name)
        if not template:
            raise Exception(f"Template no encontrado: {template_name}")
        
        prompt_text = template.get("template", "")
        
        # Reemplazar variables
        for var, value in values.items():
            prompt_text = prompt_text.replace(f"{{{var}}}", value)
        
        return prompt_text
    
    def get_library(self) -> List[Dict[str, Any]]:
        """Obtener biblioteca de prompts"""
        prompts = []
        
        for prompt_id, prompt_data in self.prompts_library.items():
            prompts.append({
                "id": prompt_id,
                "task_description": prompt_data.get("task_description"),
                "category": prompt_data.get("category"),
                "tone": prompt_data.get("tone"),
                "created_at": prompt_data.get("created_at"),
                "usage_count": prompt_data.get("usage_count", 0),
                "effectiveness_score": prompt_data.get("effectiveness_score", 0)
            })
        
        return sorted(prompts, key=lambda x: x["usage_count"], reverse=True)
    
    def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Obtener prompt específico"""
        
        if prompt_id not in self.prompts_library:
            return None
        
        prompt = self.prompts_library[prompt_id].copy()
        
        # Incrementar contador de uso
        self.prompts_library[prompt_id]["usage_count"] = prompt.get("usage_count", 0) + 1
        self._save_library()
        
        return prompt
    
    def update_effectiveness(self, prompt_id: str, score: float) -> bool:
        """Actualizar puntuación de efectividad del prompt"""
        
        if prompt_id not in self.prompts_library:
            return False
        
        # Actualizar score (promedio móvil)
        current_score = self.prompts_library[prompt_id].get("effectiveness_score", 0)
        usage_count = self.prompts_library[prompt_id].get("usage_count", 1)
        
        new_score = (current_score * (usage_count - 1) + score) / usage_count
        self.prompts_library[prompt_id]["effectiveness_score"] = new_score
        
        self._save_library()
        
        logger.info(f"Score actualizado: {prompt_id} = {new_score:.2f}")
        return True
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Eliminar prompt de la biblioteca"""
        
        if prompt_id not in self.prompts_library:
            return False
        
        del self.prompts_library[prompt_id]
        self._save_library()
        
        logger.info(f"✅ Prompt eliminado: {prompt_id}")
        return True
    
    def export_library(self, format: str = "json") -> str:
        """Exportar biblioteca de prompts"""
        
        try:
            if format == "json":
                export_file = self.prompts_dir / f"library_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(self.prompts_library, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ Biblioteca exportada: {export_file}")
                return str(export_file)
            
            elif format == "csv":
                import csv
                export_file = self.prompts_dir / f"library_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                
                with open(export_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        "id", "task_description", "category", "tone", "created_at", "usage_count", "effectiveness_score"
                    ])
                    writer.writeheader()
                    
                    for prompt_id, prompt_data in self.prompts_library.items():
                        writer.writerow({
                            "id": prompt_id,
                            "task_description": prompt_data.get("task_description"),
                            "category": prompt_data.get("category"),
                            "tone": prompt_data.get("tone"),
                            "created_at": prompt_data.get("created_at"),
                            "usage_count": prompt_data.get("usage_count", 0),
                            "effectiveness_score": prompt_data.get("effectiveness_score", 0)
                        })
                
                logger.info(f"✅ Biblioteca exportada: {export_file}")
                return str(export_file)
            
            else:
                raise Exception(f"Formato no soportado: {format}")
        
        except Exception as e:
            logger.error(f"Error exportando biblioteca: {e}")
            raise
