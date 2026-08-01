# job_market_analyzer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an open-source job market data analysis tool that generates salary/skill/competitive/strategy reports from recruitment data via Plotly HTML dashboards.

**Architecture:** Adapter pattern for data ingestion (BaseAdapter + DemoAdapter), Pydantic schemas for type-safe data contracts, modular analyzers feeding into a Plotly dashboard generator with an index page.

**Tech Stack:** Python 3.11+, Pydantic 2.0, PyYAML, pandas, numpy, Plotly, scikit-learn, jieba

**Spec:** `docs/superpowers/specs/2026-08-01-job-market-analyzer-design.md`

---

## File Structure

| File | Responsibility |
|------|----------------|
| `pyproject.toml` | Project metadata + dependencies |
| `config.yaml` | Default configuration (all values optional) |
| `src/__init__.py` | Package init |
| `src/schema.py` | JobItem, StrategyReport, JobMatch, SkillGap, ActionItem, SalaryParsed |
| `src/config.py` | Config loader (CLI > yaml > defaults) |
| `src/utils/__init__.py` | Package init |
| `src/utils/salary_parser.py` | parse_salary_string() → SalaryParsed |
| `src/utils/text_processor.py` | tokenize(), compute_tfidf() |
| `src/utils/stat_helper.py` | normalize(), bin_values(), safe_percentile() |
| `src/io/__init__.py` | Package init |
| `src/io/base_adapter.py` | BaseAdapter abstract class |
| `src/io/demo_adapter.py` | DemoAdapter with statistical data generation |
| `src/io/importer.py` | CSV/JSON/SQLite importer |
| `src/analyzer/__init__.py` | Package init |
| `src/analyzer/salary_analyzer.py` | Salary distribution analysis |
| `src/analyzer/skill_analyzer.py` | Skill frequency + salary correlation |
| `src/analyzer/competitive_analyzer.py` | Competitive index calculation |
| `src/analyzer/strategy_advisor.py` | Job matching + action items |
| `src/analyzer/resume_matcher.py` | TF-IDF resume-job matching |
| `src/visualizer/__init__.py` | Package init |
| `src/visualizer/dashboard.py` | Plotly HTML dashboard + index page |
| `scripts/run_analysis.py` | CLI entry point |
| `tests/test_schema.py` | Schema tests |
| `tests/test_salary_parser.py` | Salary parser tests |
| `tests/test_demo_adapter.py` | DemoAdapter tests |
| `tests/test_analyzers.py` | Analyzer tests |
| `tests/test_importer.py` | Importer tests |

---

## Task 1: Project Scaffolding

**Files:**
- Create: `job_market_analyzer/pyproject.toml`
- Create: `job_market_analyzer/config.yaml`
- Create: `job_market_analyzer/src/__init__.py`
- Create: `job_market_analyzer/.gitignore`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "job-market-analyzer"
version = "0.1.0"
description = "招聘市场数据分析工具 — 薪资/技能/竞争度/求职策略分析"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "pyyaml>=6.0",
    "pandas>=2.0",
    "numpy>=1.24",
    "plotly>=5.18",
    "scikit-learn>=1.3",
    "jieba>=0.42",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "ruff>=0.1"]

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]
```

- [ ] **Step 2: Create config.yaml with defaults**

```yaml
data:
  source: "demo"
  csv_path: "data/sample/jobs.csv"
  sqlite_path: "data/jobs.db"

analysis:
  salary:
    bins: [0, 10, 15, 20, 25, 30, 40, 50, 100]
    percentiles: [25, 50, 75, 90]
  skill:
    min_frequency: 0.05
    top_n: 20
  competitive:
    weights:
      job_density: 0.4
      salary_level: 0.3
      education_relaxation: 0.3

visualization:
  theme: "plotly_white"
  color_scale: "Viridis"
  chart_width: 1200
  output_dir: "output/reports"
  filename: "dashboard_{timestamp}.html"

resume:
  user_skills: []
  user_experience: ""
  user_education: ""
  target_city: ""
  target_salary: ""
