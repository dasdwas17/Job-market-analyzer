"""job_market_analyzer 一键运行入口"""
import argparse

from job_market_analyzer.analyzer.competitive_analyzer import CompetitiveAnalyzer
from job_market_analyzer.analyzer.salary_analyzer import SalaryAnalyzer
from job_market_analyzer.analyzer.skill_analyzer import SkillAnalyzer
from job_market_analyzer.analyzer.strategy_advisor import StrategyAdvisor
from job_market_analyzer.config import Config
from job_market_analyzer.io.demo_adapter import DemoAdapter
from job_market_analyzer.io.importer import import_csv, import_sqlite
from job_market_analyzer.schema import JobItem, UserProfile
from job_market_analyzer.visualizer.dashboard import DashboardGenerator


def load_data(cfg: Config) -> list[JobItem]:
    """根据配置加载数据"""
    source = cfg.data["source"]
    if source == "demo":
        print("→ 使用 DemoAdapter 生成模拟数据 (500条)")
        return DemoAdapter().fetch_jobs(n_samples=500)
    elif source == "csv":
        path = cfg.data["csv_path"]
        print(f"→ 从 CSV 导入: {path}")
        return import_csv(path)
    elif source == "sqlite":
        path = cfg.data["sqlite_path"]
        print(f"→ 从 SQLite 导入: {path}")
        return import_sqlite(path)
    else:
        print(f"⚠ 未知数据源: {source}，回退到 demo")
        return DemoAdapter().fetch_jobs(n_samples=500)


def interactive_profile() -> UserProfile:
    """交互式输入用户画像"""
    print("\n🔍 求职策略分析需要你的个人画像，请回答以下问题：\n")
    skills = input("1. 你的技能（逗号分隔）: ").strip()
    experience = input("2. 工作经验: ").strip()
    education = input("3. 最高学历: ").strip()
    city = input("4. 目标城市: ").strip()
    salary = input("5. 期望薪资范围: ").strip()

    return UserProfile(
        user_skills=[s.strip() for s in skills.split(",") if s.strip()],
        user_experience=experience,
        user_education=education,
        target_city=city,
        target_salary=salary,
    )


def main():
    parser = argparse.ArgumentParser(description="招聘市场数据分析工具")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--source", default=None, choices=["demo", "csv", "sqlite"], help="数据来源")
    parser.add_argument("--csv-path", default=None, help="CSV 文件路径")
    parser.add_argument("--interactive", action="store_true", help="交互式输入用户画像")
    parser.add_argument("--skills", default=None, help="你的技能（逗号分隔）")
    parser.add_argument("--city", default=None, help="目标城市")
    parser.add_argument("--experience", default=None, help="工作经验")
    parser.add_argument("--salary", default=None, help="期望薪资范围")
    args = parser.parse_args()

    # 加载配置
    cfg = Config.load(
        config_path=args.config,
        source=args.source,
        csv_path=args.csv_path,
        target_city=args.city,
        target_salary=args.salary,
    )

    # 加载数据
    jobs = load_data(cfg)
    print(f"✓ 已加载 {len(jobs)} 条岗位数据\n")

    # 运行分析
    print("→ 正在运行薪资分析...")
    salary_analyzer = SalaryAnalyzer(jobs)
    salary_result = {
        "distribution": salary_analyzer.distribution(cfg.analysis["salary"]["bins"]),
        "by_city": salary_analyzer.by_city(),
        "by_experience": salary_analyzer.by_experience(),
        "by_education": salary_analyzer.by_education(),
        "summary": salary_analyzer.summary(),
    }
    print("✓ 薪资分析完成")

    print("→ 正在运行技能分析...")
    skill_analyzer = SkillAnalyzer(jobs)
    skill_result = {
        "frequency": skill_analyzer.frequency(cfg.analysis["skill"]["min_frequency"]),
        "correlation": skill_analyzer.salary_correlation(),
        "top_n": skill_analyzer.top_n(cfg.analysis["skill"]["top_n"]),
    }
    print("✓ 技能分析完成")

    print("→ 正在运行竞争度分析...")
    comp_analyzer = CompetitiveAnalyzer(jobs, cfg.analysis["competitive"]["weights"])
    comp_result = comp_analyzer.city_index()
    print("✓ 竞争度分析完成")

    # 用户画像
    if args.interactive:
        profile = interactive_profile()
    else:
        resume_cfg = cfg.resume
        profile = UserProfile(
            user_skills=resume_cfg.get("user_skills", []),
            user_experience=resume_cfg.get("user_experience", ""),
            user_education=resume_cfg.get("user_education", ""),
            target_city=resume_cfg.get("target_city", ""),
            target_salary=resume_cfg.get("target_salary", ""),
        )

    if args.skills:
        profile.user_skills = [s.strip() for s in args.skills.split(",")]
    if args.experience:
        profile.user_experience = args.experience

    strategy_report = None
    if not profile.is_empty():
        print("→ 正在运行求职策略分析...")
        advisor = StrategyAdvisor(profile)
        strategy_report = advisor.generate(jobs)
        print("✓ 求职策略分析完成")
    else:
        print("⚠ 求职策略/简历诊断已跳过（未配置个人画像）")
        print("  → 运行 python scripts/run_analysis.py --interactive 配置画像")
        print("  → 或在 config.yaml 中填写 resume 字段")

    # 生成看板
    print("\n→ 正在生成可视化看板...")
    dashboard = DashboardGenerator(
        theme=cfg.visualization["theme"],
        color_scale=cfg.visualization["color_scale"],
        chart_width=cfg.visualization["chart_width"],
        output_dir=cfg.visualization["output_dir"],
    )
    index_path = dashboard.generate_all(salary_result, skill_result, comp_result, strategy_report)
    print(f"\n{'='*50}")
    print(f"✓ 报告已生成: {index_path}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
