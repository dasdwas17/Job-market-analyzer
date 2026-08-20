"""Plotly HTML 看板生成器 — UI/UX Pro Max 规范"""
from datetime import UTC, datetime
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from job_market_analyzer.schema import StrategyReport

# ── 设计系统（UI/UX Pro Max: 数据分析看板配色）────────────
_BG = "#f8fafc"          # slate-50
_SURFACE = "#ffffff"
_BORDER = "#e2e8f0"      # slate-200
_TEXT = "#0f172a"        # slate-900
_TEXT_MUTED = "#64748b"  # slate-500
_BRAND = "#4f46e5"       # indigo-600
_BRAND_LIGHT = "#6366f1"
_ACCENT = "#0d9488"      # teal-600
_WARN = "#d97706"        # amber-600
_DANGER = "#dc2626"
_BRAND_SOFT = "#eef2ff"   # indigo-50

_CHART_PALETTE = ["#4f46e5", "#0d9488", "#d97706", "#dc2626", "#7c3aed"]

_FONT_STACK = (
    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', "
    "'PingFang SC', 'Microsoft YaHei', sans-serif"
)

# ── SVG 图标（no-emoji-icons 准则）────────────────────────
_ICON_CHART = (
    '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    'stroke-linejoin="round" aria-hidden="true">'
    '<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6"/>'
    '<rect x="12" y="8" width="3" height="10"/><rect x="17" y="5" width="3" height="13"/>'
    '</svg>'
)

_CSS_BASE = f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: {_FONT_STACK};
  background: {_BG};
  color: {_TEXT};
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  font-size: 16px;
}}
:focus-visible {{
  outline: 2px solid {_BRAND};
  outline-offset: 2px;
}}
"""

_CSS_INDEX = _CSS_BASE + f"""
.hero {{
  background: linear-gradient(135deg, {_BRAND} 0%, #7c3aed 100%);
  color: #fff;
  padding: 48px 24px 40px;
  text-align: center;
}}
.hero-icon {{
  display: inline-flex; margin-bottom: 12px; opacity: 0.9;
  width: 56px; height: 56px; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.15); border-radius: 16px;
}}
.hero h1 {{ font-size: 28px; font-weight: 700; letter-spacing: -0.02em; }}
.hero p {{ opacity: 0.85; font-size: 14px; margin-top: 6px; }}
.hero .badge {{
  display: inline-block; margin-bottom: 12px;
  padding: 4px 12px; border-radius: 999px;
  background: rgba(255,255,255,0.18); font-size: 12px; font-weight: 500;
  letter-spacing: 0.05em;
}}
.metrics {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px; max-width: 960px; margin: -28px auto 0; padding: 0 24px;
  position: relative; z-index: 1;
}}
.metric {{
  background: {_SURFACE}; border: 1px solid {_BORDER}; border-radius: 12px;
  padding: 20px 24px; position: relative; overflow: hidden;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.metric:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(15,23,42,0.08); }}
