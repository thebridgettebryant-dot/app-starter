"use client";

import { useEffect, useMemo, useState } from "react";

const RIPPLE_URL = process.env.NEXT_PUBLIC_RIPPLE_URL || "http://localhost:8000";

const DEFAULT_CHANGE =
  "Leadership is postponing the Audit Log feature from Q4 2026 to Q2 2027 to free engineers for the mobile redesign. What is affected, why was it prioritised originally, and who needs to be involved?";

const STEPS = [
  "Reconstructing the original decision…",
  "Tracing dependencies through the knowledge graph…",
  "Checking commitments, policies and owners…",
  "Drafting the action plan and agent updates…",
];

const C = {
  ink: "#0f172a",
  muted: "#64748b",
  line: "#e2e8f0",
  bg: "#f4f6fb",
  card: "#ffffff",
  brand: "#4f46e5",
  red: "#dc2626",
  amber: "#d97706",
  green: "#15803d",
  slate: "#475569",
};

const CSS = `
@keyframes brainspin { to { transform: rotate(360deg); } }
@keyframes brainfade { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
.brain-fade { animation: brainfade .35s ease both; }
.brain-btn { transition: transform .12s ease, box-shadow .12s ease, background .12s ease; cursor: pointer; }
.brain-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(15,23,42,.15); }
.brain-btn:disabled { opacity: .6; cursor: not-allowed; transform: none; box-shadow: none; }
.brain-card { transition: box-shadow .15s ease, transform .15s ease; }
.brain-card:hover { box-shadow: 0 6px 18px rgba(15,23,42,.08); }
`;

const sevColor = (s: string) => (s === "high" ? C.red : s === "medium" ? C.amber : C.slate);

function Pill({ color, children }: { color: string; children: React.ReactNode }) {
  return (
    <span
      style={{
        background: color,
        color: "#fff",
        borderRadius: 999,
        padding: "2px 10px",
        fontSize: 11,
        fontWeight: 700,
        letterSpacing: 0.4,
        textTransform: "uppercase",
        marginRight: 8,
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </span>
  );
}

function Card({ children, accent }: { children: React.ReactNode; accent?: string }) {
  return (
    <div
      className="brain-card brain-fade"
      style={{
        background: C.card,
        border: `1px solid ${C.line}`,
        borderLeft: accent ? `5px solid ${accent}` : `1px solid ${C.line}`,
        borderRadius: 12,
        padding: 18,
        marginBottom: 14,
        color: C.ink,
      }}
    >
      {children}
    </div>
  );
}

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      className="brain-btn"
      onClick={onClick}
      style={{
        padding: "6px 14px",
        borderRadius: 999,
        border: `1px solid ${active ? C.brand : C.line}`,
        background: active ? C.brand : "#fff",
        color: active ? "#fff" : C.ink,
        fontSize: 13,
        fontWeight: 600,
        marginRight: 8,
        marginBottom: 8,
      }}
    >
      {children}
    </button>
  );
}

