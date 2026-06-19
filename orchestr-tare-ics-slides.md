---
marp: true
theme: default
paginate: true
---

# Orchestr + TARE + ICS
### A quality layer for the agentic stack

Internal dev session — context and direction

---

## The problem we keep running into

Every team building agents hits the same three walls:

1. **Where do agents live?** No standard place to deploy, version, and discover agentic orchestrations
2. **What are they actually costing us?** MCP servers inject tool schemas into context on every request — nobody measures this
3. **Are the instructions any good?** No way to validate whether an agent's operating instructions are well-formed before it ships

We're building one answer to all three.

---

## Three pieces, one thesis

| Piece | What it does | Status |
|---|---|---|
| **Orchestr** | Platform to deploy, manage, discover agentic orchestrations | Built, local dev, untested in real use |
| **TARE** | Benchmark + scorer for MCP server context cost | Open sourced, 8 servers measured, public web tool live |
| **ICS** | Spec for instruction quality (how operators instruct models) | Spec stage |

**Thesis:** Orchestr is the platform. TARE and ICS are why it's better than rolling your own.

---

## What is Orchestr, concretely

> GitHub for agentic orchestrations, with a runtime.

- AI engineers publish **templates** to a registry (public / org-private / private)
- Teams instantiate templates as **instances** — wizard-driven, credentials injected at runtime
- Platform handles lifecycle: start / stop / pause / resume / restart, health polling, auto-restart with backoff
- Any framework integrates via 5 HTTP endpoints + an `orchestr.json` manifest
- Execution models: daemon / event / schedule / human-in-the-loop

---

## What is TARE, concretely

> A neutral, reproducible benchmark for MCP server design quality.

- Scores any MCP server on 6 static dimensions → a 0–100 **Design Score**
- Measures real token cost with a declared reference tokenizer (o200k_base)
- No model calls, no task execution — pure static analysis, fully reproducible
- Public results today:

```
Linear      76/100    827 tokens     5 tools
GitHub      63/100    8,218 tokens   43 tools
Notion      43/100    15,720 tokens  22 tools
Salesforce  38/100    21,226 tokens  74 tools
```

- Key finding: **token cost tracks schema design, not tool count**

---

## What is ICS, concretely

> A specification for instruction quality — the operator's side of the contract.

- Where TARE asks "is this *tool* well-presented to the model?"
- ICS asks "is this *instruction* well-formed for the model to follow?"
- Sibling spec — same epistemic rigor, same conformance-profile structure
- Earlier stage than TARE; the static-checks layer is still being defined

---

## Why these three together, not separately

Each piece alone is a nice open-source artifact. Together they answer a question nobody can currently answer end-to-end:

> **"Why is my agent burning so many tokens, and where exactly is the waste coming from?"**

- Orchestr knows *which* orchestrations are running and *what* they call
- TARE knows the *cost* of every MCP integration they depend on
- ICS knows whether the *instructions* driving them are sound

No platform today connects deployment → dependency cost → instruction quality in one place.

---

## The product shape

**At publish time (registry):**
Template declares integrations in `orchestr.json` → Orchestr auto-scores each with TARE → score shown on the template page

**At instance creation:**
Team sees a cost estimate *before* deploying:
> "This orchestration uses Notion MCP (15,720 tok/req) + Salesforce MCP (21,226 tok/req). Estimated baseline cost: ~37K tokens/trigger."

**At runtime:**
Track real token spend per trigger → compare against TARE's static prediction → feed back into the benchmark

---

## The business shape

| Tier | What's included |
|---|---|
| **Free** | Open-source harness, public registry, web scorer (live today) |
| **Team** | Hosted Orchestr, org-private registry, TARE/ICS quality gates on deploy, cost dashboard |
| **Enterprise** | Custom thresholds, private benchmark sets, SSO, audit trails, SLA |

**The moat:** registry network effect + real usage data validating TARE's thresholds + becoming the standard teams optimize their orchestrations against.

---

## Where we actually are today

Let's be precise, not optimistic:

- TARE: shipped, public, some social traction attempted, modest pickup so far
- ICS: spec-stage only
- Orchestr: code exists, **only tested by one person, with AI assistance — zero real orchestrations hosted**

The commercial story above is the *destination*. It is **not** what we're building this sprint.

---

## What we're actually doing next

**Single near-term goal: get one real orchestration running end-to-end on Orchestr.**

- Use the PR review agent example as the test case
- Host it for real, wire a real webhook, let it run
- Fix whatever breaks — this is the signal that tells us if the platform is production-shaped
- No TARE integration, no registry polish, no commercial work until this works reliably

This is the "be your own first customer" milestone. Everything else is downstream of it.

---

## What I need from this team

- Help stress-testing Orchestr against a real workflow, not a demo
- Honest bug reports — we want it to break now, not after a design partner is using it
- Hold off on the TARE/registry integration work until the runtime is proven

Questions / pushback welcome.
