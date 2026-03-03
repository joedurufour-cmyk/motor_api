const ENGINE_FILES = [
  "./data/MJ7_EMULATION_ENGINE_v3.3.md",
  "./data/MJ7_KNOWLEDGE_BASE_v3.3.md",
  "./data/GPT_CORE_BEHAVIOR_v3.3.txt",
  "./data/CHARACTER_DB_ADAPTER_v1.md",
];

function normalizeNewlines(s) {
  return (s || "").replace(/\r\n/g, "\n");
}

async function loadEngine() {
  const parts = [];
  for (const path of ENGINE_FILES) {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`No pude cargar: ${path}`);
    parts.push(`### SOURCE: ${path}\n` + normalizeNewlines(await res.text()));
  }
  return parts.join("\n\n");
}

// Motor mínimo (placeholder): arma prompt “estético rico” con composición dominante.
// Luego lo refinamos con tus reglas exactas.
function buildPrompt({ brief, ar, dom, params }) {
  const subject = `female superheroine, Supergirl-inspired, elegant anime illustration, bright blue eyes, long flowing blonde hair, confident soft smile`;
  const composition =
    `composition-dominant, mid-body framing, torso-centered, clean negative space background, strong silhouette read, dynamic diagonal tension`;
  const clothing =
    `blue long-sleeve top with red cape accents, cropped shirt with subtle fabric folds, denim jeans, iconic chest emblem clearly readable`;
  const lighting =
    `soft high-key studio lighting, gentle rim separation, controlled highlights, smooth cel shading with painterly gradients`;
  const detail =
    `hyper-detailed linework, clean edges, high-resolution illustration, tasteful micro-texture, coherent anatomy, no distortions`;

  const domLine = `DOMINANCE_LOCK: ${dom}`;
  const arLine = `--ar ${ar}`;
  const p = params?.trim() ? params.trim() : "--v 7 --style raw --chaos 3 --stylize 25";

  return [
    subject,
    composition,
    clothing,
    lighting,
    detail,
    `USER_BRIEF: ${brief?.trim() || "(none)"}`,
    domLine,
    arLine,
    p,
  ].join(", ");
}

(async () => {
  const briefEl = document.getElementById("brief");
  const arEl = document.getElementById("ar");
  const domEl = document.getElementById("dom");
  const paramsEl = document.getElementById("params");
  const outEl = document.getElementById("out");
  const engineEl = document.getElementById("engine");

  let engineText = "";
  try {
    engineText = await loadEngine();
    engineEl.textContent = engineText.slice(0, 12000) + (engineText.length > 12000 ? "\n\n…(truncado)" : "");
  } catch (e) {
    engineEl.textContent = `ERROR cargando motor: ${e.message}`;
  }

  document.getElementById("btn").addEventListener("click", () => {
    const prompt = buildPrompt({
      brief: briefEl.value,
      ar: arEl.value,
      dom: domEl.value,
      params: paramsEl.value,
    });
    outEl.textContent = prompt;
  });

  document.getElementById("copy").addEventListener("click", async () => {
    const t = outEl.textContent || "";
    if (!t) return;
    await navigator.clipboard.writeText(t);
  });
})();