```

- [ ] **Step 3: Create .gitignore and src/__init__.py**

`.gitignore`:
```
__pycache__/
*.pyc
output/
data/sample/*.csv
data/sample/*.db
.venv/
*.egg-info/
dist/
build/
.pytest_cache/
```

`src/__init__.py`:
```python
"""job_market_analyzer — 招聘市场数据分析工具"""
```

- [ ] **Step 4: Create directory structure**

```bash
mkdir -p src/utils src/io src/analyzer src/visualizer data/demo data/sample tests docs scripts
```

- [ ] **Step 5: Install in dev mode and verify**

```bash
pip install -e ".[dev]"
python -c "import src; print('OK')"
```
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: project scaffolding (pyproject.toml, config.yaml, directory structure)"
```

---

## Task 2: Salary Parser Utility

**Files:**
- Create: `src/utils/__init__.py`
- Create: `src/utils/salary_parser.py`
- Create: `tests/test_salary_parser.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_salary_parser.py
import pytest
from src.utils.salary_parser import parse_salary_string, SalaryParsed


class TestParseSalary:
    def test_standard_k(self):
        result = parse_salary_string("15-25K")
        assert result is not None
        assert result.min == 15.0
        assert result.max == 25.0
        assert result.median == 20.0
        assert result.months == 12

    def test_with_months(self):
        result = parse_salary_string("15-25K·14薪")
        assert result is not None
        assert result.min == 15.0
        assert result.max == 25.0
        assert result.median == 20.0
        assert result.months == 14

    def test_single_value(self):
        result = parse_salary_string("20K")
        assert result is not None
        assert result.min == 20.0
        assert result.max == 20.0
        assert result.median == 20.0

    def test_mianyi(self):
        result = parse_salary_string("面议")
        assert result is None

    def test_empty(self):
        result = parse_salary_string("")
        assert result is None

    def test_none(self):
        result = parse_salary_string(None)
        assert result is None

    def test_lowercase_k(self):
        result = parse_salary_string("15-25k")
        assert result is not None
        assert result.min == 15.0
        assert result.max == 25.0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_salary_parser.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# src/utils/__init__.py
```

```python
# src/utils/salary_parser.py
"""薪资字符串解析器"""
import re
from dataclasses import dataclass


@dataclass
class SalaryParsed:
    """解析后的薪资结构"""
    min: float       # 最低薪资（K/月）
    max: float       # 最高薪资（K/月）
    median: float    # 中位数（K/月）
    months: int      # 年薪月数（默认12）


def parse_salary_string(raw: str | None) -> SalaryParsed | None:
    """解析薪资字符串，如 '15-25K·14薪' → SalaryParsed(min=15, max=25, median=20, months=14)"""
    if not raw or not isinstance(raw, str):
        return None

    raw = raw.strip()

    # 面议、暂无等无效值
    if raw in ("面议", "暂无", "薪资面议", ""):
        return None

    # 提取月数：·14薪 / ·13薪
    months = 12
    months_match = re.search(r'[·・]\s*(\d+)\s*薪', raw)
    if months_match:
        months = int(months_match.group(1))

    # 提取薪资范围：15-25K / 15-25k / 20K
    range_match = re.search(r'(\d+(?:\.\d+)?)\s*[-~–]\s*(\d+(?:\.\d+)?)\s*[Kk千]', raw)
    if range_match:
        sal_min = float(range_match.group(1))
        sal_max = float(range_match.group(2))
        sal_median = (sal_min + sal_max) / 2
        return SalaryParsed(min=sal_min, max=sal_max, median=sal_median, months=months)

    # 单个值：20K
    single_match = re.search(r'(\d+(?:\.\d+)?)\s*[Kk千]', raw)
    if single_match:
        val = float(single_match.group(1))
        return SalaryParsed(min=val, max=val, median=val, months=months)

    return None
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_salary_parser.py -v
```
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add src/utils/ tests/test_salary_parser.py
git commit -m "feat: salary parser utility with test coverage"
```

---

## Task 3: Schema (JobItem + Report Models)

**Files:**
- Create: `src/schema.py`
- Create: `tests/test_schema.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_schema.py
import pytest
from src.schema import JobItem, StrategyReport, JobMatch, SkillGap, ActionItem


class TestJobItem:
    def test_basic_creation(self):
        job = JobItem(
            job_id="abc123",
            job_name="数据分析师",
            company_name="某科技公司",
            city="成都",
        )
        assert job.job_name == "数据分析师"
        assert job.skill_tags == []
        assert job.salary_min is None

    def test_salary_auto_parse_from_raw(self):
        job = JobItem(
            job_id="abc123",
            job_name="数据分析师",
            company_name="某公司",
            city="北京",
            salary_raw="15-25K·14薪",
        )
        assert job.salary_min == 15.0
        assert job.salary_max == 25.0
        assert job.salary_median == 20.0
        assert job.salary_months == 14

    def test_salary_median_fallback(self):
        job = JobItem(
            job_id="abc123",
            job_name="数据分析师",
            company_name="某公司",
            city="北京",
            salary_min=15.0,
            salary_max=25.0,
        )
        assert job.salary_median == 20.0

    def test_salary_mianyi(self):
        job = JobItem(
            job_id="abc123",
            job_name="数据分析师",
            company_name="某公司",
            city="北京",
            salary_raw="面议",
        )
        assert job.salary_min is None


class TestStrategyReport:
    def test_creation(self):
        report = StrategyReport(
            matched_jobs=[
                JobMatch(
                    rank=1, job_name="数据分析师", company_name="某公司",
                    salary_range="20-25K", match_score=85.0,
                    required_skills=["Python", "SQL"],
                    matched_skills=["Python"],
                    missing_skills=["SQL"],
                )
            ],
            skill_gaps=[
                SkillGap(skill="SQL", impact="投递命中率下降30%", frequency=0.75)
            ],
            action_items=[
                ActionItem(priority="高", action="1个月内补充SQL实战", reason="SQL出现频率75%")
            ],
        )
        assert len(report.matched_jobs) == 1
        assert report.matched_jobs[0].match_score == 85.0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_schema.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# src/schema.py
"""数据模型定义"""
from pydantic import BaseModel, model_validator
from src.utils.salary_parser import parse_salary_string


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
    skill_tags: list[str] = []
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
    user_skills: list[str] = []
    user_experience: str = ""
    user_education: str = ""
    target_city: str = ""
    target_salary: str = ""

    def is_empty(self) -> bool:
        """检查画像是否为空"""
        return not self.user_skills and not self.target_city
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_schema.py -v
```
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/schema.py tests/test_schema.py
git commit -m "feat: JobItem + StrategyReport schemas with salary auto-parse"
```

---

## Task 4: Config Loader

**Files:**
- Create: `src/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
import pytest
from src.config import Config


class TestConfig:
    def test_defaults_without_yaml(self):
        """没有 config.yaml 也能加载默认值"""
        cfg = Config.load(config_path="nonexistent.yaml")
        assert cfg.data["source"] == "demo"
        assert cfg.analysis["salary"]["bins"] == [0, 10, 15, 20, 25, 30, 40, 50, 100]
        assert cfg.visualization["theme"] == "plotly_white"

    def test_cli_overrides(self):
        """CLI 参数覆盖默认值"""
        cfg = Config.load(config_path="nonexistent.yaml", source="csv")
        assert cfg.data["source"] == "csv"

    def test_yaml_override(self, tmp_path):
        """yaml 覆盖默认值"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("data:\n  source: sqlite\n", encoding="utf-8")
        cfg = Config.load(config_path=str(yaml_file))
        assert cfg.data["source"] == "sqlite"

    def test_cli_overrides_yaml(self, tmp_path):
        """CLI > yaml"""
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text("data:\n  source: sqlite\n", encoding="utf-8")
        cfg = Config.load(config_path=str(yaml_file), source="csv")
        assert cfg.data["source"] == "csv"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_config.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/config.py
"""配置加载器：CLI > yaml > 默认值"""
from pathlib import Path
import yaml


_DEFAULTS = {
    "data": {
        "source": "demo",
        "csv_path": "data/sample/jobs.csv",
        "sqlite_path": "data/jobs.db",
    },
    "analysis": {
        "salary": {
            "bins": [0, 10, 15, 20, 25, 30, 40, 50, 100],
            "percentiles": [25, 50, 75, 90],
        },
        "skill": {
            "min_frequency": 0.05,
            "top_n": 20,
        },
        "competitive": {
            "weights": {
                "job_density": 0.4,
                "salary_level": 0.3,
                "education_relaxation": 0.3,
            },
        },
    },
    "visualization": {
        "theme": "plotly_white",
        "color_scale": "Viridis",
        "chart_width": 1200,
        "output_dir": "output/reports",
        "filename": "dashboard_{timestamp}.html",
    },
    "resume": {
        "user_skills": [],
        "user_experience": "",
        "user_education": "",
        "target_city": "",
        "target_salary": "",
    },
}


class Config:
    """配置对象"""

    def __init__(self, data: dict):
        self.data = data["data"]
        self.analysis = data["analysis"]
        self.visualization = data["visualization"]
        self.resume = data["resume"]

    @classmethod
    def load(cls, config_path: str = "config.yaml", **cli_overrides) -> "Config":
        """加载配置，优先级：CLI参数 > config.yaml > 内置默认值"""
        # 1. 深拷贝默认值
        import copy
        cfg = copy.deepcopy(_DEFAULTS)

        # 2. 如果 config.yaml 存在，合并覆盖
        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                user_cfg = yaml.safe_load(f)
            if user_cfg:
                cfg = cls._deep_merge(cfg, user_cfg)

        # 3. CLI 参数最高优先级
        if cli_overrides:
            cli_cfg = {}
            for key, val in cli_overrides.items():
                if val is None:
                    continue
                # 映射 CLI 参数名到配置路径
                if key == "source":
                    cli_cfg.setdefault("data", {})["source"] = val
                elif key == "csv_path":
                    cli_cfg.setdefault("data", {})["csv_path"] = val
                elif key in ("user_skills", "user_experience", "user_education",
                             "target_city", "target_salary"):
                    cli_cfg.setdefault("resume", {})[key] = val
            if cli_cfg:
                cfg = cls._deep_merge(cfg, cli_cfg)

        return cls(cfg)

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """递归合并字典"""
        for key, val in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(val, dict):
                base[key] = Config._deep_merge(base[key], val)
            else:
                base[key] = val
        return base
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_config.py -v
```
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: config loader with CLI > yaml > defaults priority"
```

---

## Task 5: Stat Helper Utility

**Files:**
- Create: `src/utils/stat_helper.py`
- Create: `tests/test_stat_helper.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_stat_helper.py
import pytest
import numpy as np
from src.utils.stat_helper import normalize, bin_values, safe_percentile


class TestNormalize:
    def test_basic(self):
        data = [1, 2, 3, 4, 5]
        result = normalize(data)
        assert pytest.approx(result[0], abs=0.01) == 0.0
        assert pytest.approx(result[-1], abs=0.01) == 1.0

    def test_single_value(self):
        result = normalize([5])
        assert result[0] == 0.0  # 单值无法归一化，返回0

    def test_empty(self):
        result = normalize([])
        assert len(result) == 0


class TestBinValues:
    def test_basic(self):
        data = [5, 12, 18, 22, 35, 55]
        bins = [0, 10, 15, 20, 25, 30, 40, 50, 100]
        labels, counts = bin_values(data, bins)
        assert len(labels) == len(bins) - 1
        assert sum(counts) == len(data)


class TestSafePercentile:
    def test_basic(self):
        data = list(range(1, 101))
        p50 = safe_percentile(data, 50)
        assert pytest.approx(p50, abs=1) == 50

    def test_empty(self):
        assert safe_percentile([], 50) is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_stat_helper.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/utils/stat_helper.py
"""统计工具函数"""
import numpy as np


def normalize(data: list[float] | np.ndarray) -> np.ndarray:
    """Min-Max 归一化到 [0, 1]"""
    arr = np.array(data, dtype=float)
    if len(arr) == 0:
        return arr
    min_val, max_val = arr.min(), arr.max()
    if max_val == min_val:
        return np.zeros_like(arr)
    return (arr - min_val) / (max_val - min_val)


def bin_values(data: list[float], bins: list[float]) -> tuple[list[str], list[int]]:
    """将数据分箱，返回 (标签, 计数)"""
    arr = np.array(data, dtype=float)
    counts, _ = np.histogram(arr, bins=bins)
    labels = [f"{bins[i]}-{bins[i+1]}K" for i in range(len(bins) - 1)]
    return labels, counts.tolist()


def safe_percentile(data: list[float], q: float) -> float | None:
    """安全百分位计算，空数据返回 None"""
    if not data:
        return None
    return float(np.percentile(data, q))
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_stat_helper.py -v
```
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/utils/stat_helper.py tests/test_stat_helper.py
git commit -m "feat: stat helper (normalize, bin_values, safe_percentile)"
```

---

## Task 6: Text Processor Utility

**Files:**
- Create: `src/utils/text_processor.py`
- Create: `tests/test_text_processor.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_text_processor.py
import pytest
from src.utils.text_processor import tokenize, compute_tfidf_similarity


class TestTokenize:
    def test_basic(self):
        tokens = tokenize("熟练掌握Python和SQL，熟悉Excel")
        assert "Python" in tokens
        assert "SQL" in tokens
        assert "Excel" in tokens

    def test_empty(self):
        assert tokenize("") == []

    def test_skill_extraction(self):
        tokens = tokenize("需要Python, Spark, Hadoop经验")
        assert "Python" in tokens
        assert "Spark" in tokens


class TestTfidfSimilarity:
    def test_identical(self):
        text1 = "熟练Python SQL数据分析"
        text2 = "熟练Python SQL数据分析"
        score = compute_tfidf_similarity(text1, text2)
        assert score > 0.9

    def test_different(self):
        text1 = "Python数据分析"
        text2 = "Java后端开发"
        score = compute_tfidf_similarity(text1, text2)
        assert score < 0.3
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_text_processor.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/utils/text_processor.py
"""文本预处理工具：分词 + TF-IDF"""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 常见技能关键词表（用于从文本中提取技能）
_SKILL_KEYWORDS = {
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
    "Spark", "Hadoop", "Hive", "Flink", "Kafka",
    "Excel", "Tableau", "PowerBI", "Power BI", "Superset",
    "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "Linux", "Shell", "Git",
    "机器学习", "深度学习", "自然语言处理", "NLP", "计算机视觉",
    "数据分析", "数据挖掘", "商业分析", "ETL", "数仓",
    "HTML", "CSS", "React", "Vue", "Node",
    "Spring", "Django", "Flask", "FastAPI",
}


def tokenize(text: str) -> list[str]:
    """从文本中提取技能关键词"""
    if not text:
        return []
    # 在文本中搜索已知的技能关键词
    found = []
    text_lower = text.lower()
    for skill in _SKILL_KEYWORDS:
        if skill.lower() in text_lower:
            found.append(skill)
    return found


def compute_tfidf_similarity(text1: str, text2: str) -> float:
    """计算两段文本的 TF-IDF 余弦相似度 (0-1)"""
    if not text1 or not text2:
        return 0.0
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(sim)
    except ValueError:
        return 0.0
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_text_processor.py -v
```
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/utils/text_processor.py tests/test_text_processor.py
git commit -m "feat: text processor (tokenize + TF-IDF similarity)"
```

---

## Task 7: BaseAdapter + DemoAdapter

**Files:**
- Create: `src/io/__init__.py`
- Create: `src/io/base_adapter.py`
- Create: `src/io/demo_adapter.py`
- Create: `tests/test_demo_adapter.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_demo_adapter.py
import pytest
from src.io.demo_adapter import DemoAdapter
from src.schema import JobItem


class TestDemoAdapter:
    def test_default_generation(self):
        adapter = DemoAdapter()
        jobs = adapter.fetch_jobs(n_samples=100)
        assert len(jobs) == 100
        assert all(isinstance(j, JobItem) for j in jobs)

    def test_city_filter(self):
        adapter = DemoAdapter()
        jobs = adapter.fetch_jobs(n_samples=50, city="北京")
        assert len(jobs) > 0
        assert all(j.city == "北京" for j in jobs)

    def test_salary_distribution(self):
        """北京薪资应该整体高于成都"""
        adapter = DemoAdapter()
        bj_jobs = adapter.fetch_jobs(n_samples=200, city="北京")
        cd_jobs = adapter.fetch_jobs(n_samples=200, city="成都")
        bj_median = sum(j.salary_median for j in bj_jobs) / len(bj_jobs)
        cd_median = sum(j.salary_median for j in cd_jobs) / len(cd_jobs)
        assert bj_median > cd_median

    def test_max_generate_ratio_safety(self):
        """苛刻条件不会死循环"""
        adapter = DemoAdapter()
        jobs = adapter.fetch_jobs(n_samples=500, city="北京", education="博士")
        # 可能不足500，但不会死循环
        assert len(jobs) > 0

    def test_skill_tags_not_empty(self):
        adapter = DemoAdapter()
        jobs = adapter.fetch_jobs(n_samples=50)
        has_skills = any(len(j.skill_tags) > 0 for j in jobs)
        assert has_skills

    def test_job_description_not_empty(self):
        adapter = DemoAdapter()
        jobs = adapter.fetch_jobs(n_samples=50)
        has_desc = any(len(j.job_description) > 0 for j in jobs)
        assert has_desc
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_demo_adapter.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write BaseAdapter**

```python
# src/io/__init__.py
```

```python
# src/io/base_adapter.py
"""数据适配器抽象基类"""
from abc import ABC, abstractmethod
from src.schema import JobItem


class BaseAdapter(ABC):
    """数据源适配器基类，用户继承此类实现 fetch_jobs()"""

    @abstractmethod
    def fetch_jobs(self, **kwargs) -> list[JobItem]:
        """获取岗位数据，返回 JobItem 列表"""
        pass
```

- [ ] **Step 4: Write DemoAdapter**

```python
# src/io/demo_adapter.py
"""模拟数据生成器 — 生成符合真实招聘市场统计规律的演示数据"""
import hashlib
import random

import numpy as np

from src.io.base_adapter import BaseAdapter
from src.schema import JobItem


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

    def fetch_jobs(
        self,
        n_samples: int = 500,
        city: str | None = None,
        job_keyword: str | None = None,
        education: str | None = None,
        experience: str | None = None,
    ) -> list[JobItem]:
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
        # 城市
        city_name, city_coef = self._weighted_choice(list(_CITIES.items()), lambda x: x[1][0])
        city_name = city_name  # type: ignore

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
```

- [ ] **Step 5: Run test to verify it passes**

```bash
pytest tests/test_demo_adapter.py -v
```
Expected: 6 passed

- [ ] **Step 6: Commit**

```bash
git add src/io/ tests/test_demo_adapter.py
git commit -m "feat: BaseAdapter + DemoAdapter with statistical data generation"
```

---

## Task 8: Importer (CSV/JSON/SQLite)

**Files:**
- Create: `src/io/importer.py`
- Create: `tests/test_importer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_importer.py
import pytest
import csv
import json
import sqlite3
from pathlib import Path
from src.io.importer import import_csv, import_json, import_sqlite
from src.schema import JobItem


class TestImportCSV:
    def test_basic_csv(self, tmp_path):
        csv_file = tmp_path / "jobs.csv"
        csv_file.write_text(
            "job_id,job_name,company_name,city,salary_raw,experience,education\n"
            "1,数据分析师,某公司,成都,15-25K,3-5年,本科\n"
            "2,数据工程师,另一公司,北京,20-30K·14薪,5-10年,硕士\n",
            encoding="utf-8",
        )
        jobs = import_csv(str(csv_file))
        assert len(jobs) == 2
        assert jobs[0].city == "成都"
        assert jobs[0].salary_min == 15.0
        assert jobs[1].salary_months == 14


class TestImportJSON:
    def test_basic_json(self, tmp_path):
        json_file = tmp_path / "jobs.json"
        data = [
            {"job_id": "1", "job_name": "数据分析师", "company_name": "某公司",
             "city": "成都", "salary_raw": "15-25K"},
        ]
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        jobs = import_json(str(json_file))
        assert len(jobs) == 1
        assert jobs[0].salary_min == 15.0


class TestImportSQLite:
    def test_basic_sqlite(self, tmp_path):
        db_file = tmp_path / "jobs.db"
        conn = sqlite3.connect(str(db_file))
        c = conn.cursor()
        c.execute("""CREATE TABLE jobs (
            job_id TEXT, job_name TEXT, company_name TEXT,
            city TEXT, salary_raw TEXT, experience TEXT, education TEXT
        )""")
        c.execute("INSERT INTO jobs VALUES ('1', '数据分析师', '某公司', '成都', '15-25K', '3-5年', '本科')")
        conn.commit()
        conn.close()
        jobs = import_sqlite(str(db_file))
        assert len(jobs) == 1
        assert jobs[0].salary_min == 15.0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_importer.py -v
```
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write implementation**

```python
# src/io/importer.py
"""数据导入器：支持 CSV / JSON / SQLite"""
import csv
import json
import sqlite3
from pathlib import Path

from src.schema import JobItem


def _row_to_jobitem(row: dict) -> JobItem:
    """将字典行转换为 JobItem，忽略未知字段"""
    # 确保必填字段存在
    row.setdefault("job_id", "")
    row.setdefault("job_name", "")
    row.setdefault("company_name", "")
    row.setdefault("city", "")
    # 处理 skill_tags（可能是字符串）
    if "skill_tags" in row and isinstance(row["skill_tags"], str):
        row["skill_tags"] = [s.strip() for s in row["skill_tags"].split(",") if s.strip()]
    # 过滤掉 JobItem 不认识的字段
    valid_fields = JobItem.model_fields.keys()
    filtered = {k: v for k, v in row.items() if k in valid_fields}
    return JobItem(**filtered)


def import_csv(path: str) -> list[JobItem]:
    """从 CSV 文件导入"""
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [_row_to_jobitem(row) for row in reader]


def import_json(path: str) -> list[JobItem]:
    """从 JSON 文件导入"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    return [_row_to_jobitem(row) for row in data]


def import_sqlite(path: str, table: str = "jobs") -> list[JobItem]:
    """从 SQLite 数据库导入"""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return [_row_to_jobitem(row) for row in rows]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_importer.py -v
```
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/io/importer.py tests/test_importer.py
git commit -m "feat: CSV/JSON/SQLite importer"
```

---

## Task 9: Salary Analyzer

**Files:**
- Create: `src/analyzer/__init__.py`
- Create: `src/analyzer/salary_analyzer.py`
- Create: `tests/test_salary_analyzer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_salary_analyzer.py
import pytest
from src.analyzer.salary_analyzer import SalaryAnalyzer
from src.io.demo_adapter import DemoAdapter


class TestSalaryAnalyzer:
    @pytest.fixture
    def jobs(self):
        return DemoAdapter().fetch_jobs(n_samples=200)

    def test_distribution(self, jobs):
        analyzer = SalaryAnalyzer(jobs)
        result = analyzer.distribution(bins=[0, 10, 15, 20, 25, 30, 40, 50, 100])
        assert "labels" in result
        assert "counts" in result
        assert sum(result["counts"]) == len(jobs)

    def test_by_city(self, jobs):
        analyzer = SalaryAnalyzer(jobs)
        result = analyzer.by_city()
        assert isinstance(result, dict)
        assert len(result) > 0
        for city, stats in result.items():
            assert "median" in stats
            assert "min" in stats
            assert "max" in stats

    def test_by_experience(self, jobs):
        analyzer = SalaryAnalyzer(jobs)
        result = analyzer.by_experience()
        assert isinstance(result, dict)

    def test_by_education(self, jobs):
        analyzer = SalaryAnalyzer(jobs)
        result = analyzer.by_education()
        assert isinstance(result, dict)

    def test_summary(self, jobs):
        analyzer = SalaryAnalyzer(jobs)
        result = analyzer.summary()
        assert "median" in result
        assert "p25" in result
        assert "p75" in result
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_salary_analyzer.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

```python
# src/analyzer/__init__.py
```

```python
# src/analyzer/salary_analyzer.py
"""薪资分析模块"""
from collections import defaultdict

from src.schema import JobItem
from src.utils.stat_helper import bin_values, safe_percentile


class SalaryAnalyzer:
    """薪资分析器"""

    def __init__(self, jobs: list[JobItem]):
        self.jobs = [j for j in jobs if j.salary_median is not None]

    def distribution(self, bins: list[float]) -> dict:
        """薪资分布直方图"""
        salaries = [j.salary_median for j in self.jobs]
        labels, counts = bin_values(salaries, bins)
        return {"labels": labels, "counts": counts}

    def by_city(self) -> dict[str, dict]:
        """按城市分组统计"""
        groups = defaultdict(list)
        for job in self.jobs:
            groups[job.city].append(job.salary_median)
        return {
            city: {
                "median": safe_percentile(sals, 50),
                "min": min(sals),
                "max": max(sals),
                "count": len(sals),
            }
            for city, sals in groups.items()
        }

    def by_experience(self) -> dict[str, dict]:
        """按经验分组统计"""
        groups = defaultdict(list)
        for job in self.jobs:
            if job.experience:
                groups[job.experience].append(job.salary_median)
        return {
            exp: {
                "median": safe_percentile(sals, 50),
                "count": len(sals),
            }
            for exp, sals in groups.items()
        }

    def by_education(self) -> dict[str, dict]:
        """按学历分组统计"""
        groups = defaultdict(list)
        for job in self.jobs:
            if job.education:
                groups[job.education].append(job.salary_median)
        return {
            edu: {
                "median": safe_percentile(sals, 50),
                "count": len(sals),
            }
            for edu, sals in groups.items()
        }

    def summary(self) -> dict:
        """总体统计"""
        salaries = [j.salary_median for j in self.jobs]
        return {
            "median": safe_percentile(salaries, 50),
            "p25": safe_percentile(salaries, 25),
            "p75": safe_percentile(salaries, 75),
            "p90": safe_percentile(salaries, 90),
            "min": min(salaries) if salaries else None,
            "max": max(salaries) if salaries else None,
            "count": len(salaries),
        }
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_salary_analyzer.py -v
```
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/analyzer/ tests/test_salary_analyzer.py
git commit -m "feat: salary analyzer (distribution, by_city, by_experience, by_education)"
```

---

## Task 10: Skill Analyzer

**Files:**
- Create: `src/analyzer/skill_analyzer.py`
- Create: `tests/test_skill_analyzer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_skill_analyzer.py
import pytest
from src.analyzer.skill_analyzer import SkillAnalyzer
from src.io.demo_adapter import DemoAdapter


class TestSkillAnalyzer:
    @pytest.fixture
    def jobs(self):
        return DemoAdapter().fetch_jobs(n_samples=200)

    def test_frequency(self, jobs):
        analyzer = SkillAnalyzer(jobs)
        result = analyzer.frequency(min_freq=0.0)
        assert isinstance(result, dict)
        assert "Python" in result
        assert result["Python"] > 0

    def test_salary_correlation(self, jobs):
        analyzer = SkillAnalyzer(jobs)
        result = analyzer.salary_correlation()
        assert isinstance(result, dict)
        for skill, stats in result.items():
            assert "with_skill" in stats
            assert "without_skill" in stats

    def test_top_n(self, jobs):
        analyzer = SkillAnalyzer(jobs)
        result = analyzer.top_n(n=5)
        assert len(result) <= 5
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_skill_analyzer.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

```python
# src/analyzer/skill_analyzer.py
"""技能分析模块"""
from collections import Counter, defaultdict

from src.schema import JobItem
from src.utils.stat_helper import safe_percentile


class SkillAnalyzer:
    """技能分析器"""

    def __init__(self, jobs: list[JobItem]):
        self.jobs = jobs

    def frequency(self, min_freq: float = 0.05) -> dict[str, float]:
        """技能出现频率"""
        total = len(self.jobs)
        if total == 0:
            return {}
        counter = Counter()
        for job in self.jobs:
            for skill in job.skill_tags:
                counter[skill] += 1
        return {
            skill: count / total
            for skill, count in counter.items()
            if count / total >= min_freq
        }

    def salary_correlation(self) -> dict[str, dict]:
        """技能-薪资关联分析"""
        skill_salaries = defaultdict(list)
        all_salaries = []
        for job in self.jobs:
            if job.salary_median is not None:
                all_salaries.append(job.salary_median)
                for skill in job.skill_tags:
                    skill_salaries[skill].append(job.salary_median)

        result = {}
        for skill, sals in skill_salaries.items():
            without = [s for s in all_salaries if s not in sals]
            result[skill] = {
                "with_skill": safe_percentile(sals, 50),
                "without_skill": safe_percentile(without, 50) if without else None,
                "count": len(sals),
            }
        return result

    def top_n(self, n: int = 20) -> dict[str, float]:
        """前 N 个高频技能"""
        freq = self.frequency(min_freq=0.0)
        sorted_items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_items[:n])
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_skill_analyzer.py -v
```
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add src/analyzer/skill_analyzer.py tests/test_skill_analyzer.py
git commit -m "feat: skill analyzer (frequency, salary correlation, top_n)"
```

---

## Task 11: Competitive Analyzer

**Files:**
- Create: `src/analyzer/competitive_analyzer.py`
- Create: `tests/test_competitive_analyzer.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_competitive_analyzer.py
import pytest
from src.analyzer.competitive_analyzer import CompetitiveAnalyzer
from src.io.demo_adapter import DemoAdapter


class TestCompetitiveAnalyzer:
    @pytest.fixture
    def jobs(self):
        return DemoAdapter().fetch_jobs(n_samples=300)

    def test_city_index(self, jobs):
        analyzer = CompetitiveAnalyzer(jobs)
        result = analyzer.city_index()
        assert isinstance(result, dict)
        for city, score in result.items():
            assert 0 <= score <= 100

    def test_weights_configurable(self, jobs):
        analyzer = CompetitiveAnalyzer(
            jobs,
            weights={"job_density": 0.5, "salary_level": 0.3, "education_relaxation": 0.2},
        )
        result = analyzer.city_index()
        assert len(result) > 0
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_competitive_analyzer.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

```python
# src/analyzer/competitive_analyzer.py
"""竞争度分析模块"""
from collections import defaultdict

from src.schema import JobItem
from src.utils.stat_helper import normalize, safe_percentile


class CompetitiveAnalyzer:
    """竞争度分析器"""

    def __init__(
        self,
        jobs: list[JobItem],
        weights: dict[str, float] | None = None,
    ):
        self.jobs = jobs
        self.weights = weights or {
            "job_density": 0.4,
            "salary_level": 0.3,
            "education_relaxation": 0.3,
        }

    def city_index(self) -> dict[str, float]:
        """计算各城市竞争指数 (0-100，越高竞争越激烈)"""
        cities = defaultdict(list)
        for job in self.jobs:
            cities[job.city].append(job)

        total_jobs = len(self.jobs)
        city_metrics = {}
        for city, city_jobs in cities.items():
            # 岗位密度 = 该城市岗位数 / 总岗位数（越高机会越多）
            density = len(city_jobs) / total_jobs

            # 薪资中位数
            salaries = [j.salary_median for j in city_jobs if j.salary_median]
            salary_med = safe_percentile(salaries, 50) or 0

            # 学历放宽度 = 1 - (要求本科及以上的比例)
            bach_plus = sum(1 for j in city_jobs if j.education in ("本科", "硕士", "博士"))
            edu_relax = 1 - (bach_plus / len(city_jobs)) if city_jobs else 0

            city_metrics[city] = {
                "density": density,
                "salary": salary_med,
                "edu_relax": edu_relax,
            }

        # 标准化各指标
        densities = [m["density"] for m in city_metrics.values()]
        salaries = [m["salary"] for m in city_metrics.values()]
        edu_relaxes = [m["edu_relax"] for m in city_metrics.values()]

        norm_density = normalize(densities)  # 高密度→低竞争（取反）
        norm_salary = normalize(salaries)    # 高薪资→高竞争
        norm_edu = normalize(edu_relaxes)    # 高放宽→高竞争

        w1 = self.weights["job_density"]
        w2 = self.weights["salary_level"]
        w3 = self.weights["education_relaxation"]

        result = {}
        for i, city in enumerate(city_metrics):
            # 岗位密度取反（机会多→竞争低）
            score = (1 - norm_density[i]) * w1 + norm_salary[i] * w2 + norm_edu[i] * w3
            result[city] = round(score * 100, 1)

        return result
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_competitive_analyzer.py -v
```
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/analyzer/competitive_analyzer.py tests/test_competitive_analyzer.py
git commit -m "feat: competitive analyzer with weighted index formula"
```

---

## Task 12: Resume Matcher

**Files:**
- Create: `src/analyzer/resume_matcher.py`
- Create: `tests/test_resume_matcher.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_resume_matcher.py
import pytest
from src.analyzer.resume_matcher import ResumeMatcher
from src.schema import JobItem, UserProfile
from src.io.demo_adapter import DemoAdapter


class TestResumeMatcher:
    @pytest.fixture
    def jobs(self):
        return DemoAdapter().fetch_jobs(n_samples=50)

    def test_match_score(self, jobs):
        profile = UserProfile(
            user_skills=["Python", "SQL", "Excel"],
            user_experience="3-5年",
            user_education="本科",
        )
        matcher = ResumeMatcher(profile)
        scores = matcher.match_all(jobs)
        assert len(scores) == len(jobs)
        for job_id, score in scores.items():
            assert 0 <= score <= 100

    def test_skill_match(self, jobs):
        profile = UserProfile(user_skills=["Python", "SQL"])
        matcher = ResumeMatcher(profile)
        matched, missing = matcher.skill_match(jobs[0].skill_tags)
        assert "Python" in matched or "SQL" in matched
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_resume_matcher.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

```python
# src/analyzer/resume_matcher.py
"""简历-岗位匹配模块"""
from src.schema import JobItem, UserProfile
from src.utils.text_processor import compute_tfidf_similarity


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
        user_set = set(s.lower() for s in self.profile.user_skills)
        matched = [s for s in required_skills if s.lower() in user_set]
        missing = [s for s in required_skills if s.lower() not in user_set]
        return matched, missing
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_resume_matcher.py -v
```
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/analyzer/resume_matcher.py tests/test_resume_matcher.py
git commit -m "feat: resume matcher with skill + TF-IDF + experience scoring"
```

---

## Task 13: Strategy Advisor

**Files:**
- Create: `src/analyzer/strategy_advisor.py`
- Create: `tests/test_strategy_advisor.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_strategy_advisor.py
import pytest
from src.analyzer.strategy_advisor import StrategyAdvisor
from src.schema import UserProfile
from src.io.demo_adapter import DemoAdapter


class TestStrategyAdvisor:
    @pytest.fixture
    def jobs(self):
        return DemoAdapter().fetch_jobs(n_samples=100)

    def test_generate_report(self, jobs):
        profile = UserProfile(
            user_skills=["Python", "SQL"],
            user_experience="3-5年",
            user_education="本科",
            target_city="成都",
        )
        advisor = StrategyAdvisor(profile)
        report = advisor.generate(jobs)
        assert len(report.matched_jobs) <= 5
        assert len(report.skill_gaps) > 0
        assert len(report.action_items) > 0

    def test_top5_ranked(self, jobs):
        profile = UserProfile(user_skills=["Python", "SQL", "Excel"])
        advisor = StrategyAdvisor(profile)
        report = advisor.generate(jobs)
        if len(report.matched_jobs) > 1:
            scores = [j.match_score for j in report.matched_jobs]
            assert scores == sorted(scores, reverse=True)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_strategy_advisor.py -v
```
Expected: FAIL

- [ ] **Step 3: Write implementation**

```python
# src/analyzer/strategy_advisor.py
"""求职策略推荐模块"""
from src.schema import JobItem, UserProfile, StrategyReport, JobMatch, SkillGap, ActionItem
from src.analyzer.resume_matcher import ResumeMatcher
from src.analyzer.skill_analyzer import SkillAnalyzer


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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_strategy_advisor.py -v
```
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/analyzer/strategy_advisor.py tests/test_strategy_advisor.py
git commit -m "feat: strategy advisor with TOP5 matching + skill gaps + action items"
```

---

## Task 14: Dashboard Visualizer

**Files:**
- Create: `src/visualizer/__init__.py`
- Create: `src/visualizer/dashboard.py`

- [ ] **Step 1: Write the dashboard generator**

```python
# src/visualizer/__init__.py
```

```python
# src/visualizer/dashboard.py
"""Plotly HTML 看板生成器"""
from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.schema import JobItem, StrategyReport


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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

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
```

- [ ] **Step 2: Verify it runs without import errors**

```bash
python -c "from src.visualizer.dashboard import DashboardGenerator; print('OK')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add src/visualizer/
git commit -m "feat: Plotly dashboard generator with index page"
```

---

## Task 15: CLI Entry Point (run_analysis.py)

**Files:**
- Create: `scripts/run_analysis.py`

- [ ] **Step 1: Write the entry point**

```python
# scripts/run_analysis.py
"""job_market_analyzer 一键运行入口"""
import argparse
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.schema import UserProfile
from src.io.demo_adapter import DemoAdapter
from src.io.importer import import_csv, import_sqlite
from src.analyzer.salary_analyzer import SalaryAnalyzer
from src.analyzer.skill_analyzer import SkillAnalyzer
from src.analyzer.competitive_analyzer import CompetitiveAnalyzer
from src.analyzer.strategy_advisor import StrategyAdvisor
from src.visualizer.dashboard import DashboardGenerator


def load_data(cfg: Config) -> list:
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
    strategy_report = None
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
```

- [ ] **Step 2: Verify it runs**

```bash
python scripts/run_analysis.py
```
Expected: Generates `output/reports/index.html`

- [ ] **Step 3: Commit**

```bash
git add scripts/run_analysis.py
git commit -m "feat: CLI entry point with zero-config startup"
```

---

## Task 16: Run All Tests + Final Commit

- [ ] **Step 1: Run all tests**

```bash
pytest tests/ -v
```
Expected: All tests pass

- [ ] **Step 2: Verify zero-config startup**

```bash
python scripts/run_analysis.py
```
Expected: Generates report with 3 modules (no profile)

- [ ] **Step 3: Verify interactive mode**

```bash
echo "Python,SQL,Excel
3-5年
本科
成都
18-25K" | python scripts/run_analysis.py --interactive
```
Expected: Generates report with 5 modules

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: job_market_analyzer complete — 5 analysis modules + Plotly dashboard"
```

---

## Self-Review Notes

**Spec coverage check:**
- ✅ JobItem schema with job_description field (Task 3)
- ✅ DemoAdapter with filter params + MAX_GENERATE_RATIO (Task 7)
- ✅ Competitive index formula 0.4/0.3/0.3 (Task 11)
- ✅ StrategyReport with JobMatch/SkillGap/ActionItem (Task 3 + Task 13)
- ✅ config.yaml with CLI > yaml > defaults (Task 4)
- ✅ User profile 3 input methods + degradation (Task 15)
- ✅ Plotly HTML + index page (Task 14)
- ✅ BaseAdapter interface (Task 7)
- ✅ Importer CSV/JSON/SQLite (Task 8)
- ✅ Utils: salary_parser, text_processor, stat_helper (Tasks 2, 5, 6)
- ✅ All 5 analysis modules (Tasks 9-13)
- ✅ Zero-config startup (Task 15)
