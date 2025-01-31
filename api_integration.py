import google.generativeai as genai
from typing import Dict, List

def initialize_api(api_key: str) -> bool:
    """Configure the Gemini API with the provided API key."""
    try:
        genai.configure(api_key=api_key)
        print("Gemini API initialized successfully.")
        return True
    except Exception as e:
        print(f"Error initializing Gemini API: {e}")
        return False

def generate_system_designs(system_requirements: str, example_system_requirements: str, example_system_designs: Dict[str, Dict[str, List[Dict[str, str]]]]) -> str:
    """Generate system designs based on the given system requirements and example system designs."""
    try:
        query_text = f"""
        Generate system designs based on the given system requirements. Use the following example system designs and their corresponding system requirements as a reference:

        Example System Requirements:
        {example_system_requirements}

        Example System Designs:
        {example_system_designs}

        System Requirements: {system_requirements}

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