.metric::before {{
  content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
  background: {_BRAND};
}}
.metric.accent::before {{ background: {_ACCENT}; }}
.metric.warn::before {{ background: {_WARN}; }}
.metric.danger::before {{ background: {_DANGER}; }}
.metric-value {{ font-size: 32px; font-weight: 700; color: {_TEXT}; letter-spacing: -0.02em; line-height: 1.2; }}
.metric-value .unit {{ font-size: 15px; color: {_TEXT_MUTED}; font-weight: 500; margin-left: 4px; }}
.metric-label {{ font-size: 13px; color: {_TEXT_MUTED}; margin-top: 4px; }}
.nav {{
  display: flex; justify-content: center; gap: 8px;
  padding: 24px 24px 8px; flex-wrap: wrap;
}}
.nav-btn {{
  padding: 12px 24px; min-height: 44px; min-width: 44px;
  border: 1px solid {_BORDER}; border-radius: 999px;
  cursor: pointer; font-size: 14px; font-weight: 500; font-family: {_FONT_STACK};
  background: {_SURFACE}; color: {_TEXT_MUTED};
  transition: all 0.2s ease;
  display: inline-flex; align-items: center; justify-content: center;
}}
.nav-btn.active {{
  background: {_BRAND}; color: #fff; border-color: {_BRAND};
  box-shadow: 0 4px 12px rgba(79,70,229,0.25);
}}
.nav-btn:hover:not(.active) {{ border-color: {_BRAND_LIGHT}; color: {_BRAND}; }}
.content {{ max-width: 1200px; margin: 0 auto; padding: 0 24px 48px; }}
.content iframe {{
  width: 100%; min-height: 640px; border: 1px solid {_BORDER};
  border-radius: 12px; background: {_SURFACE}; display: none;
}}
.content iframe.active {{ display: block; }}
.iframe-skeleton {{
  display: none; min-height: 640px; border: 1px solid {_BORDER};
  border-radius: 12px; background: {_SURFACE}; position: relative; overflow: hidden;
}}
.iframe-skeleton.loading {{ display: block; }}
.iframe-skeleton::after {{
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent, {_BORDER} 50%, transparent);
  animation: shimmer 1.5s infinite;
}}
@keyframes shimmer {{ 0% {{ transform: translateX(-100%); }} 100% {{ transform: translateX(100%); }} }}
.footer {{
  text-align: center; padding: 24px; color: {_TEXT_MUTED}; font-size: 12px;
  border-top: 1px solid {_BORDER}; margin-top: 24px;
}}
@media (max-width: 640px) {{
  .hero {{ padding: 32px 16px 28px; }}
  .hero h1 {{ font-size: 22px; }}
  .metrics {{ grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 0 16px; }}
  .metric {{ padding: 16px; }}
  .metric-value {{ font-size: 26px; }}
  .nav {{ padding: 16px 12px 8px; gap: 6px; }}
  .nav-btn {{ padding: 10px 16px; font-size: 13px; }}
  .content {{ padding: 0 12px 32px; }}
}}
@media (prefers-reduced-motion: reduce) {{
  .metric, .nav-btn {{ transition: none; }}
  .iframe-skeleton::after {{ animation: none; }}
  html {{ scroll-behavior: auto; }}
}}
"""

_CSS_SUBPAGE = _CSS_BASE + f"""
.page-bar {{
  background: {_SURFACE}; border-bottom: 1px solid {_BORDER};
  padding: 16px 24px; position: sticky; top: 0; z-index: 10;
  display: flex; align-items: center; gap: 12px;
}}
.page-bar-icon {{
  width: 36px; height: 36px; border-radius: 8px; flex-shrink: 0;
  background: {_BRAND_SOFT}; display: inline-flex; align-items: center; justify-content: center;
}}
.page-bar h2 {{ font-size: 18px; font-weight: 600; color: {_TEXT}; }}
.page-bar p {{ font-size: 13px; color: {_TEXT_MUTED}; margin-top: 2px; }}
.chart-wrap {{ padding: 24px; }}
.footer {{
  text-align: center; padding: 16px; color: {_TEXT_MUTED}; font-size: 12px;
  border-top: 1px solid {_BORDER};
}}
@media (max-width: 640px) {{
  .page-bar {{ padding: 12px 16px; }}
  .chart-wrap {{ padding: 12px; }}
}}
"""

def _plotly_layout_config(title: str, height: int = 620, show_legend: bool = False) -> dict:
    """统一 Plotly 布局配置"""
    return {
        "title": {"text": f"<b>{title}</b>", "font": {"size": 16, "color": _TEXT}, "x": 0.02, "xanchor": "left"},
        "font": {"family": "Inter, sans-serif", "size": 13, "color": _TEXT},
        "paper_bgcolor": _SURFACE,
        "plot_bgcolor": _SURFACE,
        "margin": {"l": 50, "r": 30, "t": 60, "b": 50},
        "height": height,
        "showlegend": show_legend,
        "legend": {"orientation": "h", "y": -0.12, "font": {"size": 12, "color": _TEXT_MUTED}} if show_legend else {},
        "xaxis": {"gridcolor": _BORDER, "zerolinecolor": _BORDER, "linecolor": _BORDER},
        "yaxis": {"gridcolor": _BORDER, "zerolinecolor": _BORDER, "linecolor": _BORDER},
        "hoverlabel": {"bgcolor": _TEXT, "font": {"color": "#fff", "size": 13}},
        "hovermode": "closest",
        "colorway": _CHART_PALETTE,
    }


def _wrap_subpage(title: str, subtitle: str, chart_html: str, icon_svg: str = "") -> str:
    """将 Plotly 图表包裹在统一的 HTML 外壳中"""
    icon_html = f'<div class="page-bar-icon">{icon_svg}</div>' if icon_svg else ""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<title>{title}</title>
<style>{_CSS_SUBPAGE}</style>
</head>
<body>
<div class="page-bar">{icon_html}<div><h2>{title}</h2><p>{subtitle}</p></div></div>
<div class="chart-wrap">{chart_html}</div>
<div class="footer">Job Market Analyzer · 招聘市场分析报告</div>
</body>
</html>"""


