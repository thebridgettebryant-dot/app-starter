"""
Product Decision Impact Brain: /ripple service.

POST /ripple {"change": "<decision change in plain English>"}
  1. Three HydraDB queries (graph context ON) so the brain looks beyond what was asked:
       a. the change itself
       b. the original decision and its rationale
       c. commitments, compliance, partners, deadlines and AI-agent instructions
          that depend on it
  2. One LLM call that returns structured JSON (schema in SYSTEM_PROMPT).

Run:
  pip install fastapi uvicorn anthropic python-dotenv "hydradb-sdk>=2.1.1,<3"
  uvicorn ripple_service:app --reload --port 8000

.env:
  HYDRA_DB_API_KEY=...
  ANTHROPIC_API_KEY=...
  ANTHROPIC_MODEL=claude-sonnet-5-5   # optional
"""
import json
import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from hydra_db import HydraDB
from hydra_db.helpers import build_string

load_dotenv()

client = HydraDB(token=os.environ["HYDRA_DB_API_KEY"])
DATABASE = os.getenv("HYDRA_DATABASE", "tandem_brain")
SHARED = os.getenv("HYDRA_COLLECTION", "tandem_knowledge")

app = FastAPI(title="Product Decision Impact Brain")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RippleRequest(BaseModel):
    change: str
    graph_context: bool = True  # flip to False for the "before" half of the demo


SYSTEM_PROMPT = """You are the Product Decision Impact Brain for a Product Owner.
A product decision is changing. Using ONLY the provided company context (documents and
graph relationships), do the following:

1. Reconstruct WHY the original decision was made.
2. Trace everything that depends on it: roadmap, engineering work, customer
   commitments, compliance obligations, partners, documentation, owners, and AI agent
   instructions.
3. Surface hidden consequences: impacts the requester did NOT ask about, found by
   following relationships several steps away. Show the chain step by step.
4. Identify conflicts, risks, and the people who must be involved, and why.
5. Produce a prioritised action plan. For each action decide:
   - "act": the Product Owner's team can do it directly, or
   - "escalate": a policy or a named person must approve first.
   Follow any policy in the context about who must approve commitments.
6. For every AI agent whose instructions are now wrong or risky, draft replacement
   instructions. Drafted instructions must not create, withdraw, or promise commercial
   terms or dates that the context does not support.

Rules:
- Cite evidence by the document title or graph relationship it came from.
- If the context does not support a claim, say it is unknown. Never invent facts,
  people, dates, or numbers.
- Do not tell anyone the decision should be reversed; present consequences and options.
- Be concise: at most 6 affected items, 3 hidden consequences, 4 risks, 6 actions. Keep every text field under 40 words, and each proposed agent instruction under 120 words.

Return ONLY valid JSON (no markdown fences) in exactly this shape:
{
  "summary": "2-3 sentence plain-English headline",
  "original_rationale": {"why": "string", "evidence": ["doc title or relationship"]},
  "affected": [
    {"item": "string", "type": "roadmap|engineering|customer|compliance|partner|docs|agent|other",
     "why": "string", "evidence": "string", "severity": "high|medium|low",
     "obvious": true}
  ],
  "hidden_consequences": [
    {"title": "string", "chain": ["step 1", "step 2", "step 3"],
     "why_it_matters": "string", "evidence": ["string"]}
  ],
  "conflicts_and_risks": [
    {"risk": "string", "who_is_exposed": "string", "evidence": "string"}
  ],
  "people_to_involve": [
    {"name": "string", "role": "string", "why": "string"}
  ],
  "action_plan": [
    {"priority": 1, "action": "string", "owner": "string",
     "type": "act|escalate", "reason": "string"}
  ],
  "agent_instruction_updates": [
    {"agent": "string", "problem_with_current_instructions": "string",
     "proposed_instructions": "string", "needs_approval_from": "string"}
  ]
}
"""


def retrieve(change: str, graph_context: bool) -> str:
    queries = [
        ("CHANGE", change),
        ("ORIGINAL DECISION AND RATIONALE",
         f"Original decision, rationale, and decision owner related to: {change}"),
        ("DEPENDENCIES AND COMMITMENTS",
         "Customer commitments, contracts, compliance controls, partner integrations, "
         f"deadlines, documentation, and AI agent instructions that depend on: {change}"),
    ]
    sections = []
    for label, q in queries:
        result = client.query(
            database=DATABASE,
            collection=SHARED,
            query=q,
            type="knowledge",
            query_by="hybrid",
            mode="thinking" if graph_context else "fast",
            max_results=10,
            graph_context=graph_context,
        )
        sections.append(f"##### CONTEXT FOR: {label}\n{build_string(result)}")
    return "\n\n".join(sections)


def generate(context: str, change: str) -> dict:
    from anthropic import Anthropic

    llm = Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    resp = llm.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5"),
        max_tokens=12000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Context:\n{context}\n\nDecision change: {change}"},
        ],
    )
    raw = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    print("STOP:", resp.stop_reason, "LEN:", len(raw), flush=True)
    print(raw[:1500], "\n.....\n", raw[-700:], flush=True)
    # Keep only the JSON object, in case the model adds any surrounding text
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise json.JSONDecodeError("no JSON object found", raw, 0)
    return json.loads(raw[start : end + 1])


@app.post("/ripple")
def ripple(req: RippleRequest):
    if not req.change.strip():
        raise HTTPException(400, "change is required")
    try:
        context = retrieve(req.change, req.graph_context)
    except Exception as e:  # surface HydraDB errors clearly during the demo
        raise HTTPException(502, f"HydraDB query failed: {e}")
    try:
        analysis = generate(context, req.change)
    except json.JSONDecodeError:
        raise HTTPException(502, "LLM did not return valid JSON; retry")
    except Exception as e:
        raise HTTPException(502, f"LLM call failed: {e}")
    return {"graph_context": req.graph_context, "analysis": analysis,
            "context_chars": len(context)}


@app.get("/health")
def health():
    return {"ok": True}
