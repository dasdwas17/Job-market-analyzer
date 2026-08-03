# tests/test_stat_helper.py
import pytest

from job_market_analyzer.utils.stat_helper import bin_values, normalize, safe_percentile


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
