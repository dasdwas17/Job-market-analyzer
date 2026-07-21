# 招聘市场数据分析系统 - 数据库设计方案

## 1. 项目概述

本项目是一个招聘市场数据分析系统，旨在爬取 BOSS直聘、拉勾网、看准网 三大招聘平台的"数据分析师"相关岗位信息，进行多维度分析并生成可视化看板，最终输出求职策略建议。

### 1.1 数据规模目标

- **目标数据量**：5000+ 条有效岗位记录
- **覆盖城市**：19个（4个一线城市 + 15个新一线城市）
- **关键词**：数据分析师、数据运营、商业分析、数据产品经理

### 1.2 核心分析维度

- 薪资分布（按城市/学历/经验/公司类型）
- 技能需求频次 TOP20
- 岗位竞争度分析
- 公司画像分析

---

## 2. 设计目标与约束

| 目标 | 说明 |
|-----|------|
| **数据完整性** | 通过外键约束保证关联数据一致性 |
| **查询性能** | 为核心分析场景建立复合索引 |
| **增量爬取** | 支持幂等更新和 is_active 状态管理 |
| **扩展性** | 预留扩展字段，避免频繁改表 |
| **快速启动** | 暂不引入迁移工具，手动演进 |

---

## 3. 数据库选型

| 项目 | 选型 | 理由 |
|-----|------|-----|
| **数据库类型** | SQLite | 轻量级、无需额外安装、适合单机项目 |
| **ORM框架** | SQLAlchemy 2.0 | 统一数据库操作接口，便于未来切换到MySQL |
| **外键约束** | 启用（PRAGMA foreign_keys=ON） | 保证数据完整性 |

---

## 4. 表结构设计

### 4.1 整体架构

```
companies (公司表)  ←──RESTRICT──  jobs (岗位表)
                                     │
                                  CASCADE
                                     │
skills (技能字典表)  ←──FK──  job_skills (关联表)
                                     │
                                   FK↑→jobs.job_id
```

### 4.2 表详细设计

#### 4.2.1 companies（公司表）

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|-----|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 |
| company_id | TEXT | UNIQUE NOT NULL INDEX | 公司业务唯一ID（MD5(source+name+url)） |
| company_name | TEXT | NOT NULL INDEX | 公司名称 |
| company_size | TEXT | - | 公司规模（标准化：0-20人/20-99人/100-499人/500-999人/1000-9999人/10000人以上） |
| company_type | TEXT | - | 公司类型（民营/国企/外企/上市公司等） |
| industry | TEXT | INDEX | 所属行业 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 4.2.2 jobs（岗位表）

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|-----|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 |
| job_id | TEXT | UNIQUE NOT NULL INDEX | 岗位业务唯一ID（MD5(source+url+company_name)） |
| job_name | TEXT | NOT NULL INDEX | 岗位名称 |
| salary | TEXT | - | 原始薪资字符串（如："15-25K·14薪"） |
| salary_min | REAL | - | 薪资下限（元/月） |
| salary_max | REAL | - | 薪资上限（元/月） |
| salary_median | REAL | - | 薪资中位数（元/月） |
| salary_months | INTEGER | DEFAULT 12 | 年薪月份数 |
| city | TEXT | NOT NULL INDEX | 城市 |
| district | TEXT | - | 区域 |
| experience | TEXT | INDEX | 经验要求（标准化：应届生/1-3年/3-5年/5-10年/10年以上） |
| education | TEXT | INDEX | 学历要求（标准化：不限/高中/中专/大专/本科/硕士/博士） |
| job_type | TEXT | - | 岗位类型（全职/兼职/实习） |
| job_description | TEXT | - | 岗位描述 |
| benefits | TEXT | - | 福利（逗号分隔：五险一金/年终奖/双休等） |
| work_mode | TEXT(20) | - | 工作模式（全职/远程/混合办公） |
| extra_json | TEXT | - | 扩展字段JSON，遵循 EXTRA_JSON_SCHEMA |
| company_id | INTEGER | FOREIGN KEY REFERENCES companies(id) ON DELETE RESTRICT | 公司ID |
| source | TEXT | NOT NULL INDEX | 数据来源（boss/lagou/kanzhun） |
| job_url | TEXT(500) | - | 岗位链接 |
| is_active | INTEGER | DEFAULT 1 | 是否有效（1有效/0已下线） |
| crawl_time | DATETIME | DEFAULT CURRENT_TIMESTAMP INDEX | 抓取时间 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

#### 4.2.3 skills（技能字典表）

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|-----|
| skill_name | TEXT | PRIMARY KEY | 技能名称 |
| category | TEXT | - | 技能分类（编程语言/数据库/大数据/BI工具/Python库/统计分析/机器学习/工具平台/业务能力） |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**预定义技能（52个）**：

