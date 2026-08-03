# tests/test_demo_adapter.py
from job_market_analyzer.io.demo_adapter import DemoAdapter
from job_market_analyzer.schema import JobItem


class TestDemoAdapter:
    def test_default_generation(self):
        adapter = DemoAdapter(seed=42)
        jobs = adapter.fetch_jobs(n_samples=100)
        assert len(jobs) == 100
        assert all(isinstance(j, JobItem) for j in jobs)

    def test_city_filter(self):
        adapter = DemoAdapter(seed=42)
        jobs = adapter.fetch_jobs(n_samples=50, city="北京")
        assert len(jobs) > 0
        assert all(j.city == "北京" for j in jobs)

    def test_salary_distribution(self):
        """北京薪资应该整体高于成都"""
        adapter = DemoAdapter(seed=42)
        bj_jobs = adapter.fetch_jobs(n_samples=500, city="北京")
        cd_jobs = adapter.fetch_jobs(n_samples=500, city="成都")
        bj_median = sum(j.salary_median for j in bj_jobs) / len(bj_jobs)
        cd_median = sum(j.salary_median for j in cd_jobs) / len(cd_jobs)
        assert bj_median > cd_median

    def test_max_generate_ratio_safety(self):
        """苛刻条件不会死循环"""
        adapter = DemoAdapter(seed=42)
        jobs = adapter.fetch_jobs(n_samples=500, city="北京", education="博士")
        # 可能不足500，但不会死循环
        assert len(jobs) > 0

    def test_skill_tags_not_empty(self):
        adapter = DemoAdapter(seed=42)
        jobs = adapter.fetch_jobs(n_samples=50)
        has_skills = any(len(j.skill_tags) > 0 for j in jobs)
        assert has_skills

    def test_job_description_not_empty(self):
        adapter = DemoAdapter(seed=42)
        jobs = adapter.fetch_jobs(n_samples=50)
        has_desc = any(len(j.job_description) > 0 for j in jobs)
        assert has_desc
