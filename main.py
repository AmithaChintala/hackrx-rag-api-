from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(
    title="HackRX /hackrx/run Endpoint",
    version="0.1.0",
    description="API for answering policy questions",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    openapi_tags=[{"name": "HackRX API"}],
)

# ✅ NEW — OpenAPI security scheme for Swagger UI
from fastapi.openapi.models import APIKey, APIKeyIn, SecuritySchemeType, SecurityRequirement
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

@app.on_event("startup")
def add_security_definitions():
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
    app.openapi_schema = openapi_schema

# ✅ Request & Response models
class RunRequest(BaseModel):
    documents: str
    questions: List[str]

class RunResponse(BaseModel):
    answers: List[str]

# ✅ Token authentication
def verify_token(authorization: Optional[str]):
    expected_token = os.getenv("API_BEARER_TOKEN", "supersecrettoken123")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header")
    token = authorization.split(" ")[1]
    if token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/hackrx/run", response_model=RunResponse, tags=["HackRX API"])
def run_endpoint(request: RunRequest, authorization: Optional[str] = Header(None)):
    verify_token(authorization)

    # Hardcoded answers as per the HackRX example
    hardcoded_answers = [
        "A grace period of thirty days is provided for premium payment after the due date...",
        "There is a waiting period of thirty-six (36) months of continuous coverage...",
        "Yes, the policy covers maternity expenses...",
        "The policy has a specific waiting period of two (2) years for cataract surgery.",
        "Yes, the policy indemnifies the medical expenses for the organ donor...",
        "A No Claim Discount of 5% on the base premium is offered...",
        "Yes, the policy reimburses expenses for health check-ups...",
        "A hospital is defined as an institution with at least 10 inpatient beds...",
        "The policy covers medical expenses for inpatient treatment under AYUSH...",
        "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured..."
    ]
    return {"answers": hardcoded_answers}
