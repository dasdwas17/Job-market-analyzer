# 贡献指南

感谢你考虑为 Job Market Analyzer 贡献代码！

## 重要约束

- **不接受任何可运行的爬虫代码**。涉及数据获取的 PR 请以 `BaseAdapter` 子类示例形式提交到 `examples/`，且不包含针对特定网站的反爬逻辑。
- **不接受真实数据**。测试数据必须使用 `DemoAdapter` 或合成 CSV，禁止提交含真实公司名/岗位 ID 的样本。
- 遵循现有 TDD 流程：新功能先写测试，确保 `pytest tests/ -v` 全绿。

## 开发流程

1. Fork → 新建分支 `feat/xxx` 或 `fix/xxx`
2. `pip install -e ".[dev]"`
3. 改代码 + 写测试
4. `ruff check . && pytest tests/ -v`
5. 提交 PR，描述变更动机

## 提交信息规范

使用 Conventional Commits：`feat: ...` / `fix: ...` / `docs: ...` / `test: ...`
