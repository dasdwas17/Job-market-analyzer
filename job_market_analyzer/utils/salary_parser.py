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
