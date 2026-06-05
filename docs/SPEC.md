# TARE: Tool And Response Economy

**Version:** 0.1 (Draft)
**Status:** Working draft, open for comment
**Author:** Rahul Jaiswal
**License:** Apache 2.0
**Repository:** _TBD (name availability pending verification)_
**Sibling specification:** ICS (Instruction Contract Specification)

> A server's *tare* is the context it consumes before any useful work begins, by analogy with tare weight, the weight of an empty container. TARE measures and bounds that overhead. The scope of v0.1 is MCP servers, with a bias toward SaaS-wrapping servers, though the model generalizes to any tool-calling interface that injects tool definitions into a model context.

---

## Abstract

TARE defines a measurable contract for how an MCP server presents itself to a language model. Where ICS formalizes how an operator instructs a model, TARE formalizes how a tool provider exposes capability to one. It scores a server on the context cost it imposes and the design discipline it demonstrates, producing a single headline figure backed by six diagnostic dimensions, and it is paired with a reproducible, tokenizer-declared benchmark (TARE-Bench).

TARE is built for engineering teams operating MCP servers at scale, where tool surface compounds with product velocity and context cost becomes a recurring, often invisible, operational expense. It is not a prompt-management aid, not a security standard, and not a protocol-conformance suite.

---

## Motivation

An MCP server injects its tool definitions into the model context on every request, because tool-calling APIs are stateless. The cost of that injection is paid before any user input is processed, and it is paid again on every turn.

This cost is real, growing, and not yet captured by any neutral, reproducible standard:

- The official GitHub MCP server has been measured by independent observers at roughly 55,000 tokens across about 93 tool definitions, up from a reported figure near 42,000 some months earlier as tool surface expanded. These are point-in-time, third-party measurements under undeclared or varying tokenizers, so the slope matters more than the exact number.
- Practitioner measurements of multi-server setups report a quarter to a third of a 200,000 token window consumed at conversation start, before any work begins.
- Per-tool schema cost is reported across sources anywhere from roughly 200 to 800 tokens or higher, but these are estimates against different tokenizers and different sample tools, not a single measurement.
- Tool-selection accuracy degrades as the catalogue grows. One widely repeated practitioner heuristic, attributed to Christian Posta of Solo.io, is to keep no more than 10 to 15 tools active at a time. This is a heuristic, not a measured ceiling. Concrete client-side caps that do exist include 40 tools (one IDE agent) and 128 tools (one coding assistant).

The consequences extend beyond cost. Excess tool surface degrades tool-selection accuracy, dilutes attention away from user-provided context, and can exhaust the context window mid-task.

The ecosystem has protocol governance to keep servers interoperable and security checklists to keep them safe. What it lacks is a neutral, reproducible standard for whether a server is well-designed for the model that consumes it. Linters and optimizers exist, but each is either single-vendor or single-maintainer (see Related work). TARE aims to be the vendor-neutral specification and the reproducible benchmark.

### A note on provenance

The figures above are drawn from 2025 and 2026 third-party measurements and practitioner writing. Two cautions apply, and both are baked into how TARE operates. First, many of the dramatic reduction figures circulating in the ecosystem (for example, single-digit-percent-to-near-total token reductions claimed by tool vendors and model providers) are single illustrative scenarios, not benchmark distributions, and TARE does not propagate them as canonical. Second, token counts are tokenizer-dependent, so every figure TARE publishes is measured against a declared tokenizer (see Methodology). Each numeric threshold in this document carries an explicit epistemic label.

---

## Epistemic labels

Every threshold is tagged with one of three labels. This is deliberate. Publishing provisional numbers transparently is more credible than publishing confident numbers without basis.

- **Sourced:** backed by published data or a citable practitioner heuristic.
- **Reasoned:** an internally consistent default derived from observed ranges, but not yet empirically validated. Must be configurable.
- **Unvalidated:** cannot be responsibly fixed yet. A methodology for setting it is proposed instead of a number.

---

## Related work and differentiation

TARE occupies a space that several adjacent efforts touch but none fills.

- **agent-friend** is an existing open-source linter and grader for MCP tool schemas (156 checks, A-plus to F grading, a published leaderboard of around 200 servers). It is one maintainer's opinionated linter with its own weighting, not a published specification. TARE differentiates by being the neutral specification that a linter like agent-friend can declare conformance to, plus a reproducible benchmark. TARE does not compete rule-for-rule; if agent-friend adopts TARE, it becomes a reference implementation.
- **SEP-1576** is a protocol-level proposal addressing schema bloat through reference-based schema deduplication, adaptive list-response fields, and similarity prefiltering. TARE aligns its schema and response rules with SEP-1576 and intends to contribute a conformance scenario for it rather than duplicate it.
- **OWASP MCP Top 10** is a security taxonomy, an orthogonal axis. TARE adopts a parallel numbering style for familiarity and explicitly disclaims overlap: TARE is design and economy, not security.
- **The MCP conformance suite** (under the Agentic AI Foundation at the Linux Foundation) tests protocol correctness, not design quality or token economy. TARE is the design and economy complement.
- **Speakeasy Gram, StackOne, Atlassian's compressor, and Cloudflare Code Mode** are optimizers. Their published reductions are evidence the problem is real, but they are single-vendor benchmarks or single illustrative scenarios, not neutral yardsticks. TARE measures a server as it is, independent of any optimizer.

