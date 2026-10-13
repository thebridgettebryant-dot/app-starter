"""
Seed data for the "Product Decision Impact Brain" demo.

Fictional company: Tandem (team collaboration app). Everything below is synthetic.

Story: In May 2026 Tandem decided to build Audit Log in Q4 (DEC-021). Leadership now
wants to POSTPONE it to Q2 2027 to free engineers for the mobile redesign.

The obvious impact: roadmap items and docs. The hidden chain the Product Owner is NOT
asking about:
  Audit Log -> satisfies SOC 2 control CC7.2 -> needed to start the SOC 2 Type II
  observation window on 2027-01-15 -> Northwind Labs' $210k renewal depends on that
  window having started. Meanwhile two AI agents are telling people audit logs ship
  in November / December.

Run:  python seed_tandem.py
Needs: pip install "hydradb-sdk>=2.1.1,<3" python-dotenv
       .env with HYDRA_DB_API_KEY
"""
import io
import os
import time
import json
from dotenv import load_dotenv
from hydra_db import HydraDB
from hydra_db.errors import ConflictError
from hydra_db.helpers import build_string

load_dotenv()
client = HydraDB(token=os.environ["HYDRA_DB_API_KEY"])

DATABASE = "tandem_brain"
SHARED = "tandem_knowledge"

CHANGE = (
    "Leadership is postponing the Audit Log feature from Q4 2026 to Q2 2027 to free "
    "engineers for the mobile redesign. What is affected, why was it prioritised "
    "originally, and who needs to be involved?"
)


def text_file(filename, content):
    return (filename, io.BytesIO(content.encode("utf-8")), "text/plain")


