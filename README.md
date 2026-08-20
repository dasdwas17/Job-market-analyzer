# Job Market Analyzer

> 招聘市场数据分析工具 —— 不爬数据，只做分析。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![CI](https://github.com/dasdwas17/job-market-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/dasdwas17/job-market-analyzer/actions/workflows/ci.yml)

## 解决什么问题

求职者面对分散的招聘信息时，很难快速判断：
- 某个岗位/城市的薪资水平到底处于什么分位？
- 哪些技能真正与高薪相关，哪些只是高频但低溢价？
- 不同城市的竞争激烈程度如何量化对比？
- 自己的技能组合投递哪些岗位命中率最高？还差什么？

Job Market Analyzer 把"招聘数据 → 可读报告"这一段标准化：你提供岗位数据（CSV/JSON/SQLite 或自定义 Adapter），工具输出一份交互式 HTML 看板，覆盖薪资、技能、竞争度、求职策略四个维度。

> ⚠️ 本项目不含爬虫。数据获取由用户通过 `BaseAdapter` 接口自行实现，请阅读 [免责声明](DISCLAIMER.md)。

## 主要功能

| 模块 | 输出内容 |
|------|----------|
| 薪资分析 | 薪资分布直方图、按城市/经验/学历分组的中位数对比、总体分位数（p25/p50/p75/p90） |
| 技能分析 | 高频技能 Top N、技能-薪资关联（有此技能 vs 无此技能的中位数差异） |
| 竞争度分析 | 城市竞争指数（0-100，加权公式：岗位密度 + 薪资水平 + 学历放宽度，权重可配置） |
| 求职策略 | TOP5 匹配岗位、技能短板诊断（缺失技能 × 市场频率）、分优先级的行动建议 |

## 安装

**前置要求**：Python 3.11+

```bash
# 克隆仓库
git clone https://github.com/dasdwas17/job-market-analyzer.git
cd job-market-analyzer

# 安装（含开发依赖）
pip install -e ".[dev]"
```

依赖：pydantic、pyyaml、pandas、numpy、plotly、scikit-learn（开发额外含 pytest、ruff）。

## 使用方法

### 1. 零配置启动（模拟数据）

内置 `DemoAdapter` 生成 500 条合成岗位数据，无需任何输入即可体验：

```bash
python scripts/run_analysis.py
```

生成 3 模块报告（薪资/技能/竞争度），不含求职策略（未提供个人画像时自动跳过）。

### 2. 交互式生成完整报告

```bash
python scripts/run_analysis.py --interactive
```

按提示输入技能、经验、学历、目标城市、期望薪资，生成 5 模块完整报告（含求职策略）。

### 3. 接入自有数据 + CLI 指定画像

```bash
python scripts/run_analysis.py \
  --source csv \
  --csv-path data/sample/jobs.csv \
  --skills "Python,SQL" \
  --city "成都" \
  --experience "3-5年" \
  --salary "18-25K"
```

数据源支持 `demo` / `csv` / `sqlite`，配置也可写入 `config.yaml`（优先级：CLI > yaml > 默认值）。

## 输入输出示例

### 输入：CSV 数据格式

CSV 表头需与 `JobItem` 字段对应，未知字段会被忽略。最小可用列：

```csv
job_id,job_name,company_name,city,salary_raw,experience,education,skill_tags
j001,数据分析师,某科技公司,成都,15-25K·14薪,3-5年,本科,"Python,SQL,Excel"
j002,算法工程师,某AI公司,北京,25-40K,1-3年,硕士,"Python,PyTorch,SQL"
```

`salary_raw` 支持的格式：`15-25K`、`15-25K·14薪`、`20K`、`15-25k`（大小写不敏感）；`面议`/空值会被解析为 None。

### 输入：交互式画像

```
1. 你的技能（逗号分隔）: Python,SQL,Excel
2. 工作经验: 3-5年
3. 最高学历: 本科
4. 目标城市: 成都
5. 期望薪资范围: 18-25K
```

### 输出：HTML 看板

运行成功后在 `output/reports/` 生成：

```
output/reports/
├── index.html        # 汇总索引页（指标卡片 + Tab 切换）
├── salary.html       # 薪资分析（分布/城市/经验/学历 4 子图）
├── skill.html        # 技能分析（高频技能 + 技能-薪资关联）
├── competitive.html  # 城市竞争指数柱状图
└── strategy.html     # TOP5 匹配岗位 + 匹配度（仅交互/配置画像时生成）
```

用浏览器打开 `index.html` 即可查看完整看板。首页展示薪资中位数/p25/p75/岗位总数卡片，通过 Tab 切换各模块子页。

## 接入自己的数据

继承 `BaseAdapter` 实现 `fetch_jobs()`，参考 [base_adapter.py](job_market_analyzer/io/base_adapter.py) 源码。

## 开发

```bash
pip install -e ".[dev]"
ruff check .
pytest tests/ -v
```

贡献指南见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

MIT — 见 [LICENSE](LICENSE)。

## 版本历史 / Release Notes

### v0.2.0 — Dashboard UI/UX Pro Max Enhancements

**发布日期**：2026-08-20
**Tag**：`v0.2.0` (commit `c40dfd3`)

#### 🎨 What's New

Dashboard 视觉与交互全面升级，基于 UI/UX Pro Max 设计规范。

#### ✨ Highlights

- **可访问性**：focus-visible 状态、aria-labels、语义化 HTML5 标签
- **触摸优化**：导航按钮满足 44px 最小目标尺寸
- **键盘导航**：左右箭头键切换 Tab 模块
- **响应式**：移动端优先断点、`prefers-reduced-motion` 媒体查询
- **性能**：iframe 懒加载、骨架屏 shimmer 动画
- **视觉打磨**：SVG 图标、设计令牌精修、间距规范统一

#### 📦 Changes

- 1 file changed, 435 insertions(+), 112 deletions(-)
- 修改文件：`job_market_analyzer/visualizer/dashboard.py`
- **Full Changelog**: v0.1.0...v0.2.0

---

### v0.1.0 — Initial Release

**Tag**：`v0.1.0`

首个正式版本，包含完整的核心分析能力。

---

## 当前功能清单（v0.2.0）

| 模块 | 功能 | 输出 |
|------|------|------|
| 数据导入 | CSV / JSON / SQLite / 自定义 Adapter | JobItem 列表 |
| 模拟数据 | DemoAdapter（500 条合成数据，可设种子） | 无需输入即可体验 |
| 薪资分析 | 分布直方图、城市/经验/学历分组中位数、p25/p50/p75/p90 分位 | `salary.html` |
| 技能分析 | 高频技能 Top N、技能-薪资关联（job_id 集合运算） | `skill.html` |
| 竞争度分析 | 城市竞争指数（0-100，加权公式可配） | `competitive.html` |
| 求职策略 | TOP5 匹配岗位、技能短板诊断、优先级行动建议 | `strategy.html` |
| 简历匹配 | 技能 + TF-IDF + 经验综合评分 | 报告数据 |
| 可视化看板 | 交互式 HTML 看板，索引页 + 4 模块子页 | `index.html` |
| CLI 入口 | 零配置启动 / 交互式 / 配置文件三种模式 | `run_analysis.py` |
| 可访问性 | 键盘导航、ARIA、触摸目标、reduced-motion | v0.2.0 新增 |。
