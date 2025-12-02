import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import ParsedResult, CommentData
from typing import List
import json
import os

# Initialize App
app = FastAPI(title="Achieve Quiz Backend")

# CORS (Allow Frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock AI Logic (Replace with real Gemini code if API Key exists)
async def mock_gemini_parse(text: str, answer: str) -> List[ParsedResult]:
    # This simulates AI extracting data
    print(f"Analyzing text for answer: {answer}")
    return [
        ParsedResult(username="Demo User 1", answer=answer, is_correct=True, timestamp="2024-03-20T10:00:00Z"),
        ParsedResult(username="Wrong User", answer="Wrong", is_correct=False, timestamp="2024-03-20T10:05:00Z")
    ]

@app.get("/")
def home():
    return {"status": "Backend is Running!"}

@app.post("/api/parse-comments", response_model=List[ParsedResult])
async def parse_comments(data: CommentData):
    try:
        # Here we connect to Gemini
        results = await mock_gemini_parse(data.raw_text, data.correct_answer)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run on 0.0.0.0 to be accessible in Codespaces
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)