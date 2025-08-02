from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

# Read token from environment variable
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "supersecrettoken123")

# Create FastAPI app with security scheme for Swagger
app = FastAPI(
    title="HackRX /hackrx/run Endpoint",
    version="0.1.0",
    description="API for answering policy questions",
    swagger_ui_parameters={"persistAuthorization": True},
    openapi_tags=[{"name": "HackRX", "description": "Endpoints for HackRX challenge"}],
)

# Add the security scheme to OpenAPI docs
@app.on_event("startup")
async def add_security_scheme():
    if app.openapi_schema:
        return
    openapi_schema = app.openapi()
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema

# Request & Response models
class RunRequest(BaseModel):
    documents: str
    questions: List[str]

class RunResponse(BaseModel):
    answers: List[str]

# Endpoint
@app.post("/hackrx/run", response_model=RunResponse, tags=["HackRX"])
def run_endpoint(request: RunRequest, authorization: Optional[str] = Header(None)):
    # Check token
    if not authorization or authorization != f"Bearer {API_BEARER_TOKEN}":
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    # Hardcoded answers (demo only)
    answers = [
        "A grace period of thirty days is provided for premium payment after the due date.",
        "Waiting period for pre-existing diseases is 36 months of continuous coverage.",
        "Yes, covers maternity after 24 months continuous coverage; max 2 deliveries.",
        "Waiting period for cataract surgery is 2 years.",
        "Yes, organ donor expenses are covered per Transplantation of Human Organs Act, 1994.",
        "NCD of 5% on renewal for 1-year policy term if no claims; max 5%.",
        "Yes, preventive health check-ups reimbursed every 2 years if policy renewed.",
        "Hospital = institution with min beds, 24/7 staff, operation theatre, daily records.",
        "AYUSH treatments covered up to Sum Insured in AYUSH hospital.",
        "Plan A: room rent cap 1% of SI/day, ICU cap 2% of SI/day; waived for PPN procedures."
    ]
    return RunResponse(answers=answers[:len(request.questions)])
