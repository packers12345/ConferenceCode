import psycopg2
import google.generativeai as genai
from typing import Dict, List

def connect_to_db():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname='DatabaseHume',
            user='postgres',
            password='Bashok12!',
            host='localhost',
            port='5432'
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def list_all_tables():
    """Retrieve a list of all tables in the database."""
    conn = connect_to_db()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        print(f"Error fetching table list: {e}")
        return []

def fetch_table_structure():
    """Retrieve column details for all tables in the database."""
    conn = connect_to_db()
    if not conn:
        return {}
    
    table_structure = {}
    try:
        cursor = conn.cursor()
        tables = list_all_tables()
        for table in tables:
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';")
            columns = cursor.fetchall()
            table_structure[table] = {col[0]: col[1] for col in columns}
        conn.close()
        return table_structure
    except Exception as e:
        print(f"Error fetching table structures: {e}")
        return {}

def generate_system_designs(system_requirements: str) -> str:
    """Generate system designs using real database data."""
    try:
        table_structure = fetch_table_structure()
        
        query_text = f"""
        Generate system designs based on the given system requirements. Use the following database structure as a reference:

        Table Structures:
        {table_structure}

        Please provide:
        1. Mathematical description of the system requirements.
        2. Set of acceptable system designs with proof.
        3. Set of unacceptable system designs with proof.
        4. Recommendations for improvement.
        """
        
        model = genai.GenerativeModel("gemini-1.0-pro")
        response = model.generate_content(query_text)
        return response.text.strip()
    except Exception as e:
        return f"Error in generating system designs: {str(e)}"
