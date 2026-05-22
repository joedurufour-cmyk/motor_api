import polars as pl
from rapidfuzz import fuzz


def _blocking_key(row, cols):
    parts = []
    for c in cols[:2]:
        v = row.get(c)
        if v is None or str(v).strip() == "":
            parts.append("___")
            continue
        s = str(v).lower().replace(" ", "")
        parts.append((s + "___")[:3])
    return "|".join(parts)


def _pair_similarity(v1, v2):
    if v1 is None or v2 is None:
        return 0
    s1, s2 = str(v1).strip(), str(v2).strip()
    if not s1 or not s2:
        return 0
    if s1 == s2:
        return 100
    s1c = s1.replace(".", "").replace("-", "").replace(" ", "")
    s2c = s2.replace(".", "").replace("-", "").replace(" ", "")
    if s1c.isdigit() and s2c.isdigit():
        return 100 if s1c == s2c else 0
    if "@" in s1 or "@" in s2:
        return 100 if s1.lower() == s2.lower() else 0
    return int(fuzz.WRatio(s1, s2))


def _weighted_score(r1, r2, col_weights):
    total_w = 0.0
    score = 0.0
    for col, w in col_weights.items():
        sim = _pair_similarity(r1.get(col), r2.get(col))
        if sim == 0 and (r1.get(col) is None or r2.get(col) is None):
            continue
        score += sim * w
        total_w += w
    if total_w == 0:
        return 0
    return round(score / total_w, 2)


def _classify(score):
    if score >= 90:  return "auto_merge"
    if score >= 80:  return "recommended_merge"
    if score >= 60:  return "manual_confirm"
    if score >= 50:  return "suggest_only"
    return "reject"


def _build_master(r1, r2):
    master = {}
    for k in set(r1.keys()) | set(r2.keys()):
        v1, v2 = r1.get(k), r2.get(k)
        if v1 and not v2:    master[k] = v1
        elif v2 and not v1:  master[k] = v2
        elif v1 and v2:
            master[k] = v1 if len(str(v1)) >= len(str(v2)) else v2
        else:
            master[k] = None
    return master


def run_bibliocop(normalized, profiles, max_pairs_per_block=200):
    clusters = []
    cluster_idx = 0

    for key, df in normalized.items():
        if df.height < 2:
            continue
        prof = profiles.get(key, {})
        pk_cols = [c["column_id"] for c in prof.get("columns", []) if c.get("is_primary_key")]
        text_cols = [
            c["column_id"] for c in prof.get("columns", [])
            if c.get("inferred_type") in ("string", "email") and not c.get("is_sparse")
        ]
        match_cols = (pk_cols + text_cols)[:6]
        if not match_cols:
            continue

        weights = {}
        for c in prof.get("columns", []):
            cid = c["column_id"]
            if cid not in match_cols:
                continue
            t = c.get("inferred_type")
            if t in ("email", "phone"):
                weights[cid] = 3.0
            elif c.get("is_primary_key"):
                weights[cid] = 2.5
            else:
                weights[cid] = 1.0
        if not weights:
            continue

        full_rows = df.to_dicts()
        block_cols = [c for c in match_cols if c in df.columns][:2]
        if not block_cols:
            continue

        blocks = {}
        for i, r in enumerate(full_rows):
            bk = _blocking_key(r, block_cols)
            blocks.setdefault(bk, []).append(i)

        seen = set()
        for bk, idxs in blocks.items():
            if len(idxs) < 2:
                continue
            pair_count = 0
            for ia in range(len(idxs)):
                for ib in range(ia + 1, len(idxs)):
                    if pair_count >= max_pairs_per_block:
                        break
                    a, b = idxs[ia], idxs[ib]
                    if (a, b) in seen:
                        continue
                    seen.add((a, b))
                    pair_count += 1
                    score = _weighted_score(full_rows[a], full_rows[b], weights)
                    if score < 50:
                        continue
                    cluster_idx += 1
                    clusters.append({
                        "cluster_id": f"c_{cluster_idx:05d}",
                        "table": key,
                        "row_indices": [a, b],
                        "source_records": [full_rows[a], full_rows[b]],
                        "master_record": _build_master(full_rows[a], full_rows[b]),
                        "global_score": score,
                        "decision_status": _classify(score),
                        "match_columns": list(weights.keys()),
                    })
                if pair_count >= max_pairs_per_block:
                    break

    return clusters