import os
from flask import Flask, render_template, request, jsonify, session
from io import BytesIO
import api_integration  # Updated integration module with new PDF table extraction

# Set your API key as an environment variable so the API integration module finds it
os.environ["GOOGLE_API_KEY"] = "AIzaSyDR1xfxu_89IzzLboUZ3i3U_R5xJUQZqEQ"  # Replace with your actual API key

app = Flask(__name__)
app.secret_key = "VT202527"  # Replace with your own secret key

# Automatically load the PDF training data at startup
pdf_path = "C:\\Users\\bharg\\Downloads\\Wach_PF_D_2023 (2).pdf"
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
    session["conversation"] = []
    return render_template("index.html", conversation=session["conversation"])

@app.route("/send_combined", methods=["POST"])
def send_combined():
    """
    This endpoint retrieves both system design and verification requirements in one call.
    """
    prompt = request.form.get("prompt", "").strip()
    if not prompt:
        return jsonify({"response": "Please enter a prompt."})
    
    # Example dictionaries for the two types of requirements
    examples_design = {
        "example_reqs": "Example system requirements: [Structured requirements based on the dissertation].",
        "example_designs": "Example system designs: [Detailed design example]."
    }
    examples_verif = {
        "example_system_reqs": "Example system requirements: [Structured requirements based on the dissertation].",
        "example_verif_reqs": {"verification": {"details": [{"example": "verification requirement structure"}]}},
        "example_designs": {"design": {"details": [{"example": "system design structure"}]}}
    }
    
    try:
        system_design_output = api_integration.generate_system_designs(prompt, examples_design, pdf_data)
    except Exception as e:
        system_design_output = f"Error: {str(e)}"
    
    try:
        verification_output = api_integration.create_verification_requirements_models(prompt, examples_verif, pdf_data)
    except Exception as e:
        verification_output = f"Error: {str(e)}"
    
    # Update conversation history (optional)
    conversation = session.get("conversation", [])
    conversation.append({"sender": "User", "text": prompt})
    conversation.append({"sender": "Assistant", "text": (
        f"System Design:\n{system_design_output}\n\n"
        f"Verification Requirements:\n{verification_output}"
    )})
    session["conversation"] = conversation

    return jsonify({
        "system_design": system_design_output,
        "verification_requirements": verification_output
    })

if __name__ == "__main__":
    app.run(debug=True)
