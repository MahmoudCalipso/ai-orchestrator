
import sqlite3
import os

db_path = os.path.join(os.getcwd(), "storage", "registry.db")

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Skipping migration.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = ["language_metadata", "database_metadata", "framework_metadata"]
    
    for table in tables:
        try:
            # Check if logo_url exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [info[1] for info in cursor.fetchall()]
            
            if "logo_url" not in columns:
                print(f"Adding logo_url column to {table}...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN logo_url VARCHAR(255)")
                print(f"Column added to {table}.")
            else:
                print(f"logo_url already exists in {table}.")
        except Exception as e:
            print(f"Error migrating {table}: {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