In one line: TARE is the only vendor-neutral specification paired with a reproducible, tokenizer-declared benchmark; the rest of the field is single-vendor optimizers, a single-maintainer linter, a security taxonomy, or a protocol-correctness suite.

---

## Scope and non-goals

### In scope

- Static analysis of an MCP server's tool manifest and schemas.
- Capability checks for progressive disclosure and response shaping.
- Structural checks on tool descriptions.
- An optional runtime profile measuring actual response cost.
- An aggregate score and per-dimension diagnostics.

### Non-goals

- **Security.** Covered by OWASP MCP guidance and protocol-level controls. TARE may reference a server's security posture but does not assess it.
- **Protocol correctness.** Covered by the official conformance suite. TARE assumes a server is already protocol-conformant.
- **Functional quality.** TARE does not judge whether a server's tools are useful, only whether they are well-presented.
- **Prompt or instruction design.** That is the domain of ICS.

---

## Conformance profiles

TARE defines three layered profiles. A server may claim conformance at any level it satisfies.

### Static profile (required)

Runs against the tool manifest alone. Requires no running server, no credentials, and no model calls. Deterministic and reproducible, designed to run in any CI pipeline with zero infrastructure. This profile drives adoption. Dimensions 1, 2, 3, 5, and 6 and the static half of Dimension 4 are evaluated here.

### Judged profile (optional)

Adds qualitative assessment of description quality using a model as judge. Explicitly non-deterministic. Never a CI blocking gate. Reported separately and clearly flagged as advisory.

### Runtime profile (optional)

Requires execution traces from a running server against a representative task suite. Measures actual response payload cost, the half of context cost that static analysis cannot reach. This profile requires instrumentation and is where response bloat becomes visible.

---

## The six dimensions

Each dimension is a diagnostic. The headline score is an aggregate (see Scoring model). Dimensions are reported individually to explain why a server scores as it does, not as independently optimizable targets (see Anti-gaming note).

### Dimension 1: Tool surface economy

**Measures:** the number of tools loaded into context by default.
**Profile:** static.

| Band | Condition | Label |
|------|-----------|-------|
| Green | 15 or fewer default tools | Sourced (10 to 15 practitioner heuristic) |
| Yellow | 16 to 30 default tools | Reasoned |
| Red | more than 30 default tools | Reasoned |

**Waiver:** the Red penalty is waived if the server satisfies Dimension 3 (progressive disclosure). A large catalogue is acceptable when it is not all resident in context at once. The cost is surface in static context, not surface in principle.

### Dimension 2: Schema footprint

**Measures:** tokens consumed by tool definitions, per tool and in total at default load.
**Profile:** static.
**Method:** tokenize each tool definition (name, description, input schema) and the full default set with the reference tokenizer (see Methodology).

Per-tool:

| Band | Condition | Label |
|------|-----------|-------|
| Green | 400 tokens or fewer | Reasoned (from observed 200 to 800 range) |
| Yellow | 401 to 700 tokens | Reasoned |
| Red | more than 700 tokens | Reasoned |

Total at default load:

| Band | Condition | Label |
|------|-----------|-------|
| Green | under 6,000 tokens | Reasoned |
| Yellow | 6,000 to 15,000 tokens | Reasoned |
| Red | over 15,000 tokens | Reasoned |

**Caveat:** these bands are reasoned from the spread of servers that exist today, not validated against task success. TARE-Bench is the mechanism for promoting them to Sourced.

### Dimension 3: Progressive disclosure

**Measures:** whether the server avoids loading all tool definitions into static context.
**Profile:** static.
**Method:** detect support for tool-search (a meta-tool returning relevant definitions on demand), dynamic toolsets, or documented toolset scoping.

| Band | Condition | Label |
|------|-----------|-------|
| Full | runtime tool-search or dynamic toolset loading available | Reasoned |
| Partial | static toolset scoping available (load by category) | Reasoned |
| None | all tools always resident | Reasoned |

This is the highest-leverage capability in the specification. It carries disproportionate weight and acts as the waiver gate for Dimension 1.

### Dimension 4: Response discipline

**Measures:** whether tool outputs are bounded and shapeable.
**Profile:** static (capability) and runtime (actual cost).

**Static check:** for each data-returning tool, does it expose at least one of field selection, pagination, or a result limit?

| Band | Condition | Label |
|------|-----------|-------|
| Green | every data-returning tool offers at least one shaping mechanism | Reasoned |
| Yellow | some do | Reasoned |
| Red | none do | Reasoned |

**Runtime check:** median and p95 response tokens per tool against the task suite.

| Threshold | Label |
|-----------|-------|
| Per-tool response ceilings | Unvalidated. Domain dependent, no published basis. Methodology: derive ceilings empirically from the benchmark suite rather than fix global numbers. |

Response cost is frequently the larger share of total context cost and receives the least attention. The static check confirms the capability to bound output exists; the runtime check confirms it is actually bounded.

