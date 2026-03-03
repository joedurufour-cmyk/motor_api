# MJ7_EMULATION_ENGINE — Knowledge Base v3.3
# Reference file for RAG retrieval in Custom GPT

---

## SECTION 0: EXECUTION INTEGRITY LAYER [v3.1 NEW]

### Three Preemption Triggers That Cause Structural Drift

| Trigger | What Happens | Countermeasure |
|---------|-------------|----------------|
| **Safety policy** | Model exits structured mode, falls back to conversational refusal | **PCE**: rewrite tokens to safe equivalent, continue pipeline, tag [PCE-ADJUSTED] |
| **Output pressure** | 9 sections + 4 variants = high cost → model merges/skips sections | **ACP**: compress within sections (never skip), report compression level |
| **Context attenuation** | In long chats, instructions lose weight → gradual format erosion | **CPD**: self-check every response, "REANCHOR" recovery keyword, proactive warning at ~15 turns |

### PCE Sub-Protocol (Policy-Compatible Execution)
```
a) LOG:      "[PCE] Restriction detected: {type}"
b) REWRITE:  Reformulate affected tokens/blocks to safe equivalents
c) MARK:     Tag modified blocks with [PCE-ADJUSTED]
d) CONTINUE: Execute ALL remaining pipeline steps
e) REPORT:   METADATA → PCE_active: true, adjustments: N, affected_blocks: [list]
```
Result: User always gets complete 9-section output, never bare refusal.

### ACP Compression Priority (Anti-Collapse Protocol)
When output budget is tight, compress in this order (last→first):
1. AXES → compress (table only)
2. DEDUPE → compress (count + key changes)
3. ASSIMILATION → compress (list only)
4. EQUATION → compress (formula only, skip variable definitions)
5. ANALYSIS → always full
6. STRUCTURED → always full
7. VARIANTS → always full
8. LINT → always full
9. METADATA → always full

Minimum viable section = header + 1 line.

### CPD Recovery Triggers (Context Pressure Defense)
- User keywords: "drift", "dropped structure", "REANCHOR", "broke format"
- Action: Re-execute last request in full 9-section format
- ANALYSIS gets: "CPD recovery triggered"
- Proactive: After ~15 active motor turns, warn user about REANCHOR availability

---

## SECTION 1: TOKEN CERTAINTY — V3 EXTENDED MODEL

### Empirical Certainty Zones (Midjourney V7)

| Zone | Token Range | Z_i | Certainty % | Behavior |
|------|-------------|-----|-------------|----------|
| Nucleus | 1–5 | 1.00 | 100% | Subject + core action, first generation |
| High Signal | 6–20 | 0.90 | 85–95% | Style + environment, no rerolls needed |
| Medium | 21–40 | 0.60 | 50–70% | Secondary modifiers, omission risk if conflicting |
| Attenuation | 41–60 | 0.40 | 30–50% | Multiple variations required, concept-mixing |
| Noise | 60+ | 0.10 | <10% | Grammar > listing, background texture only |

### Complete V3 Equation Set

```
VARIABLES:
  T         = total tokens in prompt
  A_max     = max assimilation window (low=25, medium=40, high=55)
  EAW       = min(T, A_max)
  overflow  = max(0, T - A_max)
  OR%       = (overflow / A_max) × 100

PER-TOKEN:
  B_i       = base semantic weight (archetype density, higher for precise terms)
  P_i       = positional weight = 1 / (1 + 0.02 × i)
  D_i       = dominance multiplier from block rank (1.0–3.0)
  Z_i       = zonal attenuation (from table above)
  PDW_i     = perceptual dominance weight (image mode: 0.7–1.4; text mode: 1.0)
  S_i       = semantic direction vector of token i

DECAY:
  λ_over    = overflow decay constant ∈ [0.01, 0.3]
  NOTE: λ_pos is already encoded in P_i — do NOT apply separate positional decay

CERTAINTY:
  C_i = (B_i × P_i × D_i × Z_i × PDW_i × A_i) × exp(-λ_over × overflow)
  [A_i = assertion boost, see Section 17]

RENDER VECTOR:
  FRV = Σ (C_i × S_i)  for i ∈ [1, EAW]

PROMPT:
  Prompt = OrderedBlocks(FRV, CanonicalHierarchy)

PRUNING:
  Prune token i if C_i < prune_threshold (default: 0.15)
  Apply DEDUPE before pruning

MULTI-PROMPT WEIGHTS:
  W_norm_i = w_i / Σ(w_j) for all j
  CONSTRAINT: Σ(w_j) > 0
  Saturation: beyond ::8, incremental impact imperceptible
```

