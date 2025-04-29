import os
import base64
from flask import Flask, render_template, request, jsonify, session
from io import BytesIO
import api_integration  # This module contains your integrated API, DB, and Graphormer-based visualization functions

# Set your API key from environment variable
api_key = "X"
if not api_key:
    print("WARNING: API_KEY environment variable not set!")
else:
    api_integration.initialize_api(api_key)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "X")  # Get from environment or use default

# Load the PDF training data from environment variable path
pdf_path = "C://Users//X//X//Wach_PF_D_2023_main.pdf"
try:
    with open(pdf_path, "rb") as f:
        pdf_data = BytesIO(f.read())
    print(f"PDF loaded from {pdf_path}")
except Exception as e:
    pdf_data = None
    print(f"Error loading PDF: {e}")

@app.route("/")
def index():
    # Initialize conversation history in session if not present
    if "conversation" not in session:
        session["conversation"] = []
    # Pass an initial null morphism image to the template
    return render_template("index.html", conversation=session.get("conversation", []), morphism_image=None)

@app.route("/combined", methods=["POST"])
def combined():
    """
    Combined endpoint that retrieves outputs from the integration module:
      - System Design
      - Verification Requirements
      - Traceability
      - Verification Conditions
      - And the Morphism Visualization generated.
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
        msg = str(e)
        if "openai.ChatCompletion" in msg:
            msg += " Please run 'openai migrate' or install openai==0.28 to pin to the old version."
        verification_output = f"Error generating verification requirements: {msg}"
    
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
    
    # Generate the system visualization based on user input and generated outputs
    try:
        # Create graph data structure with user requirements
        graph_data = {
            'user_requirements': prompt,  # Pass the user's prompt as requirements
            'nodes': [],  # The API will generate nodes internally
            'edges': []   # The API will generate edges internally
        }
        
        # Generate the visualization using Graphviz for SysML-inspired diagrams
        morphism_image = api_integration.generate_network_visualization(graph_data, pdf_data)
        print("Length of visualization string:", len(morphism_image) if morphism_image else "None")
    except Exception as e:
        morphism_image = None
        print(f"Error generating system visualization: {e}")
        import traceback
        traceback.print_exc()

    # Update conversation history
    conversation = session.get("conversation", [])
    conversation.append({"sender": "User", "text": prompt})
    combined_text = (
        "=== System Design ===\n" + system_design_output + "\n\n" +
        "=== Verification Requirements ===\n" + verification_output + "\n\n" +
        "=== Traceability ===\n" + traceability_output + "\n\n" +
        "=== Verification Conditions ===\n" + verification_conditions_output
    )
    conversation.append({"sender": "Assistant", "text": combined_text})
    session["conversation"] = conversation

    # Return the outputs including the system visualization
    return jsonify({
        "system_design": system_design_output,
        "verification_requirements": verification_output,
        "traceability": traceability_output,
        "verification_conditions": verification_conditions_output,
        # Pass the SVG string directly for frontend rendering
        "system_visual": morphism_image
    })

if __name__ == "__main__":
    # Get port from environment variable for cloud deployment compatibility
    port = int(os.environ.get("PORT", 5000))
    # Set host to 0.0.0.0 to make it accessible outside container
    app.run(host='0.0.0.0', port=5000, debug=False)
