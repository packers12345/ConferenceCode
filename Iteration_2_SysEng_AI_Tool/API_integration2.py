import pypyodbc as odbc  # pip install pypyodbc
import google.generativeai as genai
import spacy
import re
from typing import Dict, List, Any
import PyPDF2  # Import the PyPDF2 library
from io import BytesIO
from graphviz import Digraph  # For image visualization

'''
Please make sure to input your API key in the main function for testing and ask me for any credentials for the MS DB.
'''

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
    """Establish a connection to the MS SQL Server database using ODBC."""
    try:
        conn = odbc.connect(
            "Driver={ODBC Driver 18 for SQL Server};"
            "Server= X;"
            "Database=HumeDatabaseMS;"
            "Uid=sa;"
            "Pwd=X;"
            "TrustServerCertificate=XXXXX;"
            "Connection Timeout=300;"
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def list_all_tables() -> List[str]:
    """Retrieve a list of all tables in the 'dbo' schema."""
    conn = connect_to_db()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        if tables:
            print(f"Tables have been retrieved successfully: {tables}")
        else:
            print("No tables found in the 'dbo' schema.")

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
                SELECT COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{table}';
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
        if not re.match(r'^\w+$', table_name):
            raise ValueError("Invalid table name format.")
        query = f"SELECT TOP {limit} * FROM {table_name};"
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
        for page in pdf_reader.pages:
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
1. A mathematical description of the system requirements (use LaTeX for any math equations, e.g. $$E=mc^2$$, have the tables as normal).
2. Acceptable system designs with formal proofs (using key properties and homomorphism).
3. Unacceptable designs with proofs outlining discrepancies.
4. Recommendations for improvement.
5. A formal proof of homomorphism demonstrating equivalence between requirements and designs.

IMPORTANT:
- Do NOT use any generic or fallback examples unless specified.
- Clearly label each section with appropriate headings.
- Ensure any DEFINED mathematical expressions are formatted in LaTeX.
- Keep the response self-contained and data-driven.
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

IMPORTANT:
- Do NOT use any generic or fallback examples unless specified.
- Clearly label every section (for example, 'Verification Problem Spaces', 'Verification Models', etc.).
- Format any DEFINED mathematical expressions correctly. 
- Keep the response self-contained and data-driven.
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

Please provide your answer in clearly labeled sections. Include:
1. A traceability matrix that is formatted in a clean table (no dashes or spaces or blank rows), with the system requirements on one axis and the system designs on the other.
2. A proof of traceability explanation that follows the martix table under it.

IMPORTANT:
- Do NOT use any generic or fallback examples unless specified.
- Format any DEFINED mathematical expressions in LaTeX (enclose equations in Latex).
- Clearly label each section with headers (e.g., "Traceability Matrix", "Proof of Traceability").
- Ensure the table is neatly formatted, accounting for missing data.
        """
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
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

Please provide your answer in clearly labeled sections. Include:
1. A description of the type of homomorphism (e.g., Homomorphism, Isomorphism, Identity isomorphism, Parameter morphism) along with a clear explanation.
2. A discussion of the verification requirement problem space with clear definitions.
3. A proof of the type of homomorphism and the verification requirement problem space.

IMPORTANT:
- Do NOT use any generic or fallback examples unless specified.
- Format any DEFINED mathematical expressions in LaTeX if needed.
- Clearly label each section with headers.
- Keep the response self-contained and data-driven.
        """
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(query_text)
        return response.text.strip()
    except Exception as e:
        return f"Error in generating verification conditions: {str(e)}"

# New function: Build morphism graph data using actual database and PDF content.
def build_morphism_graph_data(user_requirements: str, pdf_data: BytesIO = None) -> dict:
    """
    Build a dictionary for graph visualization from actual data.
    - Extracts key concepts from the user requirements.
    - Uses database table structure to add database-related nodes.
    - Adds a PDF node if PDF data is provided.
    - Adds nodes for system designs, verification requirements, and models.
    """
    nodes = []
    edges = []

    # Node for User Requirements
    enhanced_req = enhance_user_requirements(user_requirements)
    nodes.append({"id": "SR", "label": "User Requirements"})

    # Build database-related nodes
    table_structure = fetch_table_structure()
    if table_structure:
        nodes.append({"id": "DB", "label": "Database Tables"})
        for table in table_structure:
            table_node_id = f"DB_{table}"
            nodes.append({"id": table_node_id, "label": table})
            edges.append({"from": "DB", "to": table_node_id, "label": "contains"})
            if table.lower() in user_requirements.lower():
                edges.append({"from": "SR", "to": table_node_id, "label": "references"})
    
    # Add a PDF node if pdf_data is provided
    if pdf_data:
        pdf_text = extract_text_from_pdf(pdf_data)
        nodes.append({"id": "PDF", "label": "PDF Document"})
        edges.append({"from": "SR", "to": "PDF", "label": "details in"})

    # Add nodes for system design and verification artifacts
    nodes.extend([
        {"id": "SD", "label": "System Designs"},
        {"id": "VR", "label": "Verification Requirements"},
        {"id": "VM", "label": "Verification Models"}
    ])

    # Add edges representing the morphism relationships
    edges.extend([
        {"from": "SR", "to": "SD", "label": "design mapping"},
        {"from": "SD", "to": "VM", "label": "verification mapping"},
        {"from": "SR", "to": "VR", "label": "verification derivation"},
        {"from": "VR", "to": "VM", "label": "morphism proof"}
    ])

    return {"nodes": nodes, "edges": edges}

# New function: Generate an image visualization of morphisms using Graphviz.
def generate_morphism_graph(morphism_data: dict, output_format: str = 'png') -> Digraph:
    """
    Generates a visualization for morphisms using Graphviz.
    `morphism_data` should be a dictionary with keys "nodes" and "edges".
    """
    dot = Digraph(comment='Morphism Visualization')
    
    for node in morphism_data.get("nodes", []):
        dot.node(node['id'], node.get('label', node['id']))
    
    for edge in morphism_data.get("edges", []):
        dot.edge(edge['from'], edge['to'], label=edge.get('label', ''))
    
    dot.render('morphism_visualization', format=output_format, cleanup=True)
    return dot

if __name__ == "__main__":
    test_key = "X"
    if not initialize_api(test_key):
        print("Failed to initialize API. Exiting.")
    else:
        tables = list_all_tables()
        print(f"Tables returned: {tables}")

        structure = fetch_table_structure()
        print("Table Structure:")
        print(structure)

        user_input = (
            "I need a system design for a smart home energy management system that handles sensor data, "
            "optimizes energy usage, and allows remote control. Please consider the information provided in the attached document."
        )

        examples_design = {
            "example_reqs": "Example system requirements: [Structured requirements similar to those from the dissertation].",
            "example_designs": "Example system designs: [Detailed design example]."
        }

        try:
            with open("C:\\Users\\bharg\\Downloads\\Wach_PF_D_2023_main.pdf", "rb") as pdf_file:
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

        example_system_requirements = "Example system requirements: [Structured requirements for traceability]."
        example_system_designs = {"design": {"details": [{"example": "system design structure for traceability"}]}}
        traceability_output = get_traceability(user_input, example_system_requirements, example_system_designs)
        print("\nGenerated Traceability and Proof:")
        print(traceability_output)

        example_verification_requirements = {
            "verification": {"details": [{"example": "verification requirement structure for conditions"}]}
        }
        verification_conditions_output = get_verification_conditions(
            user_input,
            example_system_requirements,
            example_verification_requirements,
            example_system_designs
        )
        print("\nGenerated Verification Conditions:")
        print(verification_conditions_output)
        
        morphism_data = build_morphism_graph_data(user_input, pdf_data)
        graph = generate_morphism_graph(morphism_data)
        print("\nGenerated Morphism Visualization Graph DOT Source:")
        print(graph.source)