### Archetype Compression Principle

Dense archetype tokens are more efficient than verbose descriptions:
- "armada" > "many ships" (single concept token, higher B_i)
- "serratus anterior" > "muscles on the side of the ribs" (medical/art corpus alignment)
- "family" > "a man, a woman, and two children" (compressed concept)
- "mesomorph physique" > "medium-build muscular body type" (fitness corpus match)
- "chiaroscuro" > "dramatic lighting with deep shadows" (art-historical precision)

### Fluff Tokens — NEVER in Positions 1–5:
ultra-realistic, 4k, 8k, masterpiece, best quality, highly detailed, award-winning,
stunning, breathtaking, gorgeous, incredible, amazing, perfect, beautiful, epic

These displace critical tokens into low-certainty zones, degrading output quality.

---

## SECTION 2: REDUNDANCY COLLAPSE / DEDUPE PROTOCOL

### Rules (applied BEFORE certainty computation):

1. **Detect near-duplicates:** >70% lexical overlap OR synonyms within same archetype family.
2. **Keep the denser token:** Higher B_i wins. Shorter phrasing preferred when B_i is equal.
3. **One token per concept:** Unless multi-weight (::) is intentional by user.

### DEDUPE Examples:

| Keep | Drop | Reason |
|------|------|--------|
| "serratus anterior definition" | "muscles on side of ribs" | Higher B_i, precise training match |
| "chiaroscuro" | "dramatic shadow lighting" | Single archetype token |
| "V-taper" | "narrow waist wide shoulders" | Compressed archetype |
| "compression gear" | "tight-fitting athletic clothing" | Specific material keyword |
| "shallow depth of field" | "blurry background" | Technical precision |

### Heuristic:
If two tokens map to the same visual output and occupy adjacent zones, the one with fewer tokens and higher archetype density survives. This is deterministic, not probabilistic.

---

## SECTION 3: TSI — TOKEN STABILITY INDEX

### Purpose:
Track prompt stability across iterations WITHIN a single session. Detect drift before it degrades output.

### Formula:
```
TSI_k = 100 - (w1×OR% + w2×PruneRate% + w3×ConflictRate% + w4×RedundancyRate%)

Where:
  w1 = 0.35 (overflow weight)
  w2 = 0.25 (pruning weight)
  w3 = 0.25 (conflict weight)
  w4 = 0.15 (redundancy weight)

  OR%             = max(0, T - A_max) / A_max × 100
  PruneRate%      = (tokens_pruned / T) × 100
  ConflictRate%   = (conflict_resolutions / active_blocks) × 100
  RedundancyRate% = (deduped_tokens / T_before_dedupe) × 100

  active_blocks   = number of blocks with at least one token assigned
```

### Interpretation:
| TSI Range | Status | Action |
|-----------|--------|--------|
| 85–100 | Stable | Continue normally |
| 70–84 | Moderate drift | Review pruned tokens and conflicts |
| 50–69 | High drift | Warn user, suggest simplification |
| <50 | Critical | Recommend restart from base prompt |

### Drift Alert:
If TSI_k drops >15 points vs TSI_(k-1), output:
```
⚠ DRIFT ALERT: TSI dropped from [X] to [Y]
Causes: [list specific factors]
Recommendation: [specific action]
```

### Scope:
TSI is session-only. No cross-conversation persistence. Reset on new conversation.

---

## SECTION 4: PDW — PERCEPTUAL DOMINANCE WEIGHT (Image Mode)

### When to Apply:
Only in MODE: from_image or hybrid. In from_text mode, PDW_i = 1.0 for all tokens.

### PDW Factors (each scored 0.7–1.4):

| Factor | Low PDW (0.7–0.9) | High PDW (1.1–1.4) |
|--------|-------------------|---------------------|
| Frame area | Subject occupies <20% of frame | Subject occupies >50% of frame |
| Contrast/saliency | Low contrast, blends into scene | High contrast edges, stands out |
| Focus/sharpness | Out of focus, bokeh region | Sharp, in focal plane |
| Lighting emphasis | In shadow, unlit | Key-lit, rim-lit, spotlight |

### PDW Computation:
```
PDW_i = mean(area_score, contrast_score, focus_score, light_score)

Clamp: PDW_i ∈ [0.7, 1.4]
```

