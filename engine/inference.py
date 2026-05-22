from collections import Counter
import polars as pl


def run_inference(normalized, cross_refs, profiles):
    inferences = []

    for key, df in normalized.items():
        prof = profiles.get(key, {})
        for col in prof.get("columns", []):
            cname = col["column_id"]
            if col["inferred_type"] not in ("numeric", "string"):
                continue
            if cname not in df.columns:
                continue
            try:
                series = df.get_column(cname).cast(pl.String, strict=False).drop_nulls()
            except Exception:
                continue
            if series.len() < 5:
                continue
            lengths = [len(str(x)) for x in series.to_list() if x is not None]
            if not lengths:
                continue
            mode_len, mode_count = Counter(lengths).most_common(1)[0]
            if mode_len < 5:
                continue
            shorter = sum(1 for l in lengths if l < mode_len)
            total = len(lengths)
            if 0 < shorter < total * 0.4 and mode_count / total > 0.5:
                conf = round(min(0.95, 0.6 + (mode_count / total) * 0.3), 3)
                inferences.append({
                    "type": "format_recovery",
                    "reason": (
                        f"column '{cname}' in {key} has dominant length {mode_len} "
                        f"({mode_count}/{total} rows); {shorter} rows shorter "
                        f"(likely lost leading zeros)"
                    ),
                    "source": [f"{key}.{cname}"],
                    "confidence": conf,
                    "alternatives": [
                        f"pad with leading zeros to length {mode_len}",
                        "leave as-is",
                    ],
                    "table": key,
                    "column": cname,
                })

    for cr in cross_refs:
        n = cr.get("match_count", 0)
        if n < 2:
            continue
        conf = round(min(0.95, 0.5 + n / 200.0), 3)
        inferences.append({
            "type": "transitive_mapping",
            "reason": (
                f"{cr['table_a']}.{cr['column_a']} and "
                f"{cr['table_b']}.{cr['column_b']} share {n} matching values; "
                f"missing attributes can be bridged across tables"
            ),
            "source": [
                f"{cr['table_a']}.{cr['column_a']}",
                f"{cr['table_b']}.{cr['column_b']}",
            ],
            "confidence": conf,
            "alternatives": ["accept bridge", "reject"],
            "tables": [cr["table_a"], cr["table_b"]],
        })

    return inferences