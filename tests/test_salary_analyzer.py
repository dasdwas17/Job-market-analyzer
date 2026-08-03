# tests/test_salary_analyzer.py
import pytest

from job_market_analyzer.analyzer.salary_analyzer import SalaryAnalyzer
from job_market_analyzer.io.demo_adapter import DemoAdapter


class TestSalaryAnalyzer:
    @pytest.fixture
    def jobs(self):
        return DemoAdapter(seed=42).fetch_jobs(n_samples=200)

    def test_distribution(self, jobs):
        analyzer = SalaryAnalyzer(jobs)
        result = analyzer.distribution(bins=[0, 10, 15, 20, 25, 30, 40, 50, 100])
        assert "labels" in result
        assert "counts" in result
        assert sum(result["counts"]) == len(jobs)

    def test_by_city(self, jobs):
        analyzer = SalaryAnalyzer(jobs)
        result = analyzer.by_city()
        assert isinstance(result, dict)
        assert len(result) > 0
        for stats in result.values():
            assert "median" in stats
            assert "min" in stats
            assert "max" in stats

    def test_by_experience(self, jobs):
        analyzer = SalaryAnalyzer(jobs)
        result = analyzer.by_experience()
        assert isinstance(result, dict)

    def test_by_education(self, jobs):
        analyzer = SalaryAnalyzer(jobs)
        result = analyzer.by_education()
        assert isinstance(result, dict)

    def test_summary(self, jobs):
        analyzer = SalaryAnalyzer(jobs)
        result = analyzer.summary()
        assert "median" in result
        assert "p25" in result
        assert "p75" in result