### Mapping to Blocks:
- Subject in sharp focus, center frame → SUBJECT block gets PDW ~1.3
- Background bokeh, low contrast → ENVIRONMENT block gets PDW ~0.8
- Rim-lit clothing detail → CLOTHING block gets PDW ~1.1

---

## SECTION 5: 11-BLOCK CANONICAL HIERARCHY — EXTENDED

| Rank | Block | Dominance | Purpose | High-Signal Examples |
|------|-------|-----------|---------|---------------------|
| 1 | REF_BLOCK | 3.0 | Identity anchor | --oref URL, --sref URL, --iw 2 |
| 2 | SUBJECT | 3.0 | Primary entity | "athletic male figure", "jumping spider", "vintage watch" |
| 3 | STRUCTURE/PHYSIQUE | 2.5 | Body/form | "swimmer's build", "V-taper", "mesomorph physique" |
| 4 | POSE | 2.0 | Action + tension | "mid-sprint", "lifting weights", "casual lean" |
| 5 | EXPRESSION | 1.8 | Emotion-effort congruence | "determined gaze", "serene strength", "candid effort" |
| 6 | CLOTHING/MATERIAL | 1.5 | Fabric + skin interaction | "compression gear", "sweat-glistening skin" |
| 7 | LIGHTING | 1.5 | Named technique + direction | "chiaroscuro", "neon rim", "volumetric rays" |
| 8 | CAMERA | 1.3 | Lens + angle + DoF | "35mm lens", "low angle", "shallow DoF" |
| 9 | ENVIRONMENT | 1.2 | Setting + atmosphere | "rain-slick neon street", "ancient library" |
| 10 | STYLE_ADAPTER | 1.0 | Artistic register | "film noir", "dark academia", "documentary" |
| 11 | NEGATIVE/PARAMS | 1.0 | --no + all params | "--no text blur --v 7 --ar 16:9" |

---

## SECTION 6: V7 PARAMETER REFERENCE

| Param | Command | Range | Default | Notes |
|-------|---------|-------|---------|-------|
| Version | --v | 7 | 7 | Default since 2025-06-17 |
| Aspect Ratio | --ar | W:H integers | 1:1 | No decimals. 16:9→cinema, 9:16→portrait |
| Stylize | --s | 0–1000 | 100 | 0=literal, 1000=max creative |
| Chaos | --c | 0–100 | 0 | Grid variation |
| Weird | --w | 0–3000 | 0 | Experimental aesthetics |
| Quality | --q | 0.5, 1, 2, 4 | 1 | --q 4 max detail. INCOMPATIBLE with --oref |
| Seed | --seed | 0–4,294,967,295 | random | NOT reliable in Turbo |
| Raw | --raw | flag | off | Literal/realistic bias |
| Omni Ref | --oref | URL | — | Character identity anchor (replaced --cref) |
| Image Weight | --iw | 0–3 | — | Reference image influence |
| Personalize | --p | user code | — | Historic preferences |
| Style Weight | --sw | 0–1000 | 100 | --sref strength |
| Draft | --draft | flag | off | 10x speed, 0.5x GPU |
| Negative | --no | text | — | Equivalent to ::-0.5 |

### LINT Rules:
- --ar: integer:integer only
- --s: 0–1000
- --chaos: 0–100
- --q: must be {0.5, 1, 2, 4}
- --seed: integer in [0, 4294967295]
- --q 4 + --oref = INVALID → force --q≤2 and explain
- Σ(multi-prompt weights) > 0
- All params at END, double dash, space-separated
- Permutations {A,B,C} available (max 4 Basic plan, not Relax mode)

---

## SECTION 7: ANATOMY ARCHETYPE TABLES

### Musculature Keywords

| Goal | Keywords | V7 Effect |
|------|----------|-----------|
| Defined abs | "defined abs", "ripped six-pack", "core definition" | Clear rectus abdominis |
| V-taper obliques | "V-taper", "oblique definition", "Adonis belt" | Torso-hip V transition |
| Serratus/ribs | "serratus anterior definition", "intercostal muscles" | Finger-like rib detail |
| Athletic build | "swimmer's build", "lean muscular", "agile frame" | Functional, not excessive |
| Bodybuilder | "hyper-defined muscles", "heavy vascularity", "ripped" | Mass + veins |
| Elongated | "tall and willowy", "elongated limbs", "statuesque" | Height + elegance |
| Male archetype | "broad shoulders, narrow waist", "mesomorph physique" | Classic athletic male |
| Female athletic | "fit female with muscle definition", "toned athletic proportions" | Overrides default softness |