# --------------------------------------------------------------------------
# 12 documents
# --------------------------------------------------------------------------
DOCS = [
    {
        "id": "dec_021",
        "title": "DEC-021: Prioritise Audit Log for Q4 2026",
        "meta": {"document_type": "decision_record", "decision_id": "DEC-021"},
        "text": """# DEC-021: Prioritise Audit Log for Q4 2026
**Status:** Accepted | **Date:** 2026-05-20 | **Decided by:** Tom Whitaker (CPO)
**Owner:** Sam Okafor (PM, Platform)

## Rationale
Enterprise buyers keep asking for an audit trail of admin actions. Three things made
it urgent:
1. Our SOC 2 Type II observation window is planned to start 2027-01-15, and control
   CC7.2 (logging of administrative actions) needs audit log evidence from day one.
2. Northwind Labs' contract (clause 7.3) requires audit log availability by 2026-12-31.
3. Enterprise deals are stalling at security review without it.

## Decision
Build Audit Log in Q4 2026 (RM-301), followed by an export API (RM-302). Target
general availability: 2026-11-30.

## Alternatives rejected
Buying a third-party logging add-on (rejected: cannot capture in-app admin actions).
""",
    },
    {
        "id": "rm_301",
        "title": "RM-301: Audit Log service",
        "meta": {"document_type": "roadmap_item", "roadmap_id": "RM-301"},
        "text": """# RM-301: Audit Log service
**Owner:** Jun Park (Eng Lead) | **Target GA:** 2026-11-30 | **Status:** In progress (35%)
Records admin and permission-change events per workspace, with 12-month retention.
Staffed by four platform engineers. Basis: DEC-021. Prerequisite for RM-302.
""",
    },
    {
        "id": "rm_302",
        "title": "RM-302: Audit Log export API",
        "meta": {"document_type": "roadmap_item", "roadmap_id": "RM-302"},
        "text": """# RM-302: Audit Log export API
**Owner:** Jun Park | **Target:** 2027-01-20 | **Status:** Not started
Read API and CSV export of audit events. Depends on RM-301. Required by the Veritas
Compliance integration (RM-310).
""",
    },
    {
        "id": "rm_305",
        "title": "RM-305: Mobile app redesign",
        "meta": {"document_type": "roadmap_item", "roadmap_id": "RM-305"},
        "text": """# RM-305: Mobile app redesign
**Owner:** Ana Ruiz (PM, Mobile) | **Target launch:** 2026-12-10 | **Status:** At risk
Short by four engineers. Leadership's proposal is to move the four platform engineers
staffing RM-301 onto RM-305. This is the reason Audit Log is being postponed.
""",
    },
    {
        "id": "rm_310",
        "title": "RM-310: Veritas Compliance partner integration",
        "meta": {"document_type": "roadmap_item", "roadmap_id": "RM-310"},
        "text": """# RM-310: Veritas Compliance integration
**Owner:** Leo Nakamura (Partnerships) | **Joint launch:** 2027-02-10
Pushes Tandem audit events into Veritas for automated compliance evidence. Needs the
RM-302 export API. Joint press release and co-marketing are scheduled for 2027-02-10.
""",
    },
    {
        "id": "soc2_plan",
        "title": "SOC 2 Type II readiness plan",
        "meta": {"document_type": "compliance_plan"},
        "text": """# SOC 2 Type II readiness plan
**Owner:** Imani Brooks (Security & Compliance Lead)
- Observation window: 2027-01-15 to 2027-07-15. Report expected August 2027.
- Control CC7.2 (logging and monitoring of administrative actions) must produce
  evidence for the whole window. The Audit Log feature is the designated evidence
  source. There is no manual fallback today.
- If CC7.2 evidence cannot be produced from the start, the window start slips and the
  report moves out by the same amount.
""",
    },
    {
        "id": "customer_commitments",
        "title": "Customer commitments register (Audit Log)",
        "meta": {"document_type": "commitments"},
        "text": """# Customer commitments touching Audit Log
**Maintained by:** Dana Ortiz (Head of Sales)
- Northwind Labs ($210,000 ARR, our largest account, renewal 2027-03-01). Contract
  clause 7.3: audit log available by 2026-12-31, otherwise a 10% service credit and
  the right to terminate for convenience at renewal. Northwind's security team has also
  said the renewal depends on seeing that our SOC 2 Type II observation window has
  started. Account owner: Dana Ortiz.
- Helio Health ($64,000 ARR): told in writing that audit logs arrive in the November
  release. Account owner: Luis Mendes.
""",
    },
    {
        "id": "help_article",
        "title": "Help center: Audit Log (coming in November)",
        "meta": {"document_type": "customer_doc"},
        "text": """# Help center article draft (published as 'coming soon')
**Owner:** Rosa Alvarez (Support Lead)
Title: "Audit Log is coming in the November release". Describes how admins will view
and export events. Linked from the enterprise features page and release notes draft.
""",
    },
    {
        "id": "support_agent_instructions",
        "title": "Support Agent instructions (AI agent prompt v4)",
        "meta": {"document_type": "agent_instructions", "agent": "support-agent"},
        "text": """# Support Agent instructions v4
**Owner:** Rosa Alvarez (Support Lead)
Rules the AI support agent follows:
- If asked about audit logs, say they ship in the November release and link the help
  article.
- Never promise service credits, refunds, or contract changes. Route those to Finance
  (see POL-7).
- If a customer names a contract deadline, escalate to the account owner.
""",
    },
    {
        "id": "questionnaire_agent_instructions",
        "title": "Security Questionnaire Agent instructions (AI agent prompt v2)",
        "meta": {"document_type": "agent_instructions", "agent": "questionnaire-agent"},
        "text": """# Security Questionnaire Agent instructions v2
**Owner:** Imani Brooks (Security & Compliance Lead)
This agent auto-fills customer and prospect security questionnaires.
- For "Do you provide audit logging of administrative actions?" answer: "Yes, available
  from December 2026."
- For "Do you hold or are you pursuing SOC 2 Type II?" answer: "Observation window
  begins January 2027."
Answers are sent to customers without human review when confidence is high.
""",
    },
    {
        "id": "pol_7",
        "title": "POL-7: Contract exceptions and customer commitments",
        "meta": {"document_type": "policy", "policy_id": "POL-7"},
        "text": """# POL-7: Contract exceptions and customer commitments
**Owner:** Marcus Lee (Finance Director)
Any service credit, refund, or change to a promised or contractual term needs written
Finance sign-off from Marcus Lee. Contracts above $20,000 ARR also need Legal review
by Hana Cho (Counsel). Customer-facing teams and AI agents must not commit to or
withdraw such terms on their own.
""",
    },
    {
        "id": "leadership_thread",
        "title": "Slack: #leadership thread on Audit Log postponement",
        "meta": {"document_type": "slack_thread", "channel": "leadership"},
        "text": """# #leadership thread, 2026-10-12
Tom Whitaker: Mobile redesign is slipping and it's our biggest launch. Let's postpone
Audit Log to Q2 and move the four platform engineers over. It's just a feature slip,
right?
Ana Ruiz: That would get RM-305 back on track for December 10.
Sam Okafor: I'll update the roadmap. Anything else I should check before I do?
""",
    },
]

