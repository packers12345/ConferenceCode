import psycopg2
import google.generativeai as genai
import spacy
import re
from typing import Dict, List, Any
import PyPDF2  # Import the PyPDF2 library
from io import BytesIO

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")


def initialize_api(api_key: str) -> bool:
    """Initialize the Gemini API."""
    if not api_key:
        print("No API key provided.")
        return False
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
        # For extra safety, use regex to validate the table name (alphanumeric and underscore)
        if not re.match(r'^\w+$', table_name):
            raise ValueError("Invalid table name format.")
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
    Use regex to detect a table name mentioned in user_text.
    Example: if user_text contains 'table system_requirements', returns 'system_requirements'.
    """
    pattern = re.compile(r'\btable\s+([a-zA-Z0-9_]+)', re.IGNORECASE)
    match = pattern.search(user_text)
    if match:
        return match.group(1)
    return ""


def enhance_user_requirements(user_text: str) -> str:
    """
    Process and enhance the free-form user input using NLP.
    Extracts key phrases and entities to form a more precise prompt.
    """
    doc = nlp(user_text)

    # Extract noun chunks and named entities as key phrases
    key_phrases = set(chunk.text.strip() for chunk in doc.noun_chunks)
    key_phrases.update(ent.text.strip() for ent in doc.ents)

    enhanced_text = user_text.strip()
    if key_phrases:
        enhanced_text += "\nKey concepts: " + ", ".join(key_phrases)

    if len(user_text.split()) < 20:
        enhanced_text += "\n[Note: The input is brief; more detail may yield a richer design.]"

    print("Enhanced User Requirements:")
    print(enhanced_text)
    return enhanced_text


def extract_text_from_pdf(pdf_file: BytesIO) -> str:
    """Extract text from the given PDF file."""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


def generate_system_designs(
    user_requirements: str,
    examples: Any = None,
    pdf_data: BytesIO = None
) -> str:
    """Generate a concise system design document (500 words) incorporating provided data."""
    if not isinstance(examples, dict):
        print("Warning: 'examples' parameter is not a dictionary. Using default examples.")
        examples = {
            "example_reqs": "Example system requirements: [Default structured requirements].",
            "example_designs": "Example system designs: [Detailed design example]."
        }

    try:
        processed_requirements = enhance_user_requirements(user_requirements)

        table_structure = fetch_table_structure()
        referenced_table = detect_table_name(user_requirements)
        table_data_string = ""
        if referenced_table:
            rows = fetch_specific_table(referenced_table, limit=5)
            if rows:
                table_data_string = f"Sample rows from '{referenced_table}':\n"
                for i, row in enumerate(rows, start=1):
                    table_data_string += f"Row {i}: {row}\n"
            else:
                table_data_string = f"No data found for table '{referenced_table}'.\n"

        if pdf_data:
            pdf_text = extract_text_from_pdf(pdf_data)
            processed_requirements += f"\nPDF data: {pdf_text}"
        else:
            print("No PDF data provided; skipping PDF extraction.")

        # Build a concise prompt (roughly 500-1000 words)
        query_text = f"""
User Requirements (enhanced):
{processed_requirements}

Reference Requirements:
{examples.get("example_reqs", "")}

Reference Designs:
{examples.get("example_designs", "")}

Database Structure:
{table_structure}

{table_data_string}

Generate a concise system design document (500 words) that includes:
1. A mathematical description of the system requirements.
2. Acceptable system designs with formal proofs (using key properties and homomorphism).
3. Unacceptable designs with proofs outlining discrepancies.
4. Recommendations for improvement.
5. A formal proof of homomorphism demonstrating equivalence between requirements and designs.

Ensure the document is self-contained and integrates the user input, database data, and PDF content if provided.
        """

        print("Final Query Text for System Designs:")
        print(query_text)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(query_text)
        return response.text.strip()

    except Exception as e:
        return f"Error in generating system designs: {str(e)}"


def create_verification_requirements_models(
    system_requirements: str,
    examples: Any = None,
    pdf_data: BytesIO = None
) -> str:
    """Generate a concise verification requirements document (500 words) integrating provided data."""
    if not isinstance(examples, dict):
        print("Warning: 'examples' parameter is not a dictionary. Using default examples.")
        examples = {
            "example_system_reqs": "Example system requirements: [Structured requirements].",
            "example_verif_reqs": {"verification": {"details": [{"example": "verification structure"}]}},
            "example_designs": {"design": {"details": [{"example": "system design structure"}]}}
        }

    try:
        processed_requirements = enhance_user_requirements(system_requirements)

        if pdf_data:
            pdf_text = extract_text_from_pdf(pdf_data)
            processed_requirements += f"\nPDF data: {pdf_text}"
        else:
            print("No PDF data provided; skipping PDF extraction.")

        query_text = f"""
Enhanced System Requirements:
{processed_requirements}

Reference Requirements:
{examples.get("example_system_reqs", "")}

Reference Verification Examples:
{examples.get("example_verif_reqs", "")}

Reference Designs:
{examples.get("example_designs", "")}

