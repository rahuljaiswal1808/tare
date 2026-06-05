// TARE scorer — pure JS port of tare/dimensions.py + tare/scoring.py
// Tokenizer: approx char/4 (o200k_base unavailable in browser). Label results accordingly.

const META_TOOL_HINTS = new Set([
  "search_tools","list_tools","find_tools","list_toolsets",
  "enable_toolset","tool_search","search_for_tools"
]);
const SHAPING_KEYS = new Set([
  "limit","page","page_size","pagesize","cursor","offset","fields","projection",
  "select","top","max_results","maxresults","per_page","perpage","first","after"
]);
const DATA_TOOL_HINTS = ["list","get","search","read","query","find","fetch","retrieve"];
const USAGE_HINTS = ["use this","use when","when you","do not","don't","only use","avoid","prefer","instead of"];

const WEIGHTS = {
  "1_tool_surface": 15,
  "2_schema_footprint": 25,
  "3_progressive_disclosure": 20,
  "4_response_discipline": 20,
  "5_description_quality": 10,
  "6_redundancy": 10,
};

const BAND_POINTS = { green: 100, yellow: 60, red: 20, full: 100, partial: 60, none: 20 };

function approxTokens(text) {
  return Math.max(1, Math.round(text.length / 4));
}

function serializeTool(name, description, inputSchema) {
  return JSON.stringify({ name, description: description || "", inputSchema: inputSchema || {} });
}

function toolTokens(t) {
  return approxTokens(serializeTool(t.name, t.description, t.inputSchema || t.input_schema));
}

// Dimension 1
function d1_toolSurface(tools) {
  const n = tools.length;
  const band = n <= 15 ? "green" : n <= 30 ? "yellow" : "red";
  return { dimension: "Tool Surface", band, points: BAND_POINTS[band], raw: { tool_count: n } };
}

// Dimension 2
function d2_schemaFootprint(tools) {
  const perTool = tools.map(toolTokens);
  const total = perTool.reduce((a, b) => a + b, 0);
  const sorted = [...perTool].sort((a, b) => a - b);
  const median = sorted.length ? sorted[Math.floor(sorted.length / 2)] : 0;
  const p95idx = Math.min(Math.floor(sorted.length * 0.95), sorted.length - 1);
  const p95 = sorted.length ? sorted[p95idx] : 0;
  const mx = sorted.length ? sorted[sorted.length - 1] : 0;

  const ptBand = median <= 400 ? "green" : median <= 700 ? "yellow" : "red";
  const totBand = total < 6000 ? "green" : total <= 15000 ? "yellow" : "red";
  const points = Math.round((BAND_POINTS[ptBand] + BAND_POINTS[totBand]) / 2);
  const worst = BAND_POINTS[ptBand] < BAND_POINTS[totBand] ? ptBand : totBand;
  return { dimension: "Schema Footprint", band: worst, points,
    raw: { total_tokens: total, median_per_tool: median, p95_per_tool: p95, max_per_tool: mx } };
}

// Dimension 3
function d3_progressiveDisclosure(tools, declaresDynamic) {
  const names = new Set(tools.map(t => t.name.toLowerCase()));
  const hasMeta = [...names].some(n => META_TOOL_HINTS.has(n) || (n.includes("search") && n.includes("tool")));
  const band = (declaresDynamic || hasMeta) ? "full" : "none";
  return { dimension: "Progressive Disclosure", band, points: BAND_POINTS[band],
    raw: { declares_dynamic_toolsets: declaresDynamic, meta_tool_detected: hasMeta } };
}

// Dimension 4
function d4_responseDiscipline(tools) {
  const dataTools = tools.filter(t => DATA_TOOL_HINTS.some(h => t.name.toLowerCase().includes(h)));
  if (!dataTools.length) {
    return { dimension: "Response Discipline", band: "green", points: 100, raw: { data_tools: 0, with_shaping: 0 } };
  }
  let withShaping = 0;
  for (const t of dataTools) {
    const schema = t.inputSchema || t.input_schema || {};
    const props = new Set(Object.keys(schema.properties || {}).map(k => k.toLowerCase()));
    if ([...props].some(p => SHAPING_KEYS.has(p))) withShaping++;
  }
  const frac = withShaping / dataTools.length;
  const band = frac >= 0.999 ? "green" : frac > 0 ? "yellow" : "red";
  return { dimension: "Response Discipline", band, points: BAND_POINTS[band],
    raw: { data_tools: dataTools.length, with_shaping: withShaping, fraction: Math.round(frac * 100) / 100 } };
}

// Dimension 5
function d5_descriptionQuality(tools) {
  if (!tools.length) return { dimension: "Description Quality", band: "red", points: 20, raw: { tools: 0 } };
  let passing = 0;
  for (const t of tools) {
    const d = (t.description || "").trim();
    const hasDesc = d.length > 0;
    const inBand = d.length >= 20 && d.length <= 1500;
    const hasUsage = USAGE_HINTS.some(h => d.toLowerCase().includes(h));
    if (hasDesc && inBand && hasUsage) passing++;
  }
  const frac = passing / tools.length;
  const band = frac >= 0.8 ? "green" : frac >= 0.5 ? "yellow" : "red";
  return { dimension: "Description Quality", band, points: BAND_POINTS[band],
    raw: { tools: tools.length, passing, fraction: Math.round(frac * 100) / 100 } };
}

// Dimension 6
function d6_redundancy(tools) {
  const fragments = [];
  for (const t of tools) {
    const schema = t.inputSchema || t.input_schema || {};
    for (const sub of Object.values(schema.properties || {})) {
      fragments.push(JSON.stringify(sub, Object.keys(sub).sort()));
    }
  }
  const total = fragments.length;
  const unique = new Set(fragments).size;
  const ratio = total ? 1 - unique / total : 0;
  const band = ratio < 0.3 ? "green" : ratio < 0.6 ? "yellow" : "red";
  return { dimension: "Redundancy", band, points: BAND_POINTS[band],
    raw: { property_fragments: total, unique, redundancy_ratio: Math.round(ratio * 100) / 100 } };
}

export function score(manifest) {
  const tools = manifest.tools || [];
  const declaresDynamic = manifest.declares_dynamic_toolsets || false;

  const dims = [
    d1_toolSurface(tools),
    d2_schemaFootprint(tools),
    d3_progressiveDisclosure(tools, declaresDynamic),
    d4_responseDiscipline(tools),
    d5_descriptionQuality(tools),
    d6_redundancy(tools),
  ];

  const totalWeight = Object.values(WEIGHTS).reduce((a, b) => a + b, 0);
  const dimKeys = Object.keys(WEIGHTS);
  const weighted = dims.reduce((sum, d, i) => sum + d.points * Object.values(WEIGHTS)[i], 0);
  const designScore = Math.round(weighted / totalWeight);
  const staticContextCost = tools.reduce((sum, t) => sum + toolTokens(t), 0);

  return { designScore, staticContextCost, toolCount: tools.length, dimensions: dims };
}
