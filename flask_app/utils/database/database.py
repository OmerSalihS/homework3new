import mysql.connector
import glob
import json
import csv
import os
from io import StringIO
import itertools
import datetime
import hashlib
from cryptography.fernet import Fernet

class database:

    def __init__(self, purge=False):
        # Grab information from the configuration file
        self.database = 'db'
        self.host = '127.0.0.1'
        self.user = 'master'
        self.port = 3306
        self.password = 'master'
        
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
        
        self.createTables(purge=purge, data_path='flask_app/database/')

    def query(self, query="SELECT CURDATE()", parameters=None):
        cnx = mysql.connector.connect(host=self.host,
                                      user=self.user,
                                      password=self.password,
                                      port=self.port,
                                      database=self.database,
                                      charset='latin1'
                                     )

        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def about(self, nested=False):    
        query = """select concat(col.table_schema, '.', col.table_name) as 'table',
                          col.column_name                               as column_name,
                          col.column_key                                as is_key,
                          col.column_comment                            as column_comment,
                          kcu.referenced_column_name                    as fk_column_name,
                          kcu.referenced_table_name                     as fk_table_name
                    from information_schema.columns col
                    join information_schema.tables tab on col.table_schema = tab.table_schema and col.table_name = tab.table_name
                    left join information_schema.key_column_usage kcu on col.table_schema = kcu.table_schema
                                                                     and col.table_name = kcu.table_name
                                                                     and col.column_name = kcu.column_name
                                                                     and kcu.referenced_table_schema is not null
                    where col.table_schema not in('information_schema','sys', 'mysql', 'performance_schema')
                                              and tab.table_type = 'BASE TABLE'
                    order by col.table_schema, col.table_name, col.ordinal_position;"""
        results = self.query(query)
        if nested == False:
            return results

        table_info = {}
        for row in results:
            table_info[row['table']] = {} if table_info.get(row['table']) is None else table_info[row['table']]
            table_info[row['table']][row['column_name']] = {} if table_info.get(row['table']).get(row['column_name']) is None else table_info[row['table']][row['column_name']]
            table_info[row['table']][row['column_name']]['column_comment'] = row['column_comment']
            table_info[row['table']][row['column_name']]['fk_column_name'] = row['fk_column_name']
            table_info[row['table']][row['column_name']]['fk_table_name'] = row['fk_table_name']
            table_info[row['table']][row['column_name']]['is_key'] = row['is_key']
            table_info[row['table']][row['column_name']]['table'] = row['table']
        return table_info

    def createTables(self, purge=False, data_path='flask_app/database/'):
        """
        (1) Optionally drops existing tables (if purge==True).
        (2) Creates tables by running all .sql files in data_path/create_tables.
        (3) Inserts initial data from all .csv files in data_path/initial_data.
        """
        print('----- createTables() -----')
        if purge:
            print('Purging (dropping) existing tables...')
            # Temporarily turn off foreign key checks so we can drop in any order
            self.query("SET FOREIGN_KEY_CHECKS=0")
            for table in ['skills', 'experiences', 'positions', 'institutions', 'feedback', 'users']:
                try:
                    self.query(f"DROP TABLE IF EXISTS {table}")
                    print(f"Dropped table {table}")
                except Exception as e:
                    print(f"Error dropping {table}: {str(e)}")
            self.query("SET FOREIGN_KEY_CHECKS=1")
            print("Done purging!")

        # Create tables in the correct order
        table_order = ['users', 'institutions', 'positions', 'experiences', 'skills', 'feedback']
        for table in table_order:
            try:
                print(f"Running {data_path}create_tables/{table}.sql")
                with open(data_path + f"create_tables/{table}.sql") as read_file:
                    create_statement = read_file.read()
                self.query(create_statement)
            except Exception as e:
                print(f"Error executing SQL: {str(e)}")
                print(f"Problematic statement: {create_statement}")

        # Insert initial data
        for table in table_order:
            try:
                print(f"Inserting data into '{table}' from '{data_path}initial_data/{table}.csv'")
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table=table, columns=cols, parameters=params)
            except Exception as e:
                print(f"Error inserting into {table}: {str(e)}")
                if 'params' in locals() and len(params) > 0:
                    print(f"Problematic row: {params[0]}")
                else:
                    print('no initial data')

        print("----- Done creating and populating tables -----")

    def get_drop_order(self, dependencies):
        """
        Determine the order to drop tables based on dependencies.
        """
        result = []
        visited = set()
        temp_mark = set()
        
        def visit(node):
            if node in temp_mark:
                # We have a circular dependency
                return
            if node in visited:
                return
                
            temp_mark.add(node)
            
            # Visit all dependencies
            for dep in dependencies.get(node, set()):
                visit(dep)
                
            temp_mark.remove(node)
            visited.add(node)
            result.append(node)
        
        # Visit all nodes
        for node in dependencies:
            if node not in visited:
                visit(node)
                
        return result

    def insertRows(self, table='table', columns=['x', 'y'], parameters=[['v11', 'v12'], ['v21', 'v22']]):
        """
        Inserts each row in `parameters` into `table`, 
        matching each row to the list of `columns`.
        """
        # Build the "INSERT INTO tablename (col1, col2, ...) VALUES (%s, %s, ...)"
        placeholders = ", ".join(["%s"] * len(columns))
        col_names = ", ".join([f"`{c}`" for c in columns])
        sql = f"INSERT INTO `{table}` ({col_names}) VALUES ({placeholders})"

        # Insert each row
        for row in parameters:
            cleaned = []
            for val in row:
                if isinstance(val, str) and val.strip().upper() in ("NULL", ""):
                    cleaned.append(None)
                else:
                    cleaned.append(val)
            try:
                self.query(sql, cleaned)
            except mysql.connector.Error as err:
                print(f"Error inserting into {table}: {err}")
                print(f"Problematic row: {cleaned}")

    def getResumeData(self):
        """
        Returns a nested dictionary that represents the complete data
        """
        # First, get all institutions
        institutions_query = """
            SELECT inst_id, type, name, department, address, city, state, zip
            FROM institutions
        """
        institutions_data = self.query(institutions_query)
        
        result = {}
        
        for inst in institutions_data:
            inst_id = inst['inst_id']
            result[inst_id] = {
                'type': inst['type'],
                'name': inst['name'],
                'department': inst['department'],
                'address': inst['address'],
                'city': inst['city'],
                'state': inst['state'],
                'zip': inst['zip'],
                'positions': {}
            }
            
            positions_query = f"""
                SELECT position_id, title, responsibilities, start_date, end_date
                FROM positions
                WHERE inst_id = {inst_id}
            """
            positions_data = self.query(positions_query)
            
            for pos in positions_data:
                position_id = pos['position_id']
                result[inst_id]['positions'][position_id] = {
                    'title': pos['title'],
                    'responsibilities': pos['responsibilities'],
                    'start_date': pos['start_date'],
                    'end_date': pos['end_date'],
                    'experiences': {}
                }
                
                experiences_query = f"""
                    SELECT experience_id, name, description, hyperlink, start_date, end_date
                    FROM experiences
                    WHERE position_id = {position_id}
                """
                experiences_data = self.query(experiences_query)
                
                for exp in experiences_data:
                    experience_id = exp['experience_id']
                    result[inst_id]['positions'][position_id]['experiences'][experience_id] = {
                        'name': exp['name'],
                        'description': exp['description'],
                        'hyperlink': exp['hyperlink'],
                        'start_date': exp['start_date'],
                        'end_date': exp['end_date'],
                        'skills': {}
                    }
                    
                    skills_query = f"""
                        SELECT skill_id, name, skill_level
                        FROM skills
                        WHERE experience_id = {experience_id}
                    """
                    skills_data = self.query(skills_query)
                    
                    for skill in skills_data:
                        skill_id = skill['skill_id']
                        result[inst_id]['positions'][position_id]['experiences'][experience_id]['skills'][skill_id] = {
                            'name': skill['name'],
                            'skill_level': skill['skill_level']
                        }
        
        return result

    def createUser(self, email='me@email.com', password='password', role='user', name='User'):
        """
        Create a new user in the database.
        
        Args:
            email (str): User's email address
            password (str): User's password (will be encrypted)
            role (str): User's role ('guest' or 'owner')
            name (str): User's name
            
        Returns:
            dict: Information about success or failure of user creation
                {'success': 1} if successful, {'success': 0, 'message': 'error message'} if failed
        """
        try:
            # First check if user already exists
            existing_user = self.query("SELECT * FROM users WHERE email = %s", (email,))
            if existing_user:
                return {'success': 0, 'message': 'User already exists'}
            
            # Encrypt the password
            encrypted_password = self.onewayEncrypt(password)
            
            # Create new user
            self.query(
                "INSERT INTO users (email, password, role, name) VALUES (%s, %s, %s, %s)",
                (email, encrypted_password, role, name)
            )
            return {'success': 1}
        except Exception as e:
            print(f"Error creating user: {str(e)}")
            return {'success': 0, 'message': str(e)}
        
    def authenticate(self, email='me@email.com', password='password'):
        """
        Authenticate a user by checking if the email and password combination exists.
        
        Args:
            email (str): User's email address
            password (str): User's password (will be encrypted and compared)
            
        Returns:
            dict: Information about success or failure of authentication
                {'success': 1, 'role': 'user_role', 'name': 'user_name'} if successful, 
                {'success': 0, 'message': 'error message'} if failed
        """
        try:
            # Encrypt the provided password
            encrypted_password = self.onewayEncrypt(password)
            
            # Check if the email and encrypted password combination exists
            user = self.query(
                "SELECT * FROM users WHERE email = %s AND password = %s", 
                (email, encrypted_password)
            )
            
            if user:
                return {'success': 1, 'role': user[0]['role'], 'name': user[0]['name']}
            else:
                return {'success': 0, 'message': 'Invalid email or password'}
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return {'success': 0, 'message': str(e)}

    def onewayEncrypt(self, string):
        """
        Encrypt a string using scrypt (one-way encryption).
        
        Args:
            string (str): The string to encrypt
            
        Returns:
            str: The encrypted string in hexadecimal format
        """
        encrypted_string = hashlib.scrypt(
            string.encode('utf-8'),
            salt=self.encryption['oneway']['salt'],
            n=self.encryption['oneway']['n'],
            r=self.encryption['oneway']['r'],
            p=self.encryption['oneway']['p']
        ).hex()
        return encrypted_string

    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message
