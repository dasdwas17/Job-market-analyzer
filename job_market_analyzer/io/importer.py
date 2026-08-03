"""数据导入器：支持 CSV / JSON / SQLite"""
import csv
import json
import sqlite3

from job_market_analyzer.schema import JobItem


def _row_to_jobitem(row: dict) -> JobItem:
    """将字典行转换为 JobItem，忽略未知字段"""
    # 确保必填字段存在
    row.setdefault("job_id", "")
    row.setdefault("job_name", "")
    row.setdefault("company_name", "")
    row.setdefault("city", "")
    # 处理 skill_tags（可能是字符串）
    if "skill_tags" in row and isinstance(row["skill_tags"], str):
        row["skill_tags"] = [s.strip() for s in row["skill_tags"].split(",") if s.strip()]
    # 过滤掉 JobItem 不认识的字段
    valid_fields = JobItem.model_fields.keys()
    filtered = {k: v for k, v in row.items() if k in valid_fields}
    return JobItem(**filtered)


def import_csv(path: str) -> list[JobItem]:
    """从 CSV 文件导入"""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [_row_to_jobitem(row) for row in reader]


def import_json(path: str) -> list[JobItem]:
    """从 JSON 文件导入"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    return [_row_to_jobitem(row) for row in data]


def import_sqlite(path: str, table: str = "jobs") -> list[JobItem]:
    """从 SQLite 数据库导入"""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return [_row_to_jobitem(row) for row in rows]