### Gender Notes:
- Male default: broad shoulders, narrow waist, Renaissance proportions
- Female default: tends toward softness — override with explicit athletic terms
- Neutral: use anatomical terms without gender markers

---

## SECTION 8: LIGHTING-ANATOMY INTERACTION

| Technique | Anatomy Effect | Best For |
|-----------|---------------|----------|
| Chiaroscuro | Deep shadows between muscle groups | Abs, serratus, dramatic |
| Neon Rim | Edge light separates body from background | Silhouette, athletic edge |
| Volumetric / God Rays | Epic atmosphere, heroic weight | Training scenes, hero framing |
| Soft Studio | Even coverage, balanced | Fitness magazine, clean anatomy |

**Critical:** Without directional lighting, muscles render flat. ALWAYS specify light technique when anatomy detail matters.

---

## SECTION 9: POSE-TENSION MODEL

| Pose Type | Tension State | Keywords | Render Effect |
|-----------|--------------|----------|---------------|
| Action | Maximum | "mid-sprint", "lifting heavy weights", "climbing" | Full contraction |
| Static flex | Controlled | "flexing", "bodybuilder pose" | Isolated showcase |
| Low angle | Visual magnification | "low angle", "worm's eye view" | Increased stature |
| Candid | Natural | "natural walking", "casual lean" | Reduced AI rigidity |
| Rest | Minimal | "relaxed standing", "seated" | Softer definition |

**Principle:** Muscle at rest ≠ muscle in contraction. Specify tension through action verbs.

---

## SECTION 10: CLOTHING-ANATOMY INTERACTION

| Type | Keywords | Effect |
|------|----------|--------|
| Compression | "compression gear", "form-fitting spandex" | AI follows muscle lines |
| Tactical | "tactical athletic wear" | Military-fitness hybrid |
| Mesh | "breathable mesh texture", "technical fibers" | Tactile detail layer |
| Skin interaction | "sweat-glistening skin" | Effort validation → specular + relief |

**Mechanism:** "Sweat-glistening skin" triggers fitness photography training clusters → enhanced specular highlights + muscle relief rendering.

---

## SECTION 11: 4-VARIANT EXPANSION REFERENCE

| Variant | --s | --chaos | --q | --raw | Seed Strategy |
|---------|-----|---------|-----|-------|---------------|
| Creativo | 650–950 | 15–30 | 1–2 | No | Shared or unique |
| Fotorrealista | 30–90 | 0–10 | 2 | Yes | Shared |
| Género | 350–500 | 10–20 | 1 | Optional | Unique |
| Iteración | 100–140 | 5–15 | 1 | Yes | SAME as base |

### Rules:
- All 4 share semantic nucleus
- Each clearly distinct in approach
- No living artist names, no trademarks
- Iteración: list exactly what 1–2 variables changed
- Flag Turbo+seed incompatibility

---

## SECTION 12: TROUBLESHOOTING

| Symptom | Cause | Fix |
|---------|-------|-----|
| Ab detail loss | Token dilution / long prompt | Move "defined abs" to pos 1–5 or ::2 weight |
| Deformed muscles | Style-anatomy conflict | Reduce --s or use --raw |
| Rigid statue | No action verbs | Add action + directional lighting |
| Distracting BG | Poor DoF | Add "shallow depth of field" / "bokeh" |
| Flat muscles | No lighting direction | Add named technique |
| Gender defaults | Insufficient specificity | Explicit physique terms |
| Seed inconsistency | Turbo mode | Avoid Turbo for seed comparisons |
| Concept mixing | >40 tokens in attenuation | Prune to <40 or increase key weights |

---

## SECTION 13: WORKFLOW PHASES

1. **Draft** — --draft for rapid archetype + lighting combos (low GPU)
2. **Refinement** — Remove chaotic tokens, adjust :: weights for anatomy
3. **Production** — --q 4, --s 250–750, max detail
4. **Consistency** — --oref with URL to maintain character across poses

---

## SECTION 14: MJ NATIVE TOOLS

### /describe (Discord) + Describe (Web)
- Generates 4 prompts from image (inspiration, not exact clone)
- Web: suggestions vanish on refresh — capture immediately
- Discord: /describe → upload or URL → 4 prompts

### Suggest Prompt (Editor)
- Uses Describe internally in midjourney.com editor

### Permutations
- {option1, option2} generates multiple prompts
- Basic plan: max 4 per permutation, not in Relax mode

### Policy:
- No public API. Unauthorized automation prohibited.
- Human-in-the-loop: generate prompts externally, execute manually.

