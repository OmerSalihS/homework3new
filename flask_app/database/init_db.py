import sqlite3
import os
from flask import current_app

def init_db():
    """Initialize the SQLite database and create tables."""
    db_path = os.path.join(current_app.root_path, 'database', 'app.db')
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute schema.sql
    schema_path = os.path.join(current_app.root_path, 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    return db_path 