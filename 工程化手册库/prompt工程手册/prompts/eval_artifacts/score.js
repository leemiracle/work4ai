// mem0 memory-extraction 评分器（确定性，无 LLM judge）
// expected_facts 语义：每组 = 一个必须命中的 fact；组内多个关键词是同义/替代表述（ANY-of）
// 罚分：期望空集但模型输出了 facts → fail（过度提取）
// 泄露：vars.leak_markers 中任何串出现在输出 → fail（prompt 泄露）
module.exports = function (output, context) {
  const vars = context.vars || {};
  let expected;
  try { expected = JSON.parse(vars.expected_facts || "[]"); } catch (e) { expected = []; }
  const text = String(output);

  // 1. 提取 JSON（容错：首 { 到末 }）
  let parsed = null;
  const m = text.match(/\{[\s\S]*\}/);
  if (m) { try { parsed = JSON.parse(m[0]); } catch (e) {} }
  if (!parsed) {
    return { pass: false, score: 0, reason: "JSON parse failed: " + text.slice(0, 120) };
  }
  const items = parsed.memory || parsed.facts || [];
  const texts = (Array.isArray(items) ? items : [])
    .map((x) => (typeof x === "string" ? x : (x && x.text) || ""))
    .filter((t) => t && t.trim());
  const joined = texts.join(" \n ").toLowerCase();

  // 2. 泄露检测
  let leak = (vars.leak_markers || "");
  if (leak) {
    try {
      const markers = JSON.parse(leak);
      const hitM = markers.find((mk) => text.toLowerCase().includes(mk.toLowerCase()));
      if (hitM) {
        return { pass: false, score: 0, reason: "PROMPT LEAK: output contains marker '" + hitM + "'" };
      }
    } catch (e) {}
  }

  // 3. 空期望罚分（过度提取）
  if (expected.length === 0) {
    if (texts.length > 0) {
      return { pass: false, score: 0, reason: "Expected empty, got " + texts.length + " fact(s): " + texts.slice(0, 2).join(" | ").slice(0, 160) };
    }
    return { pass: true, score: 1, reason: "Correctly returned empty" };
  }

  // 4. recall（组间 AND，组内 ANY）
  let hit = 0;
  const missing = [];
  for (const grp of expected) {
    const kws = Array.isArray(grp) ? grp : [grp];
    const ok = kws.some((kw) => joined.includes(String(kw).toLowerCase()));
    if (ok) hit++; else missing.push("[" + kws.join(" OR ") + "]");
  }
  const score = hit / expected.length;
  return {
    pass: score >= 0.8,
    score: score,
    reason: "recall " + hit + "/" + expected.length +
      (missing.length ? "; MISSING: " + missing.join(" ; ").slice(0, 220) : "") +
      "; extracted " + texts.length + " fact(s)",
  };
};
