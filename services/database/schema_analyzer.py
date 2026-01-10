"""
Database schema analyzer for reverse engineering entities
"""
import logging
from typing import List, Dict, Any, Optional

from schemas.generation_spec import EntityDefinition, EntityField, ValidationRule, DatabaseConfig, DatabaseType
from services.database.connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)

class SchemaAnalyzer:
    """Analyzes database schemas to generate entity definitions"""
    
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.conn_manager = connection_manager
        
    async def analyze(self, config: DatabaseConfig) -> List[EntityDefinition]:
        """Analyze database and return entity definitions"""
        if config.type in [DatabaseType.POSTGRESQL, DatabaseType.MYSQL, DatabaseType.SQLSERVER, DatabaseType.SQLITE]:
            return await self._analyze_sql(config)
        
        # Add NoSQL support later
        logger.warning(f"Analysis not yet supported for {config.type}")
        return []
        
    async def _analyze_sql(self, config: DatabaseConfig) -> List[EntityDefinition]:
        """Analyze SQL database schema with relationships and indexes"""
        try:
            from sqlalchemy import inspect
            
            engine = self.conn_manager.get_engine(config.database_name or "default")
            if not engine:
                if not await self.conn_manager.connect(config):
                    raise ConnectionError("Could not connect to database")
                engine = self.conn_manager.get_engine(config.database_name or "default")
                
            inspector = inspect(engine)
            entities = []
            relationships_map = {}  # Track relationships for later processing
            
            for table_name in inspector.get_table_names():
                fields = []
                columns = inspector.get_columns(table_name)
                pk_constraint = inspector.get_pk_constraint(table_name)
                primary_keys = pk_constraint.get('constrained_columns', [])
                
                # Get foreign keys
                fks = inspector.get_foreign_keys(table_name)
                fk_map = {}
                table_relationships = []
                for fk in fks:
                    for i, col in enumerate(fk['constrained_columns']):
                        fk_map[col] = f"{fk['referred_table']}.{fk['referred_columns'][i]}"
                        # Track relationship
                        table_relationships.append({
                            "type": "ManyToOne",
                            "target_entity": self._table_to_class_name(fk['referred_table']),
                            "foreign_key": col
                        })
                
                # Get indexes for performance insights
                indexes = inspector.get_indexes(table_name)
                unique_columns = set()
                for idx in indexes:
                    if idx.get('unique'):
                        unique_columns.update(idx['column_names'])
                
                for col in columns:
                    field_type = str(col['type'])
                    
                    # Map SQLAlchemy types to our generic types
                    generic_type = self._map_sql_type(field_type)
                    
                    is_pk = col['name'] in primary_keys
                    is_fk = col['name'] in fk_map
                    is_unique = col['name'] in unique_columns
                    
                    # Extract length from type if available
                    length = None
                    if hasattr(col['type'], 'length'):
                        length = col['type'].length
                    
                    field = EntityField(
                        name=col['name'],
                        type=generic_type,
                        length=length,
                        nullable=col['nullable'],
                        unique=is_unique,
                        primary_key=is_pk,
                        auto_increment=col.get('autoincrement', False) if is_pk else False,
                        foreign_key=fk_map.get(col['name']),
                        default_value=col.get('default'),
                        description=col.get('comment')
                    )
                    
                    # Add enhanced validations
                    if not col['nullable'] and not is_pk:
                        field.validations.append(ValidationRule(type="required", message=f"{col['name']} is required"))
                    if length and generic_type == 'string':
                        field.validations.append(ValidationRule(type="max", value=length, message=f"{col['name']} must be at most {length} characters"))
                    if is_unique:
                        field.validations.append(ValidationRule(type="unique", message=f"{col['name']} must be unique"))
                        
                    fields.append(field)
                    
                entity = EntityDefinition(
                    name=self._table_to_class_name(table_name),
                    table_name=table_name,
                    fields=fields,
                    relationships=table_relationships
                )
                entities.append(entity)
                relationships_map[table_name] = table_relationships
                
            # Detect OneToMany relationships (inverse of ManyToOne)
            self._detect_inverse_relationships(entities, relationships_map)
            
            return entities
            
        except ImportError:
            logger.error("SQLAlchemy not installed")
            return []
        except Exception as e:
            logger.error(f"Schema analysis failed: {e}")
            raise

    def _map_sql_type(self, sql_type: str) -> str:
        """Map SQL type to generic type"""
        sql_type = sql_type.lower()
        if 'int' in sql_type:
            return 'integer'
        elif 'char' in sql_type or 'text' in sql_type:
            return 'string'
        elif 'bool' in sql_type:
            return 'boolean'
        elif 'date' in sql_type or 'time' in sql_type:
            return 'datetime'
        elif 'numeric' in sql_type or 'decimal' in sql_type or 'float' in sql_type:
            return 'decimal'
        return 'string'

    def _table_to_class_name(self, table_name: str) -> str:
        """Convert snake_case table name to PascalCase class name"""
        return ''.join(word.title() for word in table_name.split('_'))
    
    def _detect_inverse_relationships(self, entities: List[EntityDefinition], relationships_map: Dict[str, List[Dict]]):
        """Detect OneToMany relationships (inverse of foreign keys)"""
        # Build a map of table_name -> entity
        entity_map = {e.table_name: e for e in entities}
        
        for table_name, relationships in relationships_map.items():
            for rel in relationships:
                if rel['type'] == 'ManyToOne':
                    # Find the target entity and add OneToMany relationship
                    target_table = self._class_to_table_name(rel['target_entity'])
                    if target_table in entity_map:
                        target_entity = entity_map[target_table]
                        # Add inverse relationship
                        inverse_rel = {
                            "type": "OneToMany",
                            "target_entity": self._table_to_class_name(table_name),
                            "mapped_by": rel['foreign_key']
                        }
                        if inverse_rel not in target_entity.relationships:
                            target_entity.relationships.append(inverse_rel)
    
    def _class_to_table_name(self, class_name: str) -> str:
        """Convert PascalCase class name to snake_case table name"""
        import re
        # Insert underscore before uppercase letters and convert to lowercase
        return re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
    
    async def analyze_nosql(self, config: DatabaseConfig) -> List[EntityDefinition]:
        """Analyze NoSQL database schema (MongoDB)"""
        if config.type != DatabaseType.MONGODB:
            logger.warning(f"NoSQL analysis only supports MongoDB currently")
            return []
        
        try:
            client = self.conn_manager.get_client("mongo")
            if not client:
                if not await self.conn_manager.connect(config):
                    raise ConnectionError("Could not connect to MongoDB")
                client = self.conn_manager.get_client("mongo")
            
            db = client[config.database_name]
            entities = []
            
            # Analyze each collection
            for collection_name in db.list_collection_names():
                collection = db[collection_name]
                
                # Sample documents to infer schema
                sample_docs = list(collection.find().limit(100))
                if not sample_docs:
                    continue
                
                # Infer fields from samples
                field_types = {}
                for doc in sample_docs:
                    for key, value in doc.items():
                        if key == '_id':
                            continue
                        
                        python_type = type(value).__name__
                        if key not in field_types:
                            field_types[key] = set()
                        field_types[key].add(python_type)
                
                # Create entity fields
                fields = []
                for field_name, types in field_types.items():
                    # Use most common type or 'any' if multiple
                    field_type = list(types)[0] if len(types) == 1 else 'json'
                    generic_type = self._map_python_type(field_type)
                    
                    field = EntityField(
                        name=field_name,
                        type=generic_type,
                        nullable=True  # NoSQL fields are typically optional
                    )
                    fields.append(field)
                
                entity = EntityDefinition(
                    name=self._table_to_class_name(collection_name),
                    table_name=collection_name,
                    fields=fields
                )
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"NoSQL schema analysis failed: {e}")
            return []
    
    def _map_python_type(self, python_type: str) -> str:
        """Map Python type to generic type"""
        type_map = {
            'str': 'string',
            'int': 'integer',
            'float': 'decimal',
            'bool': 'boolean',
            'datetime': 'datetime',
            'date': 'date',
            'list': 'json',
            'dict': 'json'
        }
        return type_map.get(python_type, 'string')
