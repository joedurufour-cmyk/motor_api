# CHARACTER_DB_ADAPTER v1.0
# Anexo Creativo — Base de Datos de Personajes para MJ7_EMULATION_ENGINE_v3.3
# Workflow: Personaje-Primero (Character → Outfit → Background → Artifacts → Prompt)

---

## [MODULE IDENTITY]

**Name:** CHARACTER_DB_ADAPTER
**Parent:** MJ7_EMULATION_ENGINE_v3.3
**Type:** Creative Annex + Lookup Module
**Purpose:** Provide structured character selection, outfit composition, scene assembly, and artifact integration using the MJ V7 Character Database, routed through the v3.3 engine pipeline.

**What This Module Does:**
1. Receives character selection (by ID, name, alias, or descriptive query)
2. Recommends outfit + background + artifact combinations based on aesthetic coherence
3. Maps all selections to the 11-block hierarchy
4. Applies DSS (safe alias system already built into the DB)
5. Routes through full v3.3 pipeline → 11-section output + SENSORS + ROTARY

**What This Module Does NOT Do:**
- Replace the engine — it FEEDS the engine
- Store images — it stores prompt-assembly data
- Override hierarchy — it populates blocks, engine orders them

---

## [DATABASE SCHEMA SUMMARY]

### Entity Relationships

```
CHARACTER (250) ──┬── OUTFIT (700)        ──┐
                  │                          │
                  ├── ARTIFACT (1500)        ├── PROMPTKIT (700)
                  │                          │
                  └── BACKGROUND (400)  ────┘
```

### Character Entity (CH_XXXX)

| Field | Type | Engine Mapping |
|-------|------|---------------|
| character_id | CH_0001–CH_0250 | Internal lookup |
| canonical_name | String | Reference only (NEVER in prompt) |
| generic_safe_alias | String | → SUBJECT block (DSS-compliant) |
| franchise_id | String | DSS reference (for sanitization logging) |
| medium_type | Enum: comic_mainstream, anime_manga, video_game, indie_dark, obscure_pulp | → STYLE_ADAPTER influence |
| archetype | Enum: heroine, villain, antihero, support, deity | → SUBJECT + EXPRESSION influence |
| visual_signature | Array[3–6] | → STRUCTURE + CLOTHING + STYLE blocks |
| color_palette | Array | → CLOTHING + LIGHTING + ENVIRONMENT |
| do_not_use_tokens | Array | → Fluff guard extension (block these in ALL positions) |
| logo_policy | Object | → DSS rule (remove_logos: true/false) |
| era_tags | Array | → STYLE_ADAPTER |
| genre_tags | Array | → STYLE_ADAPTER + ENVIRONMENT |

### Outfit Entity (OF_XXXX)

| Field | Engine Mapping |
|-------|---------------|
| outfit_type | Enum → CLOTHING block type selector |
| materials | Array → CLOTHING/MATERIAL block (direct V7 material tokens) |
| silhouette | Array → STRUCTURE influence (body-clothing interaction) |
| primary_colors | → CLOTHING + LIGHTING color coherence |
| emblem_policy | none/generic/abstract → DSS sub-rule |
| coverage_level | modest/standard → Safety compliance |
| prompt_clothing_block | Pre-built → CLOTHING block seed text |

### Background Entity (BG_XXXX)

| Field | Engine Mapping |
|-------|---------------|
| setting_type | → ENVIRONMENT block type |
| key_visual_elements | → ENVIRONMENT detail tokens |
| prompt_block | Pre-built → ENVIRONMENT block seed text |

### Artifact Entity (AR_XXXX)

| Field | Engine Mapping |
|-------|---------------|
| type | Enum: gadget, weapon, relic, tech → Block placement strategy |
| prompt_block | Pre-built → Integrated into SUBJECT or CLOTHING depending on type |

### PromptKit Entity (PK_XXXX)