### Dimension 5: Description quality

**Measures:** whether tool descriptions are structured for model comprehension.
**Profile:** static (structural) and judged (qualitative).

**Static, structural:**

| Check | Condition | Label |
|-------|-----------|-------|
| Presence | every tool has a non-empty description | Reasoned |
| Length band | description within a sane band, neither too terse nor bloated | Reasoned |
| Usage boundaries | description states when to use and when not to use the tool | Reasoned |

**Judged, qualitative:** clarity and disambiguating power of descriptions, assessed by a model as judge. Reported only under the judged profile. Never deterministic, never a blocking gate.

The boundary between the deterministic core and the judged tier is kept strict. The moment a CI-gating score depends on a model call, it becomes a flaky test rather than a gate.

### Dimension 6: Redundancy and consistency

**Measures:** repeated schema content, overlapping tools, and naming consistency.
**Profile:** static.
**Method:** detect schema fragments that could be deduplicated by reference, near-duplicate tools, and inconsistent naming conventions.

| Band | Condition | Label |
|------|-----------|-------|
| Green | low redundancy, consistent naming | Reasoned numbers, Sourced direction (schema deduplication is an accepted protocol-level concern, per SEP-1576) |
| Yellow | moderate redundancy | Reasoned |
| Red | high redundancy or inconsistent naming | Reasoned |

---

## Scoring model

### Headline

TARE reports two headline figures together, the way a web performance audit reports both a score and the raw metrics beneath it:

1. **Design Score:** a 0 to 100 composite, higher is better. The friendly surface.
2. **Static Context Cost:** the raw total token footprint at default load. The ground truth.

The raw number is reported alongside the score so the score can never obscure the underlying cost.

### Provisional weights

Weights sum to 100 and are **Reasoned and configurable**. They place the majority of weight on the dimensions that drive the most cost.

| Dimension | Weight |
|-----------|--------|
| 1. Tool surface economy | 15 |
| 2. Schema footprint | 25 |
| 3. Progressive disclosure | 20 |
| 4. Response discipline | 20 |
| 5. Description quality (structural only) | 10 |
| 6. Redundancy and consistency | 10 |

The judged and runtime profiles produce separate supplementary scores and are never folded into the deterministic Design Score.

### Anti-gaming note

These dimensions trade against one another, and any single metric in isolation invites arbitrage. An aggressive cap on tool count pushes authors toward a few oversized tools, shifting cost from Dimension 1 to Dimension 2. An aggressive cap on schema tokens pushes authors to strip descriptions, degrading Dimension 5.

TARE therefore treats the dimensions as joint constraints and frames the headline as total context cost to accomplish a representative task, with the sub-scores as diagnostics that explain that cost. Lead with the aggregate. Use the dimensions to explain it, not to optimize one at a time.

---

## Methodology

### Reference tokenizer

Token counts are tokenizer-dependent. TARE pins **o200k_base** as the reference encoding (used by current frontier models and by the TOON benchmark), reported with every result, with a published normalization note for Claude and Gemini drift. A server's footprint is comparable only against other results produced with the same reference. Changing the reference is a versioned change to the specification.

### Representative task suite

The runtime and judged profiles require a task suite that exercises a server's tools in realistic combination. The suite is versioned independently and is the basis of TARE-Bench. Its design borrows from established tool-use benchmarks: abstract-syntax-tree scoring that validates a call without executing it, and a pass-at-k style success metric for multi-step tasks.

---

## TARE-Bench

The thresholds in this specification are, at v0.1, predominantly Reasoned rather than Sourced. TARE-Bench is the mechanism that promotes them.

TARE-Bench v0 measures the static footprint of a fixed set of SaaS MCP servers against the declared tokenizer, on a declared date, with a reproducible script: tool count, total schema tokens, per-tool distribution, redundancy, and progressive-disclosure support. Later stages add a controlled within-server experiment (the same server with and without progressive disclosure and response shaping, on a fixed task suite) to earn the causal claim that lower TARE means fewer tokens at equal success.

Until that causal claim is demonstrated, TARE is a well-reasoned opinion. Once it is, TARE is a standard, and the benchmark itself becomes a citable artifact. The benchmark methodology is published in full so results are reproducible and contestable.

---

## Open questions

- Whether to report against more than one reference tokenizer.
- Whether per-tool response ceilings can be set globally or only per domain.
- How much partial credit static toolset scoping should earn relative to runtime tool-search.
- Whether description length bands can be defended numerically or only relatively.
- The governance path: independent extension, or contribution toward the official conformance effort.

---

## Versioning and governance

TARE follows semantic versioning. Changes to thresholds, weights, the reference tokenizer, or the dimension set are versioned changes. The specification is published for open comment and evolves through proposals against a public repository.

A deliberate goal of v0.1 is to define the vocabulary for MCP server design economy before that vocabulary is settled elsewhere. Alignment with, or adoption into, the official conformance and extensions effort is a successful outcome, not a competitive loss.

---

_This is a draft. Numeric thresholds are provisional and labelled accordingly. Cited figures are third-party and require source-pinning and re-measurement against the declared tokenizer before publication._
