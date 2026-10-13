from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.schemas import LeadCreate
from backend.services import enrichment

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    leads = await enrichment.list_leads(db)
    review = {}
    for lead in leads:
        review[lead.id] = await enrichment.pending_fields(db, lead.id)
    return templates.TemplateResponse("index.html", {"request": request, "title": "CRM Enrichment Agent", "leads": leads, "review": review})

@router.post("/ui/leads")
async def ui_lead(email: str = Form(...), company: str = Form(""), role: str = Form(""), db: AsyncSession = Depends(get_db)):
    await enrichment.create_lead(db, LeadCreate(email=email, company=company, role=role))
    return RedirectResponse("/", status_code=303)

@router.post("/ui/fields/{field_id}/{decision}")
async def ui_decide(field_id: str, decision: str, db: AsyncSession = Depends(get_db)):
    await enrichment.decide(db, field_id, decision)
    return RedirectResponse("/", status_code=303)
