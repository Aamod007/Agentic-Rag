# Minimal production smoke test — run with: python test_smoke.py
# No frameworks needed; uses FastAPI's TestClient (ships with fastapi[standard])
# or falls back to httpx ASGI transport.

import asyncio
import httpx

from app.main import app
from app.agents.orchestrator import agent_service
from app.services.rag import rag_service


async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Health
        r = await client.get("/healthz")
        assert r.status_code == 200 and r.json()["status"] == "ok", r.text

        # Root and docs
        assert (await client.get("/")).status_code == 200
        assert (await client.get("/docs")).status_code == 200

        # Documents load
        r = await client.get("/documents")
        assert r.status_code == 200 and len(r.json()["documents"]) > 0

        # Tools registered
        r = await client.get("/tools")
        names = {t["name"] for t in r.json()["tools"]}
        assert {"create_calendar_event", "send_email"} <= names, names

        # Seed round-trips custom docs
        r = await client.post("/seed", json={"docs": [
            {"chunk_id": "t1", "source": "test", "text": "hello"}
        ]})
        assert r.status_code == 200 and r.json()["inserted"] == 1, r.text
        # restore defaults so other checks (and the running app) aren't polluted
        from app.data.default_documents import DEFAULT_DOCUMENTS
        await rag_service.seed_documents(DEFAULT_DOCUMENTS)

        # Validation rejects bad input
        assert (await client.post("/answer", json={})).status_code == 422
        assert (await client.post("/agent", json={"query": "x", "top_k": 99})).status_code == 422

        # 404 handler
        assert (await client.get("/nope")).status_code == 404

    # Citation extraction: valid ids kept, unknown ids dropped, order preserved
    ctx = [{"chunk_id": "a"}, {"chunk_id": "b"}]
    cites = agent_service._extract_citations("see [a] and [zzz] then [b] and [a]", ctx)
    assert cites == ["a", "b"], cites

    print("All smoke tests passed.")


if __name__ == "__main__":
    asyncio.run(main())
