# tests/test_competitive_analyzer.py
import pytest

from job_market_analyzer.analyzer.competitive_analyzer import CompetitiveAnalyzer
from job_market_analyzer.io.demo_adapter import DemoAdapter


class TestCompetitiveAnalyzer:
    @pytest.fixture
    def jobs(self):
        return DemoAdapter(seed=42).fetch_jobs(n_samples=300)

    def test_city_index(self, jobs):
        analyzer = CompetitiveAnalyzer(jobs)
        result = analyzer.city_index()
        assert isinstance(result, dict)
        for score in result.values():
            assert 0 <= score <= 100

    def test_weights_configurable(self, jobs):
        analyzer = CompetitiveAnalyzer(
            jobs,
            weights={"job_density": 0.5, "salary_level": 0.3, "education_relaxation": 0.2},
        )
        result = analyzer.city_index()
        assert len(result) > 0
