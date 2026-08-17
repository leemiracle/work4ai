// mem0 评分器 v2：recall（组间 AND / 组内 ANY）+ 空集罚分 + leak/forbidden 检测
module.exports = function (output, context) {
  const vars = context.vars || {};
  let expected;
  try { expected = JSON.parse(vars.expected_facts || "[]"); } catch (e) { expected = []; }
  const text = String(output);
  let parsed = null;
  const m = text.match(/\{[\s\S]*\}/);
  if (m) { try { parsed = JSON.parse(m[0]); } catch (e) {} }
  if (!parsed) return { pass: false, score: 0, reason: "JSON parse failed: " + text.slice(0, 100) };
  const items = parsed.memory || parsed.facts || [];
  const texts = (Array.isArray(items) ? items : [])
    .map((x) => (typeof x === "string" ? x : (x && x.text) || "")).filter((t) => t && t.trim());
  const joined = texts.join(" \n ").toLowerCase();
  for (const key of ["leak_markers", "forbidden_markers"]) {
    let mk = vars[key];
    if (mk) {
      try {
        const hit = JSON.parse(mk).find((x) => text.toLowerCase().includes(String(x).toLowerCase()));
        if (hit) return { pass: false, score: 0, reason: key.toUpperCase() + " HIT: '" + hit + "'" };
      } catch (e) {}
    }
  }
  if (expected.length === 0) {
    if (texts.length > 0)
      return { pass: false, score: 0, reason: "Expected empty, got " + texts.length + ": " + texts.slice(0, 2).join(" | ").slice(0, 150) };
    return { pass: true, score: 1, reason: "correctly empty" };
  }
  let hit = 0; const missing = [];
  for (const grp of expected) {
    const kws = Array.isArray(grp) ? grp : [grp];
    if (kws.some((kw) => joined.includes(String(kw).toLowerCase()))) hit++;
    else missing.push("[" + kws.join("|") + "]");
  }
  const score = hit / expected.length;
  return { pass: score >= 0.8, score, reason: "recall " + hit + "/" + expected.length + (missing.length ? " MISS " + missing.join(";").slice(0, 200) : "") + "; n=" + texts.length };
};
