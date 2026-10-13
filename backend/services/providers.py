"""Mock enrichment providers — stand-ins for Clearbit/Apollo-style APIs."""
from __future__ import annotations

async def firmographic_provider(email: str, company: str) -> dict[str, tuple[str, float]]:
    domain = email.split("@")[-1].lower() if "@" in email else "unknown"
    return {
        "domain": (domain, 0.95),
        "company_size": ("51-200" if "corp" not in domain else "1000+", 0.7),
        "industry": ("Software" if domain.endswith(".io") or "ai" in domain else "Services", 0.66),
    }

async def geo_provider(company: str) -> dict[str, tuple[str, float]]:
    return {"hq_country": ("PK" if company else "US", 0.52), "timezone": ("Asia/Karachi", 0.48)}
