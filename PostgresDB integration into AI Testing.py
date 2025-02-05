import psycopg2
import google.generativeai as genai
from typing import Dict, List

def initialize_api(api_key: str) -> bool:
    """
    Initialize the Gemini generative AI with the given API key.
    Return True if successful, or False otherwise.
    """
    try:
        # Configure generative AI with the provided API key
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
            dbname='DatabaseHume', #this is the postgresDB being imported, it shows up at the bottom of the screen with tables
            user='postgres',
            password='Bashok12!',
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
        
        # Print a message to confirm whether the tables have been retrieved
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

def generate_system_designs(
    user_requirements: str,
    example_reqs: str,
    example_designs: str
) -> str:
    """
    Generate system designs using real database data
    and the provided example requirements/designs.
    """
    try:
        table_structure = fetch_table_structure()

        query_text = f"""
        Based on the user's system requirements:
        {user_requirements}

        Use the following example system requirements:
        {example_reqs}

        And the following example system designs:
        {example_designs}

        Also, use the following database structure as a reference:
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
    
def create_verification_requirements_models(system_requirements: str, example_system_requirements: str, example_verification_requirements: Dict[str, Dict[str, List[Dict[str, str]]]], example_system_designs: Dict[str, Dict[str, List[Dict[str, str]]]]) -> str:
    """Generate verification requirements and models based on the given system requirements and example verification requirements."""
    try:
        query_text = f"""
        Generate verification requirements and models based on the given system requirements. The provided example system requirements, verification requirements, and system designs are for structure reference only. Do not use the example content directly.

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
    # Test the init function
    test_key = "YOUR_API_KEY_HERE"
    initialize_api(test_key)

    # Call the table list function directly for testing
    tables = list_all_tables()
    print(f"Tables returned: {tables}")
    
    # Optionally, we can fetch the structure too
    structure = fetch_table_structure()
    print("Table Structure:")
    print(structure)
