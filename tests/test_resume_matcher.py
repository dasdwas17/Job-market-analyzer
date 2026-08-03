# tests/test_resume_matcher.py
import pytest

from job_market_analyzer.analyzer.resume_matcher import ResumeMatcher
from job_market_analyzer.io.demo_adapter import DemoAdapter
from job_market_analyzer.schema import UserProfile


class TestResumeMatcher:
    @pytest.fixture
    def jobs(self):
        return DemoAdapter(seed=42).fetch_jobs(n_samples=50)

    def test_match_score(self, jobs):
        profile = UserProfile(
            user_skills=["Python", "SQL", "Excel"],
            user_experience="3-5年",
            user_education="本科",
        )
        matcher = ResumeMatcher(profile)
        scores = matcher.match_all(jobs)
        assert len(scores) == len(jobs)
        for score in scores.values():
            assert 0 <= score <= 100

    def test_skill_match(self, jobs):
        profile = UserProfile(user_skills=["Python", "SQL"])
        matcher = ResumeMatcher(profile)
        matched, _ = matcher.skill_match(jobs[0].skill_tags)
        assert "Python" in matched or "SQL" in matched
