from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Load .env file
load_dotenv(".env")

# Configure Gemini
genai.configure(api_key=os.getenv("API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-pro")

# Create FastAPI app
app = FastAPI()

# Allow all origins (adjust if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000", "http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class GenRequest(BaseModel):
    problem: str
    code: str


@app.post("/gen")
async def generate_rating(req: GenRequest):
    print("✅ Received a request from frontend")

    prompt = f"""
    You are an AI that powers a website called SlopCode. The website is like LeetCode but the purpose is to write the worst possible code while still being functional.
    You will receive a problem and its solution and give it a slop rating out of 100.

    Slop rating will be higher the more inefficient and creatively bad the code is.

    Here is the problem:
    {req.problem}

    And here is the solution. Check if it's correct. If it's incorrect, then give it a slop rating of 0.
    {req.code}

    Generate the output as JSON in the following format:
    {{
        "rating": slop_rating
    }}
    
    DO NOT put this in a code block. Just plain text output.
    """

    try:
        response = model.generate_content(prompt)
        parsed = json.loads(response.text)
        return parsed
    except Exception as e:
        print("❌ Error parsing response:", e)
        return {"error": str(e)}


# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
