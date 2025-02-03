# api_integration.py
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
        Generate system designs based on the given system requirements. The provided example system designs and their corresponding system requirements are for structure reference only. Do not use the example content directly.

        Example System Requirements (for structure reference only):
        {example_system_requirements}

        Example System Designs (for structure reference only):
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
