"""
Standalone DQ client — replaces duckdq pip package entirely.

Minimal dependencies: duckdb, postgrest (pip install duckdb postgrest).

Usage:
    from client import DQClient
    import duckdb
    from postgrest import SyncPostgrestClient

    conn = duckdb.connect(":memory:")
    conn.sql("CREATE TABLE t AS SELECT * FROM (VALUES (1,'a'),(2,'b')) AS t(id,name)")

    dq = DQClient(SyncPostgrestClient("http://localhost:3000"), conn)
    dq.register("my_data")
    dq.run("my_data", "2026-05-19")
"""

import uuid
import time
from datetime import timedelta

from postgrest import SyncPostgrestClient
import duckdb


class DQClient:
    """Register datasets and run DQ jobs against PostgREST + DuckDB.

    Uses Accept-Profile headers for PostgREST v14 multi-schema support.
    All DQ tables go to the 'validation' schema.
    """

    SCHEMA = "validation"

    def __init__(
        self,
        pg_client: SyncPostgrestClient,
        duck_conn: duckdb.DuckDBPyConnection,
    ):
        self.pg = pg_client
        self.conn = duck_conn

    def _tbl(self, name: str):
        return self.pg.schema(self.SCHEMA).from_(name)

    # ── Register ──────────────────────────────────────────────────────────

    def register(self, dataset: str):
        """Register a dataset — upserts config into opt_* tables."""
        self._tbl("opt_spark").upsert({"dataset": dataset}).execute()
        self._tbl("opt_pushdown").upsert({
            "dataset": dataset, "connection_name": "DUCKDB",
            "source_query": f"select * from {dataset}",
        }).execute()
        self._tbl("opt_profile").upsert({
            "dataset": dataset, "on": "false", "only": "false", "limit": "300",
        }).execute()
        self._tbl("opt_load").upsert({
            "dataset": dataset, "query": f"select * from {dataset}", "connectionname": "DUCKDB",
        }).execute()
        self._tbl("opt_env").upsert({
            "dataset": dataset, "jdbcprincipal": "", "jdbckeytab": "",
        }).execute()
        self._tbl("opt_owl").upsert({
            "dataset": dataset, "run_state": "DRAFT",
        }).execute()

    # ── Run ───────────────────────────────────────────────────────────────

    def run(self, dataset: str, run_id: str):
        """Profile data and write results to PostgREST."""
        job_start = time.time()
        rc = self.conn.sql(f"SELECT COUNT(*) FROM {dataset}").fetchone()[0]

        # Profile via DuckDB SUMMARIZE
        self.conn.sql(f"DROP TABLE IF EXISTS {dataset}_profile")
        self.conn.sql(f"CREATE TABLE {dataset}_profile AS SELECT * FROM (SUMMARIZE {dataset})")
        profile_df = self.conn.sql(f"SUMMARIZE {dataset}").df()

        # owl_check_history
        self._tbl("owl_check_history").upsert({
            "dataset": dataset, "run_id": run_id, "conn": "duckdb",
            "user_nm": "duckdb", "pass": "duckdb", "query": f"select * from {dataset}",
        }).execute()

        # owl_catalog
        self._tbl("owl_catalog").upsert({
            "dataset": dataset, "alias": dataset,
            "source": "dataframe", "db_nm": "duckdb", "table_nm": dataset,
        }).execute()

        # dataset_schema
        self._tbl("dataset_schema").upsert([
            {"dataset": dataset, "col_nm": r["column_name"],
             "col_schema": r["column_type"], "col_typs": r["column_type"]}
            for _, r in profile_df.iterrows()
        ]).execute()

        # dataset_field
        self._tbl("dataset_field").upsert([
            {
                "dataset": dataset, "run_id": run_id,
                "field_nm": r["column_name"],
                "null_ratio": float(r["null_percentage"] / 100.0),
                "empty_ratio": 0.0,
                "unique_ratio": float(r["approx_unique"] / rc) if rc else 0.0,
                "unique_cnt": float(r["approx_unique"]),
                "type_ratio": 0.0,
                "pass_fail": 1,
                "actual_data_type": r["column_type"],
                "min_abs": str(r["min"]) if r["min"] else None,
                "max_abs": str(r["max"]) if r["max"] else None,
                "mean_abs": str(r["avg"]) if "avg" in profile_df.columns and r["avg"] else None,
            }
            for _, r in profile_df.iterrows()
        ]).execute()

        # dataset_scan
        self._tbl("dataset_scan").upsert({
            "dataset": dataset, "run_id": run_id, "rc": rc, "score": 100,
        }).execute()

        # dataset_activity
        elapsed = str(timedelta(seconds=round(time.time() - job_start)))
        self._tbl("dataset_activity").upsert({
            "dataset": dataset, "run_id": run_id,
            "total_time": elapsed, "profile_time": elapsed, "rules_time": "00:00:00",
        }).execute()


if __name__ == "__main__":
    # Self-test
    pg = SyncPostgrestClient("http://localhost:3000")
    conn = duckdb.connect(":memory:")
    conn.sql("""
        CREATE OR REPLACE TABLE demo AS
        SELECT * FROM (VALUES (1,'Alice',32,'USA'),(2,'Bob',45,'Canada'))
        AS t(id,name,age,country)
    """)
    dq = DQClient(pg, conn)
    dq.register("demo")
    dq.run("demo", "2026-05-19")
    r = dq._tbl("dataset_scan").select("score,rc").eq("dataset", "demo").execute()
    print(f"✓ DQClient self-test: score={r.data[0]['score']}, rows={r.data[0]['rc']}")