# Capturing manifests

A manifest is a captured `tools/list` response for a server, used by the manifest
source when live fetch is not yet wired or authenticated.

Shape:

```json
{
  "captured_at": "2026-06-05T00:00:00+00:00",
  "provenance": "how and from where this was captured",
  "declares_dynamic_toolsets": false,
  "tools": [ { "name": "...", "description": "...", "inputSchema": { } } ]
}
```

How to capture:
- Live, once auth works: run `tare measure-server --server <name> --source live`,
  then save the fetched toolset, or add a small dump command.
- By hand: connect with any MCP client (Inspector, an SDK script), call `tools/list`,
  and paste the `tools` array in, filling `captured_at` and `provenance`.

Always record `captured_at` and `provenance`. Numbers without a date and a tokenizer
are not publishable.
