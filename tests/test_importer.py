# tests/test_importer.py
import json
import sqlite3

from job_market_analyzer.io.importer import import_csv, import_json, import_sqlite


class TestImportCSV:
    def test_basic_csv(self, tmp_path):
        csv_file = tmp_path / "jobs.csv"
        csv_file.write_text(
            "job_id,job_name,company_name,city,salary_raw,experience,education\n"
            "1,数据分析师,某公司,成都,15-25K,3-5年,本科\n"
            "2,数据工程师,另一公司,北京,20-30K·14薪,5-10年,硕士\n",
            encoding="utf-8",
        )
        jobs = import_csv(str(csv_file))
        assert len(jobs) == 2
        assert jobs[0].city == "成都"
        assert jobs[0].salary_min == 15.0
        assert jobs[1].salary_months == 14


class TestImportJSON:
    def test_basic_json(self, tmp_path):
        json_file = tmp_path / "jobs.json"
        data = [
            {"job_id": "1", "job_name": "数据分析师", "company_name": "某公司",
             "city": "成都", "salary_raw": "15-25K"},
        ]
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        jobs = import_json(str(json_file))
        assert len(jobs) == 1
        assert jobs[0].salary_min == 15.0


class TestImportSQLite:
    def test_basic_sqlite(self, tmp_path):
        db_file = tmp_path / "jobs.db"
        conn = sqlite3.connect(str(db_file))
        c = conn.cursor()
        c.execute("""CREATE TABLE jobs (
            job_id TEXT, job_name TEXT, company_name TEXT,
            city TEXT, salary_raw TEXT, experience TEXT, education TEXT
        )""")
        c.execute("INSERT INTO jobs VALUES ('1', '数据分析师', '某公司', '成都', '15-25K', '3-5年', '本科')")
        conn.commit()
        conn.close()
        jobs = import_sqlite(str(db_file))
        assert len(jobs) == 1
        assert jobs[0].salary_min == 15.0
