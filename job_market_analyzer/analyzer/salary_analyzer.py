"""薪资分析模块"""
from collections import defaultdict

from job_market_analyzer.schema import JobItem
from job_market_analyzer.utils.stat_helper import bin_values, safe_percentile


class SalaryAnalyzer:
    """薪资分析器"""

    def __init__(self, jobs: list[JobItem]):
        self.jobs = [j for j in jobs if j.salary_median is not None]

    def distribution(self, bins: list[float]) -> dict:
        """薪资分布直方图"""
        salaries = [j.salary_median for j in self.jobs]
        labels, counts = bin_values(salaries, bins)
        return {"labels": labels, "counts": counts}

    def by_city(self) -> dict[str, dict]:
        """按城市分组统计"""
        groups = defaultdict(list)
        for job in self.jobs:
            groups[job.city].append(job.salary_median)
        return {
            city: {
                "median": safe_percentile(sals, 50),
                "min": min(sals),
                "max": max(sals),
                "count": len(sals),
            }
            for city, sals in groups.items()
        }

    def by_experience(self) -> dict[str, dict]:
        """按经验分组统计"""
        groups = defaultdict(list)
        for job in self.jobs:
            if job.experience:
                groups[job.experience].append(job.salary_median)
        return {
            exp: {
                "median": safe_percentile(sals, 50),
                "count": len(sals),
            }
            for exp, sals in groups.items()
        }

    def by_education(self) -> dict[str, dict]:
        """按学历分组统计"""
        groups = defaultdict(list)
        for job in self.jobs:
            if job.education:
                groups[job.education].append(job.salary_median)
        return {
            edu: {
                "median": safe_percentile(sals, 50),
                "count": len(sals),
            }
            for edu, sals in groups.items()
        }

    def summary(self) -> dict:
        """总体统计"""
        salaries = [j.salary_median for j in self.jobs]
        return {
            "median": safe_percentile(salaries, 50),
            "p25": safe_percentile(salaries, 25),
            "p75": safe_percentile(salaries, 75),
            "p90": safe_percentile(salaries, 90),
            "min": min(salaries) if salaries else None,
            "max": max(salaries) if salaries else None,
            "count": len(salaries),
        }