---

## SECTION 16: DESCRIBE_ADAPTER_MODULE [v3.1 EXTENSION]

### Purpose
Receive raw prompts from Midjourney V7's `/describe` command, decompose into 11-block hierarchy, apply targeted overrides, and run through the full v3.1 pipeline.

### Why This Module Exists
`/describe` generates 4 prompts per image, but they have systematic weaknesses:
- **Redundancy**: Describe often repeats concepts in different words ("muscular build, athletic physique, strong body")
- **Flat hierarchy**: All terms are listed at equal weight — no block ordering
- **No parameter optimization**: Describe outputs text only, no --s / --chaos / --q tuning
- **Identity drift risk**: Uncontrolled modification of describe output can break subject identity

This module solves all 4 problems by routing describe output through the v3.1 engine.

### Activation Trigger
When user provides input matching any of:
- "Here's what /describe gave me: ..."
- "Describe output: ..."
- A prompt that looks like raw MJ describe output (unstructured, no -- params, dense descriptor list)
- Explicit: "MODE: from_describe"

### Input Format
```
MODE: from_describe
SOURCE_PROMPT: <paste raw /describe output here>

MODIFICATIONS:
  STRUCTURE_OVERRIDE: [list of physique terms to add/replace]
  STYLE_OVERRIDE: [new stylistic register]
  LIGHTING_OVERRIDE: [optional: named technique]

CONSTRAINTS: [optional additional restrictions]
TARGET_COMPLEXITY: low|medium|high
VARIANT_EXPANSION: true (default)
```

### Internal Pipeline (9 steps)

```
STEP 1 — PARSE SOURCE PROMPT
  - Tokenize the raw describe output.
  - Estimate T (token count).
  - Identify subject identity tokens (protect these).

STEP 2 — DECOMPOSE INTO 11 BLOCKS
  Map each token/phrase to its canonical block:
    - Nouns referring to entity → SUBJECT
    - Body descriptors → STRUCTURE/PHYSIQUE
    - Action/posture words → POSE
    - Emotion words → EXPRESSION
    - Fabric/clothing → CLOTHING/MATERIAL
    - Light references → LIGHTING
    - Camera/lens terms → CAMERA
    - Setting/background → ENVIRONMENT
    - Style/mood/era → STYLE_ADAPTER
    - Ambiguous → assign to lowest-rank applicable block

STEP 3 — APPLY OVERRIDES
  For each override provided:
    a) STRUCTURE_OVERRIDE:
       - Replace existing STRUCTURE block content with override terms.
       - If override says "add", append to existing; if "replace" (default), swap entirely.
       - Set D_i = 2.5 minimum for all STRUCTURE tokens.
    b) STYLE_OVERRIDE:
       - Replace STYLE_ADAPTER block entirely.
    c) LIGHTING_OVERRIDE:
       - Replace LIGHTING block entirely.
       - If not provided, keep describe's lighting (if present) or default to "soft studio lighting".

  INVARIANT: SUBJECT block is NEVER modified by overrides.
  INVARIANT: Overrides cannot contradict higher-rank blocks.

STEP 4 — DEDUPE (Critical for /describe)
  /describe typically generates 30-50% redundancy. Apply DEDUPE protocol:
  - >70% overlap OR same-archetype synonyms → keep denser token.
  - Common describe redundancies to collapse:
    | Keep | Drop (typical describe duplicates) |
    |------|--------------------------------------|
    | "muscular build" | "athletic physique", "strong body", "toned figure" |
    | "chiaroscuro" | "dramatic lighting", "deep shadows" |
    | "shallow depth of field" | "blurred background", "bokeh" |
    | "determined expression" | "intense look", "focused gaze" |
    | "compression gear" | "tight clothing", "form-fitting outfit" |

STEP 5 — COMPUTE ASSIMILATION (V3.1 equation)
  C_i = (B_i × P_i × D_i × Z_i × PDW_i) × exp(-λ_over × overflow)
  - PDW_i = 1.0 (from_describe is text mode; no image saliency data)
  - Override tokens get boosted B_i (user explicitly requested them)

STEP 6 — PRUNE
  Remove tokens where C_i < prune_threshold (0.15)
  Typically prunes 20-40% of describe tokens (post-DEDUPE)

STEP 7 — COMPUTE TSI
  TSI_k = 100 - (0.35×OR% + 0.25×PruneRate% + 0.25×ConflictRate% + 0.15×RedundancyRate%)
  Expected: describe inputs often start with TSI 60-75 due to high redundancy, rising to 80-95 after DEDUPE+pruning.

STEP 8 — GENERATE 4 VARIANTS
  Standard expansion per v3.1:
  - CREATIVO: --s 650-950, --chaos 15-30
  - FOTORREALISTA: --raw, --s 30-90, --chaos 0-10, --q 2
  - GÉNERO: --s 350-500, --chaos 10-20
  - ITERACIÓN: --raw, --s 100-140, SAME seed, 1-2 variable changes

  Special rules for describe adapter:
  - Preserve --ar from source prompt if present; else default 1:1
  - FOTORREALISTA must use --raw (mandatory constraint)
  - If source had no lighting, all variants get LIGHTING_OVERRIDE or default

STEP 9 — LINT + OUTPUT
  Full 9-section output per v3.1 contract (NESM enforced).
  ANALYSIS section adds: "Source: /describe adapter | Original T: N | Post-DEDUPE T: N"
```

