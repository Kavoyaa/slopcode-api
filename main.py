from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv(".env")

# Configure Gemini model
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-pro")

app = Flask(__name__)

# Enable CORS globally (all routes, all origins)
CORS(app, resources={r"/*": {"origins": "*"}})

# Add CORS headers manually to survive Vercel proxy stripping
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/gen", methods=["POST", "OPTIONS"])
def ai_response():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    print("✅ Received a request from frontend")

    data = request.get_json()
    problem = data.get("problem")
    code = data.get("code")

    if not problem or not code:
        return jsonify({"error": "Missing 'problem' or 'code'"}), 400

    prompt = f"""
    You are an AI that powers a website called SlopCode. The website is like LeetCode but the purpose is to write the worst possible code while still being functional.
    You will receive a problem and its solution and give it a slop rating out of 100.

    Slop rating will be higher the more inefficient and creatively bad the code is.

    Here is the problem:
    {problem}

    And here is the solution. Check if it's correct. If it's incorrect, then give it a slop rating of 0.
    {code}

    Generate the output as JSON in the following format: 
    {{ 
        "rating": slop_rating
    }}
    
    DO NOT put this in a code block. Just plain text output.
    """

    try:
        response = model.generate_content(prompt)
        parsed = json.loads(response.text)
        return jsonify(parsed)
    except Exception as e:
        print("error")
        return jsonify({"error": str(e)}), 500


# Required for Vercel deployment
def handler(request, *args, **kwargs):
    return app(request.environ, start_response=None)


if __name__ == "__main__":
    app.run(debug=True)
