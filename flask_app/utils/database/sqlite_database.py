import sqlite3
import os
import json
import csv
import glob
import hashlib
from cryptography.fernet import Fernet
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SQLiteDatabase:
    def __init__(self, db_path='flask_app.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Encryption settings
        self.encryption = {
            'oneway': {
                'salt': b'averysaltysailortookalongwalkoffashortbridge',
                'n': 2**5,  # CPU/memory cost factor
                'r': 9,     # Block size factor
                'p': 1      # Parallelization factor
            },
            'reversible': {
                'key': '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='
            }
        }
        
        # Connect to the database
        self.connect()
        
        # Create tables if they don't exist
        self.createTables(purge=False, data_path='flask_app/database/')
    
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # This enables column access by name
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to SQLite database at {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to SQLite database: {str(e)}")
            raise
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def query(self, query, parameters=None):
        """Execute a query and return the results"""
        try:
            if parameters:
                self.cursor.execute(query, parameters)
            else:
                self.cursor.execute(query)
            
            # For SELECT queries, fetch all results
            if query.strip().upper().startswith('SELECT'):
                results = self.cursor.fetchall()
                # Convert to list of dictionaries
                return [dict(row) for row in results]
            
            # For INSERT queries, get the last inserted ID
            elif query.strip().upper().startswith('INSERT'):
                last_id = self.cursor.lastrowid
                self.conn.commit()
                return [{'LAST_INSERT_ID()': last_id}]
            
            # For other queries, just commit
            else:
                self.conn.commit()
                return []
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(f"Query: {query}")
            if parameters:
                logger.error(f"Parameters: {parameters}")
            raise
    
    def createTables(self, purge=False, data_path='flask_app/database/'):
        """Create tables from SQL files"""
        try:
            # If purge is True, drop all existing tables
            if purge:
                self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = self.cursor.fetchall()
                for table in tables:
                    self.cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
                self.conn.commit()
                logger.info("All tables dropped")
            
            # Create tables from SQL files
            sql_files = glob.glob(os.path.join(data_path, 'create_tables', '*.sql'))
            for sql_file in sql_files:
                with open(sql_file, 'r') as f:
                    sql = f.read()
                    # Split SQL by semicolons to handle multiple statements
                    statements = sql.split(';')
                    for statement in statements:
                        if statement.strip():
                            self.cursor.execute(statement)
                self.conn.commit()
                logger.info(f"Created tables from {sql_file}")
            
            # Insert initial data from CSV files
            csv_files = glob.glob(os.path.join(data_path, 'initial_data', '*.csv'))
            for csv_file in csv_files:
                table_name = os.path.basename(csv_file).split('.')[0]
                with open(csv_file, 'r') as f:
                    csv_reader = csv.reader(f)
                    headers = next(csv_reader)
                    placeholders = ','.join(['?' for _ in headers])
                    insert_query = f"INSERT INTO {table_name} ({','.join(headers)}) VALUES ({placeholders})"
                    
                    for row in csv_reader:
                        self.cursor.execute(insert_query, row)
                self.conn.commit()
                logger.info(f"Inserted initial data into {table_name}")
            
            return True
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
    
    def insertRows(self, table='table', columns=['x', 'y'], parameters=[['v11', 'v12'], ['v21', 'v22']]):
        """Insert rows into a table"""
        try:
            placeholders = ','.join(['?' for _ in columns])
            insert_query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            
            for row in parameters:
                self.cursor.execute(insert_query, row)
            
            self.conn.commit()
            logger.info(f"Inserted {len(parameters)} rows into {table}")
            return True
        except Exception as e:
            logger.error(f"Error inserting rows: {str(e)}")
            raise
    
    def getResumeData(self):
        """Get resume data from the database"""
        try:
            # This is a simplified version - you may need to adjust based on your schema
            resume_data = {
                'personal_info': self.query("SELECT * FROM personal_info LIMIT 1"),
                'education': self.query("SELECT * FROM education"),
                'experience': self.query("SELECT * FROM experience"),
                'skills': self.query("SELECT * FROM skills")
            }
            return resume_data
        except Exception as e:
            logger.error(f"Error getting resume data: {str(e)}")
            return {}
    
    def createUser(self, email, password, name, role='user'):
        try:
            with self.conn as conn:
                cursor = conn.cursor()
                
                # Check if user already exists
                cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
                if cursor.fetchone():
                    return {'success': False, 'message': 'User already exists'}
                
                # Hash the password
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                # Insert new user
                cursor.execute('''
                    INSERT INTO users (email, password, name, role)
                    VALUES (?, ?, ?, ?)
                ''', (email, hashed_password, name, role))
                
                conn.commit()
                return {'success': True, 'message': 'User created successfully'}
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return {'success': False, 'message': 'Error creating user'}
    
    def authenticate(self, email, password):
        try:
            with self.conn as conn:
                cursor = conn.cursor()
                
                # Hash the password for comparison
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                # Get user details
                cursor.execute('''
                    SELECT email, name, role
                    FROM users
                    WHERE email = ? AND password = ?
                ''', (email, hashed_password))
                
                user = cursor.fetchone()
                if user:
                    return {
                        'success': True,
                        'email': user[0],
                        'name': user[1],
                        'role': user[2]
                    }
                else:
                    return {'success': False, 'message': 'Invalid credentials'}
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return {'success': False, 'message': 'Error authenticating user'}
    
    def onewayEncrypt(self, string):
        """One-way encryption for passwords"""
        try:
            # This is a simplified version - you may need to adjust based on your requirements
            salt = self.encryption['oneway']['salt']
            return hashlib.pbkdf2_hmac(
                'sha256',
                string.encode('utf-8'),
                salt,
                self.encryption['oneway']['n'],
                dklen=128
            ).hex()
        except Exception as e:
            logger.error(f"Error in oneway encryption: {str(e)}")
            raise
    
    def reversibleEncrypt(self, type, message):
        """Reversible encryption for session data"""
        try:
            key = self.encryption['reversible']['key'].encode('utf-8')
            f = Fernet(key)
            
            if type == 'encrypt':
                return f.encrypt(message.encode('utf-8')).decode('utf-8')
            elif type == 'decrypt':
                return f.decrypt(message.encode('utf-8')).decode('utf-8')
            else:
                raise ValueError(f"Invalid encryption type: {type}")
        except Exception as e:
            logger.error(f"Error in reversible encryption: {str(e)}")
            raise 