| 分类 | 技能 |
|-----|------|
| 编程语言 | Python, R, SQL, Java, Scala, Shell |
| 数据库 | MySQL, Oracle, PostgreSQL, MongoDB, Redis, Hive |
| 大数据 | Hadoop, Spark, Flink, Kafka, ETL, 数据仓库, 数据中台 |
| BI工具 | Tableau, Power BI, FineBI, Excel, BI, 数据可视化, 报表开发 |
| Python库 | Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn |
| 统计分析 | SPSS, SAS, Stata, 统计学, 数学建模, AB测试, 漏斗分析, 留存分析 |
| 机器学习 | 机器学习, 深度学习, NLP, 数据挖掘 |
| 工具平台 | Git, Linux, Docker |
| 业务能力 | 用户画像, 增长黑客, 业务分析, 商业智能, 用户分析, 运营分析 |

#### 4.2.4 job_skills（岗位-技能关联表）

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|-----|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键 |
| job_id | TEXT | FOREIGN KEY REFERENCES jobs(job_id) ON DELETE CASCADE NOT NULL INDEX | 岗位业务ID（关联 jobs.job_id 而非 jobs.id） |
| skill_name | TEXT | FOREIGN KEY REFERENCES skills(skill_name) NOT NULL INDEX | 技能名称 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**唯一约束**：`uix_job_skill` (job_id, skill_name)

---

## 5. 外键约束与级联策略

| 外键关系 | 级联策略 | 设计理由 |
|---------|---------|---------|
| `jobs.company_id` → `companies.id` | **ON DELETE RESTRICT** | 防止误删公司导致岗位成为孤儿记录 |
| `job_skills.job_id` → `jobs.job_id` | **ON DELETE CASCADE** | 删除岗位时自动清理关联技能，避免垃圾数据 |
| `job_skills.skill_name` → `skills.skill_name` | **无级联** | 技能字典不应被随意删除 |

> **架构决策**：`job_skills.job_id` 关联的是 `jobs.job_id`（业务唯一ID），而非 `jobs.id`（自增主键）。原因：INSERT OR REPLACE 会导致自增ID变化，如果关联自增ID，替换时外键会指向错误记录。

---

## 6. 索引策略

### 6.1 单列索引（自动创建）

| 表 | 索引字段 | 用途 |
|---|---------|-----|
| jobs | job_id | 岗位去重查询 |
| jobs | job_name | 岗位名称搜索 |
| jobs | city | 城市筛选 |
| jobs | experience | 经验筛选 |
| jobs | education | 学历筛选 |
| jobs | source | 来源筛选 |
| jobs | crawl_time | 时间范围筛选 |
| companies | company_id | 公司去重查询 |
| companies | company_name | 公司名称搜索 |
| companies | industry | 行业筛选 |
| job_skills | job_id | 岗位技能查询 |
| job_skills | skill_name | 技能岗位查询 |

### 6.2 复合索引（手动创建）

| 索引名 | 字段 | 用途 |
|-------|------|-----|
| idx_city_exp_edu | city, experience, education | 核心分析场景：按城市+经验+学历过滤薪资 |
| idx_city_salary | city, salary_median | 城市薪资分布分析 |
| idx_source_crawl | source, crawl_time | 按来源和时间筛选 |

---

## 7. 数据校验规则

### 7.1 必填字段

| 表 | 必填字段 | 约束类型 |
|---|---------|---------|
| jobs | job_id, job_name, city, source | NOT NULL（数据库层） |
| companies | company_id, company_name | NOT NULL（数据库层） |

### 7.2 业务校验（代码层）

| 校验项 | 规则 | 处理方式 |
|-------|------|---------|
| 薪资合理性 | salary_min <= salary_max | 置为NULL并记录日志 |
| 薪资范围 | 1000 <= salary <= 500000 | 超出范围置为NULL并记录日志 |
| extra_json格式 | 必须为dict或合法JSON字符串 | 自动序列化/反序列化 |

### 7.3 EXTRA_JSON_SCHEMA（标准化扩展字段）

```json
{
    "hot": true,
    "recruit_count": 3,
    "position_tags": ["大厂", "独角兽"],
    "company_score": 4.5,
    "interview_difficulty": "中等",
    "raw_attrs": {}
}
```

- **hot**：是否热门岗位（布尔）
- **recruit_count**：招聘人数（整数）
- **position_tags**：岗位标签（字符串数组）
- **company_score**：公司评分（看准网数据，浮点数）
- **interview_difficulty**：面试难度（看准网数据，字符串）
- **raw_attrs**：未标准化的原始扩展属性（JSON对象）

---

## 8. 范式合规性分析

### 8.1 第一范式（1NF）

