# Cross-benchmark comparison (validation)

Captured snapshots of servers that appear on another public MCP "Quality
Rankings" board (0-co.github.io), measured through TARE for an apples-to-apples
comparison. Approx tokenizer (char/4) was used because o200k_base cannot be
downloaded in the capture environment; treat token figures as smoke-test only.

Purpose: validate that TARE's Static Context Cost measures the same physical
footprint as an independent benchmark, and document that the Design Score is a
deliberately different axis.

## Token footprint agrees within a few percent

| Server        | Other board tokens | TARE tokens (approx) |
|---------------|--------------------|----------------------|
| SQLite        | 322                | 318                  |
| mcp-youtube   | 91                 | 90                   |
| DuckDB        | 51                 | 50                   |
| E2B           | 65                 | 72                   |

This is cross-validation of the footprint number, not a coincidence: both
measure the serialized tool definitions.

## Score is a different axis

The other board grades correctness (40%, executes the tools) + efficiency +
quality, so small functional servers cluster at 95-99 / A+. TARE's Design Score
is static design discipline (descriptions, progressive disclosure, redundancy),
so the same servers land 60-80. Matching token counts with diverging scores is
the proof that the divergence is methodological, not measurement error.

## Capture-date drift, observed live

Their snapshot of the awkoy Notion server: 5 tools / 205 tokens. Live at capture
time: 2 meta-tools (notion_execute, notion_describe) / 468 tokens. The package
was refactored between captures. This is why every TARE result records
captured_at: undated figures rot.

Captured 2026-06-05. Not part of the v0 8-server benchmark set.
