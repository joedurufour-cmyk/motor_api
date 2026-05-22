import duckdb


def _safe_ident(name: str) -> str:
    return "t_" + "".join(c if c.isalnum() else "_" for c in name)


def _safe_col(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def run_cross_reference(normalized, profiles, min_matches=2):
    con = duckdb.connect()
    keys = list(normalized.keys())
    ident_map = {k: _safe_ident(k) for k in keys}

    for k in keys:
        try:
            con.register(ident_map[k], normalized[k])
        except Exception:
            try:
                con.register(ident_map[k], normalized[k].to_arrow())
            except Exception:
                pass

    matches = []
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            ka, kb = keys[i], keys[j]
            ia, ib = ident_map[ka], ident_map[kb]
            cols_a = [
                c["column_id"] for c in profiles.get(ka, {}).get("columns", [])
                if not c.get("is_sparse") and not c.get("is_redundant")
            ]
            cols_b = [
                c["column_id"] for c in profiles.get(kb, {}).get("columns", [])
                if not c.get("is_sparse") and not c.get("is_redundant")
            ]
            for ca in cols_a:
                for cb in cols_b:
                    qa, qb = _safe_col(ca), _safe_col(cb)
                    try:
                        q = (
                            f"SELECT COUNT(*) FROM {ia} a JOIN {ib} b "
                            f"ON CAST(a.{qa} AS VARCHAR) = CAST(b.{qb} AS VARCHAR) "
                            f"WHERE a.{qa} IS NOT NULL AND b.{qb} IS NOT NULL "
                            f"  AND CAST(a.{qa} AS VARCHAR) <> ''"
                        )
                        n = con.execute(q).fetchone()[0]
                    except Exception:
                        continue
                    if n >= min_matches:
                        rel = "one_to_one"
                        if n > min(normalized[ka].height, normalized[kb].height):
                            rel = "many_to_many"
                        elif n > 1:
                            rel = "one_to_many"
                        matches.append({
                            "table_a": ka, "column_a": ca,
                            "table_b": kb, "column_b": cb,
                            "match_count": int(n),
                            "relationship_type": rel,
                        })
    con.close()
    return matches