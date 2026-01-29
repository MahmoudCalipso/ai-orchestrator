
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)

# Try with 'orchestrator' instead of 'orchestrator_user'
new_url = db_url.replace("orchestrator_user", "orchestrator")

print(f"Testing connection with 'orchestrator' user...")
try:
    engine = create_engine(new_url)
    with engine.connect() as conn:
        print("Successfully connected with 'orchestrator' user!")
except Exception as e:
    print(f"Connection with 'orchestrator' failed: {e}")

# Try with 'postgres' user
postgres_url = db_url.replace("orchestrator_user", "postgres")
print(f"Testing connection with 'postgres' user...")
try:
    engine = create_engine(postgres_url)
    with engine.connect() as conn:
        print("Successfully connected with 'postgres' user!")
except Exception as e:
    print(f"Connection with 'postgres' failed: {e}")
