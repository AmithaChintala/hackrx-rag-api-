from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os

app = FastAPI(
    title="HackRX /hackrx/run Endpoint",
    version="0.1.0",
    description="API for answering policy questions from PDF documents."
)

security = HTTPBearer()

API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "supersecrettoken123")

class RunRequest(BaseModel):
    documents: str  # URL to PDF
    questions: list[str]

class RunResponse(BaseModel):
    answers: list[str]

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme != "Bearer" or credentials.credentials != API_BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header"
        )

@app.post("/hackrx/run", response_model=RunResponse)
def run_endpoint(payload: RunRequest, token: None = Depends(verify_token)):
    # temporary hardcoded answers
    answers = [f"Answer for: {q}" for q in payload.questions]
    return {"answers": answers}
