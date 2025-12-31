# ============================================================================
# KNOWLEDGE BASE Y SISTEMA DE ENTRENAMIENTO DE IA DEL PROYECTO
# ============================================================================
# Archivo: backend/services/project_knowledge_base.py
# Entrena la IA con todos los campos, features y estrategias del proyecto
# ============================================================================

import logging
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
from enum import Enum
import uuid
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)

class DomainArea(str, Enum):
    """Áreas de dominio del proyecto"""
    ENTERPRISE_SALES = "enterprise_sales"
    CREATOR_MONETIZATION = "creator_monetization"
    AI_CAPABILITIES = "ai_capabilities"
    SECURITY = "security"
    OFFLINE_FEATURES = "offline_features"
    TECHNICAL = "technical"
    COMPLIANCE = "compliance"
    MARKET_ANALYSIS = "market_analysis"

class ProjectKnowledgeBase:
    """Base de conocimiento consolidada del proyecto"""
    
    def __init__(self, kb_dir: str = "./data/knowledge_base"):
        self.kb_dir = Path(kb_dir)
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        
        # Almacenamiento de conocimiento
        self.knowledge_store = {}
        self.domain_expertise = defaultdict(dict)
        self.learned_patterns = []
        self.training_history = []
        
        # Inicializar con conocimiento base
        self._initialize_base_knowledge()
        
        logger.info("ProjectKnowledgeBase inicializado")
    
    # ========================================================================
    # INICIALIZACIÓN DE CONOCIMIENTO BASE
    # ========================================================================
    
    def _initialize_base_knowledge(self):
        """Inicializar con todo el conocimiento del proyecto"""
        
        logger.info("📚 Inicializando Knowledge Base del proyecto...")
        
        # 1. ENTERPRISE SALES
        self._add_domain_knowledge(
            DomainArea.ENTERPRISE_SALES,
            {
                "target_markets": {
                    "governments": {
                        "segments": ["Defense", "Justice", "Health", "Finance", "Energy"],
                        "market_size": "$500B+",
                        "key_pain_points": [
                            "Data security",
                            "Regulatory compliance",
                            "Offline capability",
                            "Audit trails",
                            "Classification handling"
                        ],
                        "pricing_models": ["Perpetual License", "Annual Rental", "Hybrid"],
                        "average_deal_size": "$500K - $5M"
                    },
                    "banking": {
                        "segments": ["Central Banks", "Commercial Banks", "Financial Institutions"],
                        "market_size": "$200B+",
                        "key_pain_points": [
                            "PCI-DSS compliance",
                            "Fraud detection",
                            "Data privacy",
                            "Real-time processing",
                            "Risk management"
                        ],
                        "pricing_models": ["Perpetual License", "Per-Transaction", "Hybrid"],
                        "average_deal_size": "$1M - $10M"
                    },
                    "healthcare": {
                        "segments": ["Hospitals", "Pharma", "Research"],
                        "market_size": "$150B+",
                        "key_pain_points": [
                            "HIPAA compliance",
                            "Patient privacy",
                            "Data sensitivity",
                            "Research support",
                            "Audit requirements"
                        ],
                        "pricing_models": ["Perpetual License", "Per-Patient", "Per-Analysis"],
                        "average_deal_size": "$500K - $5M"
                    },
                    "energy": {
                        "segments": ["Grid Operators", "Generators", "Distributors"],
                        "market_size": "$100B+",
                        "key_pain_points": [
                            "Critical infrastructure",
                            "Offline capability",
                            "Real-time anomaly detection",
                            "Cybersecurity",
                            "Resilience"
                        ],
                        "pricing_models": ["Perpetual License", "Per-Site"],
                        "average_deal_size": "$2M - $10M"
                    },
                    "defense": {
                        "segments": ["Military", "Contractors", "Space Agencies"],
                        "market_size": "$300B+",
                        "key_pain_points": [
                            "Military security",
                            "Classification handling",
                            "Offline operation",
                            "Air-gapped networks",
                            "Audit trails"
                        ],
                        "pricing_models": ["Perpetual License", "Negotiated"],
                        "average_deal_size": "$5M - $50M+"
                    }
                },
                "compliance_requirements": {
                    "governments": ["ISO 27001", "NIST", "FedRAMP", "National Classification"],
                    "banking": ["PCI-DSS", "SOC 2 Type II", "ISO 27001", "Regulatory"],
                    "healthcare": ["HIPAA", "GDPR", "HITRUST", "ISO 27001"],
                    "energy": ["NERC CIP", "IEC 62351", "ISO 27001"],
                    "defense": ["Military Classification", "Common Criteria", "FIPS 140-2"]
                },
                "sales_process": [
                    "Identify decision makers",
                    "Understand budget",
                    "Map security requirements",
                    "Create POC",
                    "Technical demo",
                    "Compliance verification",
                    "Negotiate terms",
                    "Close deal"
                ],
                "key_differentiators": [
                    "100% Offline capability",
                    "Military-grade security",
                    "Full compliance",
                    "No data leaves server",
                    "Audit trails",
                    "Customizable",
                    "Lower TCO"
                ]
            }
        )
        
        # 2. CREATOR MONETIZATION
        self._add_domain_knowledge(
            DomainArea.CREATOR_MONETIZATION,
            {
                "creator_segments": {
                    "youtubers": {
                        "pain_points": [
                            "Need internet for editing",
                            "Expensive software",
                            "Can't work remotely",
                            "Publishing delays",
                            "Viral opportunities missed"
                        ],
                        "solutions": [
                            "Offline video editing",
                            "AI thumbnail generation",
                            "Auto title/description",
                            "Multi-language translation",
                            "Auto-publishing"
                        ],
                        "market_size": "50M+ creators",
                        "average_revenue": "$5K-$100K/month"
                    },
                    "tiktok_creators": {
                        "pain_points": [
                            "Need speed",
                            "Trending sounds limited",
                            "Timing critical",
                            "Competition fierce",
                            "Viral window short"
                        ],
                        "solutions": [
                            "Offline short video generation",
                            "Trending sounds locally",
                            "Trend prediction",
                            "Optimal posting time",
                            "Auto A/B testing"
                        ],
                        "market_size": "100M+ creators",
                        "average_revenue": "$1K-$50K/month"
                    },
                    "photographers": {
                        "pain_points": [
                            "Heavy editing software",
                            "Batch processing slow",
                            "Manual watermarking",
                            "Metadata processing",
                            "Variation generation"
                        ],
                        "solutions": [
                            "Offline photo editing",
                            "50+ variations per photo",
                            "Auto watermarking",
                            "Batch processing",
                            "Upscaling & enhancement"
                        ],
                        "market_size": "30M+ creators",
                        "average_revenue": "$2K-$50K/month"
                    },
                    "podcasters": {
                        "pain_points": [
                            "Audio editing complex",
                            "Transcription slow",
                            "Show notes manual",
                            "Multi-platform distribution",
                            "Metadata management"
                        ],
                        "solutions": [
                            "Offline audio editing",
                            "Auto transcription",
                            "Auto show notes",
                            "Auto translation",
                            "Multi-platform publishing"
                        ],
                        "market_size": "20M+ creators",
                        "average_revenue": "$1K-$100K/month"
                    },
                    "writers": {
                        "pain_points": [
                            "Writer's block",
                            "SEO optimization",
                            "Image generation",
                            "Multi-platform publishing",
                            "Research limitations"
                        ],
                        "solutions": [
                            "AI writing assistance",
                            "Idea generation",
                            "Image generation",
                            "SEO optimization",
                            "Auto-publishing"
                        ],
                        "market_size": "50M+ creators",
                        "average_revenue": "$500-$20K/month"
                    }
                },
                "pricing_tiers": {
                    "free": {
                        "price": "$0",
                        "features": [
                            "5 chat queries/day",
                            "1 image/day",
                            "10 min transcription/month",
                            "1GB storage"
                        ]
                    },
                    "creator": {
                        "price": "$9.99/month",
                        "features": [
                            "Unlimited chat",
                            "100 images/month",
                            "10 hours transcription/month",
                            "Basic video editing",
                            "100GB storage",
                            "1 platform publishing"
                        ]
                    },
                    "pro": {
                        "price": "$29.99/month",
                        "features": [
                            "Everything in Creator +",
                            "500 images/month",
                            "50 hours transcription/month",
                            "Advanced video editing",
                            "50+ variations",
                            "5 platform publishing",
                            "Advanced analytics",
                            "500GB storage"
                        ]
                    },
                    "studio": {
                        "price": "$99.99/month",
                        "features": [
                            "Everything in Pro +",
                            "Unlimited generation",
                            "Unlimited transcription",
                            "2TB storage",
                            "20+ platform publishing",
                            "AI Swarm",
                            "Trend Forecasting",
                            "Revenue Engine",
                            "24/7 support"
                        ]
                    }
                },
                "monetization_channels": [
                    "Freemium conversion",
                    "Premium features",
                    "Marketplace (80/20 split)",
                    "Enterprise deals",
                    "Affiliate programs"
                ],
                "regional_pricing": {
                    "latam": "$2-5/month",
                    "africa": "$1-2/month",
                    "asia": "$1-3/month",
                    "europe": "$10-20/month",
                    "usa": "$10-30/month"
                }
            }
        )
        
        # 3. AI CAPABILITIES
        self._add_domain_knowledge(
            DomainArea.AI_CAPABILITIES,
            {
                "ai_swarm": {
                    "description": "Multiple AI models voting and reaching consensus",
                    "models": ["DeepSeek-R1 7B", "Qwen2 7B", "Llama2 7B", "Mistral 7B"],
                    "benefits": [
                        "3-5x better accuracy",
                        "Hallucination detection",
                        "Explainable reasoning",
                        "Dynamic model selection"
                    ],
                    "use_cases": [
                        "Complex reasoning",
                        "Fact verification",
                        "Multi-perspective analysis",
                        "High-stakes decisions"
                    ]
                },
                "trend_forecasting": {
                    "description": "Predict trends 30-90 days in advance",
                    "data_sources": [
                        "Twitter/X",
                        "Reddit",
                        "TikTok",
                        "YouTube",
                        "Google Trends",
                        "News APIs"
                    ],
                    "methods": [
                        "Pattern analysis",
                        "Growth rate detection",
                        "Correlation analysis",
                        "Sentiment analysis",
                        "ARIMA/Prophet models"
                    ],
                    "accuracy": "70-85%",
                    "use_cases": [
                        "Content creation",
                        "Product launches",
                        "Marketing campaigns",
                        "Investment decisions"
                    ]
                },
                "content_automation": {
                    "description": "Generate 50+ content variations from 1 brief",
                    "capabilities": [
                        "Text variations (10+)",
                        "Image variations (10+)",
                        "Video variations (5+)",
                        "Captions by platform",
                        "Hashtag generation",
                        "A/B testing setup",
                        "Scheduling"
                    ],
                    "time_savings": "40 hours → 30 minutes",
                    "platforms": [
                        "Instagram",
                        "TikTok",
                        "YouTube",
                        "Twitter",
                        "LinkedIn",
                        "Facebook",
                        "Pinterest",
                        "Threads"
                    ]
                },
                "code_architect": {
                    "description": "Generate production-ready code + tests + docs",
                    "capabilities": [
                        "Architecture generation",
                        "Code generation",
                        "Test generation",
                        "Documentation",
                        "Deployment config",
                        "Security scanning",
                        "Performance optimization"
                    ],
                    "supported_stacks": [
                        "React + FastAPI + PostgreSQL",
                        "Vue + Django + MySQL",
                        "Angular + Node.js + MongoDB",
                        "Next.js + Supabase",
                        "Flutter + Firebase"
                    ],
                    "development_time": "3 months → 2 weeks"
                },
                "revenue_engine": {
                    "description": "Marketplace for monetizing content/data/services",
                    "features": [
                        "Marketplace listings",
                        "Automated payments",
                        "Revenue sharing (80/20)",
                        "Analytics",
                        "Affiliate program",
                        "Subscription builder",
                        "Blockchain integration"
                    ],
                    "potential_gmv": "$100M+ annually"
                }
            }
        )
        
        # 4. SECURITY
        self._add_domain_knowledge(
            DomainArea.SECURITY,
            {
                "anti_hacking": {
                    "techniques": [
                        "Rate limiting",
                        "Token validation",
                        "IP anomaly detection",
                        "User-agent verification",
                        "SQL injection detection",
                        "XSS prevention",
                        "Session hijacking prevention"
                    ],
                    "protections": [
                        "Secure tokens",
                        "Device fingerprinting",
                        "Behavior analysis",
                        "Intrusion detection"
                    ]
                },
                "anti_copy": {
                    "techniques": [
                        "Digital watermarking",
                        "Fingerprinting",
                        "Copy detection",
                        "Screenshot prevention",
                        "DRM integration"
                    ],
                    "effectiveness": "95%+ detection rate"
                },
                "antivirus": {
                    "techniques": [
                        "File scanning",
                        "Signature matching",
                        "Behavior analysis",
                        "Quarantine system",
                        "Threat database"
                    ],
                    "coverage": "1M+ threat signatures"
                },
                "anti_spam": {
                    "techniques": [
                        "Pattern matching",
                        "URL analysis",
                        "Sentiment analysis",
                        "Frequency analysis",
                        "ML-based detection"
                    ],
                    "accuracy": "98%+ precision"
                },
                "anti_cloning": {
                    "techniques": [
                        "Hash-based detection",
                        "Content registry",
                        "Similarity analysis",
                        "Blockchain verification"
                    ],
                    "detection_rate": "99%+ accuracy"
                },
                "drm_licensing": {
                    "models": [
                        "Perpetual license",
                        "Subscription",
                        "Trial",
                        "Rental"
                    ],
                    "enforcement": [
                        "License key validation",
                        "Device activation",
                        "Expiration checking",
                        "Revocation capability"
                    ]
                }
            }
        )
        
        # 5. OFFLINE FEATURES
        self._add_domain_knowledge(
            DomainArea.OFFLINE_FEATURES,
            {
                "sync_engine": {
                    "capabilities": [
                        "Local-first storage",
                        "Automatic sync when online",
                        "Conflict resolution",
                        "Backup & restore",
                        "Version history",
                        "Offline-first architecture"
                    ],
                    "sync_frequency": "Every 30 seconds when online",
                    "conflict_strategy": "Last-Write-Wins (LWW)"
                },
                "context_persistence": {
                    "features": [
                        "Context bridge between models",
                        "Session snapshots",
                        "Memory compression",
                        "Automatic recovery",
                        "Context prioritization",
                        "Multi-session management"
                    ],
                    "memory_efficiency": "95% compression without loss"
                },
                "enterprise_rag": {
                    "capabilities": [
                        "Semantic indexing (FAISS)",
                        "Hybrid search (BM25 + embedding)",
                        "Document intelligence",
                        "Access control",
                        "Audit trails",
                        "Version control",
                        "Context compression",
                        "Re-ranking"
                    ],
                    "search_accuracy": "92%+ relevant results"
                },
                "autonomous_agents": {
                    "capabilities": [
                        "ReAct planning",
                        "Persistent memory",
                        "Tool discovery",
                        "Safe execution",
                        "Error recovery",
                        "Multi-agent orchestration",
                        "Learning loops",
                        "Debugging"
                    ],
                    "autonomy_level": "Level 3-4 (high autonomy)"
                },
                "performance_engine": {
                    "optimizations": [
                        "Dynamic scaling",
                        "Intelligent compression",
                        "Caching strategy",
                        "Real-time monitoring",
                        "Predictive optimization",
                        "Batch processing",
                        "Fallback mechanisms"
                    ],
                    "latency_reduction": "60-80% vs cloud"
                }
            }
        )
        
        # 6. TECHNICAL
        self._add_domain_knowledge(
            DomainArea.TECHNICAL,
            {
                "architecture": {
                    "frontend": "React + TailwindCSS (Web) + React Native (Mobile)",
                    "backend": "FastAPI (Python) + C bindings for performance",
                    "database": "SQLite (local) + PostgreSQL (optional cloud)",
                    "ai_runtime": "Ollama + llama.cpp for local inference",
                    "storage": "S3 compatible (optional) + local filesystem",
                    "deployment": "Docker + Docker Compose for easy setup"
                },
                "models": {
                    "text": ["DeepSeek-R1 7B", "Qwen2 7B", "Llama2 7B", "Mistral 7B"],
                    "image": ["Stable Diffusion XL", "SDXL-Turbo"],
                    "video": ["ModelScope", "Stable Video Diffusion"],
                    "audio": ["Whisper (speech-to-text)", "Piper (text-to-speech)"],
                    "embedding": ["BAAI/bge-small-en-v1.5"],
                    "reranker": ["jina-reranker-v1-base-en"]
                },
                "performance_specs": {
                    "gpu_requirement": "6GB VRAM minimum",
                    "ram_requirement": "40GB recommended",
                    "storage": "100GB+ for models",
                    "cpu": "8+ cores recommended",
                    "latency": "50-200ms per query",
                    "throughput": "100+ queries/second"
                },
                "integrations": {
                    "social_media": [
                        "Instagram",
                        "TikTok",
                        "YouTube",
                        "Twitter/X",
                        "LinkedIn",
                        "Facebook",
                        "Pinterest",
                        "Threads"
                    ],
                    "payment": ["Stripe", "PayPal", "Crypto"],
                    "storage": ["AWS S3", "Google Cloud Storage", "Azure Blob"],
                    "analytics": ["Mixpanel", "Amplitude", "Segment"],
                    "communication": ["Slack", "Discord", "Telegram"]
                }
            }
        )
        
        # 7. COMPLIANCE
        self._add_domain_knowledge(
            DomainArea.COMPLIANCE,
            {
                "regulations": {
                    "gdpr": {
                        "scope": "EU + global",
                        "requirements": [
                            "Data minimization",
                            "Purpose limitation",
                            "Storage limitation",
                            "Integrity & confidentiality",
                            "Accountability",
                            "Right to be forgotten"
                        ],
                        "penalties": "Up to €20M or 4% revenue"
                    },
                    "hipaa": {
                        "scope": "USA healthcare",
                        "requirements": [
                            "PHI encryption",
                            "Access controls",
                            "Audit logs",
                            "Breach notification",
                            "Business associate agreements"
                        ],
                        "penalties": "Up to $1.5M per violation"
                    },
                    "pci_dss": {
                        "scope": "Payment processing",
                        "requirements": [
                            "Network security",
                            "Data protection",
                            "Vulnerability management",
                            "Access control",
                            "Testing & monitoring"
                        ],
                        "levels": "1-4 based on transaction volume"
                    },
                    "nist": {
                        "scope": "USA government",
                        "framework": [
                            "Identify",
                            "Protect",
                            "Detect",
                            "Respond",
                            "Recover"
                        ]
                    },
                    "fedramp": {
                        "scope": "USA federal systems",
                        "levels": ["Low", "Moderate", "High"],
                        "requirements": "NIST 800-53 controls"
                    }
                },
                "certifications": {
                    "iso_27001": "Information Security Management",
                    "soc_2_type_2": "Security, Availability, Processing Integrity",
                    "hitrust": "Healthcare-specific security",
                    "common_criteria": "Military-grade security",
                    "fips_140_2": "Cryptographic module validation"
                }
            }
        )
        
        # 8. MARKET ANALYSIS
        self._add_domain_knowledge(
            DomainArea.MARKET_ANALYSIS,
            {
                "tam": {
                    "enterprise": "$500B+ (governments, banking, healthcare, energy, defense)",
                    "creators": "$50B+ (content creation tools)",
                    "total": "$550B+ addressable market"
                },
                "competitors": {
                    "online_ai": ["OpenAI ChatGPT", "Anthropic Claude", "Google Gemini"],
                    "offline_ai": ["Ollama", "LM Studio", "GPT4All", "LocalAI", "LLaMA.cpp"],
                    "content_tools": ["Adobe", "Canva", "Descript", "Runway"],
                    "our_advantage": "Only 100% offline + enterprise + creators"
                },
                "market_trends": [
                    "Shift to privacy-first solutions",
                    "Demand for offline capability",
                    "Regulatory compliance increasing",
                    "Creator economy growing",
                    "Remote work expansion",
                    "Edge AI adoption"
                ],
                "revenue_potential": {
                    "year_1": "$6M",
                    "year_2": "$60M",
                    "year_3": "$300M+",
                    "year_5": "$1B+"
                }
            }
        )
        
        logger.info("✅ Knowledge Base inicializado con 8 áreas de dominio")
    
    # ========================================================================
    # AGREGAR Y RECUPERAR CONOCIMIENTO
    # ========================================================================
    
    def _add_domain_knowledge(self, domain: DomainArea, knowledge: Dict[str, Any]):
        """Agregar conocimiento a un dominio"""
        self.domain_expertise[domain.value] = knowledge
    
    def get_domain_knowledge(self, domain: DomainArea) -> Dict[str, Any]:
        """Obtener conocimiento de un dominio"""
        return self.domain_expertise.get(domain.value, {})
    
    async def learn_from_interaction(
        self,
        user_query: str,
        ai_response: str,
        domain: DomainArea,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Aprender de interacciones del usuario"""
        
        try:
            learning = {
                "id": str(uuid.uuid4())[:8],
                "query": user_query,
                "response": ai_response,
                "domain": domain.value,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat(),
                "quality_score": self._calculate_quality_score(feedback)
            }
            
            self.learned_patterns.append(learning)
            self.training_history.append(learning)
            
            logger.info(f"✅ Patrón aprendido: {domain.value}")
            
            return learning
        
        except Exception as e:
            logger.error(f"Error aprendiendo: {e}")
            raise
    
    def _calculate_quality_score(self, feedback: Optional[str]) -> float:
        """Calcular puntuación de calidad basada en feedback"""
        
        if not feedback:
            return 0.5
        
        positive_words = ["good", "great", "excellent", "perfect", "helpful", "accurate"]
        negative_words = ["bad", "poor", "wrong", "incorrect", "unhelpful"]
        
        feedback_lower = feedback.lower()
        
        positive_count = sum(1 for word in positive_words if word in feedback_lower)
        negative_count = sum(1 for word in negative_words if word in feedback_lower)
        
        score = 0.5 + (positive_count * 0.1) - (negative_count * 0.1)
        return min(1.0, max(0.0, score))
    
    # ========================================================================
    # ESPECIALIZACIÓN DE AGENTES
    # ========================================================================
    
    async def create_specialized_agent(
        self,
        domain: DomainArea,
        agent_name: str
    ) -> Dict[str, Any]:
        """Crear agente especializado en un dominio"""
        
        try:
            domain_knowledge = self.get_domain_knowledge(domain)
            
            agent = {
                "id": str(uuid.uuid4())[:8],
                "name": agent_name,
                "domain": domain.value,
                "knowledge": domain_knowledge,
                "expertise_level": "Expert",
                "capabilities": self._get_agent_capabilities(domain),
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Agente especializado creado: {agent_name} ({domain.value})")
            
            return agent
        
        except Exception as e:
            logger.error(f"Error creando agente: {e}")
            raise
    
    def _get_agent_capabilities(self, domain: DomainArea) -> List[str]:
        """Obtener capacidades de agente según dominio"""
        
        capabilities_map = {
            DomainArea.ENTERPRISE_SALES: [
                "Identify target customers",
                "Create sales proposals",
                "Handle objections",
                "Negotiate terms",
                "Manage compliance requirements"
            ],
            DomainArea.CREATOR_MONETIZATION: [
                "Generate content ideas",
                "Create content variations",
                "Optimize for platforms",
                "Predict trends",
                "Manage monetization"
            ],
            DomainArea.AI_CAPABILITIES: [
                "Generate text",
                "Generate images",
                "Analyze data",
                "Predict trends",
                "Generate code"
            ],
            DomainArea.SECURITY: [
                "Detect threats",
                "Prevent attacks",
                "Manage licenses",
                "Audit access",
                "Respond to incidents"
            ],
            DomainArea.OFFLINE_FEATURES: [
                "Manage local storage",
                "Synchronize data",
                "Resolve conflicts",
                "Optimize performance",
                "Handle offline scenarios"
            ],
            DomainArea.TECHNICAL: [
                "Design architecture",
                "Generate code",
                "Optimize performance",
                "Manage deployments",
                "Handle integrations"
            ],
            DomainArea.COMPLIANCE: [
                "Verify compliance",
                "Generate reports",
                "Manage certifications",
                "Handle audits",
                "Ensure data protection"
            ],
            DomainArea.MARKET_ANALYSIS: [
                "Analyze market trends",
                "Identify opportunities",
                "Assess competitors",
                "Project revenue",
                "Guide strategy"
            ]
        }
        
        return capabilities_map.get(domain, [])
    
    # ========================================================================
    # CONSULTA DE CONOCIMIENTO
    # ========================================================================
    
    async def query_knowledge(
        self,
        query: str,
        domains: Optional[List[DomainArea]] = None
    ) -> Dict[str, Any]:
        """Consultar la base de conocimiento"""
        
        try:
            if not domains:
                domains = list(DomainArea)
            
            results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "results": {}
            }
            
            for domain in domains:
                domain_knowledge = self.get_domain_knowledge(domain)
                
                # Buscar en conocimiento del dominio
                relevant_info = self._search_in_knowledge(query, domain_knowledge)
                
                if relevant_info:
                    results["results"][domain.value] = relevant_info
            
            return results
        
        except Exception as e:
            logger.error(f"Error consultando conocimiento: {e}")
            raise
    
    def _search_in_knowledge(self, query: str, knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Buscar información relevante en conocimiento"""
        
        query_lower = query.lower()
        relevant = {}
        
        def search_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if query_lower in key.lower():
                        relevant[new_path] = value
                    else:
                        search_recursive(value, new_path)
            elif isinstance(obj, list):
                for item in obj:
                    if isinstance(item, str) and query_lower in item.lower():
                        relevant[path] = obj
                    else:
                        search_recursive(item, path)
        
        search_recursive(knowledge)
        return relevant
    
    # ========================================================================
    # EXPORTAR E IMPORTAR CONOCIMIENTO
    # ========================================================================
    
    async def export_knowledge(self) -> str:
        """Exportar toda la base de conocimiento"""
        
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "domains": self.domain_expertise,
                "learned_patterns": self.learned_patterns,
                "training_history": self.training_history
            }
            
            export_path = self.kb_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"✅ Conocimiento exportado: {export_path}")
            
            return str(export_path)
        
        except Exception as e:
            logger.error(f"Error exportando: {e}")
            raise
    
    async def import_knowledge(self, import_path: str) -> bool:
        """Importar base de conocimiento"""
        
        try:
            import_path = Path(import_path)
            
            if not import_path.exists():
                logger.error(f"Archivo no encontrado: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            self.domain_expertise.update(import_data.get("domains", {}))
            self.learned_patterns.extend(import_data.get("learned_patterns", []))
            self.training_history.extend(import_data.get("training_history", []))
            
            logger.info(f"✅ Conocimiento importado: {import_path}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error importando: {e}")
            return False
    
    # ========================================================================
    # ESTADÍSTICAS Y ANÁLISIS
    # ========================================================================
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de conocimiento"""
        
        try:
            total_domains = len(self.domain_expertise)
            total_patterns = len(self.learned_patterns)
            total_training = len(self.training_history)
            
            avg_quality = (
                sum(p.get("quality_score", 0) for p in self.learned_patterns) / total_patterns
                if total_patterns > 0
                else 0
            )
            
            return {
                "total_domains": total_domains,
                "domains": list(self.domain_expertise.keys()),
                "total_learned_patterns": total_patterns,
                "total_training_interactions": total_training,
                "average_quality_score": avg_quality,
                "last_update": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            raise
    
    async def get_domain_expertise_level(self, domain: DomainArea) -> Dict[str, Any]:
        """Obtener nivel de expertise en un dominio"""
        
        try:
            domain_knowledge = self.get_domain_knowledge(domain)
            domain_patterns = [p for p in self.learned_patterns if p["domain"] == domain.value]
            
            expertise_level = "Beginner"
            if len(domain_patterns) > 50:
                expertise_level = "Expert"
            elif len(domain_patterns) > 20:
                expertise_level = "Advanced"
            elif len(domain_patterns) > 5:
                expertise_level = "Intermediate"
            
            avg_quality = (
                sum(p.get("quality_score", 0) for p in domain_patterns) / len(domain_patterns)
                if domain_patterns
                else 0
            )
            
            return {
                "domain": domain.value,
                "expertise_level": expertise_level,
                "knowledge_areas": len(domain_knowledge),
                "learned_patterns": len(domain_patterns),
                "average_quality": avg_quality,
                "ready_for_production": expertise_level in ["Advanced", "Expert"]
            }
        
        except Exception as e:
            logger.error(f"Error obteniendo expertise: {e}")
            raise
