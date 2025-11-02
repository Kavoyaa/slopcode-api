
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import re

load_dotenv(".env")

genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-pro")

app = Flask(__name__)
CORS(app)

@app.route("/gen", methods=["POST"])
def ai_response():
    print("Received a request from frontend")
    data = request.get_json()
    problem = data.get("problem")
    code = data.get("code")

    prompt = f"""
    You are an AI that powers a website called SlopCode. The website is like LeetCode but the purpose is to write the worst possible code while still being functional.
    You will receive a problem and its solution and give it a slop rating out of 100.

    Slop rating will be higher the more inefficient and creatively bad the code is.

    Here is the problem:
    {problem}

    And here is the solution. Check if its correct. If its incorrect then give it a slop rating of 0.
    {code}

    Generate the output as JSON in the following format. 
    {{ 
        "rating": slop_rating
    }}
    
    DO NOT put this in a codeblock. just plain text output.
    """




    response = model.generate_content(contents=prompt)

    try:
        parsed = json.loads(response.text)
        return jsonify(parsed)
    except Exception as e:
        print(e)
        return(e)


if __name__ == "__main__":
    app.run()
