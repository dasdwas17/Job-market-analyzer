# job_market_analyzer 设计文档

> **版本**: 1.0  
> **日期**: 2026-08-01  
> **状态**: 待审查

## 1. 项目定位

**招聘市场数据分析工具** —— 不爬数据，只做分析。

用户通过 Adapter 接口接入自己的数据（或使用内置 DemoAdapter 体验），生成薪资、技能、竞争度多维度分析和可视化看板，辅助求职决策。

### 核心原则

- **不包含任何可运行的爬虫代码**，主仓库只提供数据分析和可视化能力
- 通过 `BaseAdapter` 接口规范，用户自行实现数据获取
- 内置 `DemoAdapter` 生成符合真实市场分布的模拟数据，开箱即用
- MIT 开源协议 + 免责声明，用户自行承担数据获取的合规责任

## 2. 架构设计

```
用户数据 (CSV/JSON/SQLite/Adapter)
        ↓
   BaseAdapter 接口  ← DemoAdapter（内置模拟数据）
        ↓
   JobItem Schema (Pydantic，含薪资自动解析)
        ↓
  ┌─────┬──────┬──────┬──────────────┐
  │薪资 │技能  │竞争度 │求职策略+简历  │
  │分析 │分析  │分析  │诊断（需画像） │
  └─────┴──────┴──────┴──────────────┘
        ↓
   Plotly HTML 看板（含汇总索引页）
```

### 数据流

1. 数据来源（demo/csv/sqlite/自定义adapter）→ 加载为 `list[JobItem]`
2. JobItem 的 Pydantic validator 自动解析 `salary_raw` 字符串为结构化薪资字段
3. 分析模块消费 `list[JobItem]`，输出结构化分析结果
4. 可视化模块将分析结果渲染为交互式 HTML 图表 + 汇总索引页

## 3. 数据契约

### 3.1 JobItem Schema

```python
class JobItem(BaseModel):
    """岗位数据标准格式"""
    job_id: str                        # 岗位唯一ID
    job_name: str                      # 岗位名称
    company_name: str                  # 公司名
    company_size: str = ""             # 公司规模
    industry: str = ""                 # 行业
    city: str                          # 城市
    district: str = ""                 # 区域
    salary_raw: str = ""               # 原始薪资字符串 "15-25K·14薪"
    salary_min: float | None = None    # 解析后（K/月）
    salary_max: float | None = None
    salary_median: float | None = None
    salary_months: int | None = None   # 年薪月数（14薪=14）
    experience: str = ""               # 经验要求
    education: str = ""                # 学历要求
    skill_tags: list[str] = []         # 技能标签（短文本）
    job_description: str = ""          # 岗位描述（长文本，用于匹配诊断）
    job_url: str = ""                  # 岗位链接
    crawl_time: str = ""               # 数据采集时间

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
```

### 3.2 策略报告 Schema

```python
class StrategyReport(BaseModel):
    """求职策略报告"""
    matched_jobs: list[JobMatch]        # TOP 5 匹配岗位
    skill_gaps: list[SkillGap]          # 短板诊断
    action_items: list[ActionItem]      # 行动建议

class JobMatch(BaseModel):
    rank: int                           # 排名
    job_name: str
    company_name: str
    salary_range: str                   # "20-25K"
    match_score: float                  # 匹配度 0-100
    required_skills: list[str]
    matched_skills: list[str]           # 用户已具备
    missing_skills: list[str]           # 用户缺失

class SkillGap(BaseModel):
    skill: str                          # 缺失技能
    impact: str                         # "投递命中率下降30%"
    frequency: float                    # 该技能在岗位中的出现频率

class ActionItem(BaseModel):
    priority: str                       # "高/中/低"
    action: str                         # "1个月内补充Tableau实战项目"
    reason: str                         # "Tableau出现频率45%，缺失将影响XX个岗位"
```

## 4. 模块设计

### 4.1 数据接入层 (`src/io/`)

#### BaseAdapter

```python
class BaseAdapter(ABC):
    @abstractmethod
    def fetch_jobs(self, **kwargs) -> list[JobItem]:
        """获取岗位数据，子类实现"""
        pass
```

用户继承 `BaseAdapter`，实现 `fetch_jobs()` 返回 `list[JobItem]`。详见 `docs/adapter_dev.md`。

#### DemoAdapter