Pre-assembled combinations (CH + OF + BG + AR) with MJ7 params.
**Use as:** Baseline templates for the engine to decompose → optimize → expand into 4 variants.

---

## [WORKFLOW: PERSONAJE-PRIMERO]

### Pipeline Overview

```
USER INPUT                    MODULE ACTION                      ENGINE ACTION
─────────────────────────────────────────────────────────────────────────────
1. Select Character      →   Lookup CH_XXXX                  →  (wait)
2. (optional) Constraints →  Filter compatible outfits        →  (wait)
3. Recommend/Select      →   Assemble: OF + BG + AR          →  (wait)
4. Confirm selections    →   Map to 11 blocks                →  PHASE 1: Full pipeline
5. View MJ output        →   (wait)                          →  (wait)
6. Score sensors         →   (wait)                          →  PHASE 2: ROTARY correction
```

### STEP 1 — CHARACTER SELECTION

User provides ANY of:
- **By ID:** `CH_0005` → direct lookup
- **By canonical name:** `2B` → lookup + DSS applies safe alias
- **By alias:** `Gothic Battle Android` → direct match
- **By description:** `cyberpunk android with blindfold` → semantic match against visual_signature

**Output:** Character card with all fields + available outfits/backgrounds/artifacts count.

### STEP 2 — RECOMMENDATION ENGINE

Given selected character, recommend combinations based on aesthetic coherence:

**Outfit Recommendation Logic:**
```
Score_outfit = Σ(
  material_lighting_compatibility × 0.3 +
  silhouette_physique_match × 0.25 +
  color_palette_harmony × 0.2 +
  genre_alignment × 0.15 +
  era_consistency × 0.1
)
```

**Background Recommendation Logic:**
```
Score_bg = Σ(
  genre_match × 0.35 +
  color_temperature_compatibility × 0.25 +
  narrative_coherence × 0.25 +
  lighting_synergy × 0.15
)
```

**Artifact Recommendation Logic:**
```
Score_artifact = Σ(
  character_archetype_fit × 0.4 +
  visual_signature_synergy × 0.3 +
  prompt_weight_budget × 0.3
)
```

Present TOP 3 recommendations per category with scores.
User selects or requests alternatives.

### STEP 3 — BLOCK ASSEMBLY

Map selections to 11-block hierarchy:

```
[REF_BLOCK]:          --oref [URL if provided by user]
[SUBJECT]:            generic_safe_alias + archetype descriptor
[STRUCTURE/PHYSIQUE]: visual_signature physical traits + outfit silhouette interaction
[POSE]:               user-specified OR archetype-default (heroine→dynamic, villain→imposing)
[EXPRESSION]:         archetype-congruent (heroine→determined, deity→serene)
[CLOTHING/MATERIAL]:  outfit.prompt_clothing_block + materials + emblem_policy applied
[LIGHTING]:           inferred from background.setting_type OR user override
[CAMERA]:             inferred from genre OR user override
[ENVIRONMENT]:        background.prompt_block
[STYLE_ADAPTER]:      medium_type + genre_tags + era_tags
[NEGATIVE/PARAMS]:    do_not_use_tokens + logo_policy + --v 7 --ar --s --chaos --q --seed
```

### STEP 4 — ENGINE HANDOFF

Assembled blocks → v3.3 pipeline:
- DSS verifies: canonical_name NEVER in prompt, only safe_alias
- DEDUPE collapses redundant visual_signature terms
- AB boosts asserted STRUCTURE tokens from visual_signature
- Full 11-section output including MJ_SENSORS estimates
- 4 variants generated

---

## [RECOMMENDATION TABLES]

### Material-Lighting Compatibility Matrix

