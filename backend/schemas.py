from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class LeadCreate(BaseModel):
    email: str = Field(min_length=3)
    company: str = ""
    role: str = ""

class LeadOut(BaseModel):
    id: str
    email: str
    company: str
    role: str
    status: str
    enrichment: dict
    created_at: datetime

class FieldDecision(BaseModel):
    decision: str  # accepted|rejected

class HealthOut(BaseModel):
    status: str
    service: str
    version: str
    llm_mode: str
