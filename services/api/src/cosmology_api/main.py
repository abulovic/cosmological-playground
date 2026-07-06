from fastapi import FastAPI
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


app = FastAPI(
    title="Cosmology Lens API",
    version="0.1.0",
    description="Evidence-bearing analysis of cosmological commitments represented in text.",
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="cosmology-lens-api", version=app.version)
