import os
import base64
from flask import Flask, render_template, request, jsonify, session
from io import BytesIO
import api_integration  # This module contains your integrated API, DB, and visualization functions

# Set your API key as an environment variable so that the integration module can access it.
os.environ["GOOGLE_API_KEY"] = "AIzaSyANC5TtyaWK7LS1ZiOOGIzZKX4rxHWrJaA"  # Replace with your actual API key

app = Flask(__name__)
app.secret_key = "VT202527"  # Replace with your own secret key

# Automatically load the PDF training data at startup.
pdf_path = "C:\\Users\\bharg\\Downloads\\Wach_PF_D_2023_main.pdf"
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
    # Pass an initial null morphism image to the template.
    return render_template("index.html", conversation=session["conversation"], morphism_image=None)

@app.route("/combined", methods=["POST"])
def combined():
    """
    Combined endpoint that retrieves the following outputs from the integration module:
      - System Design (with clearly labeled sections and LaTeX-formatted math),
      - Verification Requirements (with tables formatted like tabulate and section headers),
      - Traceability (with an ASCII table style for the matrix and clear labels),
      - Verification Conditions (with math rendered in LaTeX and clear section labels),
      - And the Morphism Visualization (generated via Graphviz on the server).
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
    
    # Generate the morphism visualization.
    try:
        morphism_data = api_integration.build_morphism_graph_data(prompt, pdf_data)
        graph = api_integration.generate_morphism_graph(morphism_data)
        # The generate_morphism_graph function saves the image as 'morphism_visualization.png'
        image_path = "morphism_visualization.png"
        with open(image_path, "rb") as image_file:
            morphism_image = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        morphism_image = None
        print(f"Error generating morphism visualization: {e}")

    # Update conversation history.
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

    # Return all outputs as JSON, including the Base64-encoded image.
    return jsonify({
        "system_design": system_design_output,
        "verification_requirements": verification_output,
        "traceability": traceability_output,
        "verification_conditions": verification_conditions_output,
        "morphism_visual": morphism_image
    })

if __name__ == "__main__":
    app.run(debug=True)
