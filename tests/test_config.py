# tests/test_config.py
from job_market_analyzer.config import Config


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
