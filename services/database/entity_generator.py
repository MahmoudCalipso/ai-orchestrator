"""
Entity code generator
"""
import logging
from typing import List, Dict, Optional, Any

from schemas.generation_spec import EntityDefinition

logger = logging.getLogger(__name__)

class EntityGenerator:
    """Generates code from entity definitions"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator # Type: Orchestrator
        
    async def generate_models(self, entities: List[EntityDefinition], language: str, framework: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate model code for entities with validations and relationships"""
        results = {}
        
        context = context or {}
        project_description = context.get("description", "Not provided")
        project_requirements = context.get("requirements", "Not provided")
        
        prompt_template = """
        Generate a {language} data model for the following entity definition.
        Framework: {framework}
        
        --- PROJECT CONTEXT ---
        Description: {project_description}
        Requirements: {project_requirements}
        -----------------------
        
        Entity Name: {name}
        Table Name: {table_name}
        
        Fields:
        {fields}
        
        Validations:
        {validations}
        
        Relationships:
        {relationships}
        
        Requirements:
        - Include all fields with correct types
        - Implement all validation rules
        - Include relationship mappings (OneToMany, ManyToOne, etc.)
        - Follow {language} best practices
        - Use standard ORM annotations if applicable
        - Include audit fields if specified (CreatedAt, UpdatedAt, etc.)
        """
        
        for entity in entities:
            fields_desc = "\n".join([
                f"- {f.name} ({f.type}{'(' + str(f.length) + ')' if f.length else ''}): "
                f"{f.description or ''} "
                f"{'(PK)' if f.primary_key else ''} "
                f"{'(FK: ' + f.foreign_key + ')' if f.foreign_key else ''} "
                f"{'(Unique)' if f.unique else ''} "
                f"{'(Nullable)' if f.nullable else 'Required'}"
                for f in entity.fields
            ])
            
            # Format validations
            validations_desc = []
            for field in entity.fields:
                if field.validations:
                    field_validations = ", ".join([f"{v.type}{'=' + str(v.value) if v.value else ''}" for v in field.validations])
                    validations_desc.append(f"- {field.name}: {field_validations}")
            validations_str = "\n".join(validations_desc) if validations_desc else "None"
            
            # Format relationships
            relationships_desc = []
            for rel in entity.relationships:
                rel_type = rel.get('type', 'Unknown')
                target = rel.get('target_entity', 'Unknown')
                fk = rel.get('foreign_key', rel.get('mapped_by', ''))
                relationships_desc.append(f"- {rel_type} -> {target} (via {fk})")
            relationships_str = "\n".join(relationships_desc) if relationships_desc else "None"
            
            prompt = prompt_template.format(
                language=language,
                framework=framework or "Standard",
                project_description=project_description,
                project_requirements=project_requirements,
                name=entity.name,
                table_name=entity.table_name,
                fields=fields_desc,
                validations=validations_str,
                relationships=relationships_str
            )
            
            # Use the universal agent to generate the code
            # Pass full context for enhanced prompt building
            full_context = {
                "project_name": context.get("project_name", ""),
                "description": context.get("description", ""),
                "security": context.get("security", {}),
                "database": context.get("database", {}),
                "kubernetes": context.get("kubernetes", {})
            }
            result = await self.orchestrator.universal_agent.generate_code(
                requirements=prompt,
                language=language,
                framework=framework,
                context_data=full_context
            )
            
            # Extract code from result
            code = result.get("solution", "")
            results[entity.name] = code
            
        return results

    async def generate_api(self, entities: List[EntityDefinition], language: str, framework: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate API endpoints for entities"""
        results = {}
        
        context = context or {}
        project_description = context.get("description", "Not provided")
        project_requirements = context.get("requirements", "Not provided")
        
        prompt_template = """
        Generate a REST API controller/handler for the {name} entity.
        Language: {language}
        Framework: {framework}
        
        --- PROJECT CONTEXT ---
        Description: {project_description}
        Requirements: {project_requirements}
        -----------------------
        
        Operations:
        - Create (POST)
        - Read One (GET)
        - Read All (GET) with pagination
        - Update (PUT/PATCH)
        - Delete (DELETE)
        
        Entity Fields for reference:
        {fields}
        
        Requirements:
        - Implement standard error handling
        - Use dependency injection for service/repository
        - Valid status codes
        """
        
        for entity in entities:
            fields_desc = ", ".join([f.name for f in entity.fields])
            
            prompt = prompt_template.format(
                name=entity.name,
                language=language,
                framework=framework,
                project_description=project_description,
                project_requirements=project_requirements,
                fields=fields_desc
            )
            
            result = await self.orchestrator.universal_agent.generate_code(
                requirements=prompt,
                language=language,
                framework=framework,
                context_data={
                    "project_name": context.get("project_name", ""),
                    "description": context.get("description", ""),
                    "security": context.get("security", {}),
                    "database": context.get("database", {}),
                    "kubernetes": context.get("kubernetes", {})
                }
            )
            
            results[f"{entity.name}Controller"] = result.get("solution", "")
            
        return results
    
    async def generate_dtos(self, entities: List[EntityDefinition], language: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate DTO (Data Transfer Object) classes"""
        results = {}
        
        context = context or {}
        project_description = context.get("description", "Not provided")
        project_requirements = context.get("requirements", "Not provided")
        
        prompt_template = """
        Generate DTO (Data Transfer Object) classes for the {name} entity.
        Language: {language}
        
        --- PROJECT CONTEXT ---
        Description: {project_description}
        Requirements: {project_requirements}
        -----------------------
        
        Create the following DTOs:
        1. Create{name}DTO - For creating new records (exclude ID, audit fields)
        2. Update{name}DTO - For updating records (exclude audit fields)
        3. {name}ResponseDTO - For API responses (include all fields)
        
        Entity Fields:
        {fields}
        
        Requirements:
        - Include validation annotations
        - Exclude auto-generated fields from Create/Update DTOs
        - Use appropriate data types
        """
        
        for entity in entities:
            fields_desc = "\n".join([f"{f.name} ({f.type})" for f in entity.fields])
            
            prompt = prompt_template.format(
                name=entity.name,
                language=language,
                project_description=project_description,
                project_requirements=project_requirements,
                fields=fields_desc
            )
            
            result = await self.orchestrator.universal_agent.generate_code(
                requirements=prompt,
                language=language,
                context_data={
                    "project_name": context.get("project_name", ""),
                    "description": context.get("description", ""),
                    "security": context.get("security", {}),
                    "database": context.get("database", {}),
                    "kubernetes": context.get("kubernetes", {})
                }
            )
            
            results[f"{entity.name}DTOs"] = result.get("solution", "")
        
        return results
    
    async def generate_repository(self, entities: List[EntityDefinition], language: str, framework: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Generate repository/data access layer"""
        results = {}
        
        context = context or {}
        project_description = context.get("description", "Not provided")
        project_requirements = context.get("requirements", "Not provided")
        
        prompt_template = """
        Generate a Repository class for the {name} entity.
        Language: {language}
        Framework: {framework}
        
        --- PROJECT CONTEXT ---
        Description: {project_description}
        Requirements: {project_requirements}
        -----------------------
        
        Operations:
        - FindById(id)
        - FindAll(page, pageSize) with pagination
        - Create(entity)
        - Update(id, entity)
        - Delete(id)
        - Custom query methods based on unique fields
        
        Entity: {name}
        Unique Fields: {unique_fields}
        
        Requirements:
        - Use repository pattern
        - Include error handling
        - Return appropriate types
        - Use async/await if supported by language
        """
        
        for entity in entities:
            unique_fields = [f.name for f in entity.fields if f.unique]
            
            prompt = prompt_template.format(
                name=entity.name,
                language=language,
                framework=framework,
                project_description=project_description,
                project_requirements=project_requirements,
                unique_fields=", ".join(unique_fields) if unique_fields else "None"
            )
            
            result = await self.orchestrator.universal_agent.generate_code(
                requirements=prompt,
                language=language,
                framework=framework,
                context_data={
                    "project_name": context.get("project_name", ""),
                    "description": context.get("description", ""),
                    "security": context.get("security", {}),
                    "database": context.get("database", {}),
                    "kubernetes": context.get("kubernetes", {})
                }
            )
            
            results[f"{entity.name}Repository"] = result.get("solution", "")
        
        return results