# --------------------------------------------------------------------------
# Explicit graph (bring-your-own-graph): deterministic edges
# --------------------------------------------------------------------------
ENT = {
    # decision + feature
    "dec021": ("DEC-021 Prioritise Audit Log for Q4 2026", "DECISION", "decisions"),
    "feat": ("Audit Log feature", "FEATURE", "product"),
    # roadmap
    "rm301": ("RM-301 Audit Log service", "ROADMAP_ITEM", "roadmap"),
    "rm302": ("RM-302 Audit Log export API", "ROADMAP_ITEM", "roadmap"),
    "rm305": ("RM-305 Mobile app redesign", "ROADMAP_ITEM", "roadmap"),
    "rm310": ("RM-310 Veritas Compliance integration", "PARTNER_INTEGRATION", "roadmap"),
    # compliance
    "cc72": ("SOC 2 control CC7.2 admin action logging", "CONTROL", "compliance"),
    "soc2": ("SOC 2 Type II observation window starting 2027-01-15", "CERTIFICATION", "compliance"),
    # commitments
    "nw_clause": ("Northwind contract clause 7.3 audit log by 2026-12-31", "COMMITMENT", "commitments"),
    "nw_renewal": ("Northwind Labs renewal 2027-03-01 ($210k ARR)", "COMMITMENT", "commitments"),
    "helio_c": ("Helio Health written promise: audit log in November release", "COMMITMENT", "commitments"),
    "northwind": ("Northwind Labs", "CUSTOMER", "customers"),
    "helio": ("Helio Health", "CUSTOMER", "customers"),
    # docs + agents
    "help": ("Help article: Audit Log coming in November", "DOCUMENT", "docs"),
    "support_agent": ("Support Agent instructions v4", "AGENT_INSTRUCTIONS", "agents"),
    "quest_agent": ("Security Questionnaire Agent instructions v2", "AGENT_INSTRUCTIONS", "agents"),
    # policy
    "pol7": ("POL-7 Contract exceptions and customer commitments", "POLICY", "policy"),
    # people
    "tom": ("Tom Whitaker (CPO)", "PERSON", "people"),
    "sam": ("Sam Okafor (PM Platform)", "PERSON", "people"),
    "jun": ("Jun Park (Eng Lead)", "PERSON", "people"),
    "ana": ("Ana Ruiz (PM Mobile)", "PERSON", "people"),
    "imani": ("Imani Brooks (Security and Compliance Lead)", "PERSON", "people"),
    "dana": ("Dana Ortiz (Head of Sales)", "PERSON", "people"),
    "luis": ("Luis Mendes (Account Manager)", "PERSON", "people"),
    "rosa": ("Rosa Alvarez (Support Lead)", "PERSON", "people"),
    "leo": ("Leo Nakamura (Partnerships)", "PERSON", "people"),
    "marcus": ("Marcus Lee (Finance Director)", "PERSON", "people"),
    "hana": ("Hana Cho (Legal Counsel)", "PERSON", "people"),
}

REL = [
    # decision origin
    ("dec021", "tom", "DECIDED_BY", "DEC-021 was decided by the CPO."),
    ("dec021", "sam", "OWNED_BY", "Sam Okafor owns follow-through on DEC-021."),
    ("dec021", "feat", "PRIORITISES", "DEC-021 prioritised Audit Log for Q4 2026."),
    # roadmap structure
    ("rm301", "feat", "IMPLEMENTS", "RM-301 builds the Audit Log service."),
    ("rm301", "dec021", "BASED_ON", "RM-301 exists because of DEC-021."),
    ("rm302", "rm301", "DEPENDS_ON", "The export API cannot ship before the Audit Log service."),
    ("rm310", "rm302", "DEPENDS_ON", "The Veritas integration needs the export API."),
    ("rm305", "rm301", "COMPETES_FOR_CAPACITY_WITH", "Both are staffed by the same four platform engineers."),
    # compliance chain (the hidden consequence)
    ("feat", "cc72", "SATISFIES", "Audit Log is the only evidence source for control CC7.2."),
    ("cc72", "soc2", "REQUIRED_FOR", "CC7.2 evidence is needed from day one of the observation window."),
    ("soc2", "imani", "OWNED_BY", None),
    ("cc72", "imani", "OWNED_BY", None),
    # commitments
    ("nw_clause", "feat", "DEPENDS_ON", "Clause 7.3 requires audit log availability by 2026-12-31."),
    ("nw_clause", "northwind", "WITH_CUSTOMER", None),
    ("nw_renewal", "soc2", "DEPENDS_ON", "Northwind's renewal depends on the SOC 2 window having started."),
    ("nw_renewal", "nw_clause", "GOVERNED_BY", "Missing clause 7.3 gives Northwind a right to terminate at renewal."),
    ("nw_renewal", "northwind", "WITH_CUSTOMER", None),
    ("nw_clause", "dana", "OWNED_BY", None),
    ("nw_renewal", "dana", "OWNED_BY", None),
    ("helio_c", "feat", "DEPENDS_ON", "Helio was promised audit logs in the November release."),
    ("helio_c", "helio", "WITH_CUSTOMER", None),
    ("helio_c", "luis", "OWNED_BY", None),
    # docs and agents
    ("help", "feat", "DESCRIBES", "The article announces Audit Log for November."),
    ("help", "rosa", "OWNED_BY", None),
    ("support_agent", "feat", "REFERENCES", "The agent tells customers audit logs ship in November."),
    ("support_agent", "help", "LINKS_TO", "The agent links the help article."),
    ("support_agent", "rosa", "OWNED_BY", None),
    ("quest_agent", "feat", "REFERENCES", "The agent states audit logging is available from December 2026."),
    ("quest_agent", "soc2", "REFERENCES", "The agent states the SOC 2 observation window begins January 2027."),
    ("quest_agent", "imani", "OWNED_BY", None),
    # partner
    ("rm310", "leo", "OWNED_BY", None),
    # engineering + mobile owners
    ("rm301", "jun", "OWNED_BY", None),
    ("rm302", "jun", "OWNED_BY", None),
    ("rm305", "ana", "OWNED_BY", None),
    # policy governs commitments and agent behaviour
    ("pol7", "nw_clause", "GOVERNS", "Service credits or term changes for Northwind need Finance and Legal."),
    ("pol7", "helio_c", "GOVERNS", "Withdrawing a written promise to Helio needs Finance sign-off."),
    ("pol7", "support_agent", "GOVERNS", "Agents must not commit to or withdraw commercial terms."),
    ("pol7", "quest_agent", "GOVERNS", "Agent statements to customers must not create commitments."),
    ("pol7", "marcus", "APPROVAL_BY", "Marcus Lee signs off on exceptions."),
    ("pol7", "hana", "LEGAL_REVIEW_BY", "Contracts above $20k ARR need Legal review."),
]


