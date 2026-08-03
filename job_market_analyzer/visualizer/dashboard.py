"""Plotly HTML 看板生成器"""
from datetime import UTC, datetime
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from job_market_analyzer.schema import StrategyReport


class DashboardGenerator:
    """看板生成器"""

    def __init__(self, theme: str = "plotly_white", color_scale: str = "Viridis",
                 chart_width: int = 1200, output_dir: str = "output/reports"):
        self.theme = theme
        self.color_scale = color_scale
        self.chart_width = chart_width
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self, salary_result: dict, skill_result: dict,
                     comp_result: dict, strategy_report: StrategyReport | None = None) -> str:
        """生成所有图表 + 汇总索引页，返回 index.html 路径"""
        pages = []
        pages.append(("薪资分析", self._gen_salary_page(salary_result)))
        pages.append(("技能分析", self._gen_skill_page(skill_result)))
        pages.append(("竞争度分析", self._gen_competitive_page(comp_result)))
        if strategy_report:
            pages.append(("求职策略", self._gen_strategy_page(strategy_report)))

        return self._gen_index_page(pages, salary_result.get("summary", {}))

    def _gen_salary_page(self, result: dict) -> str:
        """生成薪资分析页面"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("薪资分布", "城市薪资对比", "经验-薪资", "学历-薪资"),
        )

        # 薪资分布柱状图
        dist = result.get("distribution", {})
        if dist:
            fig.add_trace(go.Bar(x=dist["labels"], y=dist["counts"], name="人数"),
                          row=1, col=1)

        # 城市薪资
        by_city = result.get("by_city", {})
        if by_city:
            cities = list(by_city.keys())
            medians = [by_city[c]["median"] for c in cities]
            fig.add_trace(go.Bar(x=cities, y=medians, name="中位数(K)"),
                          row=1, col=2)

        # 经验-薪资
        by_exp = result.get("by_experience", {})
        if by_exp:
            exps = list(by_exp.keys())
            exp_medians = [by_exp[e]["median"] for e in exps]
            fig.add_trace(go.Bar(x=exps, y=exp_medians, name="中位数(K)"),
                          row=2, col=1)

        # 学历-薪资
        by_edu = result.get("by_education", {})
        if by_edu:
            edus = list(by_edu.keys())
            edu_medians = [by_edu[e]["median"] for e in edus]
            fig.add_trace(go.Bar(x=edus, y=edu_medians, name="中位数(K)"),
                          row=2, col=2)

        fig.update_layout(template=self.theme, width=self.chart_width,
                          title_text="薪资分析", showlegend=False)
        filepath = str(self.output_dir / "salary.html")
        fig.write_html(filepath)
        return filepath

    def _gen_skill_page(self, result: dict) -> str:
        """生成技能分析页面"""
        fig = make_subplots(rows=1, cols=2, subplot_titles=("高频技能", "技能-薪资关联"))

        # 高频技能
        freq = result.get("frequency", {})
        if freq:
            skills = list(freq.keys())[:15]
            values = [freq[s] for s in skills]
            fig.add_trace(go.Bar(x=values, y=skills, orientation="h", name="频率"),
                          row=1, col=1)

        # 技能-薪资
        corr = result.get("correlation", {})
        if corr:
            skills = list(corr.keys())[:10]
            with_sal = [corr[s]["with_skill"] for s in skills]
            without_sal = [corr[s]["without_skill"] or 0 for s in skills]
            fig.add_trace(go.Bar(x=skills, y=with_sal, name="有此技能"), row=1, col=2)
            fig.add_trace(go.Bar(x=skills, y=without_sal, name="无此技能"), row=1, col=2)

        fig.update_layout(template=self.theme, width=self.chart_width,
                          title_text="技能分析", barmode="group")
        filepath = str(self.output_dir / "skill.html")
        fig.write_html(filepath)
        return filepath

    def _gen_competitive_page(self, result: dict) -> str:
        """生成竞争度分析页面"""
        fig = go.Figure()
        if result:
            cities = list(result.keys())
            scores = [result[c] for c in cities]
            fig.add_trace(go.Bar(x=cities, y=scores, name="竞争指数",
                                 marker_color=scores, marker_colorscale=self.color_scale))
        fig.update_layout(template=self.theme, width=self.chart_width,
                          title_text="城市竞争指数 (越高竞争越激烈)",
                          yaxis_title="竞争指数 (0-100)")
        filepath = str(self.output_dir / "competitive.html")
        fig.write_html(filepath)
        return filepath

    def _gen_strategy_page(self, report: StrategyReport) -> str:
        """生成求职策略页面"""
        fig = go.Figure()
        # TOP5 匹配度
        if report.matched_jobs:
            names = [f"#{j.rank} {j.company_name}" for j in report.matched_jobs]
            scores = [j.match_score for j in report.matched_jobs]
            fig.add_trace(go.Bar(x=scores, y=names, orientation="h", name="匹配度"))
        fig.update_layout(template=self.theme, width=self.chart_width,
                          title_text="求职策略 — TOP5 匹配岗位",
                          xaxis_title="匹配度 (0-100)")
        filepath = str(self.output_dir / "strategy.html")
        fig.write_html(filepath)
        return filepath

    def _gen_index_page(self, pages: list[tuple[str, str]], summary: dict) -> str:
        """生成汇总索引页"""
        timestamp = datetime.now(tz=UTC).astimezone().strftime("%Y-%m-%d %H:%M")

        # 关键指标卡片
        cards_html = ""
        median = summary.get("median")
        p25 = summary.get("p25")
        p75 = summary.get("p75")
        count = summary.get("count", 0)
        for label, value, unit in [
            ("薪资中位数", f"{median:.1f}" if median else "N/A", "K"),
            ("25分位", f"{p25:.1f}" if p25 else "N/A", "K"),
            ("75分位", f"{p75:.1f}" if p75 else "N/A", "K"),
            ("岗位总数", str(count), "条"),
        ]:
            cards_html += f'<div class="card"><div class="card-value">{value}<span class="unit">{unit}</span></div><div class="card-label">{label}</div></div>'

        # Tab 按钮
        tabs_html = ""
        for i, (name, _) in enumerate(pages):
            active = "active" if i == 0 else ""
            tabs_html += f'<button class="tab-btn {active}" onclick="showTab({i})">{name}</button>'

        # iframe 区域
        frames_html = ""
        for i, (_, filepath) in enumerate(pages):
            display = "block" if i == 0 else "none"
            filename = Path(filepath).name
            frames_html += f'<iframe id="frame-{i}" src="{filename}" style="display:{display};width:100%;height:600px;border:none;"></iframe>'

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>招聘市场分析报告 | {timestamp}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f5f5; }}
.header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
.header h1 {{ font-size: 28px; margin-bottom: 8px; }}
.header p {{ opacity: 0.9; }}
.cards {{ display: flex; justify-content: center; gap: 20px; padding: 20px; flex-wrap: wrap; }}
.card {{ background: white; border-radius: 12px; padding: 20px 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; min-width: 150px; }}
.card-value {{ font-size: 32px; font-weight: 700; color: #333; }}
.card-value .unit {{ font-size: 16px; color: #888; margin-left: 4px; }}
.card-label {{ font-size: 14px; color: #666; margin-top: 4px; }}
.tabs {{ display: flex; justify-content: center; gap: 10px; padding: 10px; }}
.tab-btn {{ padding: 10px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; background: #ddd; transition: all 0.2s; }}
.tab-btn.active {{ background: #667eea; color: white; }}
.tab-btn:hover {{ opacity: 0.85; }}
.content {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
</style>
</head>
<body>
<div class="header">
<h1>📊 招聘市场分析报告</h1>
<p>生成时间：{timestamp}</p>
</div>
<div class="cards">{cards_html}</div>
<div class="tabs">{tabs_html}</div>
<div class="content">{frames_html}</div>
<script>
function showTab(idx) {{
document.querySelectorAll('.tab-btn').forEach((btn, i) => {{
btn.classList.toggle('active', i === idx);
}});
document.querySelectorAll('iframe').forEach((frame, i) => {{
frame.style.display = i === idx ? 'block' : 'none';
}});
}}
</script>
</body>
</html>"""
        filepath = str(self.output_dir / "index.html")
        Path(filepath).write_text(html, encoding="utf-8")
        return filepath
