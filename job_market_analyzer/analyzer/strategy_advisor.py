"""求职策略推荐模块"""
from job_market_analyzer.analyzer.resume_matcher import ResumeMatcher
from job_market_analyzer.analyzer.skill_analyzer import SkillAnalyzer
from job_market_analyzer.schema import (
    ActionItem,
    JobItem,
    JobMatch,
    SkillGap,
    StrategyReport,
    UserProfile,
)


class StrategyAdvisor:
    """求职策略顾问"""

    def __init__(self, profile: UserProfile):
        self.profile = profile
        self.matcher = ResumeMatcher(profile)

    def generate(self, jobs: list[JobItem]) -> StrategyReport:
        """生成求职策略报告"""
        # 1. 计算匹配度并排序
        scores = self.matcher.match_all(jobs)
        sorted_jobs = sorted(jobs, key=lambda j: scores.get(j.job_id, 0), reverse=True)

        # 2. TOP 5 匹配岗位
        top5 = []
        for rank, job in enumerate(sorted_jobs[:5], 1):
            matched, missing = self.matcher.skill_match(job.skill_tags)
            top5.append(JobMatch(
                rank=rank,
                job_name=job.job_name,
                company_name=job.company_name,
                salary_range=f"{job.salary_min}-{job.salary_max}K" if job.salary_min else "面议",
                match_score=scores.get(job.job_id, 0),
                required_skills=job.skill_tags,
                matched_skills=matched,
                missing_skills=missing,
            ))

        # 3. 短板诊断
        skill_freq = SkillAnalyzer(jobs).frequency(min_freq=0.0)
        all_missing = set()
        for job in sorted_jobs[:20]:  # 取前20个岗位的缺失技能
            _, missing = self.matcher.skill_match(job.skill_tags)
            all_missing.update(missing)

        skill_gaps = []
        for skill in all_missing:
            freq = skill_freq.get(skill, 0)
            if freq > 0:
                impact_pct = round(freq * 100)
                skill_gaps.append(SkillGap(
                    skill=skill,
                    impact=f"投递命中率可能下降{impact_pct}%",
                    frequency=round(freq, 2),
                ))
        skill_gaps.sort(key=lambda x: x.frequency, reverse=True)

        # 4. 行动建议
        action_items = []
        for gap in skill_gaps[:3]:
            priority = "高" if gap.frequency > 0.3 else "中" if gap.frequency > 0.1 else "低"
            action_items.append(ActionItem(
                priority=priority,
                action=f"建议补充{gap.skill}相关实战经验",
                reason=f"{gap.skill}在岗位中出现频率{gap.frequency*100:.0f}%，缺失将影响投递范围",
            ))

        return StrategyReport(
            matched_jobs=top5,
            skill_gaps=skill_gaps,
            action_items=action_items,
        )