| Material | Best Lighting | Why |
|----------|-------------|-----|
| matte_spandex | soft_box, volumetric_fog | Even coverage shows form without specular noise |
| brushed_metal | neon_rim_light, chiaroscuro | Hard reflections need directional contrast |
| silk_gauze | golden_hour, soft_box | Translucency needs backlight or diffused |
| distressed_leather | chiaroscuro, cyberpunk_flicker | Texture needs shadow depth |
| polycarbonate | neon_rim_light, volumetric_fog | Smooth surfaces need edge definition |
| kevlar_mesh | chiaroscuro, low_key | Tactical materials need dramatic weight |
| lace_trim | soft_box, golden_hour | Delicate patterns need even, warm light |
| carbon_fiber | neon_rim_light, studio_hard | Woven pattern needs angular light |

### Genre-Camera Pairing

| Genre | Default Camera | Rationale |
|-------|---------------|-----------|
| cyberpunk | 35mm_anamorphic | Wide, cinematic, lens flare compatible |
| space_opera | 24mm_wide | Epic scale, environmental dominance |
| dark_fantasy | 85mm_portrait, f/1.8 | Shallow DoF, character isolation |
| pulp_noir | 50mm_standard, high_contrast | Classic film look, balanced perspective |
| biopunk | macro_detail + 35mm | Organic detail + environmental context |
| wuxia | 85mm_portrait, low_angle | Heroic framing, martial elegance |

### Archetype-Pose Defaults

| Archetype | Default Pose | Expression | Tension State |
|-----------|-------------|------------|---------------|
| heroine | Dynamic action, mid-movement | Determined, focused | Maximum |
| villain | Imposing stance, power pose | Menacing, confident | Controlled |
| antihero | Casual lean, looking away | Brooding, detached | Minimal-to-controlled |
| support | Supportive gesture, hands active | Warm, alert | Natural |
| deity | Floating/elevated, symmetrical | Serene, transcendent | Static-ethereal |

### Medium-Style Mapping

| medium_type | Style Tokens | Default --s Range | --raw? |
|-------------|-------------|-------------------|--------|
| comic_mainstream | bold colors, dynamic composition, cel-shading influence | 300–600 | No |
| anime_manga | clean lines, large expressive eyes, flat color fields | 400–700 | No |
| video_game | high-detail rendering, cinematic composition, volumetric | 200–500 | Optional |
| indie_dark | muted palette, experimental composition, hand-drawn quality | 500–800 | No |
| obscure_pulp | vintage grain, desaturated, retro printing artifacts | 150–400 | Yes |

---

## [DSS INTEGRATION — SAFE ALIAS SYSTEM]

The Character Database already implements the core DSS principle: canonical names are NEVER used in prompts.

**Workflow:**
1. User says "I want 2B" or "CH_0005"
2. Module looks up: canonical_name = "2B (YoRHa No.2 Type B)"
3. Module substitutes: generic_safe_alias = "Gothic Battle Android"
4. visual_signature provides additional safe tokens: "Black lace-slit dress, tactical visor blindfold, thigh-high leather boots"
5. do_not_use_tokens are added to fluff guard extension
6. logo_policy applied: remove_logos=true → no franchise symbols

**DSS logging in METADATA:**
```
DSS_active: true
DSS_source: CHARACTER_DB
DSS_rewrites: ["2B" → "Gothic Battle Android", "YoRHa" → removed, "NieR:Automata" → removed]
```

---

## [CROSS-ENTITY COMBINATION ENGINE]

### Aesthetic Coherence Score (ACS)

When user selects a combination, compute overall coherence:

```
ACS = Σ(
  material_lighting_compat × 0.20 +
  color_harmony × 0.20 +
  genre_consistency × 0.20 +
  silhouette_physique_match × 0.15 +
  era_alignment × 0.10 +
  narrative_logic × 0.15
)

Scale: 0–1.0
```

| ACS Range | Assessment | Action |
|-----------|-----------|--------|
| 0.8–1.0 | Excellent coherence | Proceed, no warnings |
| 0.6–0.79 | Good with minor friction | Note friction points, proceed |
| 0.4–0.59 | Mixed — intentional? | Ask user if dissonance is intentional |
| <0.4 | High dissonance | Warn, suggest alternatives, proceed only if confirmed |