内置模拟数据生成器，生成符合真实招聘市场统计规律的演示数据。

**生成规则**:

| 字段 | 生成逻辑 |
|------|---------|
| 城市 | 北上深杭 70%，成都/武汉/南京等 30% |
| 薪资 | 对数正态分布，15-25K 集中，50K+ 长尾；北京比成都高约 30% |
| 学历 | 本科 55%，硕士 25%，大专 15%，博士 5% |
| 经验 | 3-5年 40%，1-3年 30%，5-10年 20%，其他 10% |
| 技能 | Python/SQL/Excel >50%，Spark/Hadoop/Tableau 中频，高薪必带 Spark |
| 公司规模 | 100-499人 30%，1000-9999人 40%，10000+ 20% |

**过滤参数**:

```python
def fetch_jobs(
    self,
    n_samples: int = 500,
    city: str | None = None,           # 过滤城市
    job_keyword: str | None = None,    # 过滤岗位关键词
    education: str | None = None,      # 过滤学历
    experience: str | None = None,     # 过滤经验
) -> list[JobItem]:
```

**防死循环安全阀**: `MAX_GENERATE_RATIO = 5`，最多生成 `n_samples × 5` 条，仍不够则返回实际数量。

#### Importer

支持 CSV/JSON/SQLite 三种格式导入，导入时通过 JobItem validator 自动解析薪资字符串。

### 4.2 工具层 (`src/utils/`)

| 文件 | 职责 | 核心函数 |
|------|------|---------|
| `salary_parser.py` | 薪资字符串解析 | `parse_salary_string("15-25K·14薪")` → `SalaryParsed(min=15, max=25, median=20, months=14)` |
| `text_processor.py` | 文本预处理 | `tokenize()` jieba分词、`compute_tfidf()` TF-IDF 向量化 |
| `stat_helper.py` | 统计工具 | `normalize()`、`bin_values()`、`safe_percentile()` |

### 4.3 分析模块 (`src/analyzer/`)

#### salary_analyzer.py
- 薪资分布直方图（按 config.yaml 的 bins 分箱）
- 城市薪资对比（箱线图）
- 经验-薪资曲线
- 学历-薪资对比
- 行业薪资排行

#### skill_analyzer.py
- 高频技能统计（低于 min_frequency 不展示）
- 技能-薪资关联分析（有该技能 vs 无该技能的薪资差异）
- 技能组合价值分析
- 技能词云

#### competitive_analyzer.py

**竞争指数公式**:

```
竞争指数 = w1 × 标准化(岗位密度) + w2 × 标准化(薪资中位数) + w3 × 标准化(学历要求放宽度)

其中:
  岗位密度 = 该城市该岗位的招聘数量 / 该城市总招聘数量
  学历要求放宽度 = 1 - (要求本科及以上的岗位数 / 该城市该岗位总岗位数)
  w1=0.4, w2=0.3, w3=0.3（可在 config.yaml 中配置）

解读:
  岗位密度高 → 机会多 → 竞争指数低（对求职者有利）
  薪资中位数高 → 待遇好 → 竞争指数高（对求职者不利）
  学历放宽度高 → 门槛低 → 竞争指数高（对求职者不利）
```

最终归一化到 0-100，数值越高表示竞争越激烈。

#### strategy_advisor.py

**输入**: 用户画像 + 岗位数据  
**输出**: `StrategyReport`

输出包含三个部分:
1. **TOP 5 匹配岗位画像**: 公司/薪资/技能要求/匹配度评分
2. **短板诊断**: 缺失技能及其对命中率的影响
3. **行动建议**: 按优先级排序的具体行动方案

#### resume_matcher.py

**输入**: 用户简历文本 + 岗位 `job_description`  
**算法**: TF-IDF 相似度 + 技能关键词匹配  
**输出**: 匹配度评分 (0-100) + 匹配/缺失技能列表

### 4.4 可视化模块 (`src/visualizer/dashboard.py`)

- 每个分析模块独立生成一个 HTML（salary.html、skill.html、competitive.html、strategy.html）
- `generate_index_page()` 生成汇总索引页 `index.html`
- 索引页布局：顶部关键指标摘要卡片 + Tab 切换 + iframe 嵌入各模块页面
- 用户打开一个 `index.html` 即可查看全部图表

## 5. 配置系统

### 5.1 配置加载优先级

```
CLI 参数 > config.yaml > 内置默认值
```

