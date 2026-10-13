import pytest

@pytest.mark.asyncio
async def test_enrich_and_decide(client):
    r = await client.post("/api/leads", json={"email": "ceo@acme.io", "company": "Acme", "role": "CEO"})
    assert r.status_code == 200
    lead = r.json()
    assert lead["status"] == "review"
    fields = await client.get(f"/api/leads/{lead['id']}/fields")
    assert fields.status_code == 200
    pending = fields.json()["fields"]
    assert pending
    decision = await client.post(f"/api/leads/fields/{pending[0]['id']}/decision", json={"decision": "accepted"})
    assert decision.status_code == 200
    assert decision.json()["decision"] == "accepted"