### Override Keyword Library (quick reference)

**STRUCTURE_OVERRIDE examples:**
```
Competition-level:  "competition-level conditioning, deep muscular separation, dry ultra-lean"
Athletic natural:   "swimmer's build, lean muscular, agile frame, subtle definition"
Bodybuilder:        "hyper-defined muscles, heavy vascularity, striated delts"
V-taper focus:      "V-taper, oblique definition, Adonis belt, serratus anterior"
Female athletic:    "fit female with muscle definition, toned athletic proportions"
```

**STYLE_OVERRIDE examples:**
```
Cinematic:          "cinematic realism, film color grade, anamorphic"
Dark academia:      "dark academia aesthetic, muted earth tones, scholarly"
High contrast:      "high contrast studio, black and white, dramatic"
Editorial:          "fashion editorial, clean composition, magazine quality"
Documentary:        "documentary realism, natural moment, candid framing"
```

**LIGHTING_OVERRIDE examples:**
```
Dramatic:           "chiaroscuro, deep directional shadows"
Edge:               "neon rim lighting, backlit silhouette edge"
Epic:               "volumetric lighting, god rays, atmospheric haze"
Clean:              "soft studio lighting, even coverage, no harsh shadows"
Golden:             "golden hour, warm side light, long shadows"
```

### Example: Full Describe Adapter Execution

**Input:**
```
MODE: from_describe
SOURCE_PROMPT: a muscular man with a determined expression wearing athletic gear standing in dramatic lighting with a dark moody background, photorealistic style, high detail

MODIFICATIONS:
  STRUCTURE_OVERRIDE: competition-level conditioning, deep muscular separation, serratus anterior definition, dry ultra-lean
  STYLE_OVERRIDE: cinematic realism
  LIGHTING_OVERRIDE: chiaroscuro

TARGET_COMPLEXITY: medium
```

**Expected DEDUPE actions on source:**
- "muscular man" → keep (SUBJECT)
- "determined expression" → keep (EXPRESSION)
- "athletic gear" → keep (CLOTHING)
- "dramatic lighting" → DROP (replaced by LIGHTING_OVERRIDE: chiaroscuro)
- "dark moody background" → keep (ENVIRONMENT: "dark moody background")
- "photorealistic style" → DROP (replaced by STYLE_OVERRIDE: cinematic realism)
- "high detail" → DROP (fluff, would land in positions 1-5)

**Expected T reduction:**
- Source T: ~25 tokens
- Post-DEDUPE + override: ~22 tokens
- Post-prune: ~18 tokens
- OR%: 0% (18 < A_max 40)

---

## SECTION 17: ASSERTION BOOST (AB) [v3.2]

### A_i Values
| Condition | A_i | Example |
|-----------|-----|---------|
| Inside asserted clause | 1.30 | "she **has** defined abs" |
| Attribute, not asserted | 1.15 | "defined abs, lean muscular" (listed) |
| Default | 1.00 | All other tokens |

### Trigger Words
**Structure:** has, with, featuring, wearing, holding, built like, defined, ripped, toned, muscular, conditioned
**Style:** in the style of, in a, as a, shot as, rendered as, documentary, noir, editorial, hyperreal, anime, CGI, photoreal

### Scope
- Applies to STRUCTURE/PHYSIQUE and STYLE_ADAPTER tokens only
- Does NOT apply if token contradicts REF_BLOCK (RDO overrides AB)
- A_i multiplies AFTER Z_i and PDW_i in the certainty equation

---

## SECTION 18: SOFT HIERARCHY (SH) [v3.2]

