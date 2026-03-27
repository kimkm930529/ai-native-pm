#!/usr/bin/env python3
"""
Databricks API Client — databricks-agent-system
Unity Catalog 탐색 + SQL Statement Execution API 사용

연동 필요:
  .env에 다음 환경변수 추가:
    DATABRICKS_HOST=https://your-workspace.databricks.com
    DATABRICKS_TOKEN=dapi-xxxxxxxxxxxxxxxxxxxx
    DATABRICKS_WAREHOUSE_ID=your-sql-warehouse-id

사용법:
  python3 client.py --check
  python3 client.py --list-catalogs
  python3 client.py --list-schemas --catalog {catalog}
  python3 client.py --list-tables --catalog {catalog} --schema {schema}
  python3 client.py --describe --table {catalog}.{schema}.{table}
  python3 client.py --sample --table {catalog}.{schema}.{table}
  python3 client.py --execute "SELECT ..." --warehouse-id {id}
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

# .env 로드 (python-dotenv가 없으면 수동으로 읽기)
def load_env():
    env_path = Path(__file__).parents[2] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

load_env()

DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
DATABRICKS_WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID", "")


def get_headers():
    return {
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
        "Content-Type": "application/json",
    }


def api_get(path: str) -> dict:
    """GET 요청"""
    import urllib.request
    url = f"{DATABRICKS_HOST}{path}"
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def api_post(path: str, body: dict) -> dict:
    """POST 요청"""
    import urllib.request
    url = f"{DATABRICKS_HOST}{path}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=get_headers(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


# ─── 연결 확인 ──────────────────────────────────────────────

def check_connection():
    if not DATABRICKS_HOST or not DATABRICKS_TOKEN:
        print(json.dumps({
            "status": "error",
            "message": "환경변수 미설정",
            "required": {
                "DATABRICKS_HOST": bool(DATABRICKS_HOST),
                "DATABRICKS_TOKEN": bool(DATABRICKS_TOKEN),
                "DATABRICKS_WAREHOUSE_ID": bool(DATABRICKS_WAREHOUSE_ID),
            },
            "guide": "databricks-agent-system/CLAUDE.md §Step 0 참조"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    result = api_get("/api/2.0/preview/scim/v2/Me")
    if "error" in result:
        print(json.dumps({"status": "error", "message": result["error"]}, ensure_ascii=False, indent=2))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "user": result.get("displayName", "unknown"),
        "host": DATABRICKS_HOST,
        "warehouse_id_set": bool(DATABRICKS_WAREHOUSE_ID),
    }, ensure_ascii=False, indent=2))


# ─── Unity Catalog 탐색 ─────────────────────────────────────

def list_catalogs():
    result = api_get("/api/2.1/unity-catalog/catalogs")
    catalogs = result.get("catalogs", [])
    print(json.dumps({
        "catalogs": [
            {
                "name": c.get("name"),
                "comment": c.get("comment", ""),
                "owner": c.get("owner", ""),
                "updated_at": c.get("updated_at", ""),
            }
            for c in catalogs
        ],
        "count": len(catalogs),
    }, ensure_ascii=False, indent=2))


def list_schemas(catalog: str):
    result = api_get(f"/api/2.1/unity-catalog/schemas?catalog_name={catalog}")
    schemas = result.get("schemas", [])
    print(json.dumps({
        "catalog": catalog,
        "schemas": [
            {
                "name": s.get("name"),
                "full_name": s.get("full_name"),
                "comment": s.get("comment", ""),
                "owner": s.get("owner", ""),
            }
            for s in schemas
        ],
        "count": len(schemas),
    }, ensure_ascii=False, indent=2))


def list_tables(catalog: str, schema: str):
    result = api_get(
        f"/api/2.1/unity-catalog/tables?catalog_name={catalog}&schema_name={schema}"
    )
    tables = result.get("tables", [])
    print(json.dumps({
        "catalog": catalog,
        "schema": schema,
        "tables": [
            {
                "name": t.get("name"),
                "full_name": t.get("full_name"),
                "table_type": t.get("table_type"),
                "comment": t.get("comment", ""),
                "owner": t.get("owner", ""),
                "updated_at": t.get("updated_at", ""),
            }
            for t in tables
        ],
        "count": len(tables),
    }, ensure_ascii=False, indent=2))


def describe_table(table_full_name: str):
    """catalog.schema.table 형식"""
    parts = table_full_name.split(".")
    if len(parts) != 3:
        print(json.dumps({"error": "table은 catalog.schema.table 형식이어야 합니다."}, ensure_ascii=False))
        sys.exit(1)
    catalog, schema, table = parts
    result = api_get(
        f"/api/2.1/unity-catalog/tables/{catalog}.{schema}.{table}"
    )
    if "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    columns = [
        {
            "name": c.get("name"),
            "type": c.get("type_text"),
            "nullable": c.get("nullable", True),
            "comment": c.get("comment", ""),
        }
        for c in result.get("columns", [])
    ]
    print(json.dumps({
        "table": table_full_name,
        "table_type": result.get("table_type"),
        "comment": result.get("comment", ""),
        "owner": result.get("owner", ""),
        "columns": columns,
        "column_count": len(columns),
        "partitions": result.get("partitions", []),
        "storage_location": result.get("storage_location", ""),
    }, ensure_ascii=False, indent=2))


def sample_table(table_full_name: str, limit: int = 5):
    sql = f"SELECT * FROM {table_full_name} LIMIT {limit}"
    execute_sql(sql)


# ─── SQL 실행 ───────────────────────────────────────────────

WRITE_KEYWORDS = {"INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE", "MERGE"}

def is_write_query(sql: str) -> bool:
    first_token = sql.strip().split()[0].upper()
    return first_token in WRITE_KEYWORDS


def execute_sql(sql: str, warehouse_id: str = ""):
    warehouse_id = warehouse_id or DATABRICKS_WAREHOUSE_ID
    if not warehouse_id:
        print(json.dumps({
            "error": "DATABRICKS_WAREHOUSE_ID 미설정. query/analyze 모드 불가.",
            "guide": ".env에 DATABRICKS_WAREHOUSE_ID 추가 필요"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    if is_write_query(sql):
        print(json.dumps({
            "error": "쓰기 쿼리 실행 거부",
            "sql": sql[:100],
            "message": "SELECT 쿼리만 허용됩니다. INSERT/UPDATE/DELETE/DROP 등은 실행할 수 없습니다.",
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    # SQL Statement Execution API
    body = {
        "statement": sql,
        "warehouse_id": warehouse_id,
        "wait_timeout": "50s",
        "on_wait_timeout": "CANCEL",
    }
    result = api_post("/api/2.0/sql/statements", body)

    if "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(1)

    statement_id = result.get("statement_id")
    status = result.get("status", {}).get("state")

    # 폴링 (비동기 실행 시)
    max_wait = 60
    waited = 0
    while status in ("PENDING", "RUNNING") and waited < max_wait:
        time.sleep(2)
        waited += 2
        poll = api_get(f"/api/2.0/sql/statements/{statement_id}")
        status = poll.get("status", {}).get("state")
        result = poll

    if status != "SUCCEEDED":
        print(json.dumps({
            "error": f"쿼리 실패: {status}",
            "detail": result.get("status", {}).get("error", {}),
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    manifest = result.get("manifest", {})
    data_result = result.get("result", {})
    columns = [c.get("name") for c in manifest.get("schema", {}).get("columns", [])]
    rows = data_result.get("data_array", [])

    print(json.dumps({
        "sql": sql,
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "execution_time_ms": result.get("status", {}).get("execution_time_ms"),
    }, ensure_ascii=False, indent=2))


# ─── CLI ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Databricks API Client")
    parser.add_argument("--check", action="store_true", help="연결 확인")
    parser.add_argument("--list-catalogs", action="store_true")
    parser.add_argument("--list-schemas", action="store_true")
    parser.add_argument("--list-tables", action="store_true")
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--execute", type=str, metavar="SQL")
    parser.add_argument("--catalog", type=str)
    parser.add_argument("--schema", type=str)
    parser.add_argument("--table", type=str)
    parser.add_argument("--warehouse-id", type=str, default="")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    if args.check:
        check_connection()
    elif args.list_catalogs:
        list_catalogs()
    elif args.list_schemas:
        if not args.catalog:
            print(json.dumps({"error": "--catalog 필요"})); sys.exit(1)
        list_schemas(args.catalog)
    elif args.list_tables:
        if not args.catalog or not args.schema:
            print(json.dumps({"error": "--catalog, --schema 모두 필요"})); sys.exit(1)
        list_tables(args.catalog, args.schema)
    elif args.describe:
        if not args.table:
            print(json.dumps({"error": "--table 필요 (catalog.schema.table 형식)"})); sys.exit(1)
        describe_table(args.table)
    elif args.sample:
        if not args.table:
            print(json.dumps({"error": "--table 필요"})); sys.exit(1)
        sample_table(args.table, args.limit)
    elif args.execute:
        execute_sql(args.execute, args.warehouse_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
