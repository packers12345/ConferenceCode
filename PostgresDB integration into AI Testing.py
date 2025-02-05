import psycopg2
import google.generativeai as genai
from typing import Dict, List, Any

def initialize_api(api_key: str) -> bool:
    """
    Initialize the Gemini generative AI with the given API key.
    Return True if successful, or False otherwise.
    """
    try:
        genai.configure(api_key=api_key)
        print(f"API initialized with key: {api_key}")
        return True
    except Exception as e:
        print(f"Error initializing API: {e}")
        return False

def connect_to_db():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname='DatabaseHume',
            user='postgres',
            password='XXXXXXXXXXXX',
            host='localhost',
            port='5432'
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def list_all_tables() -> List[str]:
    """Retrieve a list of all tables in the 'public' schema."""
    conn = connect_to_db()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if tables:
            print(f"Tables have been retrieved successfully: {tables}")
        else:
            print("No tables found in the 'public' schema.")
        
        return tables
    except Exception as e:
        print(f"Error fetching table list: {e}")
        return []

def fetch_table_structure() -> Dict[str, Dict[str, str]]:
    """Retrieve column details for all tables in the database."""
    conn = connect_to_db()
    if not conn:
        return {}
    
    table_structure = {}
    try:
        cursor = conn.cursor()
        tables = list_all_tables()
        
        for table in tables:
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table}';
            """)
            columns = cursor.fetchall()
            table_structure[table] = {col[0]: col[1] for col in columns}
        
        conn.close()
        return table_structure
    except Exception as e:
        print(f"Error fetching table structures: {e}")
        return {}

def fetch_specific_table(table_name: str, limit: int = 5) -> List[Any]:
    """
    Fetch up to `limit` rows from the given table_name.
    Returns a list of tuples (one tuple per row).
    """
    conn = connect_to_db()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        # Safely quote the table name if needed, but for simplicity:
        query = f"SELECT * FROM {table_name} LIMIT {limit};"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error fetching data from table '{table_name}': {e}")
        return []

def detect_table_name(user_text: str) -> str:
    """
    A simple, naive approach to detect a table name mentioned in user_text.
    E.g., if user_text contains 'table system_requirements', returns 'system_requirements'.
    """
    words = user_text.lower().split()
    if "table" in words:
        idx = words.index("table")
        if idx + 1 < len(words):
            # Next word after "table" might be the table name
            possible_name = words[idx + 1]
            # Remove punctuation if needed
            return possible_name.replace(",", "").replace(".", "")
    return ""

def generate_system_designs(
    user_requirements: str,
    example_reqs: str,
    example_designs: str
) -> str:
    """
    Generate system designs using real database data
    and the provided example requirements/designs.

    Additionally, if the user mentions 'table <tablename>' in their requirements,
    we'll fetch rows from that table and embed them in the prompt.
    """
    try:
        # 1) Always fetch the overall table structure
        table_structure = fetch_table_structure()

        # 2) Check if user references a specific table in user_requirements
        referenced_table = detect_table_name(user_requirements)
        table_data_string = ""

        if referenced_table:
            # 3) If found, fetch up to 5 rows from that table
            rows = fetch_specific_table(referenced_table, limit=5)
            if rows:
                # Format the rows for the prompt
                table_data_string = f"Here are up to 5 rows from the '{referenced_table}' table:\n"
                for i, row in enumerate(rows, start=1):
                    table_data_string += f"Row {i}: {row}\n"
            else:
                table_data_string = f"No rows found or unable to fetch from table '{referenced_table}'.\n"

        # 4) Build the final query text
        query_text = f"""
        Based on the user's system requirements:
        {user_requirements}

        Use the following example system requirements:
        {example_reqs}

        And the following example system designs:
        {example_designs}

        Also, use the following database structure as a reference:
        {table_structure}

        {table_data_string}

        Please provide:
        1. Mathematical description of the system requirements.
        2. Set of acceptable system designs with proof (referencing table data if relevant).
        3. Set of unacceptable system designs with proof.
        4. Recommendations for improvement.
        5. A formal proof of homomorphism verifying the equivalence between the system requirements and the resulting system designs by comparing key properties.
        """

        model = genai.GenerativeModel("gemini-1.0-pro")
        response = model.generate_content(query_text)
        return response.text.strip()

    except Exception as e:
        return f"Error in generating system designs: {str(e)}"

def create_verification_requirements_models(
    system_requirements: str,
    example_system_requirements: str,
    example_verification_requirements: Dict[str, Dict[str, List[Dict[str, str]]]],
    example_system_designs: Dict[str, Dict[str, List[Dict[str, str]]]]
) -> str:
    """
    Generate verification requirements and models based on the given system requirements 
    and example verification requirements.
    """
    try:
        query_text = f"""
        Generate verification requirements and models based on the given system requirements. 
        The provided example system requirements, verification requirements, and system designs 
        are for structure reference only. Do not use the example content directly.

        Example System Requirements (for structure reference only):
        {example_system_requirements}

        Example Verification Requirements (for structure reference only):
        {example_verification_requirements}

        Example System Designs (for structure reference only):
        {example_system_designs}

        System Requirements: {system_requirements}

        Please provide:
        1. Verification requirement problem spaces with proof of morphism to system requirements.
        2. Verification models with proof of which verification requirement problem spaces they adhere to.
        3. Proof of homomorphism to the various system designs (Y/N proof, not type or degree).
        """

        model = genai.GenerativeModel("gemini-1.0-pro")
        response = model.generate_content(query_text)
        return response.text.strip()
    except Exception as e:
        return f"Error in generating verification requirements and models: {str(e)}"

# --------------------- #
#  MAIN FUNCTION BLOCK  #
# --------------------- #
if __name__ == "__main__":
    test_key = "YOUR_API_KEY_HERE"
    if not initialize_api(test_key):
        print("Failed to initialize API. Exiting.")
    else:
        # Quick check: list tables and structure
        tables = list_all_tables()
        print(f"Tables returned: {tables}")

        structure = fetch_table_structure()
        print("Table Structure:")
        print(structure)

