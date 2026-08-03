# tests/test_salary_parser.py
from job_market_analyzer.utils.salary_parser import parse_salary_string


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
