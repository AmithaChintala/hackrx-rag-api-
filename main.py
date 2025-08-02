import requests
import fitz  # PyMuPDF
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import os

API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "supersecrettoken123")

app = FastAPI(
    title="HackRX /hackrx/run Endpoint",
    version="0.2.0"
)

class RunRequest(BaseModel):
    documents: str  # URL to PDF
    questions: list[str]

class RunResponse(BaseModel):
    answers: list[str]

def download_pdf(url: str, save_path: str):
    """Download PDF from URL"""
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Could not download PDF")
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from PDF"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def find_answer(text: str, question: str) -> str:
    """Naive keyword search for answer in PDF text"""
    q_words = question.lower().split()
    lines = text.split("\n")
    for line in lines:
        if any(word in line.lower() for word in q_words):
            return line.strip()
    return "Answer not found in document."

@app.post("/hackrx/run", response_model=RunResponse)
def run_endpoint(request: RunRequest, authorization: str = Header(None)):
    # Auth check
    if authorization != f"Bearer {API_BEARER_TOKEN}":
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    # Download PDF
    pdf_path = "temp.pdf"
    download_pdf(request.documents, pdf_path)

    # Extract text
    pdf_text = extract_text_from_pdf(pdf_path)

    # Find answers
    answers = [find_answer(pdf_text, q) for q in request.questions]

    return RunResponse(answers=answers)
