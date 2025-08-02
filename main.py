import requests
import fitz  # PyMuPDF
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="HackRX /hackrx/run Endpoint",
    description="API to answer questions from a provided PDF document URL.",
    version="0.2.0"
)

API_BEARER_TOKEN = "supersecrettoken123"  # You can keep it in .env in production


class RunRequest(BaseModel):
    documents: str  # URL to PDF
    questions: List[str]


class RunResponse(BaseModel):
    answers: List[str]


@app.post("/hackrx/run", response_model=RunResponse, responses={
    200: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
                    "answers": [
                        "The grace period is thirty (30) days after the due date to renew or continue the policy without losing continuity benefits.",
                        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
                    ]
                }
            }
        }
    },
    401: {"description": "Missing or invalid Authorization header"}
})
def run_endpoint(request: RunRequest, authorization: Optional[str] = Header(None)):
    # Authorization check
    if not authorization or not authorization.startswith("Bearer ") or authorization.split(" ")[1] != API_BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    # Download PDF
    try:
        pdf_response = requests.get(request.documents)
        pdf_response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading PDF: {str(e)}")

    # Parse PDF
    try:
        pdf_bytes = pdf_response.content
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF: {str(e)}")

    # Dummy QA logic — Replace with real NLP/LLM
    answers = []
    for q in request.questions:
        if "grace period" in q.lower():
            answers.append("The grace period is thirty (30) days after the due date to renew or continue the policy without losing continuity benefits.")
        elif "waiting period" in q.lower() and "pre-existing" in q.lower():
            answers.append("There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.")
        else:
            answers.append(f"No exact match found for: {q}")

    return {"answers": answers}
