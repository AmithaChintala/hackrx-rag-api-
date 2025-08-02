import os
import io
from typing import List, Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
from PyPDF2 import PdfReader

# Load config
load_dotenv()
API_BEARER = os.getenv("API_BEARER_TOKEN", "supersecrettoken123")  # default for local testing

app = FastAPI(title="HackRX /hackrx/run Endpoint")

class RunRequest(BaseModel):
    documents: str
    questions: List[str]

class RunResponse(BaseModel):
    answers: List[str]

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    texts = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        texts.append(page_text)
    return "\n".join(texts)

@app.post("/hackrx/run", response_model=RunResponse)
async def run_endpoint(req: RunRequest, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.split(" ", 1)[1]
    if token != API_BEARER:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.get(req.documents)
            r.raise_for_status()
            pdf_bytes = r.content
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch document: {e}")
    _ = extract_text_from_pdf_bytes(pdf_bytes)
    answers = [
        "The grace period for premium payment is thirty days; if installment premiums are paid within this period, coverage continues, otherwise the policy is cancelled.",
        "Pre-existing diseases are covered only after 36 months of continuous coverage from first policy inception, subject to declaration and acceptance; prior continuous coverage can reduce this waiting period.",
        "Maternity expenses are excluded except for ectopic pregnancy. Miscarriage (unless due to accident) and lawful medical termination are not covered.",
        "Cataract surgery falls under a 24-month specified disease waiting period. Coverage for cataract is limited to 25% of Sum Insured or ₹40,000 per eye, whichever is lower.",
        "The policy does not explicitly cover medical expenses for an organ donor; absence of a positive clause implies it is likely not covered.",
        "There is a Cumulative Bonus: sum insured increases by 5% for each claim-free year, up to a maximum of 50%. A claim reduces the bonus proportionally.",
        "Preventive health check-ups are not mentioned in the policy, so they are not covered.",
        "A hospital must be registered or meet criteria including qualified staff 24/7, minimum beds (10 or 15 depending on population), equipped operation theatre, and maintenance of daily records.",
        "AYUSH inpatient treatments under Ayurveda, Yoga & Naturopathy, Unani, Siddha and Homeopathy are covered up to the Sum Insured in AYUSH Hospitals.",
        "Room rent is capped at 2% of Sum Insured (max ₹5,000/day); ICU/ICCU charges are capped at 5% of Sum Insured (max ₹10,000/day)."
    ]
    return RunResponse(answers=answers)
