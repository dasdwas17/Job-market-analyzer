"""简历-岗位匹配模块"""
from job_market_analyzer.schema import JobItem, UserProfile
from job_market_analyzer.utils.text_processor import compute_tfidf_similarity


class ResumeMatcher:
    """简历匹配器"""

    def __init__(self, profile: UserProfile):
        self.profile = profile

    def match_all(self, jobs: list[JobItem]) -> dict[str, float]:
        """批量计算匹配度，返回 {job_id: score}"""
        scores = {}
        for job in jobs:
            scores[job.job_id] = self.match_one(job)
        return scores

    def match_one(self, job: JobItem) -> float:
        """计算单个岗位匹配度 (0-100)"""
        scores = []

        # 1. 技能匹配 (权重50%)
        if self.profile.user_skills and job.skill_tags:
            matched, _ = self.skill_match(job.skill_tags)
            skill_score = len(matched) / len(job.skill_tags) if job.skill_tags else 0
            scores.append(skill_score * 50)
        else:
            scores.append(0)

        # 2. TF-IDF 文本相似度 (权重30%)
        if self.profile.user_skills and job.job_description:
            resume_text = " ".join(self.profile.user_skills)
            sim = compute_tfidf_similarity(resume_text, job.job_description)
            scores.append(sim * 30)
        else:
            scores.append(0)

        # 3. 经验匹配 (权重10%)
        if self.profile.user_experience and job.experience:
            exp_score = 1.0 if self.profile.user_experience == job.experience else 0.5
            scores.append(exp_score * 10)
        else:
            scores.append(5)  # 无信息给中位分

        # 4. 学历匹配 (权重10%)
        if self.profile.user_education and job.education:
            edu_score = 1.0 if self.profile.user_education == job.education else 0.5
            scores.append(edu_score * 10)
        else:
            scores.append(5)

        return round(sum(scores), 1)

    def skill_match(self, required_skills: list[str]) -> tuple[list[str], list[str]]:
        """返回 (已匹配技能, 缺失技能)"""
        user_set = {s.lower() for s in self.profile.user_skills}
        matched = [s for s in required_skills if s.lower() in user_set]
        missing = [s for s in required_skills if s.lower() not in user_set]
        return matched, missing
