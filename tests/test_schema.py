# tests/test_schema.py
from job_market_analyzer.schema import (
    ActionItem,
    JobItem,
    JobMatch,
    SkillGap,
    StrategyReport,
)


class TestJobItem:
    def test_basic_creation(self):
        job = JobItem(
            job_id="abc123",
            job_name="数据分析师",
            company_name="某科技公司",
            city="成都",
        )
        assert job.job_name == "数据分析师"
        assert job.skill_tags == []
        assert job.salary_min is None

    def test_salary_auto_parse_from_raw(self):
        job = JobItem(
            job_id="abc123",
            job_name="数据分析师",
            company_name="某公司",
            city="北京",
            salary_raw="15-25K·14薪",
        )
        assert job.salary_min == 15.0
        assert job.salary_max == 25.0
        assert job.salary_median == 20.0
        assert job.salary_months == 14

    def test_salary_median_fallback(self):
        job = JobItem(
            job_id="abc123",
            job_name="数据分析师",
            company_name="某公司",
            city="北京",
            salary_min=15.0,
            salary_max=25.0,
        )
        assert job.salary_median == 20.0

    def test_salary_mianyi(self):
        job = JobItem(
            job_id="abc123",
            job_name="数据分析师",
            company_name="某公司",
            city="北京",
            salary_raw="面议",
        )
        assert job.salary_min is None


class TestStrategyReport:
    def test_creation(self):
        report = StrategyReport(
            matched_jobs=[
                JobMatch(
                    rank=1, job_name="数据分析师", company_name="某公司",
                    salary_range="20-25K", match_score=85.0,
                    required_skills=["Python", "SQL"],
                    matched_skills=["Python"],
                    missing_skills=["SQL"],
                )
            ],
            skill_gaps=[
                SkillGap(skill="SQL", impact="投递命中率下降30%", frequency=0.75)
            ],
            action_items=[
                ActionItem(priority="高", action="1个月内补充SQL实战", reason="SQL出现频率75%")
            ],
        )
        assert len(report.matched_jobs) == 1
        assert report.matched_jobs[0].match_score == 85.0
