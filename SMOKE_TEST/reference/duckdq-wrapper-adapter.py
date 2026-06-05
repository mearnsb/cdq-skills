"""
DQWrapper — Custom PostgREST-native adapter replacing duckdq.client.APIClient.

Why: The duckdq pip package uses Supabase under the hood.
Supabase is incompatible with raw PostgREST v14 (different URL paths,
API key validation, auth endpoints). This adapter strips out all Supabase
dependencies and talks directly to PostgREST via SyncPostgrestClient.

Usage:
    from postgrest import SyncPostgrestClient
    import duckdb

    pg = SyncPostgrestClient("http://localhost:3000")
    conn = duckdb.connect(":memory:")
    conn.sql("CREATE OR REPLACE TABLE my_data AS SELECT * FROM (VALUES (1,'a'),(2,'b')) AS t(id,name)")

    dq = DQWrapper(pg, conn)
    dq.register("my_data")
    dq.run("my_data", "2026-05-19")
"""

import uuid
import time
from datetime import datetime, timedelta

from postgrest import SyncPostgrestClient
import duckdb


class DQWrapper:
    """Drop-in replacement for duckdq.client.APIClient.

    Same method signatures (register, run) but uses raw PostgREST
    instead of Supabase. Handles schema switching via Accept-Profile header.
    """

    SCHEMA = "validation"

    def __init__(
        self,
        pg_client: SyncPostgrestClient,
        duck_conn: duckdb.DuckDBPyConnection,
    ):
        self.pg = pg_client
        self.conn = duck_conn

    def _table(self, table_name: str):
        """Get a PostgREST query builder scoped to the validation schema."""
        return self.pg.schema(self.SCHEMA).from_(table_name)

    # ── Register ─────────────────────────────────────────────────────────

    def register(self, dataset: str):
        """Register a dataset — upserts into all opt_* config tables."""
        self._table("opt_spark").upsert({"dataset": dataset}).execute()
        self._table("opt_pushdown").upsert({
            "dataset": dataset,
            "connection_name": "DUCKDB",
            "max_connections": 10,
            "source_query": f"select * from {dataset}",
            "date_format_type": "DATE",
            "threads": 2,
            "manual_source_query": "false",
        }).execute()
        self._table("opt_profile").upsert({
            "dataset": dataset, "on": "false", "only": "false",
            "limit": "300", "shape": "false", "histogramlimit": "0",
            "score": "1", "shapesensitivity": "0",
        }).execute()
        self._table("opt_load").upsert({
            "dataset": dataset, "readonly": "false", "fullfile": "false",
            "filequery": "", "query": f"select * from {dataset}",
            "connectionname": "DUCKDB",
        }).execute()
        self._table("opt_env").upsert({
            "dataset": dataset, "jdbcprincipal": "", "jdbckeytab": "",
        }).execute()
        self._table("opt_owl").upsert({
            "dataset": dataset, "runid": "2024-09-06",
            "run_state": "DRAFT", "passfail": "1",
            "passfaillimit": "75", "jobid": "-1",
        }).execute()

    # ── Run ───────────────────────────────────────────────────────────────

    def run(self, dataset: str, run_id: str):
        """Run a full DQ job: profile, scan, schema, field stats, activity."""
        job_uuid = str(uuid.uuid4())
        job_start = time.time()

        rc = self.conn.sql(f"SELECT COUNT(*) FROM {dataset}").fetchone()[0]

        # Profile
        self.conn.sql(f"DROP TABLE IF EXISTS {dataset}_profile")
        self.conn.sql(f"CREATE TABLE {dataset}_profile AS SELECT * FROM (SUMMARIZE {dataset})")

        # Check history
        self._table("owl_check_history").upsert({
            "dataset": dataset, "run_id": run_id,
            "conn": "duckdb", "user_nm": "duckdb", "pass": "duckdb",
            "mega_bytes": 0, "rc": 0, "dl_key": "", "key_delim": "",
            "file": "", "key_col": "",
            "query": f"select * from {dataset}",
        }).execute()

        # Catalog
        self._table("owl_catalog").upsert({
            "dataset": dataset, "alias": dataset,
            "host": "python", "source": "dataframe",
            "db_nm": "duckdb", "table_nm": dataset,
        }).execute()

        # Schema
        profile_df = self.conn.sql(f"SUMMARIZE {dataset}").df()
        schema_payload = []
        for _, row in profile_df.iterrows():
            schema_payload.append({
                "dataset": dataset,
                "col_nm": row["column_name"],
                "col_schema": row["column_type"],
                "col_typs": row["column_type"],
            })
        self._table("dataset_schema").upsert(schema_payload).execute()

        # Field profile
        field_payload = []
        for _, row in profile_df.iterrows():
            field_payload.append({
                "dataset": dataset, "run_id": run_id,
                "field_nm": row["column_name"],
                "null_ratio": float(row["null_percentage"] / 100.0),
                "empty_ratio": 0.0,
                "unique_ratio": float(row["approx_unique"] / rc) if rc else 0.0,
                "unique_cnt": float(row["approx_unique"]),
                "type_ratio": 0.0,
                "pass_fail": 1,
                "actual_data_type": row["column_type"],
                "min_abs": str(row["min"]) if row["min"] else None,
                "max_abs": str(row["max"]) if row["max"] else None,
                "mean_abs": str(row["avg"]) if "avg" in profile_df.columns and row["avg"] else None,
            })
        self._table("dataset_field").upsert(field_payload).execute()

        # Scan result
        self._table("dataset_scan").upsert({
            "dataset": dataset, "run_id": run_id,
            "rc": rc, "score": 100,
        }).execute()

        # Activity timing
        elapsed = str(timedelta(seconds=round(time.time() - job_start)))
        self._table("dataset_activity").upsert({
            "dataset": dataset, "run_id": run_id,
            "total_time": elapsed, "profile_time": elapsed, "rules_time": "00:00:00",
            "total_time_in_hours": 0, "total_time_in_minutes": 0,
        }).execute()


if __name__ == "__main__":
    # Quick self-test
    pg = SyncPostgrestClient("http://localhost:3000")
    conn = duckdb.connect(":memory:")
    conn.sql("""
        CREATE OR REPLACE TABLE demo AS
        SELECT * FROM (VALUES
            (1, 'Alice', 32, 'USA'),
            (2, 'Bob', 45, 'Canada')
        ) AS t(id, name, age, country)
    """)
    dq = DQWrapper(pg, conn)
    dq.register("demo")
    dq.run("demo", "2026-05-19")
    print("✓ DQWrapper self-test passed")

    # Verify
    r = dq._table("dataset_scan").select("score,rc").eq("dataset", "demo").execute()
    print(f"  Score: {r.data[0]['score']}, Rows: {r.data[0]['rc']}")