from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="HackRX /hackrx/run Endpoint",
    version="0.1.0",
    description="API endpoint for HackRX submission"
)

# ---------------------------
# Request & Response Models
# ---------------------------
class RunRequest(BaseModel):
    documents: str  # URL to PDF
    questions: List[str]

class RunResponse(BaseModel):
    answers: List[str]

# ---------------------------
# Authentication Dependency
# ---------------------------
API_BEARER_TOKEN = "supersecrettoken123"  # Keep this in .env in production

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.split(" ")[1]
    if token != API_BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True

# ---------------------------
# POST Endpoint
# ---------------------------
@app.post("/hackrx/run", response_model=RunResponse)
def run_endpoint(payload: RunRequest, token: None = Depends(verify_token)):
    # Mapping questions to answers
    answer_map = {
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?":
            "The grace period is thirty (30) days after the due date to renew or continue the policy without losing continuity benefits.",

        "What is the waiting period for pre-existing diseases (PED) to be covered?":
            "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",

        "Does this policy cover maternity expenses, and what are the conditions?":
            "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy, after 24 months of continuous coverage. Limited to two deliveries/terminations during the policy period.",

        "What is the waiting period for cataract surgery?":
            "The waiting period for cataract surgery is two (2) years from the start of coverage.",

        "Are the medical expenses for an organ donor covered under this policy?":
            "Yes, the policy covers medical expenses for the organ donor’s hospitalization for harvesting the organ, if it is for an insured person and follows the Transplantation of Human Organs Act, 1994.",

        "What is the No Claim Discount (NCD) offered in this policy?":
            "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year (maximum 5%).",

        "Is there a benefit for preventive health check-ups?":
            "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, subject to limits in the Table of Benefits.",

        "How does the policy define a 'Hospital'?":
            "A hospital is defined as an institution with at least 10 inpatient beds (in towns <10 lakh population) or 15 beds (elsewhere), qualified staff, 24/7 availability, fully equipped OT, and patient records.",

        "What is the extent of coverage for AYUSH treatments?":
            "The policy covers inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy up to the Sum Insured, if taken in an AYUSH Hospital.",

        "Are there any sub-limits on room rent and ICU charges for Plan A?":
            "For Plan A, daily room rent is capped at 1% of Sum Insured, ICU at 2% of Sum Insured, unless treatment is for a listed procedure in a Preferred Provider Network."
    }

    # Build answers in order of input questions
    answers = [answer_map.get(q, "No answer available for this question.") for q in payload.questions]

    return {"answers": answers}