即使 `config.yaml` 不存在也能运行（使用默认配置 + demo 数据源）。

### 5.2 config.yaml 完整结构

```yaml
data:
  source: "demo"              # demo | csv | sqlite | adapter
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

### 5.3 用户画像输入

三种方式:

| 方式 | 命令 | 场景 |
|------|------|------|
| config.yaml | 预先填写 `resume` 字段 | 重复使用 |
| CLI 参数 | `--skills "Python,SQL" --city "成都" --experience "3-5年" --salary "18-25K"` | 临时指定 |
| 交互式引导 | `python run_analysis.py --interactive` | 首次使用 |

交互式引导完成后自动写入 config.yaml，下次无需重复输入。

**无画像时降级**: 跳过 strategy_advisor 和 resume_matcher，仅运行薪资/技能/竞争度分析，输出 3 模块报告并提示用户配置画像。

## 6. 合规设计

| 措施 | 说明 |
|------|------|
| 无爬虫代码 | 主仓库不含任何可运行的爬虫 |
| BaseAdapter 接口 | 用户自行实现数据获取，项目不提供 |
| 免责声明 | README + LICENSE 双重声明，用户自行承担数据获取合规责任 |
| 反爬指南 | `docs/anti_crawling_guide.md` 纯学术讨论，不贴可用代码 |
| License | MIT |

## 7. 依赖

```toml
[project]
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
```

## 8. 目录结构

```
job_market_analyzer/
├── README.md                  # 徽章 + 免责声明 + 快速入门
├── LICENSE                    # MIT
├── pyproject.toml             # 依赖管理
├── config.yaml                # 全局配置（全部有默认值，可零配置启动）
├── data/
│   ├── demo/                  # 预制 CSV 演示数据
│   └── sample/                # 用户放自己的 CSV
├── src/
│   ├── schema.py              # JobItem + StrategyReport 等数据模型
│   ├── config.py              # 配置加载器（CLI > yaml > 默认值）
│   ├── io/
│   │   ├── base_adapter.py    # BaseAdapter 抽象类
│   │   ├── demo_adapter.py    # 模拟数据生成器（含防死循环安全阀）
│   │   └── importer.py        # CSV/JSON/SQLite 导入
│   ├── utils/
│   │   ├── salary_parser.py   # 薪资字符串解析
│   │   ├── text_processor.py  # 分词 + TF-IDF
│   │   └── stat_helper.py     # 统计工具
│   ├── analyzer/
│   │   ├── salary_analyzer.py
│   │   ├── skill_analyzer.py
│   │   ├── competitive_analyzer.py
│   │   ├── strategy_advisor.py
│   │   └── resume_matcher.py
│   └── visualizer/
│       └── dashboard.py       # Plotly HTML 看板 + 汇总索引页
├── docs/
│   ├── anti_crawling_guide.md # 反爬技术指南（学术层面）
│   └── adapter_dev.md         # Adapter 开发指南
└── scripts/
    └── run_analysis.py        # 一键运行入口
```

## 9. 启动命令

```bash
# 零配置启动（demo 数据，3模块报告）
python scripts/run_analysis.py

# 交互式配置画像后生成完整5模块报告
python scripts/run_analysis.py --interactive

# 指定数据源和个人画像
python scripts/run_analysis.py --source csv --csv-path data/sample/jobs.csv \
  --skills "Python,SQL,Tableau" --city "成都" --experience "3-5年" --salary "18-25K"
```

## 10. 设计决策记录

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 项目定位 | 分析工具（不爬数据） | 规避法律风险，聚焦核心价值 |
| 爬虫代码 | BaseAdapter 接口 | 用户自行实现，项目不提供可运行爬虫 |
| 数据契约 | Pydantic JobItem | 类型安全 + 自动验证 + 薪资自动解析 |
| 演示数据 | 代码生成 + 预制CSV | 符合真实分布，双模式支持 |
| 可视化 | Plotly + HTML | 轻量、交互式、无需后端 |
| 索引页 | iframe + Tab切换 | 单页查看全貌 |
| 配置 | CLI > yaml > 默认值 | 零配置可启动 |
| 画像缺失 | 降级跳过 | 不阻塞基础分析 |
| 竞争指数 | 加权公式(0.4/0.3/0.3) | 可解释、可配置 |
| License | MIT | 最宽松，利于传播 |