Report ACS in METADATA when CHARACTER_DB_ADAPTER is active.

---

## [COMBINATORIA CREATIVA — CROSS-STYLE FUSION]

### Outfit Swaps (Cross-Character)

Apply Outfit from Character A to Character B:
- Preserve Character B's SUBJECT + visual_signature core
- Apply Character A's outfit materials + silhouette
- Resolve conflicts: if outfit.silhouette contradicts character.visual_signature → SH promotes character traits

Example:
```
Character: CH_0010 (Motoko Kusanagi → "Cybernetic Tactical Chief")
Outfit swap: OF_0003 (Battle Gown from CH_0007 Chun-Li)
Result: Cybernetic tactical chief in blue silk structural qipao with gold embroidery,
        violet cropped hair, high-tech accessories visible beneath ceremonial fabric
```

### Genre Crossover

Place a character in a genre they don't belong to:
- Preserve SUBJECT + STRUCTURE
- Replace STYLE_ADAPTER + ENVIRONMENT with target genre
- Adjust LIGHTING to match new genre
- Compute ACS — low scores expected, flag as intentional artistic choice

Example:
```
Character: CH_0001 (Golden Age Stuntwoman → obscure_pulp)
Target genre: cyberpunk
Result: 1940s stuntwoman vigilante in neon-lit rain-slick alley,
        tactical dark gear, holographic ad reflections,
        vintage athletic build contrasted with futuristic setting
```

### Era Shift

Temporal displacement — same character, different decade:
- Preserve SUBJECT identity
- Shift outfit materials + silhouette to target era
- Shift ENVIRONMENT to era-appropriate setting
- STYLE_ADAPTER absorbs era tags

---

## [SAMPLE PROMPTKITS — ENGINE-PROCESSED]

### Example 1: CH_0005 (2B) — Standard Assembly

**Selections:**
- Character: CH_0005 → "Gothic Battle Android"
- Outfit: OF_0001 → "Yorha Combat Unit" (heavy_silk, lace_trim, leather)
- Background: BG_0004 → Cathedral Ruins
- Artifact: AR_0002 → Virtuous Contract (ornate white katana)

**Block Assembly:**
```
[REF_BLOCK]:          (none — no --oref provided)
[SUBJECT]:            Gothic battle android woman with yellowish-white hair
[STRUCTURE/PHYSIQUE]: athletic combat-ready frame, precise mechanical proportions
[POSE]:               mid-swing with ornate white katana, dynamic weight shift
[EXPRESSION]:         focused determination, emotionless precision
[CLOTHING/MATERIAL]:  black heavy silk dress with lace embroidery, open back, thigh-high leather boots
[LIGHTING]:           moonbeams through broken stained glass, volumetric dust
[CAMERA]:             85mm portrait, f/1.8, low angle
[ENVIRONMENT]:        gothic cathedral ruins, shattered rose window, stone debris, moonlight
[STYLE_ADAPTER]:      dark fantasy, video game cinematic, atmospheric
[NEGATIVE/PARAMS]:    --no text blur logo --v 7 --ar 2:3 --s 350 --chaos 10 --q 2 --seed 884721
```

**ACS:** 0.91 (excellent — dark fantasy character in dark fantasy environment)

→ This block assembly feeds directly into v3.3 PHASE 1 pipeline for 4-variant expansion.

### Example 2: CH_0010 (Motoko) — Genre Crossover

**Selections:**
- Character: CH_0010 → "Cybernetic Tactical Chief"
- Outfit: OF_0004 → "Section 9 Tactical" (matte_neoprene, carbon_fiber)
- Background: BG_0002 → Celestial Library (CROSS-GENRE: cyberpunk→fantasy)
- Artifact: AR_0004 → Sandevistan Spine (neural spinal implant)

