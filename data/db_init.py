import os
import sqlite3

def init_db(db_path='data/discovery.db', schema_path='data/schema.sql'):
    """Initializes the SQLite database with the schema."""
    # Ensure data directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created directory: {db_dir}")

    # Read the schema file
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Connect and execute schema
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"Database successfully initialized at {db_path}")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    # Determine base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_p = os.path.join(base_dir, 'data', 'discovery.db')
    schema_p = os.path.join(base_dir, 'data', 'schema.sql')
    init_db(db_p, schema_p)
