"""数据模型定义"""
from pydantic import BaseModel, Field, model_validator

from job_market_analyzer.utils.salary_parser import parse_salary_string


class JobItem(BaseModel):
    """岗位数据标准格式"""
    job_id: str
    job_name: str
    company_name: str
    company_size: str = ""
    industry: str = ""
    city: str
    district: str = ""
    salary_raw: str = ""
    salary_min: float | None = None
    salary_max: float | None = None
    salary_median: float | None = None
    salary_months: int | None = None
    experience: str = ""
    education: str = ""
    skill_tags: list[str] = Field(default_factory=list)
    job_description: str = ""
    job_url: str = ""
    crawl_time: str = ""

    @model_validator(mode='after')
    def auto_parse_salary(self):
        """如果传入了 salary_raw 但 min/max/median 为空，自动解析"""
        if self.salary_raw and self.salary_min is None:
            parsed = parse_salary_string(self.salary_raw)
            if parsed:
                self.salary_min = parsed.min
                self.salary_max = parsed.max
                self.salary_median = parsed.median
                self.salary_months = parsed.months
        # 兜底：如果 median 为空但 min/max 有值，取平均
        if self.salary_min and self.salary_max and self.salary_median is None:
            self.salary_median = (self.salary_min + self.salary_max) / 2
        return self


class JobMatch(BaseModel):
    """匹配岗位"""
    rank: int
    job_name: str
    company_name: str
    salary_range: str
    match_score: float
    required_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]


class SkillGap(BaseModel):
    """技能短板"""
    skill: str
    impact: str
    frequency: float


class ActionItem(BaseModel):
    """行动建议"""
    priority: str
    action: str
    reason: str


class StrategyReport(BaseModel):
    """求职策略报告"""
    matched_jobs: list[JobMatch]
    skill_gaps: list[SkillGap]
    action_items: list[ActionItem]


class UserProfile(BaseModel):
    """用户画像"""
    user_skills: list[str] = Field(default_factory=list)
    user_experience: str = ""
    user_education: str = ""
    target_city: str = ""
    target_salary: str = ""

    def is_empty(self) -> bool:
        """检查画像是否为空"""
        return not self.user_skills and not self.target_city
