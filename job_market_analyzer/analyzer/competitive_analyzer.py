"""竞争度分析模块"""
from collections import defaultdict

from job_market_analyzer.schema import JobItem
from job_market_analyzer.utils.stat_helper import normalize, safe_percentile


class CompetitiveAnalyzer:
    """竞争度分析器"""

    def __init__(
        self,
        jobs: list[JobItem],
        weights: dict[str, float] | None = None,
    ):
        self.jobs = jobs
        self.weights = weights or {
            "job_density": 0.4,
            "salary_level": 0.3,
            "education_relaxation": 0.3,
        }

    def city_index(self) -> dict[str, float]:
        """计算各城市竞争指数 (0-100，越高竞争越激烈)"""
        cities = defaultdict(list)
        for job in self.jobs:
            cities[job.city].append(job)

        total_jobs = len(self.jobs)
        city_metrics = {}
        for city, city_jobs in cities.items():
            # 岗位密度 = 该城市岗位数 / 总岗位数（越高机会越多）
            density = len(city_jobs) / total_jobs

            # 薪资中位数
            salaries = [j.salary_median for j in city_jobs if j.salary_median]
            salary_med = safe_percentile(salaries, 50) or 0

            # 学历放宽度 = 1 - (要求本科及以上的比例)
            bach_plus = sum(1 for j in city_jobs if j.education in ("本科", "硕士", "博士"))
            edu_relax = 1 - (bach_plus / len(city_jobs)) if city_jobs else 0

            city_metrics[city] = {
                "density": density,
                "salary": salary_med,
                "edu_relax": edu_relax,
            }

        # 标准化各指标
        densities = [m["density"] for m in city_metrics.values()]
        salaries = [m["salary"] for m in city_metrics.values()]
        edu_relaxes = [m["edu_relax"] for m in city_metrics.values()]

        norm_density = normalize(densities)  # 高密度→低竞争（取反）
        norm_salary = normalize(salaries)    # 高薪资→高竞争
        norm_edu = normalize(edu_relaxes)    # 高放宽→高竞争

        w1 = self.weights["job_density"]
        w2 = self.weights["salary_level"]
        w3 = self.weights["education_relaxation"]

        result = {}
        for i, city in enumerate(city_metrics):
            # 岗位密度取反（机会多→竞争低）
            score = (1 - norm_density[i]) * w1 + norm_salary[i] * w2 + norm_edu[i] * w3
            result[city] = round(score * 100, 1)

        return result
