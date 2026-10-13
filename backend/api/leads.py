import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.schemas import FieldDecision, LeadCreate, LeadOut
from backend.services import enrichment

router = APIRouter()

def to_out(lead) -> LeadOut:
    return LeadOut(id=lead.id, email=lead.email, company=lead.company, role=lead.role,
        status=lead.status, enrichment=json.loads(lead.enrichment_json or "{}"), created_at=lead.created_at)

@router.get("", response_model=list[LeadOut])
async def list_leads(db: AsyncSession = Depends(get_db)):
    return [to_out(l) for l in await enrichment.list_leads(db)]

@router.post("", response_model=LeadOut)
async def create_lead(payload: LeadCreate, db: AsyncSession = Depends(get_db)):
    return to_out(await enrichment.create_lead(db, payload))

@router.get("/{lead_id}/fields")
async def fields(lead_id: str, db: AsyncSession = Depends(get_db)):
    rows = await enrichment.pending_fields(db, lead_id)
    return {"fields": [{"id": f.id, "field": f.field, "value": f.value, "confidence": f.confidence, "provider": f.provider, "decision": f.decision} for f in rows]}

@router.post("/fields/{field_id}/decision")
async def decide(field_id: str, body: FieldDecision, db: AsyncSession = Depends(get_db)):
    try:
        f = await enrichment.decide(db, field_id, body.decision)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"id": f.id, "decision": f.decision}
