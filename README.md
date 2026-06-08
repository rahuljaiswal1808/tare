# TARE: Tool And Response Economy

**An open benchmark and specification for the context-window cost of MCP servers.**

There are existing linters for MCP tool quality (agent-friend being the most complete) but no neutral, reproducible benchmark -- a dated, tokenizer-declared measurement of real production servers that anyone can re-run and compare against. TARE fills that gap.

Every MCP server injects its tool definitions into the model context on every request -- before any user input, on every turn. TARE measures that overhead and scores the design discipline behind it. The *tare weight* of a server is what it costs the model to hold it, empty, before any work begins.

## TARE-Bench v0: 8 SaaS servers, measured

Measured 2026-06-05 against the reference tokenizer (o200k_base). Scripts and manifests in this repo.

| # | Server | Design Score | Tokens | Tools |
|---|--------|:---:|---:|---:|
| 1 | Linear | **76** | 827 | 5 |
| 2 | Slack | **68** | 687 | 8 |
| 3 | GitHub | **63** | 8,218 | 43 |
| 4 | Stripe | **62** | 2,367 | 23 |
| 5 | MongoDB | **54** | 4,078 | 25 |
| 6 | Atlassian | **46** | 19,983 | 73 |
| 7 | Notion | **43** | 15,720 | 22 |
| 8 | Salesforce | **38** | 21,226 | 74 |

Design Score is 0–100, higher is better. Tokens is the full schema footprint at default load, lower is better. Full per-dimension breakdown: [`docs/SPEC.md`](docs/SPEC.md#tare-bench-v0-results).

### Three things the numbers show

**Schema design dominates footprint — tool count doesn't.** Notion (22 tools) costs 19× more tokens than Linear (5 tools) and nearly twice as much as GitHub (43 tools). The cost is not proportional to tool count; it is proportional to schema verbosity. Notion's server is generated from the Notion OpenAPI spec and carries the full parameter schema verbatim on every tool.

**Progressive disclosure is rare and high-leverage.** GitHub is the only server of the eight to implement runtime toolset scoping (43 tools default, 82 with `--toolsets all`). No other server in the set exposes a comparable mechanism.

**Descriptions are universally weak.** Every server scores red on description quality. Descriptions are informative but none include the usage-boundary language (when to use / when not to) that guides tool selection at scale.

---

## Measure your own server

**Browser:** paste a `tools/list` response at [rahuljaiswal1808.github.io/tare](https://rahuljaiswal1808.github.io/tare) — no install, instant results with the approx tokenizer.

**Canonical (o200k_base):** the tokenizer vocab is vendored in `vendor/tiktoken/` so measurements are fully reproducible offline.

```sh
pip install -e '.[dev]'

# From a manifest file:
tare measure-server --server <name> --source manifest
tare report

# From a live server (needs mcp extra):
pip install -e '.[live]'
tare measure-server --server <name> --source live
```

## How scoring works

TARE scores six static dimensions and weights them into a 0–100 Design Score:

| Dimension | Weight | What it checks |
|-----------|:------:|----------------|
| D1 Tool Surface | 15% | Total tool count (≤15 green, ≤30 yellow, >30 red) |
| D2 Schema Footprint | 25% | Per-tool token median and total cost |
| D3 Progressive Disclosure | 20% | Runtime toolset discovery or meta-tools |
| D4 Response Discipline | 20% | Pagination/shaping params on data tools |
| D5 Description Quality | 10% | Usage-boundary language in descriptions |
| D6 Redundancy | 10% | Duplicate property schema fragments |

Each dimension returns green / yellow / red (100 / 60 / 20 pts). Details in [`docs/SPEC.md`](docs/SPEC.md).

## Reproducibility

- Every result records its tokenizer (`o200k_base`) and capture date.
- The o200k_base vocab is vendored at `vendor/tiktoken/` (SHA256 `446a9538…`, matches the official OpenAI distribution) — no network required.
- Manifests are captured snapshots of `tools/list` with provenance notes; see `manifests/`.
- Approx-tokenizer output (browser, offline smoke tests) is explicitly labelled and must not be published as a canonical measurement.

## What this is and is not

TARE is **not** a security standard (see OWASP MCP Top 10), not a protocol-conformance suite (see the official MCP conformance suite under the Agentic AI Foundation), and not a prompt-design aid (see ICS, its sibling spec). It measures whether a server is *well-designed for the model that consumes it*.

License: Apache 2.0.
