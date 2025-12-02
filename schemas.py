from pydantic import BaseModel
from typing import List, Optional

class ScrapeRequest(BaseModel):
    url: str
    expected_answer: str

class ParsedResult(BaseModel):
    username: str
    answer: str
    is_correct: bool
    timestamp: str

class CommentData(BaseModel):
    raw_text: str
    correct_answer: str