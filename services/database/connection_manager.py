"""
Database connection manager and utilities
"""
import logging
from typing import Dict, Any

from schemas.generation_spec import DatabaseConfig, DatabaseType

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """Manages connections to various database types"""
    
    def __init__(self):
        self._engines: Dict[str, Any] = {}
        self._connections: Dict[str, Any] = {}
        
    async def get_connection_string(self, config: DatabaseConfig) -> str:
        """Generate connection string based on config"""
        if config.connection_string:
            return config.connection_string
            
        if config.type == DatabaseType.POSTGRESQL:
            return f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database_name}"
        elif config.type == DatabaseType.MYSQL:
            return f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database_name}"
        elif config.type == DatabaseType.SQLSERVER:
            return f"mssql+pyodbc://{config.username}:{config.password}@{config.host}:{config.port}/{config.database_name}?driver=ODBC+Driver+17+for+SQL+Server"
        elif config.type == DatabaseType.SQLITE:
            return f"sqlite:///{config.database_name}"
        elif config.type == DatabaseType.MONGODB:
            creds = f"{config.username}:{config.password}@" if config.username else ""
            return f"mongodb://{creds}{config.host}:{config.port}/{config.database_name}"
        # Add support for others
        return ""

    async def connect(self, config: DatabaseConfig) -> bool:
        """Establish connection to database"""
        try:
            conn_str = await self.get_connection_string(config)
            
            if config.type in [DatabaseType.POSTGRESQL, DatabaseType.MYSQL, DatabaseType.SQLITE, DatabaseType.SQLSERVER]:
                return await self._connect_sql(conn_str, config.database_name)
            elif config.type == DatabaseType.MONGODB:
                return await self._connect_mongo(conn_str)
            elif config.type == DatabaseType.REDIS:
                return await self._connect_redis(config)
            
            logger.warning(f"Unsupported database type: {config.type}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def _connect_sql(self, conn_str: str, name: str) -> bool:
        """Connect to SQL database using SQLAlchemy"""
        try:
            from sqlalchemy import create_engine, text
            
            engine = create_engine(conn_str)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            self._engines[name or "default"] = engine
            logger.info(f"Connected to SQL database: {name}")
            return True
        except ImportError:
            logger.error("SQLAlchemy not installed")
            return False
        except Exception as e:
            logger.error(f"SQL connection error: {e}")
            return False

    async def _connect_mongo(self, conn_str: str) -> bool:
        """Connect to MongoDB"""
        try:
            from pymongo import MongoClient
            
            client = MongoClient(conn_str)
            # Test connection
            client.admin.command('ping')
            
            self._connections["mongo"] = client
            logger.info("Connected to MongoDB")
            return True
        except ImportError:
            logger.error("pymongo not installed")
            return False
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            return False
            
    async def _connect_redis(self, config: DatabaseConfig) -> bool:
        """Connect to Redis"""
        try:
            import redis
            
            r = redis.Redis(
                host=config.host,
                port=config.port,
                password=config.password,
                decode_responses=True
            )
            r.ping()
            
            self._connections["redis"] = r
            logger.info("Connected to Redis")
            return True
        except ImportError:
            logger.error("redis not installed")
            return False
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            return False

    def get_engine(self, name: str = "default") -> Any:
        """Get SQLAlchemy engine"""
        return self._engines.get(name)
        
    def get_client(self, type_key: str = "mongo") -> Any:
        """Get native client (mongo, redis, etc)"""
        return self._connections.get(type_key)
