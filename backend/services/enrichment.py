from __future__ import annotations
import json, uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import EnrichmentField, Lead
from backend.schemas import LeadCreate
from backend.services.providers import firmographic_provider, geo_provider

async def create_lead(session: AsyncSession, payload: LeadCreate) -> Lead:
    lead = Lead(id=uuid.uuid4().hex[:10], email=payload.email.lower().strip(), company=payload.company, role=payload.role)
    session.add(lead); await session.flush()

    fields: dict[str, tuple[str, float, str]] = {}
    for k, (v, c) in (await firmographic_provider(lead.email, lead.company)).items():
        fields[k] = (v, c, "firmographic")
    for k, (v, c) in (await geo_provider(lead.company)).items():
        fields[k] = (v, c, "geo")

    llm = get_llm()
    llm_fields = await llm.complete_json(
        f"Enrich CRM lead JSON fields for email={lead.email} company={lead.company}",
        system="Return enrichment fields with confidence.",
    )
    for k, meta in (llm_fields.get("fields") or {}).items():
        if isinstance(meta, dict) and "value" in meta:
            fields[k] = (str(meta["value"]), float(meta.get("confidence") or 0.5), "llm")

    for field, (value, confidence, provider) in fields.items():
        session.add(EnrichmentField(
            id=uuid.uuid4().hex[:10], lead_id=lead.id, field=field, value=value,
            confidence=confidence, provider=provider, decision="pending",
        ))
    lead.status = "review"
    lead.enrichment_json = json.dumps({k: {"value": v, "confidence": c, "provider": p} for k, (v, c, p) in fields.items()})
    await session.commit(); await session.refresh(lead); return lead

async def list_leads(session: AsyncSession) -> list[Lead]:
    return list((await session.execute(select(Lead).order_by(Lead.created_at.desc()))).scalars())

async def pending_fields(session: AsyncSession, lead_id: str) -> list[EnrichmentField]:
    rows = await session.execute(select(EnrichmentField).where(EnrichmentField.lead_id == lead_id, EnrichmentField.decision == "pending"))
    return list(rows.scalars())

async def decide(session: AsyncSession, field_id: str, decision: str) -> EnrichmentField:
    field = await session.get(EnrichmentField, field_id)
    if not field: raise ValueError("field not found")
    if decision not in {"accepted", "rejected"}: raise ValueError("bad decision")
    field.decision = decision
    await session.commit(); await session.refresh(field); return field
