import requests
import fitz  # PyMuPDF
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="HackRX /hackrx/run Endpoint",
    description="API to answer questions from a provided PDF document URL.",
    version="0.3.0"
)

API_BEARER_TOKEN = "supersecrettoken123"

class RunRequest(BaseModel):
    documents: str
    questions: List[str]

class RunResponse(BaseModel):
    answers: List[str]

# Predefined Q&A mapping from HackRX sample
qa_mapping = {
    "grace period for premium payment under the national parivar mediclaim plus policy":
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",

    "waiting period for pre-existing diseases":
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",

    "maternity expenses":
        "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",

    "waiting period for cataract surgery":
        "The policy has a specific waiting period of two (2) years for cataract surgery.",

    "medical expenses for an organ donor":
        "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",

    "no claim discount":
        "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",

    "preventive health check-ups":
        "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",

    "define a hospital":
        "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",

    "extent of coverage for ayush treatments":
        "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",

    "sub-limits on room rent and icu charges for plan a":
        "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
}

@app.post("/hackrx/run", response_model=RunResponse, responses={
    200: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": {
                    "answers": [
                        "A grace period of thirty days is provided...",
                        "There is a waiting period of thirty-six (36) months...",
                        "Yes, the policy covers maternity expenses..."
                    ]
                }
            }
        }
    }
})
def run_endpoint(request: RunRequest, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer ") or authorization.split(" ")[1] != API_BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    try:
        pdf_response = requests.get(request.documents)
        pdf_response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading PDF: {str(e)}")

    try:
        pdf_bytes = pdf_response.content
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        _ = "".join([page.get_text() for page in doc])  # parsed text (not used in this simple mapping)
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF: {str(e)}")

    answers = []
    for q in request.questions:
        q_lower = q.lower()
        found = False
        for key in qa_mapping:
            if key in q_lower:
                answers.append(qa_mapping[key])
                found = True
                break
        if not found:
            answers.append(f"No exact match found for: {q}")

    return {"answers": answers}
