# tests/test_strategy_advisor.py
import pytest

from job_market_analyzer.analyzer.strategy_advisor import StrategyAdvisor
from job_market_analyzer.io.demo_adapter import DemoAdapter
from job_market_analyzer.schema import UserProfile


class TestStrategyAdvisor:
    @pytest.fixture
    def jobs(self):
        return DemoAdapter(seed=42).fetch_jobs(n_samples=100)

    def test_generate_report(self, jobs):
        profile = UserProfile(
            user_skills=["Python", "SQL"],
            user_experience="3-5年",
            user_education="本科",
            target_city="成都",
        )
        advisor = StrategyAdvisor(profile)
        report = advisor.generate(jobs)
        assert len(report.matched_jobs) <= 5
        assert len(report.skill_gaps) > 0
        assert len(report.action_items) > 0

    def test_top5_ranked(self, jobs):
        profile = UserProfile(user_skills=["Python", "SQL", "Excel"])
        advisor = StrategyAdvisor(profile)
        report = advisor.generate(jobs)
        if len(report.matched_jobs) > 1:
            scores = [j.match_score for j in report.matched_jobs]
            assert scores == sorted(scores, reverse=True)
