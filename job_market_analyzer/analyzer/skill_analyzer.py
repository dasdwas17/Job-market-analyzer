"""技能分析模块"""
from collections import Counter, defaultdict

from job_market_analyzer.schema import JobItem
from job_market_analyzer.utils.stat_helper import safe_percentile


class SkillAnalyzer:
    """技能分析器"""

    def __init__(self, jobs: list[JobItem]):
        self.jobs = jobs

    def frequency(self, min_freq: float = 0.05) -> dict[str, float]:
        """技能出现频率"""
        total = len(self.jobs)
        if total == 0:
            return {}
        counter = Counter()
        for job in self.jobs:
            for skill in job.skill_tags:
                counter[skill] += 1
        return {
            skill: count / total
            for skill, count in counter.items()
            if count / total >= min_freq
        }

    def salary_correlation(self) -> dict[str, dict]:
        """技能-薪资关联分析（基于 job_id 差集，避免薪资值碰撞误剔除）"""
        valid_jobs = [j for j in self.jobs if j.salary_median is not None]

        skill_jobs: dict[str, list] = defaultdict(list)
        for job in valid_jobs:
            for skill in job.skill_tags:
                skill_jobs[skill].append(job)

        result = {}
        for skill, jobs_with in skill_jobs.items():
            with_sals = [j.salary_median for j in jobs_with]
            with_ids = {j.job_id for j in jobs_with}
            without_sals = [j.salary_median for j in valid_jobs if j.job_id not in with_ids]
            result[skill] = {
                "with_skill": safe_percentile(with_sals, 50),
                "without_skill": safe_percentile(without_sals, 50) if without_sals else None,
                "count": len(with_sals),
            }
        return result

    def top_n(self, n: int = 20) -> dict[str, float]:
        """前 N 个高频技能"""
        freq = self.frequency(min_freq=0.0)
        sorted_items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_items[:n])
