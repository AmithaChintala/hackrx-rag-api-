from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import fitz  # PyMuPDF for PDF text extraction
import os

API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "supersecrettoken123")

app = FastAPI(title="HackRX /hackrx/run Endpoint")

class RunRequest(BaseModel):
    documents: str  # URL to PDF
    questions: list[str]

@app.post("/hackrx/run")
async def run_endpoint(
    authorization: str = Header(..., alias="Authorization"),
    documents: str = Form(None),
    questions: str = Form(None),
    file: UploadFile = File(None)
):
    # ✅ Check token
    if not authorization.startswith("Bearer ") or authorization.split(" ")[1] != API_BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    pdf_text = ""

    # Case 1: If URL is provided
    if documents:
        try:
            response = requests.get(documents)
            response.raise_for_status()
            with open("temp.pdf", "wb") as f:
                f.write(response.content)
            pdf_text = extract_text_from_pdf("temp.pdf")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not download PDF: {str(e)}")

    # Case 2: If file is uploaded
    elif file:
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())
        pdf_text = extract_text_from_pdf(file_location)

    else:
        raise HTTPException(status_code=400, detail="No PDF URL or file uploaded")

    # Simple mock answers (replace with RAG logic later)
    answers = ["Answer placeholder for: " + q for q in (questions.split(",") if questions else [])]

    return JSONResponse(content={"answers": answers})

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text
