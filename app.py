import os
from flask import Flask, render_template, request, jsonify, session
from io import BytesIO
import api_integration  # This module should contain your integrated API and DB functions

# Set your API key as an environment variable so that the integration module can access it.
os.environ["GOOGLE_API_KEY"] = "X"  # Replace with your actual API key

app = Flask(__name__)
app.secret_key = "X"  # Replace with your own secret key

# Automatically load the PDF training data at startup.
pdf_path = "C:\\Users\\X\\Downloads\\Wach_PF_D_2023 (2).pdf"
try:
    with open(pdf_path, "rb") as f:
        pdf_data = BytesIO(f.read())
    print(f"PDF loaded from {pdf_path}")
except Exception as e:
    pdf_data = None
    print(f"Error loading PDF: {e}")

@app.route("/")
def index():
    # Initialize conversation history in session if not present.
    session["conversation"] = []
    return render_template("index.html", conversation=session["conversation"])

@app.route("/combined", methods=["POST"])
def combined():
    """
    Combined endpoint that retrieves system design, verification requirements,
    traceability, and verification conditions in one call.
    """
    prompt = request.form.get("prompt", "").strip()
    if not prompt:
        return jsonify({"response": "Please enter a prompt."})
    
    # Example dictionaries for system design and verification requirements.
    examples_design = {
        "example_reqs": "Example system requirements: [Structured requirements based on the dissertation].",
        "example_designs": "Example system designs: [Detailed design example]."
    }
    examples_verif = {
        "example_system_reqs": "Example system requirements: [Structured requirements based on the dissertation].",
        "example_verif_reqs": {"verification": {"details": [{"example": "verification requirement structure"}]}},
        "example_designs": {"design": {"details": [{"example": "system design structure"}]}}
    }
    
    # Additional examples for traceability and verification conditions.
    example_system_requirements = "Example system requirements: [Structured requirements based on the dissertation]."
    example_system_designs = {"design": {"details": [{"example": "system design structure"}]}}
    example_verification_requirements = {"verification": {"details": [{"example": "verification requirement structure"}]}}

    # Generate outputs from the integration module.
    try:
        system_design_output = api_integration.generate_system_designs(prompt, examples_design, pdf_data)
    except Exception as e:
        system_design_output = f"Error generating system design: {str(e)}"
    
    try:
        verification_output = api_integration.create_verification_requirements_models(prompt, examples_verif, pdf_data)
    except Exception as e:
        verification_output = f"Error generating verification requirements: {str(e)}"
    
    try:
        traceability_output = api_integration.get_traceability(prompt, example_system_requirements, example_system_designs)
    except Exception as e:
        traceability_output = f"Error generating traceability: {str(e)}"
    
    try:
        verification_conditions_output = api_integration.get_verification_conditions(
            prompt,
            example_system_requirements,
            example_verification_requirements,
            example_system_designs
        )
    except Exception as e:
        verification_conditions_output = f"Error generating verification conditions: {str(e)}"
    
    # Optionally update the conversation history.
    conversation = session.get("conversation", [])
    conversation.append({"sender": "User", "text": prompt})
    combined_text = (
        f"System Design:\n{system_design_output}\n\n"
        f"Verification Requirements:\n{verification_output}\n\n"
        f"Traceability:\n{traceability_output}\n\n"
        f"Verification Conditions:\n{verification_conditions_output}"
    )
    conversation.append({"sender": "Assistant", "text": combined_text})
    session["conversation"] = conversation

    # Return all outputs as JSON.
    return jsonify({
        "system_design": system_design_output,
        "verification_requirements": verification_output,
        "traceability": traceability_output,
        "verification_conditions": verification_conditions_output
    })

if __name__ == "__main__":
    app.run(debug=True)