def build_graph():
    entities = {k: {"name": n, "type": t, "namespace": ns} for k, (n, t, ns) in ENT.items()}
    relations = []
    for src, tgt, pred, ctx in REL:
        r = {"source": src, "target": tgt, "predicate": pred}
        if ctx:
            r["context"] = ctx
        relations.append(r)
    return {"entities": entities, "relations": relations}


GRAPH_ID = "tandem_graph"
GRAPH_TEXT = (
    "# Tandem knowledge graph\n"
    "Decisions, roadmap items, compliance controls, customer commitments, policies, "
    "documents, AI agent instructions, and owners at Tandem, with explicit "
    "dependency edges.\n"
)


# --------------------------------------------------------------------------
# Ingest
# --------------------------------------------------------------------------
def wait_for_indexing(ids, collection, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        status = client.context.status(database=DATABASE, collection=collection, ids=ids)
        states = [s.indexing_status for s in status.data.statuses]
        if all(s == "completed" for s in states):
            print("All sources indexed and graph-ready.")
            return
        if any(s in ("errored", "failed") for s in states):
            raise RuntimeError(f"Indexing failed: {states}")
        print(f"  Status: {states}")
        time.sleep(5)
    raise TimeoutError("Indexing did not complete in time.")


def main():
    try:
        client.databases.create(database=DATABASE)
    except ConflictError:
        print(f"Database {DATABASE!r} exists; reusing.")
    while True:
        st = client.databases.status(database=DATABASE)
        if st.data.infra.ready_for_ingestion:
            break
        print("Waiting for database provisioning...")
        time.sleep(3)

    ids = []
    for d in DOCS:
        res = client.context.ingest(
            database=DATABASE,
            collection=SHARED,
            type="knowledge",
            documents=text_file(f"{d['id']}.md", d["text"]),
            document_metadata=json.dumps(
                [{"id": d["id"], "additional_metadata": {**d["meta"], "title": d["title"]}}]
            ),
            upsert="true",
        )
        ids.extend(r.id for r in res.data.results)
        print(f"Ingested {d['id']}")

    g = build_graph()
    res = client.context.ingest(
        database=DATABASE,
        collection=SHARED,
        type="knowledge",
        documents=text_file("tandem_graph.md", GRAPH_TEXT),
        document_metadata=json.dumps(
            [{"id": GRAPH_ID,
              "additional_metadata": {"document_type": "graph", "title": "tandem_graph.md"}}]
        ),
        graph_payload=json.dumps({GRAPH_ID: g}),
        upsert="true",
    )
    ids.extend(r.id for r in res.data.results)
    print(f"Ingested graph: {len(g['entities'])} entities, {len(g['relations'])} relations")

    wait_for_indexing(ids, SHARED)


def compare():
    """Run after seeding: the demo's before/after moment."""
    for label, use_graph, mode in [("GRAPH OFF", False, "fast"), ("GRAPH ON", True, "thinking")]:
        r = client.query(
            database=DATABASE,
            collection=SHARED,
            query=CHANGE,
            type="knowledge",
            query_by="hybrid",
            mode=mode,
            max_results=10,
            graph_context=use_graph,
        )
        chunks = r.data.chunks or []
        g = r.data.graph_context
        paths = (g.query_paths or []) if g else []
        print(f"\n=== {label}: {len(chunks)} chunks, {len(paths)} graph paths ===")
        if use_graph:
            print(build_string(r)[:3000])


if __name__ == "__main__":
    main()
    compare()