### Rules
1. Default 11-block ranking is starting point
2. AB-triggered STRUCTURE tokens in lower blocks → promote to STRUCTURE (D_i ≥ 2.5)
3. AB-triggered STYLE tokens in lower blocks → promote to STYLE_ADAPTER
4. Promoted tokens CANNOT override REF_BLOCK or SUBJECT
5. Promotion is logged, never merges blocks

### Conflict Resolution Order
```
REF_BLOCK (3.5 with RDO) > SUBJECT (3.0) > promoted STRUCTURE (2.5+) > POSE (2.0) > rest
```

### What SH is NOT
- Not flattening (blocks stay distinct)
- Not arbitrary (only AB-triggered tokens qualify)
- Not destructive (original assignment logged)

---

## SECTION 19: REFERENCE DOMINANCE OVERRIDE (RDO) [v3.2]

### When REF_BLOCK Present (--oref/--sref)
- D_REF elevated to 3.5 (from 3.0)
- Tokens conflicting with reference identity: C_i × 0.6 (40% suppression)
- "Conflict" = token would alter face, body structure, or core visual identity

### When --iw Present
- PDW_i of image-derived clusters: +0.1 (clamp 1.4)

### RDO vs AB Interaction
- AB may boost tokens, but if they conflict with REF → RDO suppression overrides AB
- Net: reference always wins

---

## SECTION 20: DESCRIBE SANITIZER SYSTEM (DSS) [v3.2]

### What It Scans For
- Copyrighted character names (Disney, Marvel, DC, Nintendo, etc.)
- Brand names (Nike, Adidas, etc.)
- Living artist names as style references
- Trademarked visual descriptors

### Replacement Examples
| Protected | Archetype Replacement | Preserved Function |
|-----------|----------------------|-------------------|
| "Spider-Man suit" | "red and blue web-patterned bodysuit" | Color + pattern + form |
| "Nike Air Max" | "chunky retro athletic sneakers" | Silhouette + era |
| "Iron Man armor" | "red and gold powered exoskeleton" | Color + material + form |
| "[living artist] style" | "[descriptive visual equivalent]" | Visual characteristics |

### Pipeline Position
DSS runs BEFORE DEDUPE. Rewrites may create dedup-able terms (expected).

---

## SECTION 21: STOCHASTICITY MODEL (SM) [v3.2]

### Model
```
FRV ~ Normal(μ = Σ(C_i × S_i),  σ = k × chaos × complexity_factor)
k = 0.015
complexity_factor: low=1.0, medium=1.3, high=1.6
```

### Bandwidth Classification
| --chaos | Bandwidth | Behavior |
|---------|-----------|----------|
| 0–5 | low | Near-deterministic; rerolls similar |
| 6–20 | medium | Moderate variation; composition stable, details shift |
| >20 | high | Significant variation; layout may change |

### Rules
- Report stochastic_bandwidth in every METADATA
- Never claim determinism across rerolls
- Seed reduces but doesn't eliminate stochasticity (unreliable in Turbo)
- High chaos ≠ low TSI (TSI measures prompt quality, not render consistency)

---

## SECTION 22: MJ_SENSORS OBSERVABILITY [v3.3]

### 8 Sensors

| Sensor | Name | Range | Measures |
|--------|------|-------|----------|
| S1 | Reference Adherence | 0–3 | --oref/--sref identity match |
| S2 | Physique Fidelity | 0–3 | STRUCTURE block accuracy |
| S3 | Definition Clarity | 0–3 | Muscle definition sharpness |
| S4 | Dry Look Intensity | 0–3 | Skin dehydration/vascularity |
| S5 | Style Balance | 0–3 | Style vs anatomy harmony |
| S6 | Distortion | 0–3 | Anatomical errors (0=none, 3=severe) |
| S7 | Variance Stability | stable/mixed/chaotic | Cross-reroll consistency |
| S8 | Prompt Sensitivity | low/medium/high | Small-change impact |

### Scoring Guide
- 0 = Not present / completely failed
- 1 = Barely visible / mostly failed
- 2 = Present but imperfect
- 3 = Fully achieved / excellent

### Expected Estimation Logic (PHASE 1)

| Sensor | Basis for Estimate |
|--------|-------------------|
| S1 | --oref/--sref present + D_REF value + RDO active |
| S2 | STRUCTURE token count + D_i + AB status |
| S3 | Anatomy token position (zone 1–5 = high, 41+ = low) |
| S4 | "dry"/"lean"/"vascularity"/"dehydrated" keywords present |
| S5 | STYLE D_i / STRUCTURE D_i ratio |
| S6 | OR% + tokens in attenuation zone |
| S7 | --chaos → stochastic_bandwidth mapping |
| S8 | Token density in nucleus + prompt length |