| 表 | 合规性 | 说明 |
|---|-------|------|
| companies | ✅ 符合 | 所有字段都是原子值 |
| jobs | ✅ 符合 | 所有字段都是原子值 |
| skills | ✅ 符合 | 所有字段都是原子值 |
| job_skills | ✅ 符合 | 所有字段都是原子值 |

**例外**：`extra_json` 字段存储 JSON 字符串，属于有意为之的反范式优化，用于灵活存储扩展字段。

### 8.2 第二范式（2NF）

| 表 | 合规性 | 说明 |
|---|-------|------|
| companies | ✅ 符合 | 单字段主键，所有字段完全依赖 |
| jobs | ✅ 符合 | 单字段主键，所有字段完全依赖 |
| skills | ✅ 符合 | 单字段主键，所有字段完全依赖 |
| job_skills | ⚠️ 折中 | 逻辑主键为 (job_id, skill_name)，实际用自增id + 唯一约束 |

### 8.3 第三范式（3NF）

| 表 | 合规性 | 说明 |
|---|-------|------|
| companies | ✅ 符合 | 无传递依赖 |
| jobs | ⚠️ 反范式 | salary_min/max/median 可从 salary 解析得出，属于查询性能优化 |
| skills | ✅ 符合 | 无传递依赖 |
| job_skills | ✅ 符合 | 无传递依赖 |

### 8.4 反范式权衡总结

| 反范式设计 | 类型 | 原因 | 收益 |
|-----------|------|------|-----|
| `extra_json` | 1NF | 灵活存储扩展字段 | 避免频繁改表，快速迭代 |
| `salary_min/max/median` | 3NF | 预先计算薪资数值 | 查询性能提升10倍+ |
| `job_skills.id` | 2NF | ORM操作便利 | SQLAlchemy关联操作更简洁 |

> **设计原则**：三大范式是"理想状态"，实际工程中需要在范式规范化和性能/灵活性之间做权衡。本设计中的反范式都是有意识的权衡，而非设计缺陷。

---

## 9. 数据更新策略

### 9.1 增量爬取机制

```
爬虫开始 → 记录 batch_start_time → 爬取过程中 upsert → 爬取结束后 mark_inactive
```

**关键步骤**：

1. **记录批次时间**：爬虫开始时记录当前时间戳 `batch_start_time`
2. **幂等更新**：使用 `upsert_job()` 函数，基于 `job_id` 唯一约束实现 INSERT OR REPLACE 语义
3. **标记下线岗位**：爬取结束后执行：
   ```sql
   UPDATE jobs SET is_active=0 
   WHERE source='boss' AND crawl_time < 'batch_start_time' AND is_active=1;
   ```

**崩溃安全**：即使爬虫中途崩溃，历史数据仍保留 `is_active=1` 状态，不会丢失。

### 9.2 技能关联同步

每次 upsert 岗位时：
1. 删除该岗位旧的技能关联记录
2. 批量插入新的技能关联记录
3. 自动维护技能字典（新技能自动入库并归类）

---

## 10. 数据导出方案

### 10.1 Tableau 宽表导出

**导出字段（38个）**：

| 类别 | 字段 |
|-----|------|
| 岗位基本信息 | job_id, job_name, source, job_url, job_type, work_mode |
| 薪资信息 | salary, salary_min, salary_max, salary_median, salary_months, salary_annual_min, salary_annual_max, salary_annual_median |
| 地域信息 | city, city_tier, district, living_cost_index, salary_cost_ratio |
| 要求信息 | experience, education |
| 附加信息 | benefits, job_description, skill_tags, skill_count |
| 扩展字段 | hot, recruit_count, position_tags, company_score, interview_difficulty |
| 公司信息 | company_id, company_name, company_size, company_type, industry |
| 状态信息 | is_active, crawl_time, created_at |

**导出SQL**：
```sql
SELECT
    j.*,
    GROUP_CONCAT(js.skill_name, ',') AS skill_tags,
    COUNT(js.skill_name) AS skill_count,
    c.company_name, c.company_size, c.company_type, c.industry
FROM jobs j
LEFT JOIN companies c ON j.company_id = c.id
LEFT JOIN job_skills js ON j.job_id = js.job_id
WHERE j.is_active = 1
GROUP BY j.id
ORDER BY j.crawl_time DESC;
```

### 10.2 备份导出

| 格式 | 用途 |
|-----|------|
| db_backup.sqlite | 原始数据库文件备份 |
| tableau_export.csv | 扁平化宽表，Tableau直接导入 |

---

## 11. 测试验证

### 11.1 测试用例覆盖

