import polars as pl

from .ingestion import ingest
from .profiling import profile_dataframes
from .normalization import normalize_dataframes
from .bibliocop import run_bibliocop
from .cross_reference import run_cross_reference
from .inference import run_inference


class Pipeline:
    def __init__(self):
        self.manifest = {}
        self.raw_dfs = {}
        self.profiles = {}
        self.normalized = {}
        self.unresolved = []
        self.clusters = []
        self.cross_refs = []
        self.inferences = []
        self.session_id = None

    def run(self, paths):
        if not paths:
            return self._mock_run()
        self.manifest, self.raw_dfs = ingest(paths)
        self.session_id = self.manifest["session_id"]
        self.profiles = profile_dataframes(self.raw_dfs)
        self.normalized, self.unresolved = normalize_dataframes(self.raw_dfs, self.profiles)
        self.clusters = run_bibliocop(self.normalized, self.profiles)
        self.cross_refs = run_cross_reference(self.normalized, self.profiles)
        self.inferences = run_inference(self.normalized, self.cross_refs, self.profiles)
        return self.summary()

    def summary(self):
        n_rows = sum(df.height for df in self.normalized.values())
        merged_auto = sum(
            1 for c in self.clusters
            if c["decision_status"] in ("auto_merge", "recommended_merge")
        )
        return {
            "session_id": self.session_id,
            "total_rows": int(n_rows),
            "duplicates_fused": int(merged_auto),
            "missing_inferred": len(self.inferences),
            "unresolved": len(self.unresolved),
            "global_quality": self._quality_score(),
        }

    def _quality_score(self):
        if not self.profiles:
            return 0.0
        total_cols = sum(len(p["columns"]) for p in self.profiles.values())
        if total_cols == 0:
            return 0.0
        sparse = sum(
            1 for p in self.profiles.values() for c in p["columns"] if c["is_sparse"]
        )
        n_rows = max(1, sum(df.height for df in self.normalized.values()))
        score = 100.0 * (1 - sparse / total_cols) - (len(self.unresolved) / n_rows) * 50
        return round(max(0.0, min(100.0, score)), 2)

    def get_normalized_serialized(self, max_rows=500):
        out = {}
        for k, df in self.normalized.items():
            out[k] = {
                "columns": df.columns,
                "rows": df.head(max_rows).to_dicts(),
                "total_rows": df.height,
            }
        return out

    def _mock_run(self):
        self.session_id = "MOCK-DEMO"
        df_a = pl.DataFrame({
            "id":    ["A001", "A002", "A003", "A004", "A005"],
            "name":  ["Acme Corp", "Acme Incorporated", "Globex", "Initech", "ACME corp"],
            "email": ["info@acme.com", "info@acme.com", "hi@globex.com", None, "info@acme.com"],
            "city":  ["Panama City", "Panama City", "Boquete", "David", "Panama City"],
        })
        df_b = pl.DataFrame({
            "ref_id":  ["A001", "A003", "A005", "A007"],
            "country": ["Panama", "Panama", "Panama", "Costa Rica"],
            "phone":   ["+50712345678", "+50798765432", "+50711122233", "+50644455566"],
        })
        df_c = pl.DataFrame({
            "client_id": ["A001", "A002", "A003"],
            "amount":    [1500.50, 2300.00, 875.25],
            "currency":  ["USD", "USD", "USD"],
            "date":      ["2026-01-15", "2026-02-20", "2026-03-05"],
        })
        self.raw_dfs = {
            "f0__demo_clients":   df_a,
            "f1__demo_locations": df_b,
            "f2__demo_orders":    df_c,
        }
        self.manifest = {
            "session_id": self.session_id,
            "files": [
                {"file_id": "f0", "filename": "demo_clients.xlsx",
                 "path": "(mock)", "extension": ".xlsx", "filesize": 0,
                 "sheets": [{"sheet_name": "demo_clients", "row_count": 5,
                             "column_count": 4, "hidden_columns": [],
                             "hidden_rows": [], "merged_ranges": [],
                             "formula_cells": []}]},
                {"file_id": "f1", "filename": "demo_locations.xlsx",
                 "path": "(mock)", "extension": ".xlsx", "filesize": 0,
                 "sheets": [{"sheet_name": "demo_locations", "row_count": 4,
                             "column_count": 3, "hidden_columns": [],
                             "hidden_rows": [], "merged_ranges": [],
                             "formula_cells": []}]},
                {"file_id": "f2", "filename": "demo_orders.xlsx",
                 "path": "(mock)", "extension": ".xlsx", "filesize": 0,
                 "sheets": [{"sheet_name": "demo_orders", "row_count": 3,
                             "column_count": 4, "hidden_columns": [],
                             "hidden_rows": [], "merged_ranges": [],
                             "formula_cells": []}]},
            ],
            "anomalies": {
                "merged_cells_count": 0, "hidden_columns_count": 0,
                "hidden_rows_count": 0, "formula_cells_count": 0,
            },
        }
        self.profiles = profile_dataframes(self.raw_dfs)
        self.normalized, self.unresolved = normalize_dataframes(
            self.raw_dfs, self.profiles
        )
        self.clusters = run_bibliocop(self.normalized, self.profiles)
        self.cross_refs = run_cross_reference(self.normalized, self.profiles)
        self.inferences = run_inference(
            self.normalized, self.cross_refs, self.profiles
        )
        return self.summary()