# 子页面图标
_ICON_SALARY = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>'
    '</svg>'
)
_ICON_SKILL = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0d9488" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'
    '</svg>'
)
_ICON_COMPETITIVE = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d97706" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>'
    '</svg>'
)
_ICON_STRATEGY = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>'
    '</svg>'
)


class DashboardGenerator:
    """看板生成器 — UI/UX Pro Max 规范"""

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
        pages.append(("薪资分析", "薪资分布与分组统计", self._gen_salary_page(salary_result)))
        pages.append(("技能分析", "技能频率与薪资关联", self._gen_skill_page(skill_result)))
        pages.append(("竞争度", "城市竞争指数", self._gen_competitive_page(comp_result)))
        if strategy_report:
            pages.append(("求职策略", "岗位匹配与行动建议", self._gen_strategy_page(strategy_report)))
        return self._gen_index_page(pages, salary_result.get("summary", {}))

    def _gen_salary_page(self, result: dict) -> str:
        """生成薪资分析页面"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("薪资分布", "城市薪资中位数", "经验-薪资", "学历-薪资"),
        )
        dist = result.get("distribution", {})
        if dist:
            fig.add_trace(go.Bar(x=dist["labels"], y=dist["counts"], name="人数",
                                 marker_color=_CHART_PALETTE[0],
                                 hovertemplate="区间: %{x}<br>人数: %{y}<extra></extra>"), row=1, col=1)
        by_city = result.get("by_city", {})
        if by_city:
            cities = sorted(by_city.keys(), key=lambda c: -by_city[c]["median"])
            fig.add_trace(go.Bar(x=cities, y=[by_city[c]["median"] for c in cities],
                                 name="中位数K", marker_color=_CHART_PALETTE[1],
                                 hovertemplate="%{x}<br>中位: %{y}K<extra></extra>"), row=1, col=2)
        by_exp = result.get("by_experience", {})
        if by_exp:
            fig.add_trace(go.Bar(x=list(by_exp.keys()),
                                 y=[by_exp[e]["median"] for e in by_exp],
                                 name="中位数K", marker_color=_CHART_PALETTE[2],
                                 hovertemplate="%{x}<br>中位: %{y}K<extra></extra>"), row=2, col=1)
        by_edu = result.get("by_education", {})
        if by_edu:
            fig.add_trace(go.Bar(x=list(by_edu.keys()),
                                 y=[by_edu[e]["median"] for e in by_edu],
                                 name="中位数K", marker_color=_CHART_PALETTE[3],
                                 hovertemplate="%{x}<br>中位: %{y}K<extra></extra>"), row=2, col=2)
        fig.update_layout(**_plotly_layout_config("薪资分析", 720))
        chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
        filepath = str(self.output_dir / "salary.html")
        Path(filepath).write_text(
            _wrap_subpage("薪资分析", "薪资分布直方图 + 按城市/经验/学历分组中位数",
                          chart_html, _ICON_SALARY),
            encoding="utf-8")
        return filepath

    def _gen_skill_page(self, result: dict) -> str:
        """生成技能分析页面"""
        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=("高频技能 Top 15", "技能-薪资关联 Top 10"))
        freq = result.get("frequency", {})
        if freq:
            skills = list(freq.keys())[:15]
            values = [freq[s] * 100 for s in skills]
            fig.add_trace(go.Bar(x=values, y=skills, orientation="h", name="频率%",
                                 marker_color=_CHART_PALETTE[0],
                                 hovertemplate="%{y}<br>频率: %{x:.1f}%<extra></extra>"), row=1, col=1)
            fig.update_yaxes(autorange="reversed", row=1, col=1)
        corr = result.get("correlation", {})
        if corr:
            skills = list(corr.keys())[:10]
            with_sal = [corr[s]["with_skill"] for s in skills]
            without_sal = [corr[s]["without_skill"] or 0 for s in skills]
            fig.add_trace(go.Bar(x=skills, y=with_sal, name="有此技能",
                                 marker_color=_CHART_PALETTE[0],
                                 hovertemplate="%{x}<br>有: %{y}K<extra></extra>"), row=1, col=2)
            fig.add_trace(go.Bar(x=skills, y=without_sal, name="无此技能",
                                 marker_color=_CHART_PALETTE[1],
                                 hovertemplate="%{x}<br>无: %{y}K<extra></extra>"), row=1, col=2)
        layout = _plotly_layout_config("技能分析", 560, show_legend=True)
        layout["barmode"] = "group"
        fig.update_layout(**layout)
        chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
        filepath = str(self.output_dir / "skill.html")
        Path(filepath).write_text(
            _wrap_subpage("技能分析", "技能出现频率 + 有/无此技能的薪资中位数对比",
                          chart_html, _ICON_SKILL),
            encoding="utf-8")
        return filepath

    def _gen_competitive_page(self, result: dict) -> str:
        """生成竞争度分析页面"""
        fig = go.Figure()
        if result:
            cities = sorted(result.keys(), key=lambda c: -result[c])
            scores = [result[c] for c in cities]
            fig.add_trace(go.Bar(x=cities, y=scores, name="竞争指数",
                                 marker={"color": scores, "colorscale": "Tealgrn",
                                             "line": {"color": _BORDER, "width": 1}},
                                 hovertemplate="%{x}<br>指数: %{y:.1f}<extra></extra>"))
            fig.update_traces(texttemplate="%{y:.1f}", textposition="outside")
        layout = _plotly_layout_config("城市竞争指数", 520)
        layout["yaxis"] = {**layout["yaxis"], "title": "竞争指数 (0-100)"}
        fig.update_layout(**layout)
        chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
        filepath = str(self.output_dir / "competitive.html")
        Path(filepath).write_text(
            _wrap_subpage("城市竞争指数",
                          "指数越高竞争越激烈（加权：岗位密度取反 + 薪资 + 学历放宽）",
                          chart_html, _ICON_COMPETITIVE),
            encoding="utf-8")
        return filepath

    def _gen_strategy_page(self, report: StrategyReport) -> str:
        """生成求职策略页面"""
        fig = go.Figure()
        if report.matched_jobs:
            names = [f"#{j.rank} {j.company_name}" for j in report.matched_jobs]
            scores = [j.match_score for j in report.matched_jobs]
            fig.add_trace(go.Bar(x=scores, y=names, orientation="h", name="匹配度",
                                 marker_color=_CHART_PALETTE[0],
                                 text=[f"{s:.1f}" for s in scores], textposition="outside",
                                 hovertemplate="%{y}<br>匹配度: %{x:.1f}<extra></extra>"))
            fig.update_yaxes(autorange="reversed")
        layout = _plotly_layout_config("求职策略 — TOP5 匹配岗位", 460)
        layout["xaxis"] = {**layout["xaxis"], "range": [0, 100], "title": "匹配度 (0-100)"}
        fig.update_layout(**layout)
        chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

        # 行动建议 + 技能短板
        extras_html = ""
        if report.action_items:
            items = "".join(
                f'<li><span class="tag tag-{a.priority}">{a.priority}</span>'
                f'<span class="action-text">{a.action}</span>'
                f'<span class="reason">{a.reason}</span></li>'
                for a in report.action_items
            )
            extras_html += f"""
