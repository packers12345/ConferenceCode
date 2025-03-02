import pypyodbc as odbc  # pip install pypyodbc
import google.generativeai as genai
import spacy
import re
from typing import Dict, List, Any
import PyPDF2  # Import the PyPDF2 library
from io import BytesIO
import base64
import os

# For Graphormer integration and visualization
import numpy as np
import torch
from transformers import GraphormerConfig, GraphormerModel
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA  # principal component analysis

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
    """Establish a connection to the MS SQL Server database using ODBC with environment variables."""
    try:
        # Get database connection parameters from environment variables
        db_server = os.environ.get("DB_SERVER", "57.151.97.31,1433")
        db_name = os.environ.get("DB_NAME", "HumeDatabaseMS")
        db_user = os.environ.get("DB_USER", "sa")
        db_password = os.environ.get("DB_PASSWORD", "HumeDBTheory")
        
        conn = odbc.connect(
            "Driver={ODBC Driver 18 for SQL Server};"
            f"Server={db_server};"
            f"Database={db_name};"
            f"Uid={db_user};"
            f"Pwd={db_password};"
            "TrustServerCertificate=yes;"
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

def generate_system_designs(user_requirements: str, examples: Any = None, pdf_data: BytesIO = None) -> str:
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
1. A mathematical description of the system requirements (use LaTeX for any math equations, e.g. $$E=mc^2$$, and include tables as regular HTML).
2. Acceptable system designs with formal proofs (using key properties and homomorphism).
3. Unacceptable designs with proofs outlining discrepancies.
4. Recommendations for improvement.
5. A formal proof of homomorphism demonstrating equivalence between requirements and designs.

IMPORTANT:
- Do NOT use any generic or fallback examples unless specified.
- Clearly label each section with appropriate headings.
- Ensure any defined mathematical expressions are formatted in LaTeX.
- Keep the response self-contained and data-driven.
        """
        print("Final Query Text for System Designs:")
        print(query_text)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(query_text)
        return response.text.strip()
    except Exception as e:
        return f"Error in generating system designs: {str(e)}"

def create_verification_requirements_models(system_requirements: str, examples: Any = None, pdf_data: BytesIO = None) -> str:
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
- Format any defined mathematical expressions correctly.
- Keep the response self-contained and data-driven.
        """
        print("Final Query Text for Verification Requirements:")
        print(query_text)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(query_text)
        return response.text.strip()
    except Exception as e:
        return f"Error in generating verification requirements and models: {str(e)}"

def get_traceability(system_requirements: str, example_system_requirements: str,
                      example_system_designs: Dict[str, Dict[str, List[Dict[str, str]]]]) -> str:
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
1. A traceability matrix formatted as a clean HTML table (with bold headers and no extraneous rows).
2. A short, spaced proof of traceability explanation that follows the table.

IMPORTANT:
- Do NOT use any generic or fallback examples unless specified.
- Format any defined mathematical expressions in LaTeX.
- Clearly label each section with headers (e.g., "Traceability Matrix", "Proof of Traceability").
- Ensure the table is neatly formatted, accounting for missing data.
        """
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(query_text)
        return response.text.strip()
    except Exception as e:
        return f"Error in generating traceability: {str(e)}"

def get_verification_conditions(system_requirements: str, example_system_requirements: str,
                                example_verification_requirements: Dict[str, Dict[str, List[Dict[str, str]]]],
                                example_system_designs: Dict[str, Dict[str, List[Dict[str, str]]]]) -> str:
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
- Format any defined mathematical expressions in LaTeX if needed.
- Clearly label each section with headers.
- Keep the response self-contained and data-driven.
        """
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(query_text)
        return response.text.strip()
    except Exception as e:
        return f"Error in generating verification conditions: {str(e)}"

def generate_graphormer_visualization(graph_data, pdf_data=None):
    """
    Generates a detailed system-specific graph visualization showing relationships
    between requirements, constraints, verification models and traceability.
    Adaptable to different system types based on user requirements.
    """
    try:
        # Extract requirements and perform deeper analysis
        user_reqs = graph_data.get('user_requirements', '')
        doc = nlp(user_reqs)
        
        # Detect system type from user requirements
        system_type = "Generic System"  # Default system type
        system_id = "SYS"  # Default system ID
        
        # Detect system types based on keywords
        system_keywords = {
            "autonomous vehicle": ("Autonomous Vehicle", "AV"),
            "self-driving": ("Autonomous Vehicle", "AV"),
            "smart home": ("Smart Home System", "SHS"),
            "energy management": ("Energy Management System", "EMS"),
            "healthcare": ("Healthcare System", "HCS"),
            "medical": ("Medical System", "MED"),
            "finance": ("Financial System", "FIN"),
            "banking": ("Banking System", "BNK"),
            "security": ("Security System", "SEC"),
            "manufacturing": ("Manufacturing System", "MFG"),
            "education": ("Education System", "EDU"),
            "retail": ("Retail System", "RET"),
            "transportation": ("Transportation System", "TRN"),
            "logistics": ("Logistics System", "LOG"),
            "communication": ("Communication System", "COM"),
            "network": ("Network System", "NET"),
            "data": ("Data Management System", "DMS"),
            "cloud": ("Cloud System", "CLD"),
            "iot": ("IoT System", "IOT"),
            "robot": ("Robotic System", "ROB")
        }
        
        for keyword, (name, id_code) in system_keywords.items():
            if keyword in user_reqs.lower():
                system_type = name
                system_id = id_code
                break
        
        # Extract technical specifications and requirements
        specs = {
            'performance': [],
            'stability': [], 
            'safety': [],
            'verification': []
        }
        
        # Parse user input for specific requirements
        for sent in doc.sents:
            text = sent.text.lower()
            if any(term in text for term in ['speed', 'acceleration', 'time', 'performance', 'efficiency', 'throughput', 'response']):
                specs['performance'].append(sent.text)
            if any(term in text for term in ['balance', 'stability', 'control', 'reliability', 'robustness', 'consistent']):
                specs['stability'].append(sent.text)
            if any(term in text for term in ['safe', 'emergency', 'protect', 'security', 'privacy', 'backup']):
                specs['safety'].append(sent.text)
            if any(term in text for term in ['verify', 'validate', 'test', 'simulation', 'check', 'audit', 'monitor']):
                specs['verification'].append(sent.text)

        # Define system-specific components with detailed relationships
        nodes = [
            # Core System Layer
            {"id": system_id, "label": system_type, "type": "core", "group": 0},
            
            # Requirements Layer  
            {"id": "SR", "label": f"{system_id} System Requirements", "type": "req", "group": 1},
            {"id": "FR", "label": f"{system_id} Functional Requirements", "type": "req", "group": 1},
            {"id": "NFR", "label": f"{system_id} Non-Functional Requirements", "type": "req", "group": 1},
            
            # Constraints Layer
            {"id": "SC", "label": f"{system_id} Stability Constraints", "type": "constraint", "group": 2},
            {"id": "PC", "label": f"{system_id} Performance Constraints", "type": "constraint", "group": 2},
            {"id": "SAF", "label": f"{system_id} Safety Constraints", "type": "constraint", "group": 2},
            
            # Verification Layer
            {"id": "VM", "label": f"{system_id} Mathematical Model", "type": "verify", "group": 3},
            {"id": "TR", "label": f"{system_id} Traceability Matrix", "type": "verify", "group": 3},
            {"id": "VC", "label": f"{system_id} Verification Conditions", "type": "verify", "group": 3}
        ]

        # Add specific requirement nodes based on extracted specs
        for category, items in specs.items():
            for i, spec in enumerate(items):
                nodes.append({
                    "id": f"{category[:3]}_{i}",
                    "label": spec[:30] + "..." if len(spec) > 30 else spec,
                    "type": "spec",
                    "group": 4
                })

        # Define logical connections showing requirement flow
        edges = [
            # Core system connections
            {"from": system_id, "to": "SR", "label": "defines"},
            {"from": "SR", "to": "FR", "label": "includes"},
            {"from": "SR", "to": "NFR", "label": "includes"},
            
            # Constraint relationships
            {"from": "FR", "to": "SC", "label": "imposes"},
            {"from": "FR", "to": "PC", "label": "imposes"},
            {"from": "FR", "to": "SAF", "label": "imposes"},
            
            # Verification relationships
            {"from": "SC", "to": "VM", "label": "validates"},
            {"from": "PC", "to": "VM", "label": "validates"},
            {"from": "SAF", "to": "VM", "label": "validates"},
            
            # Traceability connections
            {"from": "VM", "to": "TR", "label": "generates"},
            {"from": "TR", "to": "VC", "label": "defines"}
        ]

        # Connect specifications to their respective categories
        for node in nodes:
            if node["type"] == "spec":
                category = node["id"][:3]
                if category == "per":  # Performance
                    edges.append({"from": "PC", "to": node["id"], "label": "specifies"})
                elif category == "sta":  # Stability
                    edges.append({"from": "SC", "to": node["id"], "label": "specifies"})
                elif category == "saf":  # Safety
                    edges.append({"from": "SAF", "to": node["id"], "label": "specifies"})
                elif category == "ver":  # Verification
                    edges.append({"from": "VM", "to": node["id"], "label": "implements"})

        # Create visualization
        plt.figure(figsize=(12, 8))
        
        # Layout nodes in layers with improved spacing
        layers = {0: 0.9, 1: 0.7, 2: 0.5, 3: 0.3, 4: 0.1}  # y-coordinates for each layer
        pos_x = []
        pos_y = []
        
        for node in nodes:
            group = node["group"]
            layer_nodes = sum(1 for n in nodes if n["group"] == group)
            node_index = sum(1 for n in nodes[:nodes.index(node)] if n["group"] == group)
            
            # Calculate position within layer
            x = 0.1 + (node_index + 1) * (0.8 / (layer_nodes + 1))
            y = layers[group]
            
            pos_x.append(x)
            pos_y.append(y)

        # Choose color scheme based on system type
        color_schemes = {
            "AV": {  # Autonomous Vehicle
                'core': '#F08080',    # Light Coral
                'req': '#90EE90',     # Light Green
                'constraint': '#87CEFA',  # Light Sky Blue
                'verify': '#FFD700',   # Gold
                'spec': '#DDA0DD'      # Plum
            },
            "SHS": {  # Smart Home System
                'core': '#20B2AA',    # Light Sea Green
                'req': '#FFB6C1',     # Light Pink
                'constraint': '#B0C4DE',  # Light Steel Blue
                'verify': '#F0E68C',   # Khaki
                'spec': '#D8BFD8'      # Thistle
            },
            "EMS": {  # Energy Management System
                'core': '#3CB371',    # Medium Sea Green
                'req': '#FFDAB9',     # Peach Puff
                'constraint': '#ADD8E6',  # Light Blue
                'verify': '#FFFACD',   # Lemon Chiffon
                'spec': '#E6E6FA'      # Lavender
            },
            # Default color scheme
            "default": {
                'core': '#FF9999',    # Red shade
                'req': '#99FF99',     # Green shade
                'constraint': '#9999FF',  # Blue shade
                'verify': '#FFFF99',   # Yellow shade
                'spec': '#FF99FF'      # Purple shade
            }
        }
        
        # Select color scheme based on system ID, fallback to default
        colors = color_schemes.get(system_id, color_schemes["default"])

        # Draw nodes
        for i, node in enumerate(nodes):
            plt.scatter(pos_x[i], pos_y[i], c=colors[node["type"]], s=100, alpha=0.8, edgecolor='black')
            plt.text(pos_x[i], pos_y[i], node["label"], 
                    fontsize=7, ha='center', va='bottom', wrap=True)

        # Draw edges with arrows
        for edge in edges:
            i = next(i for i, n in enumerate(nodes) if n["id"] == edge["from"])
            j = next(i for i, n in enumerate(nodes) if n["id"] == edge["to"])
            
            # Draw arrow with improved visibility
            plt.annotate("",
                        xy=(pos_x[j], pos_y[j]),
                        xytext=(pos_x[i], pos_y[i]),
                        arrowprops=dict(arrowstyle="->", color="gray", alpha=0.6, lw=1.5))
            
            # Add edge label
            mid_x = (pos_x[i] + pos_x[j]) / 2
            mid_y = (pos_y[i] + pos_y[j]) / 2
            plt.text(mid_x, mid_y, edge["label"], fontsize=6, ha='center', va='center', 
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1))

        plt.title(f"{system_type} Architecture and Requirements Flow", fontsize=14)
        plt.axis('off')
        
        # Convert to Base64
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    except Exception as e:
        print(f"Error in visualization: {e}")
        return None

if __name__ == "__main__":
    test_key = "AIzaSyANC5TtyaWK7LS1ZiOOGIzZKX4rxHWrJaA"
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
        # For demonstration, add the user requirements into the morphism_data so the graph node can display it.
        morphism_data = {
            "user_requirements": user_input,
            "nodes": [{"id": "SR", "label": "User Requirements"}, {"id": "DB", "label": "Database Tables"}],
            "edges": [{"from": "SR", "to": "DB", "label": "references"}]
        }
        
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
        
        # Generate Graphormer-based visualization using the updated morphism_data.
        graph_image_b64 = generate_graphormer_visualization(morphism_data, pdf_data)
        print("\nGenerated Graphormer-based Visualization (Base64):")
        print(graph_image_b64)

