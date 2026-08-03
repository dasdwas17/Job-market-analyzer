# Job Market Analyzer

> 招聘市场数据分析工具 —— 不爬数据，只做分析。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![CI](https://github.com/my-username/job-market-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/my-username/job-market-analyzer/actions/workflows/ci.yml)

## 这是什么

一个开源的招聘市场数据分析工具，生成薪资、技能、竞争度、求职策略多维度分析报告。通过 Adapter 接口接入你自己的数据（或使用内置模拟数据体验），输出交互式 Plotly HTML 看板。

> ⚠️ 本项目不含爬虫。请阅读 [免责声明](DISCLAIMER.md)。

## Quickstart

```bash
# 零配置启动（模拟数据，生成 3 模块报告）
python scripts/run_analysis.py

# 交互式输入个人画像，生成完整 5 模块报告
python scripts/run_analysis.py --interactive

# 指定数据源和个人画像
python scripts/run_analysis.py --source csv --csv-path data/sample/jobs.csv \
  --skills "Python,SQL" --city "成都" --experience "3-5年" --salary "18-25K"
```

打开生成的 `output/reports/index.html` 查看完整看板。

## 功能

- 薪资分析：分布 / 城市对比 / 经验曲线 / 学历对比
- 技能分析：高频统计 / 技能-薪资关联
- 竞争度分析：城市竞争指数（加权公式，可配置）
- 求职策略：TOP5 匹配岗位 + 技能短板诊断 + 行动建议

## 接入自己的数据

继承 `BaseAdapter` 实现 `fetch_jobs()`，参考 [base_adapter.py](job_market_analyzer/io/base_adapter.py) 源码。

## 开发

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## License

MIT — 见 [LICENSE](LICENSE)。