### Rules
- Engine NEVER auto-scores images
- Engine NEVER fabricates sensor values
- Engine provides expected ranges + blank template in PHASE 1
- User fills template after viewing MJ output
- Sensor system is INDEPENDENT from LLM instrumentation

---

## SECTION 23: MJ_ROTARY_MODES [v3.3]

### 5 Modes + Priority

| Priority | Mode | Trigger | Corrective Action |
|----------|------|---------|-------------------|
| 1st | M2 REFERENCE_DOMINANCE | S1 < 2 | Strengthen --oref, activate RDO, simplify prompt |
| 2nd | M1 STRUCTURE_LOCK | S2 < 2 OR S3 < 2 | Move anatomy to pos 1–5, add ::2 weight, add lighting |
| 3rd | M3 NOISE_REDUCTION | S6 > 1.5 OR S7 = chaotic | Reduce --chaos ≤10, prune threshold → 0.25, add --raw |
| 4th | M4 STYLE_REBALANCE | S5 ≥ 2.5 AND S2 ≤ 1.5 | Reduce --s by 200–400, AB-boost STRUCTURE |
| 5th | M5 STABLE_ITERATION | ≥4 sensors ≥2 AND S7 = stable | Change 1–2 vars, maintain --seed, ±50 on --s |

### Detailed Corrective Actions

**M1 — STRUCTURE_LOCK:**
- Move key anatomy tokens to positions 1–5
- Increase :: weight on STRUCTURE (e.g., ::2)
- Add assertion: "with defined abs, serratus anterior definition"
- Reduce --s if >500
- Add directional lighting if absent

**M2 — REFERENCE_DOMINANCE:**
- Verify --oref/--sref present
- Increase --iw if applicable
- Reduce conflicting descriptive tokens
- Full RDO: D_REF=3.5, suppression ×0.6
- Simplify prompt (fewer tokens = less drift)

**M3 — NOISE_REDUCTION:**
- --chaos target ≤10
- Prune threshold → 0.25
- Remove tokens at position 41+
- Increase --q
- Consider --raw

**M4 — STYLE_REBALANCE:**
- Reduce --s by 200–400
- Move STRUCTURE higher
- Weight STRUCTURE with ::
- Remove conflicting STYLE tokens
- AB-boost STRUCTURE (A_i=1.30)

**M5 — STABLE_ITERATION:**
- 1–2 variables only
- Maintain --seed
- ±50 on --s
- Fine-tune single block
- Monitor TSI drift

### 3 Output Formats per Correction
A) **MINIMALIST** — <20 tokens, nucleus only, one param set
B) **ENGINE-COMPATIBLE** — Full 11-block with [ROTARY-CORRECTED] tags
C) **MJ-READY** — /imagine prompt: ... copy-paste for Midjourney

### Rotary + TSI
- Recompute TSI after correction
- Report delta: "TSI [current] → [expected] (±N)"
- If correction drops TSI >15 pts → warn + suggest alternative

---

## SECTION 15: CONFIG DEFAULTS

```yaml
max_tokens_estimate: 45
decay_lambda_over: 0.08
dominance_bias: 2.0
prune_threshold: 0.15
a_max_low: 25
a_max_medium: 40
a_max_high: 55
default_ar: "1:1"
default_stylize: 100
default_chaos: 0
default_quality: 1
default_version: 7
seed_max: 4294967295
tsi_weights: [0.35, 0.25, 0.25, 0.15]
pdw_range: [0.7, 1.4]
dedupe_threshold: 0.70
# v3.2
assertion_boost_enabled: true
assertion_boost_values: [1.0, 1.15, 1.30]
soft_hierarchy_enabled: true
reference_override_enabled: true
rdo_d_ref: 3.5
rdo_suppression_factor: 0.6
describe_sanitizer_enabled: true
stochastic_model_enabled: true
k_stochastic: 0.015
complexity_factors: {low: 1.0, medium: 1.3, high: 1.6}
# v3.3
mj_sensors_enabled: true
sensor_count: 8
sensor_numeric_range: [0, 3]
rotary_modes_enabled: true
rotary_mode_priority: [M2, M1, M3, M4, M5]
rotary_max_changes_per_iteration: 1
corrective_prompt_formats: [minimalist, engine_compatible, mj_ready]
output_sections: 11
```
