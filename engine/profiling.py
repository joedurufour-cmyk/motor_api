import re
import math
import polars as pl

DATE_PATTERNS = [
    re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$"),
    re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$"),
    re.compile(r"^\d{1,2}-\d{1,2}-\d{2,4}$"),
    re.compile(r"^\d{4}/\d{1,2}/\d{1,2}$"),
]
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PHONE_RE = re.compile(r"^[\+\(\)\-\s\d]{7,}$")
CURRENCY_RE = re.compile(r"^[\$\€\£\¥]?\s?-?[\d,]+(\.\d+)?$")


def _column_entropy(series: pl.Series) -> float:
    try:
        s = series.cast(pl.String, strict=False).drop_nulls()
        if s.len() == 0:
            return 0.0
        counts = s.value_counts(sort=False)
        n = counts["count"].sum()
        if n <= 0:
            return 0.0
        probs = counts["count"].cast(pl.Float64) / n
        ent = -float((probs * probs.log(base=2.0)).sum())
        return ent if not math.isnan(ent) else 0.0
    except Exception:
        return 0.0


def _infer_type(series: pl.Series) -> str:
    try:
        s = series.cast(pl.String, strict=False).drop_nulls()
        if s.len() == 0:
            return "unknown"
        sample = [str(x).strip() for x in s.head(200).to_list() if x is not None]
        if not sample:
            return "unknown"
        n = len(sample)

        def hit_ratio(rx):
            return sum(1 for v in sample if rx.match(v)) / n

        if max((hit_ratio(p) for p in DATE_PATTERNS), default=0) > 0.7:
            return "iso_date"
        if hit_ratio(EMAIL_RE) > 0.7:
            return "email"
        if hit_ratio(CURRENCY_RE) > 0.7:
            return "currency"
        digit_heavy = sum(1 for v in sample if sum(c.isdigit() for c in v) >= 7)
        if digit_heavy / n > 0.7 and hit_ratio(PHONE_RE) > 0.5:
            return "phone"
        ok = 0
        for v in sample:
            try:
                float(v.replace(",", ""))
                ok += 1
            except ValueError:
                pass
        if ok / n > 0.85:
            return "numeric"
        return "string"
    except Exception:
        return "string"


def profile_dataframes(all_dfs):
    profiles = {}
    for key, df in all_dfs.items():
        cols_meta = []
        n_rows = df.height
        max_ent = math.log2(max(2, n_rows))
        for cname in df.columns:
            col = df.get_column(cname)
            null_count = int(col.null_count())
            null_ratio = null_count / max(1, n_rows)
            ent = _column_entropy(col)
            inferred = _infer_type(col)
            is_pk = (
                n_rows > 1
                and max_ent > 0
                and (ent / max_ent) > 0.95
                and null_ratio < 0.05
            )
            cols_meta.append({
                "column_id": cname,
                "inferred_type": inferred,
                "null_ratio": round(null_ratio, 4),
                "shannon_entropy": round(ent, 4),
                "max_entropy": round(max_ent, 4),
                "is_primary_key": bool(is_pk),
                "is_sparse": null_ratio > 0.85,
                "is_redundant": ent < 0.01,
            })
        profiles[key] = {"row_count": n_rows, "columns": cols_meta}
    return profiles