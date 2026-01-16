"""
Intelligent Description Analyzer
Parses complex project descriptions and extracts structured requirements
"""
import logging
import re
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ProjectAnalysis:
    """Structured analysis of a project description"""
    project_type: str
    core_features: List[str]
    technical_requirements: List[str]
    recommended_stack: Dict[str, str]
    architecture_patterns: List[str]
    scalability_requirements: List[str]
    integration_points: List[str]
    security_requirements: List[str]
    database_type: str
    deployment_strategy: str
    estimated_complexity: str  # low, medium, high, enterprise
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DescriptionAnalyzer:
    """
    AI-powered analyzer for complex project descriptions
    Extracts structured requirements from natural language
    """
    
    def __init__(self, llm_inference=None):
        self.llm = llm_inference
        
        # Keyword patterns for feature detection
        self.feature_patterns = {
            "authentication": r"\b(auth|login|signup|user management|oauth|sso|jwt)\b",
            "payment": r"\b(payment|checkout|stripe|paypal|transaction|billing)\b",
            "analytics": r"\b(analytics|metrics|tracking|insights|reporting|dashboard)\b",
            "search": r"\b(search|elasticsearch|algolia|full-text)\b",
            "api": r"\b(api|rest|graphql|endpoint|webhook)\b",
            "real-time": r"\b(real-time|websocket|live|streaming|notification)\b",
            "multi-tenant": r"\b(multi-tenant|tenant|organization|workspace)\b",
            "e-commerce": r"\b(e-commerce|ecommerce|commerce|store|shop|catalog|cart|order)\b",
            "cms": r"\b(cms|content management|blog|article|page builder)\b",
            "ai": r"\b(ai|machine learning|ml|artificial intelligence|recommendation|personalization)\b",
            "automation": r"\b(automation|workflow|pipeline|ci/cd|devops)\b",
            "internationalization": r"\b(i18n|internationalization|multi-language|translation|locale)\b",
            "mobile": r"\b(mobile|ios|android|react native|flutter)\b",
        }
        
        # Technology stack patterns
        self.tech_patterns = {
            "python": r"\b(python|django|flask|fastapi)\b",
            "javascript": r"\b(javascript|node|react|vue|angular|next\.js)\b",
            "java": r"\b(java|spring|springboot)\b",
            "dotnet": r"\b(\.net|c#|asp\.net)\b",
            "go": r"\b(golang|go)\b",
            "rust": r"\b(rust)\b",
        }
        
        # Database patterns
        self.db_patterns = {
            "postgresql": r"\b(postgres|postgresql)\b",
            "mongodb": r"\b(mongo|mongodb|nosql)\b",
            "mysql": r"\b(mysql|mariadb)\b",
            "redis": r"\b(redis|cache)\b",
            "elasticsearch": r"\b(elasticsearch|elastic)\b",
        }
        
        # Architecture patterns
        self.architecture_patterns_map = {
            "microservices": r"\b(microservice|micro-service|service-oriented)\b",
            "serverless": r"\b(serverless|lambda|function-as-a-service)\b",
            "event-driven": r"\b(event-driven|event sourcing|cqrs|message queue)\b",
            "api-first": r"\b(api-first|headless|decoupled)\b",
            "monolith": r"\b(monolith|monolithic)\b",
        }
    
    async def analyze(self, description: str, context: Dict[str, Any] = None) -> ProjectAnalysis:
        """
        Analyze a project description and extract structured requirements
        
        Args:
            description: Natural language project description
            context: Additional context (languages, frameworks, etc.)
        
        Returns:
            ProjectAnalysis with extracted requirements
        """
        context = context or {}
        description_lower = description.lower()
        
        logger.info(f"Analyzing project description ({len(description)} chars)")
        
        # 1. Detect project type
        project_type = self._detect_project_type(description_lower)
        
        # 2. Extract core features
        core_features = self._extract_features(description_lower)
        
        # 3. Detect technical requirements
        technical_requirements = self._extract_technical_requirements(description)
        
        # 4. Recommend technology stack
        recommended_stack = await self._recommend_stack(
            description, 
            project_type, 
            core_features,
            context
        )
        
        # 5. Identify architecture patterns
        architecture_patterns = self._detect_architecture_patterns(description_lower)
        
        # 6. Extract scalability requirements
        scalability_requirements = self._extract_scalability_requirements(description)
        
        # 7. Identify integration points
        integration_points = self._extract_integration_points(description)
        
        # 8. Detect security requirements
        security_requirements = self._extract_security_requirements(description)
        
        # 9. Recommend database
        database_type = self._recommend_database(description_lower, core_features)
        
        # 10. Determine deployment strategy
        deployment_strategy = self._determine_deployment_strategy(description_lower)
        
        # 11. Estimate complexity
        complexity = self._estimate_complexity(
            core_features,
            scalability_requirements,
            integration_points
        )
        
        analysis = ProjectAnalysis(
            project_type=project_type,
            core_features=core_features,
            technical_requirements=technical_requirements,
            recommended_stack=recommended_stack,
            architecture_patterns=architecture_patterns,
            scalability_requirements=scalability_requirements,
            integration_points=integration_points,
            security_requirements=security_requirements,
            database_type=database_type,
            deployment_strategy=deployment_strategy,
            estimated_complexity=complexity
        )
        
        logger.info(f"Analysis complete: {project_type} project with {len(core_features)} features")
        return analysis
    
    def _detect_project_type(self, description: str) -> str:
        """Detect the primary project type"""
        type_scores = {
            "e-commerce": 0,
            "saas": 0,
            "cms": 0,
            "api": 0,
            "mobile": 0,
            "analytics": 0,
            "social": 0,
            "fintech": 0,
        }
        
        # E-commerce indicators
        if re.search(r"\b(e-commerce|ecommerce|store|shop|cart|checkout|product|catalog)\b", description):
            type_scores["e-commerce"] += 3
        if re.search(r"\b(payment|order|inventory|shipping)\b", description):
            type_scores["e-commerce"] += 2
        
        # SaaS indicators
        if re.search(r"\b(saas|platform|service|subscription|tenant)\b", description):
            type_scores["saas"] += 3
        if re.search(r"\b(multi-tenant|workspace|organization)\b", description):
            type_scores["saas"] += 2
        
        # CMS indicators
        if re.search(r"\b(cms|content|blog|article|page|editor)\b", description):
            type_scores["cms"] += 3
        
        # API/Backend indicators
        if re.search(r"\b(api|backend|microservice|rest|graphql)\b", description):
            type_scores["api"] += 2
        
        # Mobile indicators
        if re.search(r"\b(mobile|ios|android|app)\b", description):
            type_scores["mobile"] += 3
        
        # Analytics indicators
        if re.search(r"\b(analytics|metrics|dashboard|reporting|insights)\b", description):
            type_scores["analytics"] += 2
        
        # Social indicators
        if re.search(r"\b(social|feed|post|comment|like|follow)\b", description):
            type_scores["social"] += 3
        
        # Fintech indicators
        if re.search(r"\b(fintech|banking|finance|trading|investment|wallet)\b", description):
            type_scores["fintech"] += 3
        
        # Return highest scoring type
        max_type = max(type_scores.items(), key=lambda x: x[1])
        return max_type[0] if max_type[1] > 0 else "web-application"
    
    def _extract_features(self, description: str) -> List[str]:
        """Extract core features from description"""
        features = []
        
        for feature, pattern in self.feature_patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                features.append(feature)
        
        return features
    
    def _extract_technical_requirements(self, description: str) -> List[str]:
        """Extract technical requirements"""
        requirements = []
        
        # High traffic
        if re.search(r"\b(high traffic|high volume|scale|scalable|millions of users)\b", description, re.IGNORECASE):
            requirements.append("high-traffic-support")
        
        # Real-time
        if re.search(r"\b(real-time|live|instant|websocket)\b", description, re.IGNORECASE):
            requirements.append("real-time-capabilities")
        
        # Global
        if re.search(r"\b(global|worldwide|international|multi-region)\b", description, re.IGNORECASE):
            requirements.append("global-deployment")
        
        # Performance
        if re.search(r"\b(performance|fast|speed|optimize|low latency)\b", description, re.IGNORECASE):
            requirements.append("high-performance")
        
        # Reliability
        if re.search(r"\b(reliable|uptime|availability|fault-tolerant|resilient)\b", description, re.IGNORECASE):
            requirements.append("high-availability")
        
        return requirements
    
    async def _recommend_stack(
        self, 
        description: str, 
        project_type: str,
        features: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Recommend technology stack based on analysis"""
        
        # Check if user specified languages
        user_languages = context.get("languages", [])
        if user_languages:
            # User specified, respect their choice
            backend = user_languages[0] if len(user_languages) > 0 else "python"
            frontend = user_languages[1] if len(user_languages) > 1 else "react"
        else:
            # Auto-recommend based on project type
            if project_type == "e-commerce":
                backend = "python"  # FastAPI for high performance
                frontend = "nextjs"  # Next.js for SEO
            elif project_type == "saas":
                backend = "python"  # FastAPI or Django
                frontend = "react"
            elif project_type == "api":
                backend = "python"  # FastAPI
                frontend = "none"
            elif project_type == "mobile":
                backend = "python"
                frontend = "flutter"
            else:
                backend = "python"
                frontend = "react"
        
        # Database recommendation
        if "e-commerce" in features or project_type == "e-commerce":
            database = "postgresql"  # Relational for transactions
            cache = "redis"
        elif "analytics" in features:
            database = "postgresql"
            cache = "redis"
            search = "elasticsearch"
        else:
            database = "postgresql"
            cache = "redis"
        
        stack = {
            "backend": backend,
            "frontend": frontend,
            "database": database,
            "cache": cache,
        }
        
        # Add search if needed
        if "search" in features:
            stack["search"] = "elasticsearch"
        
        # Add message queue for scalability
        if "high-traffic-support" in self._extract_technical_requirements(description):
            stack["message_queue"] = "rabbitmq"
        
        return stack
    
    def _detect_architecture_patterns(self, description: str) -> List[str]:
        """Detect recommended architecture patterns"""
        patterns = []
        
        for pattern, regex in self.architecture_patterns_map.items():
            if re.search(regex, description, re.IGNORECASE):
                patterns.append(pattern)
        
        # Default recommendations based on keywords
        if not patterns:
            if re.search(r"\b(scale|scalable|distributed)\b", description):
                patterns.append("microservices")
            if re.search(r"\b(api|headless|decoupled)\b", description):
                patterns.append("api-first")
        
        return patterns if patterns else ["monolith"]  # Default to monolith for simplicity
    
    def _extract_scalability_requirements(self, description: str) -> List[str]:
        """Extract scalability requirements"""
        requirements = []
        
        patterns = {
            "horizontal-scaling": r"\b(horizontal scal|scale out|distributed|cluster)\b",
            "load-balancing": r"\b(load balanc|traffic distribution)\b",
            "caching": r"\b(cache|caching|redis|memcached)\b",
            "cdn": r"\b(cdn|content delivery|cloudflare)\b",
            "auto-scaling": r"\b(auto-scal|elastic|dynamic scaling)\b",
        }
        
        for req, pattern in patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                requirements.append(req)
        
        return requirements
    
    def _extract_integration_points(self, description: str) -> List[str]:
        """Extract external integration requirements"""
        integrations = []
        
        integration_patterns = {
            "payment-gateway": r"\b(stripe|paypal|payment gateway|checkout)\b",
            "email-service": r"\b(email|sendgrid|mailgun|ses)\b",
            "sms-service": r"\b(sms|twilio|text message)\b",
            "erp": r"\b(erp|enterprise resource)\b",
            "crm": r"\b(crm|salesforce|customer relationship)\b",
            "logistics": r"\b(shipping|logistics|fedex|ups|dhl)\b",
            "analytics": r"\b(google analytics|mixpanel|segment)\b",
            "social-media": r"\b(facebook|twitter|instagram|social media)\b",
        }
        
        for integration, pattern in integration_patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                integrations.append(integration)
        
        return integrations
    
    def _extract_security_requirements(self, description: str) -> List[str]:
        """Extract security requirements"""
        security = []
        
        security_patterns = {
            "authentication": r"\b(auth|authentication|login|oauth|sso)\b",
            "authorization": r"\b(authorization|rbac|permissions|access control)\b",
            "encryption": r"\b(encrypt|ssl|tls|https)\b",
            "pci-compliance": r"\b(pci|payment card|card data)\b",
            "gdpr": r"\b(gdpr|privacy|data protection)\b",
            "audit-logging": r"\b(audit|logging|compliance|trail)\b",
            "rate-limiting": r"\b(rate limit|throttle|ddos)\b",
        }
        
        for req, pattern in security_patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                security.append(req)
        
        # Default security requirements
        if not security:
            security = ["authentication", "authorization", "encryption"]
        
        return security
    
    def _recommend_database(self, description: str, features: List[str]) -> str:
        """Recommend database type"""
        
        # Check for explicit mentions
        for db, pattern in self.db_patterns.items():
            if re.search(pattern, description):
                return db
        
        # Recommend based on features
        if "e-commerce" in features or "payment" in features:
            return "postgresql"  # ACID compliance for transactions
        elif "analytics" in features:
            return "postgresql"  # Good for analytics
        elif "real-time" in features:
            return "mongodb"  # Fast writes
        else:
            return "postgresql"  # Default
    
    def _determine_deployment_strategy(self, description: str) -> str:
        """Determine deployment strategy"""
        
        if re.search(r"\b(kubernetes|k8s|container orchestration)\b", description):
            return "kubernetes"
        elif re.search(r"\b(docker|container)\b", description):
            return "docker-compose"
        elif re.search(r"\b(serverless|lambda)\b", description):
            return "serverless"
        elif re.search(r"\b(cloud|aws|azure|gcp)\b", description):
            return "cloud-native"
        else:
            return "docker-compose"  # Default
    
    def _estimate_complexity(
        self,
        features: List[str],
        scalability_reqs: List[str],
        integrations: List[str]
    ) -> str:
        """Estimate project complexity"""
        
        score = 0
        score += len(features) * 2
        score += len(scalability_reqs) * 3
        score += len(integrations) * 2
        
        if score < 10:
            return "low"
        elif score < 20:
            return "medium"
        elif score < 35:
            return "high"
        else:
            return "enterprise"
    
    async def build_generation_config(
        self, 
        analysis: ProjectAnalysis, 
        project_name: str,
        description: str,
        language_registry=None
    ) -> Dict[str, Any]:
        """
        Build complete generation configuration with latest framework versions from registry
        
        Args:
            analysis: ProjectAnalysis from analyze()
            project_name: Name of the project
            description: Original description
            language_registry: LanguageRegistry instance for version lookup
        
        Returns:
            Complete generation config ready for /api/generate
        """
        logger.info("🔧 Building generation config with latest framework versions from registry")
        
        # Get backend language and frontend tech
        backend_lang = analysis.recommended_stack.get("backend", "python")
        frontend_tech = analysis.recommended_stack.get("frontend", "react")
        
        # Initialize framework info
        backend_framework = None
        backend_version = None
        frontend_framework = None
        frontend_version = None
        
        # Get latest versions from registry
        if language_registry:
            # Backend framework version
            backend_config = language_registry.get_language_config(backend_lang)
            if backend_config:
                frameworks = backend_config.get("frameworks", [])
                
                # Map backend language to framework
                if backend_lang == "python":
                    # Prefer FastAPI for APIs, Django for full-stack
                    if "api" in analysis.architecture_patterns or analysis.project_type == "api":
                        backend_framework = next((f for f in frameworks if f["name"] == "FastAPI"), None)
                    else:
                        backend_framework = next((f for f in frameworks if f["name"] == "Django"), None)
                        if not backend_framework:
                            backend_framework = next((f for f in frameworks if f["name"] == "FastAPI"), None)
                elif backend_lang == "java":
                    backend_framework = next((f for f in frameworks if "Spring" in f["name"]), None)
                elif backend_lang == "dotnet":
                    backend_framework = next((f for f in frameworks if "ASP.NET" in f["name"]), None)
                
                if backend_framework:
                    backend_version = backend_framework.get("version")
                    logger.info(f"✓ Selected {backend_framework['name']} v{backend_version}")
            
            # Frontend framework version
            if frontend_tech != "none":
                frontend_config = language_registry.get_language_config("javascript")
                if frontend_config:
                    frameworks = frontend_config.get("frameworks", [])
                    
                    # Map frontend tech to framework
                    if frontend_tech == "react":
                        frontend_framework = next((f for f in frameworks if f["name"] == "React"), None)
                    elif frontend_tech == "nextjs":
                        frontend_framework = next((f for f in frameworks if f["name"] == "Next.js"), None)
                    elif frontend_tech == "vue":
                        frontend_framework = next((f for f in frameworks if f["name"] == "Vue.js"), None)
                    elif frontend_tech == "angular":
                        frontend_framework = next((f for f in frameworks if f["name"] == "Angular"), None)
                    
                    if frontend_framework:
                        frontend_version = frontend_framework.get("version")
                        logger.info(f"✓ Selected {frontend_framework['name']} v{frontend_version}")
        
        # Build complete config
        config = {
            "project_name": project_name,
            "description": description,
            "project_type": analysis.project_type,
            
            # Languages with versions from registry
            "languages": [
                {
                    "name": backend_lang,
                    "framework": backend_framework["name"] if backend_framework else "FastAPI",
                    "version": backend_version or "latest"
                }
            ],
            
            # Frontend configuration
            "frontend": None,
            
            # Database configuration
            "database": {
                "type": analysis.database_type,
                "generate_from_schema": False,
                "include_migrations": True,
                "include_seeders": True
            },
            
            # Security configuration (auto-configured from analysis)
            "security": {
                "enable_authentication": "authentication" in analysis.security_requirements,
                "enable_authorization": "authorization" in analysis.security_requirements,
                "enable_encryption": "encryption" in analysis.security_requirements,
                "enable_rate_limiting": "rate-limiting" in analysis.security_requirements,
                "enable_cors": True,
                "pci_compliance": "pci-compliance" in analysis.security_requirements,
                "gdpr_compliance": "gdpr" in analysis.security_requirements
            },
            
            # Features (auto-detected)
            "features": analysis.core_features,
            
            # Architecture (auto-configured)
            "architecture": {
                "patterns": analysis.architecture_patterns,
                "microservices": "microservices" in analysis.architecture_patterns,
                "api_first": "api-first" in analysis.architecture_patterns,
                "event_driven": "event-driven" in analysis.architecture_patterns
            },
            
            # Scalability (auto-configured)
            "scalability": {
                "requirements": analysis.scalability_requirements,
                "enable_caching": "caching" in analysis.scalability_requirements,
                "enable_load_balancing": "load-balancing" in analysis.scalability_requirements,
                "enable_cdn": "cdn" in analysis.scalability_requirements,
                "enable_auto_scaling": "auto-scaling" in analysis.scalability_requirements
            },
            
            # Integrations (auto-detected)
            "integrations": {
                "required": analysis.integration_points,
                "payment_gateway": "payment-gateway" in analysis.integration_points,
                "email_service": "email-service" in analysis.integration_points,
                "sms_service": "sms-service" in analysis.integration_points,
                "analytics": "analytics" in analysis.integration_points
            },
            
            # Deployment (auto-configured)
            "deployment": {
                "strategy": analysis.deployment_strategy,
                "generate_dockerfile": True,
                "generate_docker_compose": True,
                "generate_kubernetes": analysis.deployment_strategy == "kubernetes",
                "generate_ci_cd": True
            },
            
            # Additional stack components
            "stack_components": {
                "cache": analysis.recommended_stack.get("cache", "redis"),
                "message_queue": analysis.recommended_stack.get("message_queue"),
                "search_engine": analysis.recommended_stack.get("search")
            },
            
            # Complexity and requirements
            "estimated_complexity": analysis.estimated_complexity,
            "technical_requirements": analysis.technical_requirements
        }
        
        # Add frontend if not "none"
        if frontend_tech != "none":
            config["frontend"] = {
                "framework": frontend_framework["name"] if frontend_framework else frontend_tech,
                "version": frontend_version or "latest",
                "ssr": frontend_tech == "nextjs",
                "typescript": True
            }
            config["languages"].append({
                "name": "javascript",
                "framework": frontend_framework["name"] if frontend_framework else frontend_tech,
                "version": frontend_version or "latest"
            })
        
        logger.info(f"✅ Generation config built: {len(config['languages'])} languages, {len(config['features'])} features, {config['estimated_complexity']} complexity")
        return config
