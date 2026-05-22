import re
import unicodedata
from datetime import datetime
import polars as pl

WS_RE = re.compile(r"\s+")
PHONE_STRIP = re.compile(r"[^\d+]")
CURRENCY_STRIP = re.compile(r"[^\d\.\-]")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
DATE_FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
                "%Y/%m/%d", "%d.%m.%Y"]


def _norm_text(v):
    if v is None:
        return None
    s = unicodedata.normalize("NFKC", str(v))
    s = WS_RE.sub(" ", s).strip()
    return s if s else None


def _norm_date(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    if isinstance(v, datetime):
        return v.date().isoformat()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _norm_currency(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    s = CURRENCY_STRIP.sub("", s.replace(",", ""))
    try:
        return round(float(s), 2)
    except ValueError:
        return None


def _norm_phone(v):
    if v is None:
        return None
    s = PHONE_STRIP.sub("", str(v))
    if len(s) < 7:
        return None
    return s


def _norm_email(v):
    if v is None:
        return None
    s = str(v).strip().lower()
    return s if EMAIL_RE.match(s) else None


def _norm_numeric(v):
    if v is None:
        return None
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def normalize_dataframes(all_dfs, profiles):
    normalized = {}
    unresolved = []
    for key, df in all_dfs.items():
        prof = profiles.get(key, {})
        col_types = {c["column_id"]: c["inferred_type"] for c in prof.get("columns", [])}
        new_cols = {}

        for cname in df.columns:
            t = col_types.get(cname, "string")
            col = df.get_column(cname)
            try:
                if t == "iso_date":
                    new = col.map_elements(_norm_date, return_dtype=pl.String)
                elif t == "currency":
                    new = col.map_elements(_norm_currency, return_dtype=pl.Float64)
                elif t == "phone":
                    new = col.map_elements(_norm_phone, return_dtype=pl.String)
                elif t == "email":
                    new = col.map_elements(_norm_email, return_dtype=pl.String)
                elif t == "numeric":
                    new = col.map_elements(_norm_numeric, return_dtype=pl.Float64)
                else:
                    new = col.map_elements(_norm_text, return_dtype=pl.String)
            except Exception:
                new = col.map_elements(_norm_text, return_dtype=pl.String)
            new_cols[cname] = new

        try:
            new_df = pl.DataFrame(new_cols)
        except Exception:
            cast_cols = {k: v.cast(pl.String, strict=False) for k, v in new_cols.items()}
            new_df = pl.DataFrame(cast_cols)
        normalized[key] = new_df

        for cname in df.columns:
            t = col_types.get(cname, "string")
            if t in ("string", "unknown"):
                continue
            orig = df.get_column(cname).to_list()
            norm = new_df.get_column(cname).to_list()
            for i, (ov, nv) in enumerate(zip(orig, norm)):
                if ov is not None and (nv is None or nv == ""):
                    unresolved.append({
                        "table": key,
                        "row": i,
                        "column": cname,
                        "original": str(ov)[:200],
                        "reason": f"failed_{t}_normalization",
                    })
                    if len(unresolved) >= 500:
                        return normalized, unresolved
    return normalized, unresolved