**Block Assembly:**
```
[REF_BLOCK]:          (none)
[SUBJECT]:            Cybernetic tactical chief, violet cropped hair, detached demeanor
[STRUCTURE/PHYSIQUE]: lean athletic cybernetic frame, visible spinal implant with orange glowing fibers
[POSE]:               standing alert, scanning environment, hand on utility belt
[EXPRESSION]:         calculated detachment, hyper-aware
[CLOTHING/MATERIAL]:  matte neoprene stealth suit, carbon fiber utility belt, high-neck collar
[LIGHTING]:           golden dust motes, cosmic light, warm volumetric
[CAMERA]:             35mm anamorphic, eye level
[ENVIRONMENT]:        towering celestial library, floating spellbooks, infinite shelves, cosmic glow
[STYLE_ADAPTER]:      cyberpunk-fantasy fusion, atmospheric, cinematic
[NEGATIVE/PARAMS]:    --no text blur --v 7 --ar 16:9 --s 450 --chaos 15 --q 2 --seed 331205
```

**ACS:** 0.62 (good with friction — cyberpunk character in fantasy setting, intentional crossover)
**Friction points:** material palette (neoprene/carbon) vs setting (cosmic/golden). Contrast is the artistic intent.

---

## [INPUT FORMAT FOR THIS MODULE]

```
MODE: character_first

# Step 1 — Character selection (any format):
CHARACTER: CH_0005 | "2B" | "gothic android" | "blindfolded combat android"

# Step 2 — Optional constraints:
OUTFIT_PREFERENCE: [outfit_type] | [material preference] | OF_XXXX
BACKGROUND_PREFERENCE: [setting_type] | [genre] | BG_XXXX
ARTIFACT_PREFERENCE: [type] | AR_XXXX
GENRE_OVERRIDE: [target genre if cross-genre desired]
ERA_OVERRIDE: [target era if era-shift desired]

# Step 3 — Engine params:
TARGET_COMPLEXITY: low | medium | high
VARIANT_EXPANSION: true (default)
POSE_OVERRIDE: [optional custom pose]
LIGHTING_OVERRIDE: [optional named technique]

# Optional — return sensor data for PHASE 2:
MJ_SENSORS:
  S1: ___  S2: ___  S3: ___  S4: ___
  S5: ___  S6: ___  S7: ___  S8: ___
```

---

## [INTEGRATION WITH v3.3 ENGINE]

### New MODE Addition
The engine now supports: `from_text | from_image | hybrid | from_describe | character_first`

### Pipeline Integration Point
CHARACTER_DB_ADAPTER executes BEFORE STEP 1 of the v3.3 pipeline:

```
STEP 0 — CHARACTER_DB_ADAPTER (if MODE=character_first)
  0.1 Lookup character
  0.2 Recommend or accept outfit/bg/artifact
  0.3 Compute ACS
  0.4 Map to 11 blocks
  0.5 Apply DSS (safe alias)
  0.6 Hand off populated blocks to STEP 1

STEP 1 — ANALYZE (v3.3 pipeline continues normally)
...
```

### METADATA Additions
When CHARACTER_DB_ADAPTER is active:
```
CDA_active: true
CDA_character: CH_XXXX (safe_alias)
CDA_outfit: OF_XXXX
CDA_background: BG_XXXX
CDA_artifacts: [AR_XXXX, ...]
CDA_ACS: 0.XX
CDA_crossover: none | genre | era | outfit_swap
CDA_friction_points: [list if ACS < 0.8]
```

---

## [CONFIG]

```yaml
character_db_adapter_enabled: true
acs_threshold_warning: 0.4
acs_threshold_friction: 0.6
recommendation_top_n: 3
default_pose_by_archetype: true
default_lighting_by_genre: true
default_camera_by_genre: true
cross_genre_allowed: true
era_shift_allowed: true
outfit_swap_allowed: true
safe_alias_mandatory: true
```
