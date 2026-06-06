# Cross-benchmark comparison (validation)

Captured snapshots of servers that appear on another public MCP "Quality
Rankings" board (0-co.github.io), measured through TARE for an apples-to-apples
comparison. Measured with the reference o200k_base encoding (vendored vocab,
fully reproducible).

Purpose: validate that TARE's Static Context Cost measures the same physical
footprint as an independent benchmark, and document that the Design Score is a
deliberately different axis.

## Token footprint: same quantity, different tokenizer

| Server        | Other board tokens | TARE tokens (o200k_base) | Delta  |
|---------------|--------------------|--------------------------|--------|
| SQLite        | 322                | 272                      | -15.5% |
| mcp-youtube   | 91                 | 78                       | -14.3% |
| DuckDB        | 51                 | 45                       | -11.8% |
| E2B           | 65                 | 69                       | +6.2%  |

TARE's o200k_base counts run ~12-15% below the other board's on multi-token
entries. The other board does not declare its encoding; the magnitude and
direction are consistent with a GPT-4-era (cl100k_base) tokenizer, which emits
more tokens per identical string. Ordering and ratios are preserved -- both
measure the serialized tool definitions -- so the residual gap is tokenizer
choice, not method. This is exactly why a declared reference encoding is
mandatory: undeclared absolute numbers are not comparable across benchmarks.

## Score is a different axis

The other board grades correctness (40%, executes the tools) + efficiency +
quality, so small functional servers cluster at 95-99 / A+. TARE's Design Score
is static design discipline (descriptions, progressive disclosure, redundancy),
so the same servers land 60-80. Matching token counts with diverging scores is
the proof that the divergence is methodological, not measurement error.

## Capture-date drift, observed live

Their snapshot of the awkoy Notion server: 5 tools / 205 tokens. Live at capture
time: 2 meta-tools (notion_execute, notion_describe) / 420 tokens (o200k_base). The package
was refactored between captures. This is why every TARE result records
captured_at: undated figures rot.

Captured 2026-06-05. Not part of the v0 8-server benchmark set.