export default function ImpactPage() {
  const [change, setChange] = useState(DEFAULT_CHANGE);
  const [useGraph, setUseGraph] = useState(true);
  const [ranWithGraph, setRanWithGraph] = useState(true);
  const [loading, setLoading] = useState(false);
  const [stepIdx, setStepIdx] = useState(0);
  const [error, setError] = useState("");
  const [a, setA] = useState<any>(null);
  const [tab, setTab] = useState("overview");
  const [sev, setSev] = useState("all");
  const [planFilter, setPlanFilter] = useState("all");
  const [done, setDone] = useState<Record<number, boolean>>({});
  const [copied, setCopied] = useState("");

  useEffect(() => {
    if (!loading) return;
    setStepIdx(0);
    const t = setInterval(() => setStepIdx((i) => (i + 1) % STEPS.length), 6000);
    return () => clearInterval(t);
  }, [loading]);

  async function run() {
    setLoading(true);
    setError("");
    setA(null);
    setDone({});
    setTab("overview");
    try {
      const res = await fetch(`${RIPPLE_URL}/ripple`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ change, graph_context: useGraph }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Request failed");
      setA(data.analysis);
      setRanWithGraph(useGraph);
    } catch (e: any) {
      setError(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function copy(key: string, text: string) {
    try {
      navigator.clipboard.writeText(text);
      setCopied(key);
      setTimeout(() => setCopied(""), 1500);
    } catch {
      /* ignore */
    }
  }

  const affected: any[] = (a && a.affected) || [];
  const hidden: any[] = (a && a.hidden_consequences) || [];
  const risks: any[] = (a && a.conflicts_and_risks) || [];
  const people: any[] = (a && a.people_to_involve) || [];
  const plan: any[] = (a && a.action_plan) || [];
  const agents: any[] = (a && a.agent_instruction_updates) || [];

  const filteredAffected = useMemo(
    () => affected.filter((x) => sev === "all" || x.severity === sev),
    [affected, sev]
  );
  const filteredPlan = useMemo(
    () => plan.filter((x) => planFilter === "all" || x.type === planFilter),
    [plan, planFilter]
  );
  const escalations = plan.filter((x) => x.type === "escalate").length;
  const doneCount = Object.values(done).filter(Boolean).length;

  const tabs = [
    { k: "overview", label: "Overview" },
    { k: "hidden", label: `Hidden consequences (${hidden.length})` },
    { k: "affected", label: `Affected (${affected.length})` },
    { k: "people", label: `People & risks (${people.length})` },
    { k: "plan", label: `Action plan (${plan.length})` },
    { k: "agents", label: `Agent updates (${agents.length})` },
  ];

  return (
    <div style={{ background: C.bg, minHeight: "100vh", color: C.ink }}>
      <style>{CSS}</style>

      <div style={{ background: `linear-gradient(135deg, ${C.brand}, #7c3aed)`, color: "#fff", padding: "36px 24px" }}>
        <div style={{ maxWidth: 980, margin: "0 auto" }}>
          <div style={{ fontSize: 13, opacity: 0.85, letterSpacing: 1, textTransform: "uppercase" }}>
            Company Brain
          </div>
          <h1 style={{ fontSize: 32, fontWeight: 800, margin: "6px 0" }}>Product Decision Impact Brain</h1>
          <p style={{ opacity: 0.9, maxWidth: 640 }}>
            When a product decision changes, the brain recovers why it was made, traces what depends on it, and
            tells you who to involve and what to do next.
          </p>
        </div>
      </div>

      <main style={{ maxWidth: 980, margin: "0 auto", padding: 24 }}>
        <Card>
          <div style={{ fontWeight: 700, marginBottom: 8 }}>The decision change</div>
          <textarea
            value={change}
            onChange={(e) => setChange(e.target.value)}
            rows={4}
            style={{
              width: "100%",
              padding: 12,
              border: `1px solid ${C.line}`,
              borderRadius: 8,
              color: C.ink,
              background: "#fff",
              fontSize: 15,
              resize: "vertical",
            }}
          />
          <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: 16, marginTop: 12 }}>
            <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer", fontSize: 14 }}>
              <input type="checkbox" checked={useGraph} onChange={(e) => setUseGraph(e.target.checked)} />
              Use knowledge graph (relationships between decisions, roadmap, customers, policies)
            </label>
            <button
              className="brain-btn"
              onClick={run}
              disabled={loading || !change.trim()}
              style={{
                background: C.brand,
                color: "#fff",
                border: "none",
                borderRadius: 8,
                padding: "10px 22px",
                fontWeight: 700,
                fontSize: 15,
              }}
            >
              {loading ? "Analyzing…" : "Analyze impact"}
            </button>
            <button
              className="brain-btn"
              onClick={() => setChange(DEFAULT_CHANGE)}
              style={{ background: "transparent", border: "none", color: C.muted, fontSize: 13, textDecoration: "underline" }}
            >
              Reset example
            </button>
          </div>
        </Card>

        {loading && (
          <Card>
            <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
              <div
                style={{
                  width: 22,
                  height: 22,
                  border: `3px solid ${C.line}`,
                  borderTopColor: C.brand,
                  borderRadius: "50%",
                  animation: "brainspin 0.9s linear infinite",
                }}
              />
              <div>
                <div style={{ fontWeight: 700 }}>{STEPS[stepIdx]}</div>
                <div style={{ color: C.muted, fontSize: 13 }}>This usually takes under a minute.</div>
              </div>
            </div>
          </Card>
        )}

        {error && (
          <Card accent={C.red}>
            <strong style={{ color: C.red }}>Something went wrong.</strong>
            <div style={{ marginTop: 6 }}>{error}</div>
            <button
              className="brain-btn"
              onClick={run}
              style={{ marginTop: 10, padding: "6px 14px", borderRadius: 8, border: `1px solid ${C.line}`, background: "#fff" }}
            >
              Try again
            </button>
          </Card>
        )}

        {a && (
          <>
            <div style={{ marginBottom: 12, display: "flex", flexWrap: "wrap" }}>
              {tabs.map((t) => (
                <Chip key={t.k} active={tab === t.k} onClick={() => setTab(t.k)}>
                  {t.label}
                </Chip>
              ))}
            </div>
            <div style={{ fontSize: 12, color: C.muted, marginBottom: 12 }}>
              Knowledge graph: <strong>{ranWithGraph ? "ON" : "OFF"}</strong>
              {!ranWithGraph && " — turn it on and re-run to see relationship-based findings."}
            </div>

            {tab === "overview" && (
              <>
                <Card accent={C.brand}>
                  <div style={{ fontWeight: 800, fontSize: 18, marginBottom: 6 }}>Summary</div>
                  <p style={{ lineHeight: 1.6 }}>{a.summary}</p>
                </Card>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: 12, marginBottom: 14 }}>
                  {[
                    { n: hidden.length, l: "Hidden consequences", k: "hidden", c: C.amber },
                    { n: affected.filter((x) => x.severity === "high").length, l: "High-severity items", k: "affected", c: C.red },
                    { n: escalations, l: "Need approval first", k: "plan", c: C.brand },
                    { n: agents.length, l: "AI agents to update", k: "agents", c: C.green },
                  ].map((s) => (
                    <button
                      key={s.l}
                      className="brain-btn"
                      onClick={() => setTab(s.k)}
                      style={{
                        background: "#fff",
                        border: `1px solid ${C.line}`,
                        borderTop: `4px solid ${s.c}`,
                        borderRadius: 12,
                        padding: 16,
                        textAlign: "left",
                      }}
                    >
                      <div style={{ fontSize: 30, fontWeight: 800, color: s.c }}>{s.n}</div>
                      <div style={{ color: C.muted, fontSize: 13 }}>{s.l}</div>
                    </button>
                  ))}
                </div>

                {a.original_rationale && (
                  <Card>
                    <div style={{ fontWeight: 800, fontSize: 18, marginBottom: 6 }}>Why the original decision was made</div>
                    <p style={{ lineHeight: 1.6 }}>{a.original_rationale.why}</p>
                    <div style={{ marginTop: 10, color: C.muted, fontSize: 12 }}>
                      Evidence from the brain:
                      {(a.original_rationale.evidence || []).map((e: string, i: number) => (
                        <div key={i}>• {e}</div>
                      ))}
                    </div>
                  </Card>
                )}
              </>
            )}

            {tab === "hidden" &&
              (hidden.length === 0 ? (
                <Card>No hidden consequences found.</Card>
              ) : (
                hidden.map((h, i) => (
                  <Card key={i} accent={C.amber}>
                    <div style={{ fontWeight: 800, fontSize: 17 }}>{h.title}</div>
                    <div style={{ marginTop: 12 }}>
                      {(h.chain || []).map((step: string, j: number, arr: string[]) => (
                        <div key={j} style={{ display: "flex", gap: 12 }}>
                          <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                            <div
                              style={{
                                width: 26,
                                height: 26,
                                borderRadius: "50%",
                                background: j === arr.length - 1 ? C.red : C.amber,
                                color: "#fff",
                                fontWeight: 700,
                                fontSize: 13,
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                flexShrink: 0,
                              }}
                            >
                              {j + 1}
                            </div>
                            {j < arr.length - 1 && <div style={{ width: 2, flex: 1, background: C.line, minHeight: 14 }} />}
                          </div>
                          <div style={{ paddingBottom: 12, lineHeight: 1.5 }}>{step}</div>
                        </div>
                      ))}
                    </div>
                    <p style={{ marginTop: 6, lineHeight: 1.6 }}>
                      <strong>Why it matters:</strong> {h.why_it_matters}
                    </p>
                    {(h.evidence || []).length > 0 && (
                      <div style={{ marginTop: 6, color: C.muted, fontSize: 12 }}>
                        Evidence: {(h.evidence || []).join(" · ")}
                      </div>
                    )}
                  </Card>
                ))
              ))}

            {tab === "affected" && (
              <>
                <div style={{ marginBottom: 8 }}>
                  {["all", "high", "medium", "low"].map((s) => (
                    <Chip key={s} active={sev === s} onClick={() => setSev(s)}>
                      {s === "all" ? "All" : s[0].toUpperCase() + s.slice(1)}
                    </Chip>
                  ))}
                </div>
                {filteredAffected.map((x, i) => (
                  <Card key={i} accent={sevColor(x.severity)}>
                    <div>
                      <Pill color={sevColor(x.severity)}>{x.severity}</Pill>
                      <Pill color={C.slate}>{x.type}</Pill>
                      {x.obvious === false && <Pill color={C.amber}>not obvious</Pill>}
                    </div>
                    <div style={{ fontWeight: 700, fontSize: 16, margin: "8px 0 4px" }}>{x.item}</div>
                    <div style={{ lineHeight: 1.6 }}>{x.why}</div>
                    <div style={{ marginTop: 6, color: C.muted, fontSize: 12 }}>Evidence: {x.evidence}</div>
                  </Card>
                ))}
                {filteredAffected.length === 0 && <Card>Nothing at this severity.</Card>}
              </>
            )}

            {tab === "people" && (
              <>
                <div style={{ fontWeight: 800, fontSize: 18, margin: "4px 0 10px" }}>People to involve</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: 12 }}>
                  {people.map((p, i) => (
                    <div key={i} className="brain-card brain-fade" style={{ background: "#fff", border: `1px solid ${C.line}`, borderRadius: 12, padding: 14, display: "flex", gap: 12 }}>
                      <div
                        style={{
                          width: 40,
                          height: 40,
                          borderRadius: "50%",
                          background: C.brand,
                          color: "#fff",
                          fontWeight: 700,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          flexShrink: 0,
                        }}
                      >
                        {String(p.name || "?").split(" ").map((w: string) => w[0]).slice(0, 2).join("")}
                      </div>
                      <div>
                        <div style={{ fontWeight: 700 }}>{p.name}</div>
                        <div style={{ color: C.muted, fontSize: 13 }}>{p.role}</div>
                        <div style={{ marginTop: 4, fontSize: 14, lineHeight: 1.5 }}>{p.why}</div>
                      </div>
                    </div>
                  ))}
                </div>
                <div style={{ fontWeight: 800, fontSize: 18, margin: "20px 0 10px" }}>Risks and conflicts</div>
                {risks.map((r, i) => (
                  <Card key={i} accent={C.red}>
                    <div style={{ fontWeight: 700 }}>⚠ {r.risk}</div>
                    <div style={{ color: C.muted, fontSize: 13, marginTop: 4 }}>Exposed: {r.who_is_exposed}</div>
                  </Card>
                ))}
              </>
            )}

            {tab === "plan" && (
              <>
                <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", marginBottom: 8 }}>
                  {[
                    ["all", "All"],
                    ["act", "Do now"],
                    ["escalate", "Needs approval"],
                  ].map(([k, l]) => (
                    <Chip key={k} active={planFilter === k} onClick={() => setPlanFilter(k)}>
                      {l}
                    </Chip>
                  ))}
                  <span style={{ marginLeft: "auto", color: C.muted, fontSize: 13, marginBottom: 8 }}>
                    {doneCount} of {plan.length} done
                  </span>
                </div>
                {filteredPlan.map((x) => {
                  const idx = plan.indexOf(x);
                  const isDone = !!done[idx];
                  return (
                    <Card key={idx} accent={x.type === "escalate" ? C.red : C.green}>
                      <div style={{ display: "flex", gap: 12, opacity: isDone ? 0.55 : 1 }}>
                        <input
                          type="checkbox"
                          checked={isDone}
                          onChange={() => setDone({ ...done, [idx]: !isDone })}
                          style={{ width: 20, height: 20, marginTop: 2, cursor: "pointer" }}
                        />
                        <div>
                          <div>
                            <Pill color={x.type === "escalate" ? C.red : C.green}>
                              {x.type === "escalate" ? "Needs approval" : "Do now"}
                            </Pill>
                            <span style={{ color: C.muted, fontSize: 13 }}>Priority {x.priority}</span>
                          </div>
                          <div style={{ fontWeight: 700, fontSize: 16, margin: "6px 0 2px", textDecoration: isDone ? "line-through" : "none" }}>
                            {x.action}
                          </div>
                          <div style={{ fontSize: 14 }}>
                            <strong>Owner:</strong> {x.owner}
                          </div>
                          <div style={{ color: C.muted, fontSize: 13, marginTop: 4 }}>{x.reason}</div>
                        </div>
                      </div>
                    </Card>
                  );
                })}
              </>
            )}

            {tab === "agents" &&
              (agents.length === 0 ? (
                <Card>No agent instructions need to change.</Card>
              ) : (
                agents.map((u, i) => (
                  <Card key={i} accent={C.green}>
                    <div style={{ fontWeight: 800, fontSize: 17 }}>{u.agent}</div>
                    <div style={{ marginTop: 6, color: C.red, fontSize: 14, lineHeight: 1.5 }}>
                      <strong>Problem:</strong> {u.problem_with_current_instructions}
                    </div>
                    <div style={{ margin: "12px 0 4px", fontWeight: 700, fontSize: 13, color: C.muted, textTransform: "uppercase", letterSpacing: 0.5 }}>
                      Proposed instructions
                    </div>
                    <pre
                      style={{
                        whiteSpace: "pre-wrap",
                        background: "#0f172a",
                        color: "#e2e8f0",
                        padding: 14,
                        borderRadius: 8,
                        fontSize: 13.5,
                        lineHeight: 1.55,
                      }}
                    >
                      {u.proposed_instructions}
                    </pre>
                    <div style={{ display: "flex", alignItems: "center", gap: 12, marginTop: 8 }}>
                      <button
                        className="brain-btn"
                        onClick={() => copy(`agent-${i}`, u.proposed_instructions || "")}
                        style={{ padding: "6px 14px", borderRadius: 8, border: `1px solid ${C.line}`, background: "#fff", fontWeight: 600 }}
                      >
                        {copied === `agent-${i}` ? "Copied ✓" : "Copy instructions"}
                      </button>
                      <span style={{ color: C.muted, fontSize: 13 }}>Approval needed from: {u.needs_approval_from}</span>
                    </div>
                  </Card>
                ))
              ))}
          </>
        )}
      </main>
    </div>
  );
}