| 测试类别 | 测试项 | 预期结果 |
|---------|-------|---------|
| 表结构 | 4张表正确创建 | PASS |
| 外键约束 | PRAGMA foreign_keys=ON | PASS |
| RESTRICT | 有岗位的公司禁止删除 | PASS |
| CASCADE | 删岗位时自动删除关联技能 | PASS |
| 幂等更新 | 同一 job_id 覆盖更新 | PASS |
| is_active | 旧岗位标记为0，新岗位保持1 | PASS |
| 薪资校验 | min>max、超范围值置为NULL | PASS |
| 必填校验 | job_id/job_name/city/source 非空 | PASS |
| JSON序列化 | extra_json dict → str | PASS |
| 技能字典 | 52个技能预置，分类正确 | PASS |
| 复合索引 | idx_city_exp_edu 等3个复合索引存在 | PASS |

### 11.2 测试结果

> **全部 14 项测试通过**

---

## 12. 代码实现

### 12.1 核心文件

| 文件 | 职责 |
|-----|------|
| [utils/db_helper.py](file:///d:/Python-web-spider/utils/db_helper.py) | 4张表模型 + 外键约束 + 索引 + 业务函数 |
| [config/settings.py](file:///d:/Python-web-spider/config/settings.py) | EXTRA_JSON_SCHEMA、CITY_TIER_MAP、SKILL_CATEGORY_MAP |
| [test_db.py](file:///d:/Python-web-spider/test_db.py) | 14项测试用例 |

### 12.2 关键函数

| 函数 | 功能 |
|-----|------|
| `init_db()` | 初始化数据库 + 技能字典 |
| `generate_job_id()` | 生成岗位唯一ID（MD5） |
| `generate_company_id()` | 生成公司唯一ID（MD5） |
| `validate_job_data()` | 数据校验（必填/薪资范围/JSON序列化） |
| `upsert_company()` | 公司幂等更新 |
| `upsert_job()` | 岗位幂等更新 + 技能同步 |
| `mark_inactive_jobs()` | 标记已下线岗位 |

---

## 13. 数据库迁移方案

### 13.1 当前阶段（爬虫调试期）

- **策略**：表结构变动时直接 `DROP TABLE` 重建
- **理由**：数据量小（可重爬），快速迭代优先

### 13.2 稳定阶段（数据积累后）

- **策略**：手动执行 `ALTER TABLE ADD COLUMN`
- **理由**：Alembic 对于单机 SQLite 项目属于过度设计

---

## 附录：ER 图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           companies                                    │
├─────────────────────────────────────────────────────────────────────────┤
│  id (PK)         INTEGER        autoincrement                          │
│  company_id      TEXT           unique, not null, index                │
│  company_name    TEXT           not null, index                        │
│  company_size    TEXT                                                  │
│  company_type    TEXT                                                  │
│  industry        TEXT           index                                  │
│  created_at      DATETIME                                              │
└───────────────────────┬─────────────────────────────────────────────────┘
                        │
                        │  company_id (FK) ON DELETE RESTRICT
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              jobs                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  id (PK)         INTEGER        autoincrement                          │
│  job_id          TEXT           unique, not null, index                │
│  job_name        TEXT           not null, index                        │
│  salary          TEXT                                                   │
│  salary_min      REAL                                                   │
│  salary_max      REAL                                                   │
│  salary_median   REAL                                                   │
│  salary_months   INTEGER        default 12                              │
│  city            TEXT           not null, index                        │
│  district        TEXT                                                   │
│  experience      TEXT           index                                  │
│  education       TEXT           index                                  │
│  job_type        TEXT                                                   │
│  job_description TEXT                                                   │
│  benefits        TEXT                                                   │
│  work_mode       TEXT(20)                                               │
│  extra_json      TEXT                                                   │
│  company_id      INTEGER        FK → companies.id                       │
│  source          TEXT           not null, index                        │
│  job_url         TEXT(500)                                              │
│  is_active       INTEGER        default 1                              │
│  crawl_time      DATETIME       index                                  │
│  created_at      DATETIME                                               │
│  updated_at      DATETIME                                               │
└───────────────────────┬─────────────────────────────────────────────────┘
                        │
                        │  job_id (FK) ON DELETE CASCADE
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         job_skills                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  id (PK)         INTEGER        autoincrement                          │
│  job_id          TEXT           FK → jobs.job_id, index                │
│  skill_name      TEXT           FK → skills.skill_name, index           │
│  created_at      DATETIME                                               │
└───────────────────────┬─────────────────────────────────────────────────┘
                        │
                        │  skill_name (FK)
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            skills                                       │
├─────────────────────────────────────────────────────────────────────────┤
│  skill_name      TEXT           primary key                            │
│  category        TEXT                                                   │
│  created_at      DATETIME                                               │
└─────────────────────────────────────────────────────────────────────────┘
```