Generate a concise verification requirements document (500 words) that includes:
1. Detailed verification problem spaces with proofs of morphism to the system requirements.
2. Verification models with proofs indicating adherence to these problem spaces.
3. A formal yes/no proof of homomorphism demonstrating equivalence between system designs and verification requirements.

Ensure the output is self-contained and integrates all provided data.
        """

        print("Final Query Text for Verification Requirements:")
        print(query_text)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(query_text)
        return response.text.strip()
    except Exception as e:
        return f"Error in generating verification requirements and models: {str(e)}"


def get_traceability(
    system_requirements: str,
    example_system_requirements: str,
    example_system_designs: Dict[str, Dict[str, List[Dict[str, str]]]]
) -> str:
    """Generate traceability and proof based on the given system requirements and example system designs in 500 words."""
    try:
        query_text = f"""
Generate traceability and proof based on the given system requirements. The provided example system designs and their corresponding system requirements are for structure reference only. Do not use the example content directly.

Example System Requirements (for structure reference only):
{example_system_requirements}

Example System Designs (for structure reference only):
{example_system_designs}

System Requirements: {system_requirements}

Please provide in 500 words:
1. Traceability matrix.
2. Proof of traceability.
        """
        model = genai.GenerativeModel("gemini-1.0-pro")
        response = model.generate_content(query_text)
        return response.text.strip()
    except Exception as e:
        return f"Error in generating traceability: {str(e)}"


def get_verification_conditions(
    system_requirements: str,
    example_system_requirements: str,
    example_verification_requirements: Dict[str, Dict[str, List[Dict[str, str]]]],
    example_system_designs: Dict[str, Dict[str, List[Dict[str, str]]]]
) -> str:
    """Generate verification conditions based on the given system requirements and example verification requirements in 500 words."""
    try:
        query_text = f"""
Generate verification conditions based on the given system requirements. The provided example system requirements, verification requirements, and system designs are for structure reference only. Do not use the example content directly.

Example System Requirements (for structure reference only):
{example_system_requirements}

Example Verification Requirements (for structure reference only):
{example_verification_requirements}

Example System Designs (for structure reference only):
{example_system_designs}

System Requirements: {system_requirements}

Please provide in 500 words:
1. Type of homomorphism (Homomorphism, Isomorphism, Identity isomorphism, Parameter morphism), plus clear explanation.
2. Verification requirement problem space (selectable), plus clear explanation.
3. Proof of the type of homomorphism and verification requirement problem space.
        """
        model = genai.GenerativeModel("gemini-1.0-pro")
        response = model.generate_content(query_text)
        return response.text.strip()
    except Exception as e:
        return f"Error in generating verification conditions: {str(e)}"


if __name__ == "__main__":
    # Initialize the API with a test key.
    test_key = "X"
    if not initialize_api(test_key):
        print("Failed to initialize API. Exiting.")
    else:
        # Quick check: list tables and structure.
        tables = list_all_tables()
        print(f"Tables returned: {tables}")

        structure = fetch_table_structure()
        print("Table Structure:")
        print(structure)

        # Example usage with PDF:
        user_input = (
            "I need a system design for a smart home energy management system that handles sensor data, "
            "optimizes energy usage, and allows remote control. Please consider the information provided in the attached document."
        )

        # Example reference texts bundled into a dictionary for system design.
        examples_design = {
            "example_reqs": "Example system requirements: [Structured requirements similar to those from the dissertation].",
            "example_designs": "Example system designs: [Detailed design example]."
        }

        try:
            with open("C:\\Users\\bharg\\Downloads\\Wach_PF_D_2023 (2).pdf", "rb") as pdf_file:
                pdf_data = BytesIO(pdf_file.read())
        except FileNotFoundError:
            pdf_data = None
            print("PDF file not found! Example will run without PDF data.")

        design_output = generate_system_designs(user_input, examples_design, pdf_data)
        print("\nGenerated System Design Document:")
        print(design_output)

        examples_verif = {
            "example_system_reqs": "Example system requirements: [Structured requirements based on the dissertation].",
            "example_verif_reqs": {"verification": {"details": [{"example": "verification requirement structure"}]}},
            "example_designs": {"design": {"details": [{"example": "system design structure"}]}}
        }
        verification_output = create_verification_requirements_models(user_input, examples_verif, pdf_data)
        print("\nGenerated Verification Requirements and Models:")
        print(verification_output)

        # Example usage for traceability.
        example_system_requirements = "Example system requirements: [Structured requirements for traceability]."
        example_system_designs = {
            "design": {
                "details": [
                    {"example": "system design structure for traceability"}
                ]
            }
        }
        traceability_output = get_traceability(user_input, example_system_requirements, example_system_designs)
        print("\nGenerated Traceability and Proof:")
        print(traceability_output)

        # Example usage for verification conditions.
        example_verification_requirements = {
            "verification": {
                "details": [
                    {"example": "verification requirement structure for conditions"}
                ]
            }
        }
        verification_conditions_output = get_verification_conditions(
            user_input,
            example_system_requirements,
            example_verification_requirements,
            example_system_designs
        )
        print("\nGenerated Verification Conditions:")
        print(verification_conditions_output)




