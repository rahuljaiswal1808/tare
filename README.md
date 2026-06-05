# TARE: Tool And Response Economy

TARE is an open standard, benchmark, and reference tooling for the context-window cost
and design economy of MCP servers.

A server's *tare* is the context it consumes before any useful work begins, by analogy
with tare weight, the weight of an empty container. Every MCP server injects its tool
definitions into the model context on every request, and that overhead is paid before
any work starts and again on every turn. TARE measures it and scores the design
discipline behind it.

The project has three parts:

- **The specification** ([`docs/SPEC.md`](docs/SPEC.md)): six diagnostic dimensions, two
  headline figures (a 0-100 Design Score and the raw Static Context Cost), three
  conformance profiles, and an explicit epistemic label on every threshold.
- **The benchmark** (TARE-Bench): a reproducible, tokenizer-declared measurement of real
  SaaS MCP servers. This repository contains the v0 static measurement engine behind it.

TARE is vendor-neutral by design. It measures a server as it is, independent of any
optimizer or hosting platform. It is not a security standard (that is OWASP MCP Top 10),
not a protocol-conformance suite (that is the official MCP conformance suite), and not a
prompt-design aid (that is ICS, its sibling specification).

## What this v0 does

- Pulls a server's tool list by one of two paths: live `tools/list` over MCP
  (authoritative) or a captured manifest on disk (fast, partial fallback).
- Tokenizes each tool definition with the reference encoding (o200k_base) and computes
  the static dimensions from the spec: tool surface, schema footprint, progressive
  disclosure, response discipline (static capability), description quality (structural),
  and redundancy.
- Emits two headline figures per server, a 0-100 Design Score and the raw Static
  Context Cost in tokens, and builds a leaderboard across servers.

The runtime profile (actual response payload cost) and the judged profile (description
quality by model-as-judge) are out of scope for this static harness and belong to a
later stage.

## Install

```
pip install -e .          # core (static + manifest path)
pip install -e '.[live]'  # adds the mcp SDK for live tools/list
pip install -e '.[dev]'   # adds pytest
```

## Run

```
# offline smoke test against the bundled fixture (approx tokenizer, not publishable)
tare measure-server --server fixture --config servers.smoke.toml --source manifest --tokenizer approx
tare report

# real measurement (needs o200k_base, which downloads its vocab on first use)
tare measure-server --server github --source manifest      # once a manifest is captured
tare measure-server --server all --source auto             # live, falling back to manifest
tare report
```

## Honesty rules baked in

- Every result records its tokenizer and capture date. Approx-tokenizer output is
  labelled and must never be published as a real measurement.
- Server endpoints and auth in `servers.toml` are starting points and must be verified
  before live fetching.
- Thresholds are provisional (see the epistemic labels in `docs/SPEC.md`). The
  controlled benchmark that would promote them to validated is a later stage.

License: Apache 2.0.
