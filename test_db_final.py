
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
# Manual override based on my findings
db_url = "postgresql://orchestrator:MAHMOUD1996*369*PgSqlPassWd@127.0.0.1:5432/ai_orchestrator"

print(f"Testing connection with 'orchestrator' user and password from .env...")
try:
    engine = create_engine(db_url)
    with engine.connect() as conn:
        print("Successfully connected to the database!")
except Exception as e:
    print(f"Connection failed: {e}")