<div class="actions-section">
<h3>行动建议</h3>
<ul class="action-list">{items}</ul>
</div>"""

        if report.skill_gaps:
            gaps = "".join(
                f'<li><span class="gap-skill">{g.skill}</span>'
                f'<span class="gap-freq">频率 {g.frequency*100:.0f}%</span>'
                f'<span class="gap-impact">{g.impact}</span></li>'
                for g in report.skill_gaps
            )
            extras_html += f"""
<div class="actions-section">
<h3>技能短板</h3>
<ul class="action-list">{gaps}</ul>
</div>"""

        if extras_html:
            extras_html += f"""
<style>
.actions-section {{ margin-top: 32px; padding: 0 24px 24px; }}
.actions-section h3 {{ font-size: 16px; font-weight: 600; margin-bottom: 12px; color: {_TEXT}; }}
.action-list {{ list-style: none; }}
.action-list li {{
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  padding: 12px 16px; background: {_SURFACE};
  border: 1px solid {_BORDER}; border-radius: 8px; margin-bottom: 8px;
}}
.tag {{
  padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; flex-shrink: 0;
}}
.tag-高 {{ background: #fee2e2; color: {_DANGER}; }}
.tag-中 {{ background: #fef3c7; color: {_WARN}; }}
.tag-低 {{ background: #d1fae5; color: #059669; }}
.action-text {{ font-size: 14px; color: {_TEXT}; }}
.gap-skill {{ font-size: 14px; font-weight: 600; color: {_BRAND}; }}
.gap-freq {{ font-size: 12px; color: {_TEXT_MUTED}; }}
.gap-impact {{ font-size: 12px; color: {_TEXT_MUTED}; margin-left: auto; }}
.reason {{ font-size: 12px; color: {_TEXT_MUTED}; margin-left: auto; }}
</style>"""

        filepath = str(self.output_dir / "strategy.html")
        full_html = _wrap_subpage(
            "求职策略", "TOP5 匹配岗位匹配度 + 技能短板行动建议",
            chart_html, _ICON_STRATEGY
        )
        if extras_html:
            full_html = full_html.replace(
                '<div class="footer">',
                f'{extras_html}\n<div class="footer">'
            )
        Path(filepath).write_text(full_html, encoding="utf-8")
        return filepath

    def _gen_index_page(self, pages: list[tuple[str, str, str]], summary: dict) -> str:
        """生成汇总索引页"""
        timestamp = datetime.now(tz=UTC).astimezone().strftime("%Y-%m-%d %H:%M")

        median = summary.get("median")
        p25 = summary.get("p25")
        p75 = summary.get("p75")
        p90 = summary.get("p90")
        count = summary.get("count", 0)
        cards = [
            ("薪资中位数", f"{median:.1f}" if median else "N/A", "K", ""),
            ("P25 分位", f"{p25:.1f}" if p25 else "N/A", "K", "accent"),
            ("P75 分位", f"{p75:.1f}" if p75 else "N/A", "K", "accent"),
            ("P90 分位", f"{p90:.1f}" if p90 else "N/A", "K", "warn"),
            ("岗位总数", str(count), "条", "danger"),
        ]
        cards_html = "".join(
            f'<div class="metric {cls}">'
            f'<div class="metric-value">{val}<span class="unit">{unit}</span></div>'
            f'<div class="metric-label">{label}</div></div>'
            for label, val, unit, cls in cards
        )

        nav_html = "".join(
            f'<button class="nav-btn {"active" if i == 0 else ""}" '
            f'onclick="showTab({i})" aria-label="切换到{name}" '
            f'aria-pressed="{"true" if i == 0 else "false"}" '
            f'tabindex="0">{name}</button>'
            for i, (name, _, _) in enumerate(pages)
        )

        frames_html = "".join(
            f'<iframe id="frame-{i}" src="{Path(fp).name}" '
            f'class="{"active" if i == 0 else ""}" '
            f'loading="{"eager" if i == 0 else "lazy"}" '
            f'title="{name}页面" '
            f'aria-hidden="{"false" if i == 0 else "true"}"></iframe>'
            for i, (name, _, fp) in enumerate(pages)
        )

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="招聘市场数据分析报告 - 薪资/技能/竞争度/求职策略">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<title>招聘市场分析报告 | {timestamp}</title>
<style>{_CSS_INDEX}</style>
</head>
<body>
<div class="hero">
  <div class="hero-icon">{_ICON_CHART}</div>
  <span class="badge">JOB MARKET ANALYZER</span>
  <h1>招聘市场分析报告</h1>
  <p>生成时间：{timestamp} · 数据驱动决策</p>
</div>
<div class="metrics" role="region" aria-label="关键指标">{cards_html}</div>
<nav class="nav" role="tablist" aria-label="分析模块导航">{nav_html}</nav>
<main class="content">{frames_html}</main>
<footer class="footer">Job Market Analyzer · 开源招聘市场数据分析工具 · MIT License</footer>
<script>
function showTab(idx) {{
  document.querySelectorAll('.nav-btn').forEach((btn, i) => {{
    const active = i === idx;
    btn.classList.toggle('active', active);
    btn.setAttribute('aria-pressed', active);
  }});
  document.querySelectorAll('.content iframe').forEach((frame, i) => {{
    const active = i === idx;
    frame.classList.toggle('active', active);
    frame.setAttribute('aria-hidden', !active);
  }});
}}
// 键盘导航：左右箭头切换 Tab
document.addEventListener('keydown', (e) => {{
  if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
  const btns = [...document.querySelectorAll('.nav-btn')];
  const current = btns.findIndex(b => b.classList.contains('active'));
  if (current === -1) return;
  const next = e.key === 'ArrowLeft'
    ? (current - 1 + btns.length) % btns.length
    : (current + 1) % btns.length;
  btns[next].focus();
  showTab(next);
}});
</script>
</body>
</html>"""
        filepath = str(self.output_dir / "index.html")
        Path(filepath).write_text(html, encoding="utf-8")
        return filepath
