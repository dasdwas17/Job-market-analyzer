# tests/test_skill_analyzer.py
import pytest

from job_market_analyzer.analyzer.skill_analyzer import SkillAnalyzer
from job_market_analyzer.io.demo_adapter import DemoAdapter


class TestSkillAnalyzer:
    @pytest.fixture
    def jobs(self):
        return DemoAdapter(seed=42).fetch_jobs(n_samples=200)

    def test_frequency(self, jobs):
        analyzer = SkillAnalyzer(jobs)
        result = analyzer.frequency(min_freq=0.0)
        assert isinstance(result, dict)
        assert "Python" in result
        assert result["Python"] > 0

    def test_salary_correlation(self, jobs):
        analyzer = SkillAnalyzer(jobs)
        result = analyzer.salary_correlation()
        assert isinstance(result, dict)
        for stats in result.values():
            assert "with_skill" in stats
            assert "without_skill" in stats

    def test_top_n(self, jobs):
        analyzer = SkillAnalyzer(jobs)
        result = analyzer.top_n(n=5)
        assert len(result) <= 5
