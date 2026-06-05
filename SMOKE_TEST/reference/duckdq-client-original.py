from __future__ import annotations

import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd 
import duckdb
import supabase
import uuid
import warnings
from itertools import repeat
import uuid
from datetime import datetime 
import time
from typing import ( TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple, Type, Union, )
from datetime import timedelta 
from supabase import create_client, Client
url: str = os.environ.get("API_URL")
key: str = os.environ.get("API_KEY")
supabase_client: Client = create_client(url, key)
SCHEMA = "validation" # TODO Make this property of client 

if TYPE_CHECKING:
    import supabase
    import duckdb
class APIClient:
    def __init__(
        self,
        client: Optional[supabase.api.Client] = None,
        conn: Optional[duckdb.DuckDBPyConnection] = None,
    ) -> None:
        """Initialize api."""
        try:
            import supabase
            import duckdb 
        except ImportError:
            raise ImportError(
                "Could not import supabase python package. "
                "Please install it with `pip install supabase`."
            )

        self.client = client or supabase
        self.conn = conn or duckdb.connect(':memory:')

    # Insert
    # dataset_scan
    def insert_dataset_scan(self, dataset, run_id, rc, score): 
        response = self.client.schema(SCHEMA).table("dataset_scan")\
        .upsert({
            "dataset": dataset, 
            "run_id": run_id, 
            "rc" : rc,
            "score" : score
            }).execute()
        return response

    # Select
    # dataset_scan
    def get_dataset_scan_all(self):
        response = self.client.schema(SCHEMA).table("dataset_scan").select("*").execute()
        return response

    # dataset_scan
    def get_dataset_scan(self, dataset, run_id):
        response = self.client.schema(SCHEMA).table("dataset_scan").select("*").eq("dataset", dataset).eq("run_id", run_id).execute()
        return response
    
    # Delete
    # dataset_scan
    def delete_dataset_scan(self, dataset, run_id) -> None:
        self.client.schema(SCHEMA).from_("dataset_scan").delete().eq("dataset", dataset).eq("run_id", run_id).execute()

    # Insert
    # dataset_field
    def insert_dataset_field(self, dataset, run_id, rc):
        # Connect to DuckDB
        # conn = duckdb.connect(':memory:')

        # Create table if not exists
        # conn.sql(f"drop table if exists {dataset} ")
        # conn.sql(f"create table if not exists {dataset} as select * from read_csv_auto('./data/fake_customers.csv')")

        # Get row count
        # rc = self.conn.execute(f"SELECT COUNT(*) FROM {dataset}").fetchone()[0]
        # print(rc)

        # Get profile
        #profile_df = self.conn.execute(f"SUMMARIZE {dataset}").df()
        profile_df = self.conn.execute(f"select * from {dataset}_profile  ").df()
        print(profile_df.columns)

        # Get columns
        columns = profile_df['column_name'].tolist()
        payload = []
        for c in columns:
            # Filter the profile for the current column
            column_profile = profile_df[profile_df['column_name'] == c].iloc[0]

            payload.append({
                "dataset": dataset,
                "run_id": run_id,
                "field_nm": c,
                "null_ratio": str(column_profile['null_percentage'] / 100.0),
                "empty_ratio": 0.0, #str((column_profile['null_percentage'] / 100.0) if 'null_percentage' in column_profile else None),
                "unique_ratio": str((column_profile['approx_unique'] / rc)),
                "unique_cnt":  str(column_profile['approx_unique']),
                "type_ratio":  0.0, 
                "mean_abs": str(column_profile['avg'] if 'avg' in column_profile else None),
                "min_abs": str(column_profile['min'] if 'min' in column_profile else None),
                "max_abs": str(column_profile['max'] if 'max' in column_profile else None),
                "pass_fail": 1,  # You might want to implement a condition for this
                "actual_data_type": column_profile['column_type'],
            })

        self.client.schema(SCHEMA).table("dataset_field")\
        .upsert(payload).execute()

        #conn.close()

    # get
    # dataset_field
    def get_dataset_field(self, dataset, run_id):
        response = self.client.schema(SCHEMA).table("dataset_field").select("*").eq("dataset", dataset).eq("run_id", run_id).execute()
        return response
    
    # delete
    # dataset_field
    def delete_dataset_field(self, dataset, run_id):
        self.client.schema(SCHEMA).from_("dataset_field").delete().eq("dataset", dataset).eq("run_id", run_id).execute()

    # Insert
    # dataset_schema
    def insert_dataset_schema(self, dataset):
        # Connect to DuckDB
        # conn = duckdb.connect(':memory:')

        # Create table if not exists
        #conn.sql(f"drop table if exists {dataset} ")
        # conn.sql(f"create table if not exists {dataset} as select * from read_csv_auto('./data/fake_customers.csv')")

        # Get profile
        profile_df = self.conn.execute(f"SUMMARIZE {dataset}").df()

        # Get columns
        columns = profile_df['column_name'].tolist()
        payload = []
        for c in columns:
            column_profile = profile_df[profile_df['column_name'] == c].iloc[0]
            payload.append({
                    "dataset": dataset,
                    "col_nm": c,
                    "col_schema": column_profile['column_type'],
                    "col_typs": column_profile['column_type'],
                })
        self.client.schema(SCHEMA).table("dataset_schema")\
            .upsert(payload).execute()
        
        #conn.close()

    # get
    # dataset_schema
    def get_dataset_schema(self, dataset):
        response = self.client.schema(SCHEMA).table("dataset_schema").select("*").eq("dataset", dataset).execute()
        return response

    # delete
    # dataset_schema
    def delete_dataset_schema(self, dataset):
        self.client.schema(SCHEMA).from_("dataset_schema").delete().eq("dataset", dataset).execute()

    # Insert
    # owl_catalog
    def insert_owl_catalog(self, dataset):
        self.client.schema(SCHEMA).table("owl_catalog")\
        .upsert({
            "dataset": dataset,
            "alias": dataset,
            "host" : "python",
            "source" : "dataframe",
            "db_nm" : "duckdb",
            "table_nm" : dataset
            }).execute()
    
    # get
    # owl_catalog
    def get_owl_catalog(self, dataset):
        response = self.client.schema(SCHEMA).table("owl_catalog").select("*").eq("dataset", dataset).execute()
        return response
    
    # delete
    # owl_catalog
    def delete_owl_catalog(self, dataset):
        self.client.schema(SCHEMA).from_("owl_catalog").delete().eq("dataset", dataset).execute()
        
    # insert
    # owl_check_history
    def insert_owl_check_history(self, dataset, run_id):
        self.client.schema(SCHEMA).table("owl_check_history")\
        .upsert({
            "dataset": dataset,
            "run_id": run_id,
            "conn" : "duckdb",
            "user_nm" : "duckdb",
            "pass" : "duckdb",
            "mega_bytes" : 0,
            "rc" : 0,
            "dl_key" : "",
            "key_delim" : "",
            "file" : "",
            "key_col" : "",
            "query" : f"select * from {dataset}",
            }).execute()
    
    # get
    # owl_check_history
    def get_owl_check_history(self, dataset):
        response = self.client.schema(SCHEMA).table("owl_check_history").select("*").eq("dataset", dataset).execute()
        return response
    
    # delete
    # owl_check_history
    def delete_owl_check_history(self, dataset):
        self.client.schema(SCHEMA).from_("owl_check_history").delete().eq("dataset", dataset).execute()

    # get
    # owl_rule 
    def get_owl_rule(self, dataset):
        response = self.client.schema(SCHEMA).table("owl_rule").select("*").eq("dataset", dataset).execute()
        return response
    
    # delete
    # owl_rule
    def delete_owl_rule(self, dataset):
        self.client.schema(SCHEMA).from_("owl_rule").delete().eq("dataset", dataset).execute()

    # insert 
    # rule_output
    def insert_rule_output(self, dataset, run_id, rule_nm, rule_value, score, perc, assignment_uuid=None, rule_output_assignment_id=None):

        self.client.schema(SCHEMA).table("rule_output")\
        .upsert({
            "dataset": dataset,
            "run_id": run_id,
            "rule_type": "SQLF",
            "rule_nm": rule_nm,
            "rule_value": rule_value,
            "score": score,
            "perc" : perc,
            "assignment_uuid": assignment_uuid,
            "assignment_id": rule_output_assignment_id
            }).execute()
            
    # delete
    # rule_output
    def delete_rule_output(self, dataset, run_id):
        self.client.schema(SCHEMA).from_("rule_output").delete().eq("dataset", dataset).eq("run_id", run_id).execute()
    
    def run_rules(self, dataset, run_id, rc):
        rules_score = 0
        rules = self.get_owl_rule(dataset).data 
        rules_breaking_count = 0
        self.delete_dq_inbox(dataset, run_id)
        # Connect to DuckDB
        # conn = duckdb.connect(':memory:')
        # conn.sql(f"create table if not exists {dataset} as select * from read_csv_auto('./data/fake_customers.csv')")
        
        for r in rules: 
            assignment_uuid = str(uuid.uuid4())
            
            query = r['rule_value']
            rows = self.conn.sql(f"select count(*) from ( {query} ) ").fetchone()[0]
            if rows > 0: 
                score = 0
                rules_breaking_count += 1
                if rows/rc > 0.0 : 
                    score = ((rows/rc)*100) * r['points'] #to do absolute scoring
                    perc = (rows/rc) * 100
                    rules_score += score
                self.insert_assignment_q(dataset, run_id, assignment_uuid, 'RULE')
                assignment_q_id = self.get_assignment_q(dataset, run_id, assignment_uuid, 'RULE')
                rule_output_assignment_id = assignment_q_id.data[0]['id']
                self.insert_rule_output(dataset, run_id, r['rule_nm'], r['rule_value'], int(score), perc, assignment_uuid, rule_output_assignment_id)
                self.insert_data_preview(dataset, run_id, r['rule_nm'], r['rule_value'])
            else: 
                self.insert_rule_output(dataset, run_id, r['rule_nm'], r['rule_value'], 0, 0)
        
        if rules_breaking_count > 0:  #TODO Move outside of rules 
            self.insert_dq_inbox(dataset, run_id, 'Break records, records that do not meet defined conditions', 'RULE', rules_breaking_count)
        return rules_score 
        
    #get 
    # rule_output
    def get_rule_output(self, dataset, run_id): 
        response = self.client.schema(SCHEMA).table("rule_output").select("*").eq("dataset", dataset).eq("run_id", run_id).execute()
        return response
    
    # delete
    # rule_output
    def delete_rule_output(self, dataset, run_id):
        self.client.schema(SCHEMA).from_("rule_output").delete().eq("dataset", dataset).eq("run_id", run_id).execute()


    ##INSERT INTO "validation"."opt_spark" ("dataset", "num_executors", "driver_memory", "executor_cores", "executor_memory", "conf", "queue", "master", "principal", "key_tab", "deploy_mode", "jars", "packages", "files") VALUES ('test', '3', '', '1', '', '', '', 'local[*]', '', '', '', null, null, null);
    # opt_spark
    # insert
    def insert_opt_spark(self, dataset):
        self.client.schema(SCHEMA).table("opt_spark")\
        .upsert({
            "dataset": dataset
        }).execute()
        
    
    # opt_spark
    # get
    def get_opt_spark(self, dataset):
        response = self.client.schema(SCHEMA).table("opt_spark").select("*").eq("dataset", dataset).execute()
        return response
    
    # delete
    # opt_spark
    def delete_opt_spark(self, dataset):
        self.client.schema(SCHEMA).from_("opt_spark").delete().eq("dataset", dataset).execute()
    
    #INSERT INTO "validation"."opt_pushdown" ("dataset", "connection_name", "max_connections", "source_query", "date_format_type", "threads", "manual_source_query", "key", "source_output_schema", "source_break_rules", "source_break_outliers", "source_break_dupes", "source_break_shapes", "sql_logging_toggle", "source_break_results") VALUES ('test', 'DUCKDB', '10', 'select * from test', 'DATE', '2', 'false', '', '', 'false', 'false', 'false', 'false', 'false', 'false');
    # opt_pushdown
    # insert 
    def insert_opt_pushdown(self, dataset):
        self.client.schema(SCHEMA).table("opt_pushdown")\
        .upsert({
            "dataset": dataset, 
            "connection_name": "DUCKDB", 
            "max_connections": 10, 
            "source_query": f"select * from {dataset}", 
            "date_format_type": "DATE", 
            "threads": 2,
            "manual_source_query": "false",
        }).execute()
        
    # opt_pushdown
    # get
    def get_opt_pushdown(self, dataset):
        response = self.client.schema(SCHEMA).table("opt_pushdown").select("*").eq("dataset", dataset).execute()
        return response
    
    # delete
    # opt_pushdown
    def delete_opt_pushdown(self, dataset):
        self.client.schema(SCHEMA).from_("opt_pushdown").delete().eq("dataset", dataset).execute()


    ##INSERT INTO "validation"."opt_env" ("dataset", "jdbcprincipal", "jdbckeytab") VALUES ('test', '', '');
    # opt_env
    # insert
    def insert_opt_env(self, dataset):
        self.client.schema(SCHEMA).table("opt_env")\
        .upsert({
            "dataset": dataset, 
            "jdbcprincipal": "", 
            "jdbckeytab": "", 
            }).execute()
    
    # opt_env
    # delete
    def delete_opt_env(self, dataset):
        self.client.schema(SCHEMA).from_("opt_env").delete().eq("dataset", dataset).execute()

    # opt_env
    # get
    def get_opt_env(self, dataset):
        response = self.client.schema(SCHEMA).table("opt_env").select("*").eq("dataset", dataset).execute()
        return response
    
    # #INSERT INTO "validation"."opt_owl" ("dataset", "runid", "runidend", "run_state", "passfail", "passfaillimit", "jobid", "job_uuid", "agent_id", "linkid", "licensekey", "logfile", "loglevel", "hootonly", "prettyprint", "usetemplate", "parallel", "plan", "datapreviewoff", "datasetsafeoff", "obslimit", "pguser", "pgpassword", "host", "port", "user", "alertemail", "schemascore", "option_append", "schedule_time", "key_delimiter", "pipeline", "agent_uuid", "job_description") VALUES ('test', '2024-09-06', null, 'DRAFT', '1', '75', '-1', null, '0', null, '', '', 'INFO', 'false', 'true', 'false', 'false', 'false', 'false', 'false', '300', '', '', 'aws-0-us-east-1.pooler.supabase.com:5432/postgres?currentSchema=validation&currentSchema=validation', null, 'brian', '', '1', '', null, '~~', '{}', null, '');
    # opt_owl
    # insert
    def insert_opt_owl(self, dataset):
        self.client.schema(SCHEMA).table("opt_owl")\
        .upsert({
            "dataset": dataset, 
            "runid": "2024-09-06", 
            "run_state": "DRAFT", 
            "passfail": "1", 
            "passfaillimit": "75", 
            "jobid": "-1", 
        }).execute()
    
    def delete_opt_owl(self, dataset):
        self.client.schema(SCHEMA).from_("opt_owl").delete().eq("dataset", dataset).execute()

    # opt_owl
    # get
    def get_opt_owl(self, dataset):
        response = self.client.schema(SCHEMA).table("opt_owl").select("*").eq("dataset", dataset).execute()
        return response

    #    #INSERT INTO "validation"."opt_profile" ("dataset", "on", "only", "include", "exclude", "limit", "shape", "correlation", "histogram", "semantic", "histogramlimit", "score", "shapesensitivity", "shapetotalscore", "shapemaxpercol", "shapemaxcolsize", "behavioraldimension", "behavioraldimensiongroup", "behavioralvaluecolumn", "behaviorscoreoff", "behavior_lookback", "behavior_min_support", "behavior_row_check", "behavior_time_check", "behavior_min_value_check", "behavior_max_value_check", "behavior_null_check", "behavior_empty_check", "behavior_unique_check", "behavior_mean_value_check", "push_down", "data_concept_id", "shape_granular", "profile_string_length", "detect_string_numerics", "detect_topn_botn", "detect_scale_precision") VALUES ('test', 'false', 'false', null, null, '300', 'false', null, null, null, '0', '1', '0', '0', '20', '12', '', '', '', 'false', '10', '4', 'true', 'false', 'false', 'false', 'true', 'true', 'true', 'false', '{"count","distinct","mean","minmax","quality"}', '300', null, 'false', 'false', 'false', 'false');
    # opt_profile
    # insert
    def insert_opt_profile(self, dataset):
        self.client.schema(SCHEMA).table("opt_profile")\
        .upsert({
            "dataset": dataset, 
            "on": "false", 
            "only": "false",  
            "limit": "300",
            "shape": "false",
            "histogramlimit": "0",
            "score": "1",
            "shapesensitivity": "0",
            
        }).execute()
    # delete
    # opt_profile
    def delete_opt_profile(self, dataset):
        self.client.schema(SCHEMA).from_("opt_profile").delete().eq("dataset", dataset).execute()

    # get 
    # opt_profile
    def get_opt_profile(self, dataset):
        response = self.client.schema(SCHEMA).table("opt_profile").select("*").eq("dataset", dataset).execute()
        return response
    
    #INSERT INTO "validation"."opt_load" ("dataset", "readonly", "fullfile", "filequery", "fileheader", "filetype", "passwordmanager", "avroschema", "xmlrowtag", "dateformat", "timeformat", "filepath", "delimiter", "unionlookback", "cache", "timestamp", "inferschema", "key", "lib", "lowerbound", "upperbound", "numpartitions", "sample", "usesql", "zerofillnull", "stringmode", "alias", "backrun", "back_run_bin", "columnname", "drivername", "connectionname", "filecharset", "hivenative", "hivenativehwc", "adddatecolumn", "filter", "filternot", "flatten", "handlemaps", "handlemixedjson", "multiline", "replacenulls", "expression", "escapewithbacktick", "escapecharacter", "escapewithsinglequote", "escapewithdoublequote", "connectionurl", "username", "password", "query", "connectionproperties", "operator", "date_column", "transform", "skiplines", "query_history", "additional_lib", "unionlookbackminrow", "check_header", "partition_number", "archive_breaks", "archive_connection", "rule_serial", "core_fetch_mode") VALUES ('test', 'false', 'false', '', null, null, null, '', '', 'yyyy-MM-dd', 'HH:mm:ss.SSS', '', ',', 'false', 'true', 'false', 'true', '', '', null, null, '0', '1', 'true', 'false', 'false', '', '0', 'DAY', null, null, '', 'UTF-8', null, 'false', 'false', '', '', 'false', 'false', 'false', 'false', '', '', 'false', '', 'false', 'false', '', '', '', '', null, null, null, null, '0', '', '', '0', 'true', '0', 'false', '', 'false', 'false');
    # opt_load
    # insert
    def insert_opt_load(self, dataset):
        self.client.schema(SCHEMA).table("opt_load")\
        .upsert({
            "dataset": dataset, 
            "readonly": "false", 
            "fullfile": "false", 
            "filequery": "", 
            "query": f"select * from {dataset}",
            "connectionname": "DUCKDB",
        }).execute()

    # opt_load  
    # get
    def get_opt_load(self, dataset):
        response = self.client.schema(SCHEMA).table("opt_load").select("*").eq("dataset", dataset).execute()
        return response

    # delete
    # opt_load
    def delete_opt_load(self, dataset):
        self.client.schema(SCHEMA).from_("opt_load").delete().eq("dataset", dataset).execute()

    # connections
    #INSERT INTO "validation"."connections" ("aliasname", "hostname", "portnum", "drivername", "username", "password", "driverlocation", "driverprops", "is_template", "is_hive", "use_pwd_mgr", "is_kerb", "keytab", "principal", "is_global", "conn_type", "auth_type", "prompt_creds", "access_role", "region", "img", "escape_begin", "escape_end", "core_sub_driver_dir", "source_name", "is_pushdown", "connection_id", "db_brand_id", "break_records_location", "archive_breaks", "bucket_name", "path_style_access") VALUES ('CONNECT', 'jdbc:hive2://35.194.91.201:10000/default', '10000', 'com.cloudera.hive.jdbc41.HS2Driver', 'root', '', '/opt/owl/drivers/hivedrivers/', 'hive.resultset.use.unique.column.names=false', '0', '1', '0', '0', '', '', '1', 'JDBC', 'usernamepass', 'false', '', '', '/img/connections/hive.svg', '`', '`', 'false', '', '1', '3', '10', '', 'false', null, 'true');
    # insert
    def insert_connection(self):
        self.client.schema(SCHEMA).table("connections")\
        .upsert({
            "aliasname": "DUCKDB", 
            "hostname": "jdbc:duckdb://:memory:", 
            "portnum": "10000", 
            "drivername": "org.duckdb.DuckDBDriver", 
            
        }).execute()

    def data_key_value(self, dataset, run_id, row_key, query=None):

        df = self.conn.sql(query).to_df()[:30] #TODO limit 30, make configurable, limit before taking 30 
        rows = []
        for idx, row in df.iterrows():
            # import uuid
            # uid = str(uuid.uuid4())
            for col in df.columns:
                rows.append({'dataset': dataset, 'run_id': run_id, 'row_cnt': idx, 'row_key': row_key, 'field_nm': col, 'field_value': str(row[col]), 'issue_type' : ''}) # TODO handle nulls and other data types 
        return rows
    
    # INSERT INTO "validation"."data_preview" ("dataset", "run_id", "row_cnt", "row_key", "field_nm", "field_value", "issue_type", "updt_ts") VALUES ('public.sales_data', '2024-08-21 00:00:00+00', '1000000000', '_', 'Daily_ID', '1', '', '2024-08-21 17:00:35.161809');
    # data_preview
    # insert
    def insert_data_preview(self, dataset, run_id, row_key, query=None):
        if query == None:
            query = f"select * from {dataset} limit 30 " #TODO limit 30, make configurable, limit before taking 30 
        else: 
            query = f" select * from ({query}) limit 30 " #TODO limit 30, make configurable, limit before taking 30 

        rows = self.data_key_value(dataset, run_id, row_key, query)
        self.client.schema(SCHEMA).table("data_preview")\
        .upsert(rows).execute()
    
    # data_preview
    # get
    def get_data_preview(self, dataset, run_id):
        response = self.client.schema(SCHEMA).table("data_preview").select("*").eq("dataset", dataset).eq("run_id", run_id).execute()
        return response
    
    # data_preview
    # delete
    def delete_data_preview(self, dataset, run_id):
        self.client.schema(SCHEMA).from_("data_preview").delete().eq("dataset", dataset).eq("run_id", run_id).execute() 

    # INSERT INTO "validation"."owlcheck_q" ("job_id", "job_uuid", "agent_id", "dataset", "run_id", "status", "activity", "activity_status", "cmd_line", "description", "job_exception", "username", "updt_ts", "pid", "remote_job_id", "notified", "agent_job_id", "agent_job_uuid", "agent_uuid", "start_time") VALUES ('1', 'd398429e-66e6-46fc-8db7-8508c2313485', null, 'public.sales_data', '2024-08-21 00:00:00+00', 'FINISHED', null, null, '', null, null, 'brian', '2024-08-21 16:57:48.91233+00', null, null, null, null, null, null, '2024-08-21 16:57:14.858+00');
    # owlcheck_q
    # insert
    #now = datetime.now()
    def insert_owlcheck_q(self, dataset, run_id, status='FINISHED', job_uuid=str(uuid.uuid4())):
        self.client.schema(SCHEMA).table("owlcheck_q")\
        .upsert({
            "job_uuid": job_uuid ,
            "agent_id": 0, 
            "dataset": dataset, 
            "run_id": run_id, 
            "status": status, 
            "cmd_line": "",  
            "username": "brian",
            'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        }).execute()

    def update_owlcheck_q(self, dataset, run_id, status, job_uuid):
        self.client.schema(SCHEMA).table("owlcheck_q")\
        .update({ 
            "status": status
        }).eq('dataset', dataset).eq('run_id', run_id).eq('job_uuid', job_uuid).execute()
    
    # owlcheck_q
    # get
    def get_owlcheck_q(self, dataset, run_id, job_uuid):
        response = self.client.schema(SCHEMA).table("owlcheck_q").select("*").eq("dataset", dataset).eq("run_id", run_id).eq("job_uuid", job_uuid).execute()
        return response
    
    # owlcheck_q
    # delete
    def delete_owlcheck_q(self, dataset, run_id):
        self.client.schema(SCHEMA).from_("owlcheck_q").delete().eq("dataset", dataset).eq("run_id", run_id).execute()
    
    # owlcheck_q
    # update
    # def update_owlcheck_q(self, dataset, run_id, status):
    #     self.client.schema(SCHEMA).table("owlcheck_q").update({"status": status}).eq("dataset", dataset).eq("run_id", run_id).execute()

    # job_log
    # insert
    def insert_job_log(self, job_id, job_uuid, activity, stage, log_desc, log_hint='', stage_time=None):
        self.client.schema(SCHEMA).table("job_log")\
        .upsert({
            "job_id": job_id,
            "job_uuid": job_uuid,
            "activity": activity,
            "stage": stage,
            "log_desc": log_desc,
            "log_hint": log_hint,
            "stage_time": stage_time
        }).execute()
    
    # job_log
    # get
    def get_job_log(self, dataset, run_id):
        response = self.client.schema(SCHEMA).table("job_log").select("*").eq("dataset", dataset).eq("run_id", run_id).execute()
        return response
    
    # job_log
    # delete
    def delete_job_log(self, dataset, run_id):
        self.client.schema(SCHEMA).from_("job_log").delete().eq("dataset", dataset).eq("run_id", run_id).execute()
    

    # INSERT INTO "validation"."assignment_q" ("id", "uuid", "managed_assignment_id", "managed_assignment_uuid", "dataset", "run_id", "assigned_to", "state", "type", "description", "created_at", "updated_by", "updated_at", "assigned_to_group", "additional_fields") VALUES ('17', 'aaec09c6-c262-49fd-ad39-d87e7a07aa63', null, null, 'public.sales_data', '2024-08-21 00:00:00+00', null, 'UNASSIGNED', 'RULE', null, '2024-08-21 17:00:20.774347+00', null, null, null, null);
    # assignment_q
    # insert
    def insert_assignment_q(self, dataset, run_id, uuid, assignment_type):
        self.client.schema(SCHEMA).table("assignment_q")\
        .upsert({
            "uuid": uuid,
            "dataset": dataset, 
            "run_id": run_id, 
            "state": "UNASSIGNED", 
            "type": assignment_type,
            "description": "null",
        }).execute()
    
    # assignment_q
    # get
    def get_assignment_q(self, dataset, run_id, uuid, assignment_type):
        response = self.client.schema(SCHEMA).table("assignment_q").select("*").eq("dataset", dataset).eq("run_id", run_id).eq("uuid", uuid).eq("type", assignment_type).execute()
        return response
    
    # assignment_q
    # delete
    def delete_assignment_q(self, dataset, run_id):
        self.client.schema(SCHEMA).from_("assignment_q").delete().eq("dataset", dataset).eq("run_id", run_id).execute() # .eq("uuid", uuid).eq("type", assignment_type)


    # INSERT INTO "validation"."dq_inbox" ("dataset", "run_id", "item_nm", "item_type", "item_cnt", "item_dt", "is_read", "is_ack", "owl_rank", "dq_impact", "item_sub_type") VALUES ('public.sales_data', '2024-08-21 00:00:00+00', 'Break records, records that do not meet defined conditions', 'RULE', '14', '2024-08-21', null, null, '14', 'NO', 'NA');
    # dq_inbox
    # insert
    def insert_dq_inbox(self, dataset, run_id, item_nm, item_type, item_cnt):
        self.client.schema(SCHEMA).table("dq_inbox")\
        .upsert({
            "dataset": dataset, 
            "run_id": run_id, 
            "item_nm": item_nm,  # Break records, records that do not meet defined conditions
            "item_type": item_type,  # RULE
            "item_cnt": item_cnt, 
        }).execute()    
    
    # dq_inbox
    # get
    def get_dq_inbox(self, dataset, run_id):
        response = self.client.schema(SCHEMA).table("dq_inbox").select("*").eq("dataset", dataset).eq("run_id", run_id).execute()
        return response
    
    # dq_inbox
    # delete
    def delete_dq_inbox(self, dataset, run_id):
        self.client.schema(SCHEMA).from_("dq_inbox").delete().eq("dataset", dataset).eq("run_id", run_id).execute()
    
    # INSERT INTO "validation"."dataset_activity" ("dataset", "run_id", "total_time", "load_time", "profile_time", "dupe_time", "outlier_time", "fpg_time", "validate_src_time", "rules_time", "total_time_in_hours", "total_time_in_minutes", "total_time_in_seconds") VALUES ('public.sales_data', '2024-08-21 00:00:00+00', '00:00:39', null, '00:00:14', null, null, null, null, '00:00:14', '0', '0', '39');
    # dataset_activity
    # insert
    def insert_dataset_activity(self, dataset, run_id, total_time, profile_time, rules_time):
        self.client.schema(SCHEMA).table("dataset_activity")\
        .upsert({
            "dataset": dataset, 
            "run_id": run_id, 
            "total_time": total_time, 
            "profile_time": profile_time, 
            "rules_time": rules_time, 
            "total_time_in_hours": 0, 
            "total_time_in_minutes": 0, 
        }).execute()

    def get_dataset_activity(self, dataset, run_id):
        response = self.client.schema(SCHEMA).table("dataset_activity").select("*").eq("dataset", dataset).eq("run_id", run_id).execute()
        return response

    def delete_dataset_activity(self, dataset, run_id):
        self.client.schema(SCHEMA).from_("dataset_activity").delete().eq("dataset", dataset).eq("run_id", run_id).execute()
             
    # INSERT INTO "validation"."dataset_field_value" ("dataset", "run_id", "field_nm", "field_value", "field_func", "unique_cnt", "updt_ts") VALUES ('default.claims_gcs', '2024-09-23 00:00:00+00', 'income', '0.00', 'TOPN', '2317', '2024-09-23 18:31:23.923604');
    # dataset_field_value
    # insert
    def insert_dataset_field_value(self, payload):
        self.client.schema(SCHEMA).table("dataset_field_value")\
        .upsert(payload).execute()

    # dataset_field_value
    # get
    def get_dataset_field_value(self, dataset, run_id, field_nm):
        response = self.client.schema(SCHEMA).table("dataset_field_value").select("*").eq("dataset", dataset).eq("run_id", run_id).eq("field_nm", field_nm).execute()
        return response
    
    # dataset_field_value
    # delete
    def delete_dataset_field_value(self, dataset, run_id):
        self.client.schema(SCHEMA).from_("dataset_field_value").delete().eq("dataset", dataset).eq("run_id", run_id).execute()

    def parse_and_insert_dataset_field_value_original(self, dataset, run_id, field_nm, field_func):
        # Query the data and group by the specified field
        query = f"SELECT COUNT(*) as unique_cnt, cast ( case when {field_nm}  is null then 'null' else {field_nm} end as string) as field_value FROM {dataset} GROUP BY {field_nm} ORDER BY unique_cnt DESC LIMIT 10"
        
        if field_func == 'BOTTOMN':
            query = f"SELECT COUNT(*) as unique_cnt, cast (case when {field_nm} is null then 'null' else {field_nm} end as string) as field_value FROM {dataset} GROUP BY {field_nm} ORDER BY unique_cnt ASC LIMIT 10"

        if field_func == 'SHAPETOPN':
            query = f""" 
           select 
           REGEXP_REPLACE(case when {field_nm} is null then '' else {field_nm} end, '[a-zA-Z0-9]', 'x', 'g') AS field_value, count(*) as unique_cnt 
           from {dataset}
           group by field_value 
           order by unique_cnt desc limit 10
           """

        result = self.conn.sql(query).fetchdf()
        
        # Add dataset and run_id columns
        result['dataset'] = dataset
        result['run_id'] = run_id
        result['field_func'] = field_func
        result['field_nm'] = field_nm

        # Convert DataFrame to array of JSON objects
        json_array = result.to_dict(orient='records')
        # Insert the array of JSON objects into the data preview
        return json_array
        #self.insert_dataset_field_value(json_array)
        #return result
    
    def parse_and_insert_dataset_field_value(self, dataset, run_id, field_nm, field_func, topn_columns):
        
        from threading import Thread, current_thread
        # Query the data and group by the specified field
        read_thread_count = 5
        threads = []

        self.conn.sql(f""" drop table if exists {dataset}_topn """)
        self.conn.sql(f""" create or replace table {dataset}_topn (
                    field_nm VARCHAR,
                    field_value VARCHAR,
                    unique_cnt BIGINT
        ) """)

        def read_from_thread(duckdb_con, query, column_nm, dataset):
            # Create a DuckDB connection specifically for this thread
            local_con = duckdb_con.cursor()
            name = "thread_"+column_nm
            results = local_con.execute(query).fetchall()
            # print('Name:', name, 'Column: ', column_nm, 'Results: ', results)

        for c in topn_columns: 
            query = f""" INSERT INTO {dataset}_topn (field_nm, field_value, unique_cnt) SELECT
                '{c}' as field_nm,  case when {c} is null then 'null' else {c} end as field_value, count(*) as unique_cnt
                FROM {dataset}  
                GROUP BY  1, 2
                ORDER BY unique_cnt desc 
                LIMIT 5  """
            threads.append(Thread(target = read_from_thread,
                                    args = (self.conn,),
                                    name = 'read_thread_' + str(c),
                                    kwargs = {'query': query, 'column_nm': c, 'dataset': dataset}
                                    )
                                    )

        # Kick off all threads in parallel
        for thread in threads:
            thread.start()

        # Ensure all threads complete before printing final results
        for thread in threads:
            thread.join()

        result = self.conn.sql(f""" select '{dataset}' as dataset, '{run_id}' as run_id, '{field_func}' as field_func, * from {dataset}_topn """).fetchdf()

        json_array = result.to_dict(orient='records')
        return json_array
    
    # Reset Opts
    def register(self, dataset):

        # opt_spark
        self.delete_opt_spark(dataset)
        self.insert_opt_spark(dataset)
        rs = self.get_opt_spark(dataset)
        print(rs)

        # opt_pushdown
        self.delete_opt_pushdown(dataset)
        self.insert_opt_pushdown(dataset)
        rs = self.get_opt_pushdown(dataset)
        print(rs)

        # opt_profile
        self.delete_opt_profile(dataset)
        self.insert_opt_profile(dataset)
        rs = self.get_opt_profile(dataset)
        print(rs)

        # opt_load
        self.delete_opt_load(dataset)
        self.insert_opt_load(dataset)
        rs = self.get_opt_load(dataset)
        print(rs)

        # opt_profile
        self.delete_opt_profile(dataset)
        self.insert_opt_profile(dataset)
        rs = self.get_opt_profile(dataset)
        print(rs)

        # opt_env
        self.delete_opt_env(dataset)
        self.insert_opt_env(dataset)
        rs = self.get_opt_env(dataset)
        print(rs)

        # opt_owl
        self.delete_opt_owl(dataset)
        self.insert_opt_owl(dataset)
        rs = self.get_opt_owl(dataset)
        print(rs)

    
    # Run 
    def run(self, dataset, run_id):

        # INIT
        dataset_activity = {}
        job_start_time = time.time()
        job_uuid = str(uuid.uuid4())
        self.insert_owlcheck_q(dataset, run_id, 'INIT', job_uuid)
        rs = self.get_owlcheck_q(dataset, run_id, job_uuid)
        job_id = rs.data[0]['job_id']
        print(job_id)
        
        rc = self.conn.sql(f"select count(*) from {dataset}").fetchone()[0]
        self.conn.sql(f"drop table if exists {dataset}_profile " )
        self.conn.sql(f"create table {dataset}_profile as  select * from ( summarize from {dataset} ) ")
        
        # TODO add topn_columns to config on percentage unique
        topn_cutoff = self.conn.sql(f"""select column_name, q50 from ( summarize from {dataset}_profile ) where column_name = 'approx_unique' """).fetchone()[1]
        topn_columns = self.conn.sql(f"""
                select * from {dataset}_profile 

                """).to_df()['column_name'].tolist()
        # select * from {dataset}_profile 
        # where approx_unique < {topn_cutoff} 
        # and approx_unique > 1
        # and null_percentage  < {rc}
        # order by approx_unique desc
        print(f"Row Count: {rc}")
        print(f"TopN Columns: {len(topn_columns)}")

        # pre-routine section for clearing previous runs 
        start_time = time.time()
        self.delete_data_preview(dataset, run_id) # TODO pre-routine section for clearing previous runs 
        self.delete_owl_check_history(dataset)
        self.insert_owl_check_history(dataset, run_id)
        # rs = self.get_owl_check_history(dataset)
        # print(rs)
        finish_time = time.time()  # Track finish time
        print(f"History Time taken: {finish_time - start_time} seconds")

        # owl_catalog, 
        # Delete, Insert, Read
        start_time = time.time() 
        # self.delete_owl_catalog(dataset)
        self.insert_owl_catalog(dataset)
        # rs = self.get_owl_catalog(dataset)
        # print(rs)
        finish_time = time.time()  # Track finish time
        print(f"Catalog Time taken: {finish_time - start_time} seconds")

        # RUNNING
        self.update_owlcheck_q(dataset, run_id, 'RUNNING', job_uuid)

        # dataset_schema, 
        # Delete, Insert, Read
        start_time = time.time()
        self.insert_job_log(job_id, job_uuid, 'SCHEMA', 'START', 'Start Schema activity')
        self.delete_dataset_schema(dataset)
        self.insert_dataset_schema(dataset)
        finish_time = time.time()  # Track finish time
        print(f"Schema Time taken: {finish_time - start_time} seconds")
        self.insert_job_log(job_id, job_uuid, 'SCHEMA', 'END', 'Completed Schema activity', stage_time=round(finish_time - start_time))

        # dataset_field, # profile 
        # Delete, Insert, Read
        start_time = time.time()
        self.insert_job_log(job_id, job_uuid, 'PROFILE', 'START', 'Start Profile activity')
        self.delete_dataset_field(dataset, run_id)
        self.insert_dataset_field(dataset, run_id, rc)
        # rs = self.get_dataset_field(dataset, run_id)
        # print(rs)
        finish_time = time.time()  # Track finish time
        self.insert_job_log(job_id, job_uuid, 'PROFILE', 'END', 'Completed Profile activity', stage_time=round(finish_time - start_time))
        dataset_activity['profile_time'] = str(timedelta(seconds=round(finish_time - start_time)))
        print(f"Profile Time taken: {finish_time - start_time} seconds")
                                               
        # topN
        # Retrieve column names from the dataset
        # columns = self.conn.sql(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{dataset}'  AND data_type = 'VARCHAR'").fetchdf()['column_name'].tolist() #TODO rewire for df input 
        start_time = time.time()
        self.delete_dataset_field_value(dataset, run_id)
        
        topn_array = self.parse_and_insert_dataset_field_value(dataset, run_id, topn_columns, 'TOPN', topn_columns)
        print("TOPNARRAY: ", len(topn_array))
        #for column in topn_columns:
            #topn_array.extend(self.parse_and_insert_dataset_field_value(dataset, run_id, column, 'TOPN'))
        
        self.insert_dataset_field_value(topn_array)
        #   self.parse_and_insert_dataset_field_value(dataset, run_id, column, 'BOTTOMN')
    
        # for column in columns:
        #     self.parse_and_insert_dataset_field_value(dataset, run_id, column, 'SHAPETOPN')

        finish_time = time.time() 
        print(f"TopN Time taken: {finish_time - start_time} seconds")
        
        # run rules 
        self.insert_job_log(job_id, job_uuid, 'RULE', 'START', 'Start Running Rules')
        start_time = time.time()
        self.delete_rule_output(dataset, run_id)
        rule_score = self.run_rules(dataset, run_id, rc)

        # rule score 
        # rule_output = self.get_rule_output(dataset, run_id)
        # print(str(rule_output.data))
        # rule_score = 0
        # for r in rule_output.data:
        #     rule_score += r['score']
        # print(str(rule_score))
        self.insert_job_log(job_id, job_uuid, 'RULE', 'END', 'Completed Running Rules', stage_time=round(finish_time - start_time))
        finish_time = time.time() 
        print(f"Rules Time taken: {finish_time - start_time} seconds")
        dataset_activity['rules_time'] = str(timedelta(seconds=round(finish_time - start_time)))

        # dataset_scan, 
        # Delete, Insert, Read
        start_time = time.time()
        # rc = self.conn.execute(f"SELECT COUNT(*) FROM {dataset}").fetchone()[0] #TODO add property for client 
        self.delete_dataset_scan(dataset, run_id)
        self.insert_dataset_scan(dataset, run_id, rc, round(100 - rule_score))
        # rs = self.get_dataset_scan(dataset, run_id)
        # print(rs.data)
        finish_time = time.time()  # Track finish time
        print(f"Scan Ledger Time taken: {finish_time - start_time} seconds")

        # owlcheck_q
        # Delete, Insert, Read
        start_time = time.time()
        self.update_owlcheck_q(dataset, run_id, 'FINISHED', job_uuid)
        # rs = self.get_owlcheck_q(dataset, run_id, job_uuid)
        # print(rs.data)
        # print(rs.data[0]['job_id'])
        
        # post routines 
        # data_preview
        self.insert_data_preview(dataset, run_id, '_')
        # rs = self.get_data_preview(dataset, run_id)
        # print(rs.data)

        job_finish_time = time.time()   
        total_time = str(timedelta(seconds=round(job_finish_time - job_start_time)))
        
        #total_time_in_hours = round(total_time / 3600)
        #total_time_in_minutes = round(total_time / 60)
        self.delete_dataset_activity(dataset, run_id)
        self.insert_dataset_activity(dataset, run_id, total_time, dataset_activity['profile_time'], dataset_activity['rules_time'])
        # rs = self.get_dataset_activity(dataset, run_id)
        # print(rs.data)
        finish_time = time.time() 
        print(f"Final Steps Time taken: {finish_time - start_time} seconds")
