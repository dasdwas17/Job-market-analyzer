"""模拟数据生成器 — 生成符合真实招聘市场统计规律的演示数据"""
import hashlib
import random

import numpy as np

from job_market_analyzer.io.base_adapter import BaseAdapter
from job_market_analyzer.schema import JobItem

# 城市权重 + 薪资系数
_CITIES = {
    "北京": (0.20, 1.30), "上海": (0.20, 1.28), "深圳": (0.15, 1.25),
    "杭州": (0.15, 1.15), "成都": (0.05, 1.00), "武汉": (0.04, 0.90),
    "南京": (0.04, 0.95), "广州": (0.05, 1.10), "苏州": (0.03, 1.05),
    "西安": (0.03, 0.85), "长沙": (0.03, 0.88), "重庆": (0.03, 0.90),
}

_EDUCATION = [
    ("本科", 0.55), ("硕士", 0.25), ("大专", 0.15), ("博士", 0.05),
]

_EXPERIENCE = [
    ("3-5年", 0.40), ("1-3年", 0.30), ("5-10年", 0.20),
    ("经验不限", 0.05), ("在校/应届", 0.05),
]

_COMPANY_SIZES = [
    ("100-499人", 0.30), ("1000-9999人", 0.40), ("10000人以上", 0.20), ("20-99人", 0.10),
]

# 技能池：高频 / 中频 / 高薪附加
_HIGH_FREQ_SKILLS = ["Python", "SQL", "Excel"]
_MID_FREQ_SKILLS = ["Spark", "Hadoop", "Tableau", "Pandas", "机器学习"]
_BONUS_SKILLS = ["深度学习", "NLP", "计算机视觉", "TensorFlow", "PyTorch"]

# 公司名模板
_COMPANY_PREFIXES = ["数智", "云图", "创元", "汇科", "智联", "芯动", "数维", "聚源"]
_COMPANY_SUFFIXES = ["科技", "数据", "信息", "网络", "智能", "云服"]


class DemoAdapter(BaseAdapter):
    """生成符合真实招聘市场分布的模拟数据"""

    MAX_GENERATE_RATIO = 5

    def __init__(self, seed: int | None = None):
        """seed: 随机种子，传入则结果可复现（测试用）"""
        self.seed = seed

    def fetch_jobs(
        self,
        n_samples: int = 500,
        city: str | None = None,
        job_keyword: str | None = None,
        education: str | None = None,
        experience: str | None = None,
    ) -> list[JobItem]:
        if self.seed is not None:
            random.seed(self.seed)
            np.random.seed(self.seed)
        collected: list[JobItem] = []
        max_total = n_samples * self.MAX_GENERATE_RATIO
        batch_size = max(n_samples * 2, 200)

        while len(collected) < n_samples:
            remaining = min(batch_size, max_total - len(collected))
            if remaining <= 0:
                break
            batch = self._generate_batch(remaining)
            batch = self._apply_filters(batch, city, job_keyword, education, experience)
            collected.extend(batch)

        return collected[:n_samples]

    def _generate_batch(self, n: int) -> list[JobItem]:
        jobs = []
        for _ in range(n):
            jobs.append(self._generate_one())
        return jobs

    def _generate_one(self) -> JobItem:
        # 城市（直接 random.choices 返回完整 tuple，避免 _weighted_choice 返回类型歧义）
        city_items = list(_CITIES.items())
        city_weights = [c[1][0] for c in city_items]
        city_name, (_weight, city_coef) = random.choices(city_items, weights=city_weights, k=1)[0]

        # 薪资：对数正态分布
        base_salary = float(np.random.lognormal(mean=2.9, sigma=0.35))  # 中位数约18K
        base_salary = max(5, min(base_salary, 80))
        sal_min = round(base_salary * 0.8 * city_coef, 1)  # type: ignore
        sal_max = round(base_salary * 1.2 * city_coef, 1)  # type: ignore
        sal_median = round((sal_min + sal_max) / 2, 1)
        months = random.choice([12, 12, 12, 13, 14, 14, 15, 16])

        # 学历
        edu = self._weighted_choice(_EDUCATION)

        # 经验
        exp = self._weighted_choice(_EXPERIENCE)

        # 公司
        comp_name = random.choice(_COMPANY_PREFIXES) + random.choice(_COMPANY_SUFFIXES) + "有限公司"
        comp_size = self._weighted_choice(_COMPANY_SIZES)

        # 技能
        skills = list(_HIGH_FREQ_SKILLS)  # 高频必选部分
        if random.random() < 0.6:
            skills.append(random.choice(_MID_FREQ_SKILLS))
        if random.random() < 0.3:
            skills.append(random.choice(_MID_FREQ_SKILLS))
        # 高薪附加
        if sal_median > 30:
            skills.append(random.choice(_BONUS_SKILLS))
        random.shuffle(skills)
        skills = skills[:random.randint(3, 6)]

        # 岗位描述
        desc = self._generate_description(skills, exp, edu, city_name)

        # job_id
        raw_id = f"{city_name}_{comp_name}_{sal_median}_{random.random()}"
        job_id = hashlib.md5(raw_id.encode()).hexdigest()[:12]

        return JobItem(
            job_id=job_id,
            job_name="数据分析师",
            company_name=comp_name,
            company_size=comp_size,  # type: ignore
            industry=random.choice(["互联网", "金融科技", "电子商务", "人工智能", "企业服务"]),
            city=city_name,  # type: ignore
            salary_min=sal_min,
            salary_max=sal_max,
            salary_median=sal_median,
            salary_months=months,
            experience=exp,  # type: ignore
            education=edu,  # type: ignore
            skill_tags=skills,
            job_description=desc,
            crawl_time="2026-08-01",
        )

    def _generate_description(self, skills: list[str], exp: str, edu: str, city: str) -> str:
        """生成岗位描述"""
        skill_text = "、".join(skills)
        return (
            f"岗位职责：\n1. 负责业务数据分析，为决策提供数据支持；\n"
            f"2. 使用 {skill_text} 等工具进行数据建模和可视化；\n"
            f"3. 搭建数据指标体系，监控业务核心指标。\n\n"
            f"任职要求：\n1. {edu}及以上学历，{exp}相关工作经验；\n"
            f"2. 熟练掌握 {skill_text}；\n"
            f"3. 具备良好的业务理解能力和沟通能力。"
        )

    def _apply_filters(
        self,
        jobs: list[JobItem],
        city: str | None,
        job_keyword: str | None,
        education: str | None,
        experience: str | None,
    ) -> list[JobItem]:
        result = jobs
        if city:
            result = [j for j in result if j.city == city]
        if job_keyword:
            result = [j for j in result if job_keyword in j.job_name]
        if education:
            result = [j for j in result if j.education == education]
        if experience:
            result = [j for j in result if j.experience == experience]
        return result

    @staticmethod
    def _weighted_choice(items: list, weight_fn=None):
        """加权随机选择"""
        if weight_fn:
            weights = [weight_fn(item) for item in items]
        else:
            weights = [item[1] for item in items]
        chosen = random.choices(items, weights=weights, k=1)[0]
        return chosen[0] if isinstance(chosen, tuple) else chosen
